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
import feedparser
import ctypes
from operator import itemgetter

#HTTP Handlers
import requests

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

    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]

        #URL Fetchers & Integrated Utilities

        if msg.startswith("!bbc"):
            fd = feedparser.parse('http://feeds.bbci.co.uk/news/rss.xml?edition=int')
            title = fd.entries[0].title
            description = fd.entries[0].description
            link = fd.entries[0].link
            fd = "%s - %s - Read More: %s" % (title, description, link)

            self.msg(channel, fd.encode('UTF-8'))

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

        if msg.startswith("!qdb"):
            #Fetches the quote with the assigned number from the ArloriaNET Quote Database

            wlist = msg.split(' ')

            addend = itemgetter(1)(wlist)
            url = "http://www.arloria.net/qdb/%s" % addend
            msg = url
            self.msg(channel, msg)

        if msg == "!joke":
            #Fetches an ol' fashioned Chuck Norris joke and prints it

            r = requests.get("http://api.icndb.com/jokes/random?")
            rj = r.json()
            msg = rj['value']['joke']
            self.msg(channel, msg.encode('utf-8', 'ignore'))

        #Logging Things

        #Misc

        if msg == "!dance":
            msg = "<(o.o<)\r\n" \
                  "(>o.o)>\r\n" \
                  "^(o.o)^\r\n" \
                  "v(o.o)v\r\n" \
                  "<(o.o)>\r\n"
            self.msg(channel, msg)

        if msg == "!help":
            #TODO find a better way to list commands. Perhaps in a private message?

            msg = "Commands: !dance, !disconnect, !joke, " \
                  "!version, !info," \
                  " !t [source lang] [target lang], !dt [foreign text], !qdb [number]"
            self.msg(channel, msg)

        if msg == "!version":
            #Passes version and version number to channel
            msg = "Version | {vnam} | {vnum} | {venv}".format(vnam=versionName, vnum=versionNumber,
                                                                         venv=versionEnv)
            self.msg(channel, msg)

        if msg.startswith("!info"):
            #If called, states owner and nickname
            owner = cfg.get('Users', 'Owner')
            msg = "Hello, {u}. I am {n}, a bot belonging to {o}".format(u=user, n=self.nickname, o=owner)
            self.msg(channel, msg)

        if msg == "!disconnect" and user == str('Serio'):
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