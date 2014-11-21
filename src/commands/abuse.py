from operator import itemgetter
import random

# Project imports
from .base import BaseCommand, OneLiner
from ..modules import dictionaries

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


        if msg == "!joke":
            #I hate this function. Why do I keep it?

            r = requests.get("http://api.icndb.com/jokes/random?")
            rj = r.json()
            msg = rj['value']['joke']
            self.msg(channel, msg.encode('utf-8', 'ignore'))

        # Misc

class PornHub(OneLiner):
    listen = 'pornhub'
    msg = "I'm not that kind of bot."

class PronHub(OneLiner):
    listen = "pronhub"
    msg = "Did you mean !pornhub?"