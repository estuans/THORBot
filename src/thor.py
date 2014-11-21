#!/usr/bin/python


'''
THOR connects to an IRC network, joins a channel, and keeps a log of everything that goes on.
WolframAlpha integration will come later.
'''

# TWISTED Imports
from twisted.words.protocols import irc

# INTERNAL Imports
from src.commands import BaseCommand

# SYS Imports
import datetime
import platform

# OTHER Imports
import ConfigParser
import feedparser
import ctypes

# HTTP Handlers
import requests
import goslate

versionName = "Magni"
versionEnv = "Python 2.7.3"

if "window" in platform.system().lower():
    ctypes.windll.kernel32.SetConsoleTitleA("THORBot @ Valhalla")

cfg = ConfigParser.RawConfigParser(allow_no_value=True)
cfg.read("mothi.ini")


class ThorBot(irc.IRCClient):
    """
    Primary IRC class. Controls just about everything that isn't a module.
    Below you'll find a bunch of options that are handled by hammer.ini.
    """

    def __init__(self):
        nickname = cfg.get('Bot Settings', 'Nickname')
        password = cfg.get('Bot Settings', 'NickPass')
        advanced_mode = cfg.getboolean('Bot Settings', 'Advanced')
        realname = 'Mothi[THORBOT] @ VALHALLA'

        self.realname = realname
        self.nickname = nickname
        self.password = password
        self.advanced = advanced_mode
        self.superusers = cfg.get('Users', 'Superusers')
        self.lineRate = 1

    def connectionMade(self):

        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def irc_ERR_ERRONEUSNICKNAME(self, prefix, params):
        print "irc_ERR_ERRONEUSNICKNAME called"

    def irc_ERR_PASSWDMISMATCH(self, prefix, params):
        print "!!!INCORRECT PASSWORD!!!\n Check hammer.ini for the NICKPASS parameter"
        return

    #TODO Rectify the lack of irc_RPC responses. It's an outrage.

    #EVENTS

    def irc_unknown(self, prefix, command, params):

        ic = ["#jacoders", "#church_of_smek"]

        if command == "INVITE":
            if params[1] in ic[:]:
                return
            else:
                self.join(params[1])

    def signedOn(self):
        #Called when signing on
        print "Signed on successfully"
        self.join(self.factory.channel)

    def whois(self, nickname, server=None):
        #Blatantly stolen from http://goo.gl/lwD47Q
        if server is None:
            pass
        else:
            self.sendline('WHOIS %s %s' % (server, nickname))

    def joined(self, channel):

        #Called when joining a channel
        print "Joined %s" % channel
        self.sendLine("MODE {nickname} {mode}".format(nickname=self.nickname, mode="+B"))

    def userJoined(self, user, channel):
        #Checks when a user joins if there are any reminders available for them
        sh = shelve.open('reminders')
        rfor = user
        check = sh.has_key(rfor)

        if check is True:
            #Checks if key exists
            reminder = sh[rfor]
            reply = "[%s] %s" % (user, reminder)
            self.msg(channel, reply)

            #And deletes them
            del sh[rfor]

        elif check is False:
            pass

        #Called when another user joins a channel
        print "%s has joined %s" % (user, channel)

    def privmsg(self, user, channel, msg):
        # For use in class based responses.
        class_args = {'instance':self,
                      'user':user,
                      'chan':channel,
                      'message':msg}

        if msg:
            #Iterate through the registered commands and perform actions as necessary.
            for klass in BaseCommand.__subclasses__():
                result = klass(**class_args).test_message()
                if result:
                    break

        if msg.startswith("!shakeit"):
            d = dictionaries.Randict
            shake = random.choice(d.shakespeare)
            self.msg(channel, shake)

        #Help utilities

        if msg.startswith("!help bbc"):
            msg = "Retrieves the most recent news article from BBC News and posts a summary. Use !bbc random for a" \
                  "random, recent news story. "
            self.msg(channel, msg)

        if msg.startswith("!help roll"):
            msg = "'Rolls' a number between 1 and 100."
            self.msg(channel, msg)

        if msg.startswith("!help me"):
            msg = "I'm sorry, I can't help you."
            self.msg(channel, msg)

        if msg.startswith("!help calc"):
            if not self.advanced:
                msg = "I can perform addition, subtraction, multiplication, division and modulo. e.g. 10 + 10"
            else:
                msg = "I can perform any operation supported by the Python math module - https://docs.python.org/2/library/math.html"
            self.msg(channel, msg)

        if msg.startswith("!help t"):
            msg = "Takes two arguments; A and B. Argument A will be the source language, argument B will be the target" \
                  " language. Languages follow ISO 639-1. (See: http://goo.gl/nVuDQJ )"
            self.msg(channel, msg)

        if msg.startswith("!help dt"):
            msg = "Detects the language the sentence is written in and returns a translation in English. No language" \
                  " codes are required."
            self.msg(channel, msg)

        if msg.startswith("!help qdb"):
            msg = "Fetches the quote with the number requested. Lazily coded."
            self.msg(channel, msg)

        #URL Fetchers & Integrated Utilities

        if msg == "!bbc":
            fd = feedparser.parse('http://feeds.bbci.co.uk/news/rss.xml?edition=int')
            description = fd.entries[0].description
            link = fd.entries[0].link
            fd = "\x02THE NEWS\x02: \x1D%s\x1D - \x02Read More\x02: %s" % (description, link)

            self.msg(channel, fd.encode('UTF-8'))

        if msg == "!bbc random":
            r = random.randint(0, 72)
            fd = feedparser.parse('http://feeds.bbci.co.uk/news/rss.xml?edition=int')
            description = fd.entries[r].description
            link = fd.entries[r].link
            fd = "\x02THE NEWS\x02: \x1D%s\x1D - \x02Read More\x02: %s" % (description, link)
            self.lineRate = 2

            self.msg(channel, fd.encode('UTF-8'))

        if msg.startswith("!qdb"):
            #This is lazy. It's unorthodox. Why do I use it? Because it works.
            #99.98% of the time, anyway.

            #TODO The above is unacceptable. Find another way to make it work.
            #TODO: Use requests.

            wlist = msg.split(' ')

            addend = itemgetter(1)(wlist)
            url = "http://www.arloria.net/qdb/%s" % addend
            quote = requests.get(url)

            import rpdb; rpdb.set_trace()

            msg = url
            self.msg(channel, msg)

        if msg == "!help":
            msg = "Commands: !dance, !disconnect, !joke, !version, !info, !t [source lang] [target lang], !dt [foreign " \
                  "text], !qdb [number]"
            self.notice(user, msg)


    #IRC CALLBACKS

    #TODO Add more?

    def alterCollidedNick(self, nickname):
        return nickname + 'Clone'