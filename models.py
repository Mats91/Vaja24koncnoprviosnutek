from google.appengine.ext import ndb  #ndb je paket za bazo, tip podatkov ki vpisemo, string oziroma tekst

class Sporocilo(ndb.Model):
    vnos = ndb.StringProperty()
    nastanek = ndb.DateTimeProperty(auto_now_add=True) #iz ndb uvozis in potem auto zapise ko vneses
    izbrisan = ndb.BooleanProperty(default=False)
    cas = ndb.StringProperty()