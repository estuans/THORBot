#!/usr/bin/python

'''
THOR connects to an IRC network, joins a channel, and keeps a log of everything that goes on.
WolframAlpha integration will come later.
'''

#TWISTED Imports
from twisted.words.protocols import irc

#INTERNAL Imports
from modules import goslate

#SYS Imports
import time
import random

#OTHER Imports
import ConfigParser
import json
import urllib2
import ctypes
from operator import itemgetter

#Version Information

#None of the following lines down to the config parser are of any consequence
#to the code itself, and were merely added to poke fun at the sometimes
#arbitrary nature of version numbers in software today.

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
gobblenumber = random.choice(alphabet) + str(random.randrange(0, 2000)) + "." + str(random.randint(0, 1))

versionName = "Magni"
versionNumber = "{g}".format(g=gobblenumber)
versionEnv = "Python 2.7.3"

ctypes.windll.kernel32.SetConsoleTitleA("THORBot @ Valhalla")

#Config parser. Could be replaced in the future?

cfg = ConfigParser.RawConfigParser(allow_no_value=True)
cfg.read("magni.ini")

#Globals(These are ABSOLUTELY necessary to declare here, otherwise the code won't work.
#Don't sue me. I'm just making sure it won't throw syntax warnings at me.)
#TODO ... Clean these up. Seriously. Move them to appropriate locations in ThorBot.

illegal_channels = ['#jacoders']


