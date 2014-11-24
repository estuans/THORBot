from operator import itemgetter
import random
import requests
import HTMLParser

# Project imports
from .base import BaseCommand, OneLiner
from ..modules import dictionaries

htmlparse = HTMLParser.HTMLParser()

class Slap(BaseCommand):

    help_message = "Slaps named user with a weapon from the armoury"
    listen = "slap"

    def perform_action(self):
        user = self.user.split('!', 1)[0]
        slappee = self.message.split(' ')
        slapped = itemgetter(1)(slappee)
        weapon = dictionaries.Randict.weapons
        weaponscore = random.choice(weapon)
        attack = "\x02%s slapped %s with %s\x02" % (user, slapped, weaponscore)

        self.respond(attack)

class Joke(BaseCommand):
    listen = "joke"

    def perform_action(self):
        r = requests.get("http://api.icndb.com/jokes/random?")
        rj = r.json()
        msg = rj['value']['joke']
        self.respond(htmlparse.unescape(msg).encode('utf-8', 'ignore'))

class PornHub(OneLiner):
    listen = 'pornhub'
    msg = "I'm not that kind of bot."

class PronHub(OneLiner):
    listen = "pronhub"
    msg = "Did you mean !pornhub?"