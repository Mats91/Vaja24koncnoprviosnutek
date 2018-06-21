#!/usr/bin/env python
import os
import jinja2
import webapp2

from models import Sporocilo
import time
from google.appengine.api import users
from google.appengine.api import urlfetch
import json


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if params is None:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            logiran = True
            logout_url = users.create_logout_url('/')

            params = {"logiran": logiran, "logout_url": logout_url, "user": user}
        else:
            logiran = False
            login_url = users.create_login_url('/')

            params = {"logiran": logiran, "login_url": login_url, "user": user}

        return self.render_template("hello.html", params)


    def post(self):
        rezultat = "Uporabnik je vpisal: " + self.request.get('vnos')
        params = {
            'rezultat': rezultat
        }

        return self.render_template("hello.html", params=params)


class RezultatHandler(BaseHandler):
    def post(self):
        vnos = self.request.get('vnos')
        sporocilo = Sporocilo(vnos=vnos) #inicializiramo sporocilo ki mu damo kar smo poslali v formi
        sporocilo.put() #za shrant

        #sporocila = Sporocilo.query(Sporocilo.izbrisan == False).fetch()  # ukaz za potegnemo sporocilo iz baze
        #params = {"sporocila": sporocila}
        #return self.render_template("seznam_sporocil.html", params=params)
        return self.redirect_to('seznam_sporocil')

class SeznamSporocilHandler(BaseHandler):
    def get(self):
        time.sleep(0.3)
        sporocila = Sporocilo.query(Sporocilo.izbrisan == False).fetch() #ukaz za potegnemo sporocilo iz baze
        params = {"sporocila": sporocila}
        return self.render_template("seznam_sporocil.html", params=params)

class PosameznoSporociloHandler(BaseHandler):
    def get(self, sporocilo_id): #poleg self se drug parameter
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id)) #getbyid je metoda in v intiger
        params = {"sporocilo": sporocilo}
        return self.render_template("posamezno_sporocilo.html", params=params)

class PrejetoSporociloHandler(BaseHandler):

    def get(self, sporocilo_id):
        pass

class UrediSporociloHandler(BaseHandler):
    def get(self, sporocilo_id): #poleg self se drug parameter iz urlja se potegne
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id)) #getbyid je metoda in v intiger
        params = {"sporocilo": sporocilo}
        return self.render_template("uredi_sporocilo.html", params=params)

    def post(self, sporocilo_id):
        vnos = self.request.get('vnos')
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        sporocilo.vnos = vnos
        sporocilo.put()
        return self.redirect_to("seznam_sporocil")

class IzbrisiSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
            sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
            params = {"sporocilo": sporocilo}
            return self.render_template("izbrisi_sporocilo.html", params=params)

    def post(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        sporocilo.izbrisan = True
        sporocilo.key.delete()
        return self.redirect_to("seznam_sporocil")

class WeatherHandler(BaseHandler):
    def get(self):
        url = "http://api.openweathermap.org/data/2.5/weather?q=London,uk&units=metric&appid=eda1b8211059e52682d0652026080d6c"

        result = urlfetch.fetch(url)

        podatki = json.loads(result.content)

        params = {"podatki": podatki}

        self.render_template("vreme.html", params)

    def post(self):
        city = self.request.get('city')
        url = "http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid=eda1b8211059e52682d0652026080d6c".format(city=city)
        print url
        result = urlfetch.fetch(url)

        podatki = json.loads(result.content)
        print podatki

        params = {"podatki": podatki}

        if podatki['weather'][0]['description'] == 'clear sky':
            podatki['icon'] = 'fa-sun'
        elif 'cloud' in podatki['weather'][0]['description']:
            podatki['icon'] = 'fa-cloud'
        else:
            podatki['icon']= 'fa-neki'

        self.render_template("vreme.html", params)


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/rezultat', RezultatHandler),
    webapp2.Route('/seznam_sporocil', SeznamSporocilHandler, name='seznam_sporocil'),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>', PosameznoSporociloHandler), #imeparametradvopicje in regex \d+ (enkrat ali vec) izraz
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/uredi', UrediSporociloHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/izbrisi', IzbrisiSporociloHandler),
    webapp2.Route('/vreme', WeatherHandler),
], debug=True)