class ThorBot(irc.IRCClient):
    """
    Primary IRC class. Controls just about everything that isn't a module.
    Below you'll find a bunch of options that are handled by hammer.ini.
    """

    def __init__(self):
        #TODO Cthulhu must answer for his crimes against my code!
        #nickname = cfg.get('Bot Settings', 'Nickname')
        #password = cfg.get('Bot Settings', 'NickPass')
        #realname = "THORBot @ VALHALLA"
        nickname = 'Magni'
        password = ''
        realname = 'Magni[THORBOT] @ VALHALLA'

        self.realname = realname
        self.nickname = nickname
        self.password = password
        self.lineRate = 1

    def connectionMade(self):
        #First we connect
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def irc_ERR_ERRONEUSNICKNAME(self, prefix, params):
        print "irc_ERR_ERRONEUSNICKNAME called"

    def irc_ERR_PASSWDMISMATCH(self, prefix, params):
        print "!!!INCORRECT PASSWORD!!!\n Check hammer.ini for the NICKPASS parameter"
        return

    #EVENTS

    def signedOn(self):
        #Called when signing on
        print "Signed on successfully"
        self.join(self.factory.channel)

    def joined(self, channel):
        #Called when joining a channel
        print "Joined %s" % channel
        self.sendLine("MODE {nickname} {mode}".format(nickname=self.nickname, mode="+B"))

    def userJoined(self, user, channel):
        #Called when another user joins a channel
        print "%s has joined %s" % (user, channel)

        chance = random.random()

        if chance >= 0.2:
            print "Welcomed %s. Chance: %s" % (user, chance)
            msg = "Welcome to %s, %s" % (channel, user)
            self.msg(channel, msg)
        if chance <= 0.2:
            print "Chance:", chance

    def kickedFrom(self, channel, kicker, message):
        self.join(channel)
        msg = "How fucking dare you, {ki}".format(ki=kicker)
        self.msg(channel, msg)

    def userKicked(self, kickee, channel, kicker, message):
        msg = "{us} must have pissed {ki} off!".format(us=kickee, ki=kicker)
        self.msg(channel, msg)

    def irc_unknown(self, prefix, command, params):
        #TODO send an error message describing why I /can't/ join the channel

        if command == "INVITE":
            if params[1] in illegal_channels[:]:
                print "INVITED BUT NOT ALLOWED TO JOIN"

            else:
                self.join(params[1])

    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]

        #Globals
        global chttb
        global randrep

        #TODO reformat the code to render the below variables redundant
        owner = cfg.get('Users', 'Owner')
        admins = cfg.get('Users', 'Admins')
        ignored = cfg.get('Users', 'Ignored')
        gglapi = cfg.get('API', 'Google')
        ggid = cfg.get('API', 'Google ID')

        #URL Fetchers & Integrated Utilities

        if msg.startswith("!t "):
            #Translates the source language into the target language

            gs = goslate.Goslate()

            wlist = msg.split(' ')

            slang = itemgetter(1)(wlist)
            tlang = itemgetter(2)(wlist)

            slangrep = '%s' % slang
            tlangrep = '%s' % tlang

            phrase = itemgetter(slice(3, None))(wlist)

            phrase_ = ' '.join(phrase)
            reply = gs.translate(phrase_, tlangrep, slangrep)

            self.msg(channel, reply.encode('UTF-8'))

        if msg.startswith("!dt "):
            #Translates the detected string to English

            gs = goslate.Goslate()

            wlist = msg.split(' ')

            trans = itemgetter(slice(1, None))(wlist)

            trans = ' '.join(trans)

            source = gs.detect(trans)
            reply = gs.translate(trans, 'en', source)

            self.msg(channel, reply.encode('UTF-8'))

        if msg.startswith("!g"):
            #Returns the first result off the page

            wlist = msg.split(' ')

            append = itemgetter(slice(1, None))(wlist)
            append = '+'.join(append)

            url = "https://www.googleapis.com/customsearch/v1?key=%s&cx=%s&q=%s&num=1" % (gglapi, ggid, append)
            metdat = urllib2.urlopen(url).read()
            parsdat = json.loads(metdat)
            items = parsdat['items']
            for result in items:
                link = result['link']

                self.msg(channel, link.encode('UTF-8'))

        if msg.startswith("!qdb"):
            #Fetches the quote with the assigned number from the ArloriaNET Quote Database

            wlist = msg.split(' ')

            addend = itemgetter(1)(wlist)
            url = "http://www.arloria.net/qdb/%s" % addend
            msg = url
            self.msg(channel, msg)

        if msg == "!joke":
            #Fetches an ol' fashioned Chuck Norris joke and prints it

            rq = urllib2.Request("http://api.icndb.com/jokes/random?")
            joke = urllib2.urlopen(rq).read()
            data = json.loads(joke)
            msg = data['value']['joke']
            msg = msg.replace('&quot;', '"')
            self.msg(channel, msg.encode('utf-8', 'ignore'))

        #Logging Things

        #Misc
        if msg.startswith("!s ") and user == ignored:
            msg == "No."
            self.msg(channel, msg)

        if msg.startswith("!s ") and user != ignored:
            #Sends message to target channel

            wlist = msg.split(' ')
            targ = itemgetter(1)(wlist)

            #Slice 'n dice the message we want to send
            tsay = itemgetter(slice(2, None))(wlist)

            #Piece it back together
            tsay = ' '.join(tsay)

            self.sendLine('PRIVMSG {targ} {tsay}'.format(targ=targ, tsay=tsay))

        if msg.startswith("!inv"):
            #Invites target user into present channel.
            #May be expanded upon in the future.

            invchan = channel
            wlist = msg.split(' ')
            targ = itemgetter(1)(wlist)

            self.sendLine('INVITE {t} {c}'.format(c=invchan, t=targ))

            pending = "Inviting {t} into {c}".format(t=targ, c=channel)

            self.msg(channel, pending)

        if msg.startswith("!j "):

            #Joins designated channel.

            wlist = msg.split(' ')
            targ = itemgetter(1)(wlist)

            if targ in illegal_channels[:]:
                #If target is found in illegal channels list,
                #cancels operation and apologises in a polite manner.

                msg = "Sorry, {u}, I'm too sane to join {t}".format(u=user, t=targ)
                self.msg(channel, msg)

            else:
                #Checks target against illegal channels list.
                #If not present, will join the channel.

                self.sendLine('join {c}'.format(c=targ))
                msg = "Joining {c}".format(c=targ)

                self.msg(channel, msg)

        if msg.startswith("!leave "):
            #Sends a part message to the server,
            #leaving the designated channel(even if not sent from aforementioned channel)

            wlist = msg.split(' ')
            targ = itemgetter(1)(wlist)

            msg = "Leaving {c}".format(c=targ)
            self.msg(channel, msg)

            self.sendLine('part {c}'.format(c=targ))

        if msg.startswith("!nick ") and user == owner:
            text = msg.split()
            new_nick = itemgetter(1)(text)
            self.nickname = new_nick

            self.sendLine('nick {c}'.format(c=new_nick))

        if msg == "!dance":
            msg = "<(o.o<)\r\n" \
                  "(>o.o)>\r\n" \
                  "^(o.o)^\r\n" \
                  "v(o.o)v\r\n" \
                  "<(o.o)>\r\n"
            self.msg(channel, msg)

        if msg == "!help":
            #TODO find a better way to list commands. Perhaps in a private message?

            msg = "Commands: !dance, !j [channel], !leave [channel], !disconnect, !rickroll, !joke, " \
                  "!chatterbot [on/off], !rejoin, !version, !info, !inv [user], !s [channel] [message]" \
                  ", !t [source lang] [target lang], !dt [foreign text], !g [search term], !qdb [number]"
            self.msg(channel, msg)

        if msg == "!rejoin":
            #Rejoins channel
            self.leave(channel, reason="Cycling")
            time.sleep(1)
            self.join(channel)
            time.sleep(1)
            msg = "Rejoined successfully"
            self.msg(channel, msg)

        if msg == "!version":
            #Passes version and version number to channel
            msg = "Version | {vnam} | {vnum} | {venv}".format(vnam=versionName, vnum=versionNumber,
                                                                         venv=versionEnv)
            self.msg(channel, msg)

        if msg == "!rickroll":
            #... It was a silly idea, okay?
            msg = "Never gonna give you up,\nNever gonna let you down,\n" \
                  "Never gonna run around and desert you.\n" \
                  "Never gonna make you cry,\nNever gonna say goodbye,\nNever gonna tell a lie and hurt you.\n"
            self.msg(channel, msg)

        if msg.startswith("!info"):
            #If called, states owner and nickname
            owner = cfg.get('Users', 'Owner')
            msg = "Hello, {u}. I am {n}, a bot belonging to {o}".format(u=user, n=self.nickname, o=owner)
            self.msg(channel, msg)

        if msg == "!disconnect" and user == (owner or admins):
            msg = "Severing connection..."
            self.msg(channel, msg)
            time.sleep(2)
            self.quit(message="Disconnected per request")
            print "Disconnected."

    def action(self, user, channel, message):
        user = user.split('!', 1)[0]

    #IRC CALLBACKS

    def irc_NICK(self, prefix, params):
        old_nick = prefix.split('!')[0]
        new_nick = params[0]

    def alterCollidedNick(self, nickname):
        return nickname + 'Clone'