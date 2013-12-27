'''
THOR connects to an IRC network, joins a channel, and keeps a log of everything that goes on.
WolframAlpha integration will come later.
'''

#TWISTED Imports

from twisted.words.protocols import irc

#INTERNAL Imports

#SYS Imports
import time
import random
import re
import os
import redis
from collections import defaultdict

#OTHER Imports
import ConfigParser
import wolframalpha

#Basic Inf
versionName = "Tarvos"
versionNumber = "1.0"

#The below lines have been, mostly, commented out due to the deprecation of their functions
#I retain them here in order to roll back in case of emergency

cfg = ConfigParser.RawConfigParser()
cfg.read("hammer.ini")

logfile = cfg.get('Connection', 'Logfile')

# WOLFRAMALPHA implementation

client = wolframalpha.Client('YT6T34-E7L5L5YWWK')

#MARKOV integration
markov = defaultdict(list)
STOP_WORD = "\n"


def add_to_brain(msg, chain_length, write_to_file=False):
    if write_to_file:
        f = open('brain.txt', 'a')
        f.write(msg + '\n')
        f.close()
    buf = [STOP_WORD] * chain_length
    for word in msg.split():
        markov[tuple(buf)].append(word)
        del buf[0]
        buf.append(word)
    markov[tuple(buf)].append(STOP_WORD)


def generate_sentence(msg, chain_length, max_words):
    buf = msg.split()[:chain_length]
    if len(msg.split()) > chain_length:
        message = buf[:]
    else:
        message = []
        for i in xrange(chain_length):
            message.append(random.choice(markov[random.choice(markov.keys())]))
        for i in xrange(max_words):
            try:
                next_word = random.choice(markov[tuple(buf)])
            except IndexError:
                continue
            if next_word == STOP_WORD:
                break
            message.append(next_word)
            del buf[0]
            buf.append(next_word)
        return ' '.join(message)


class Bin:
    """
    The Bin class contains basic logging functionality, although with how expanded
    ThorBot is now, I'm not certain if it's necessary any longer.
    """
    def __init__(self, fl):
        self.logfile = logfile
        self.fl = fl

    def log(self, message):
        timestamp = time.strftime("[%H:%M]", time.localtime(time.time()))
        self.fl.write('%s %s\n' % (timestamp, message))
        self.fl.flush()

    def close(self):
        self.fl.close()


class ThorBot(irc.IRCClient):
    """
    This class will log events and, eventually, pull answers from the internet on queries
    At the present time, there's a failure to respond correctly to queries made
    but hopefully, once resolve it will be able to respond with a Markov chain as well.
    """

    def __init__(self):
        nickname = cfg.get('Bot Settings', 'Nickname')
        realname = cfg.get('Bot Settings', 'Realname')
        self.nickname = nickname
        self.realname = realname

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger = Bin(open(self.factory.filename, "a"))
        self.logger.log("[CONNECTED @ %s]" % time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log("[DISCONNECTED @ %s]" % time.asctime(time.localtime(time.time())))
        self.logger.close()

    def irc_ERR_ERRONEUSNICKNAME(self, prefix, params):
        print "irc_ERR_ERRONEUSNICKNAME called"
        self.logger.log("[%s]Erroneus Nickname" % time.asctime(time.localtime(time.time())))
        if not self._registered:
            self.setNick(self.fbnick)

    #EVENTS

    def signedOn(self):
        #Called when signing on
        print "Signed on successfully"
        self.join(self.factory.channel)

    def joined(self, channel):
        #Called when joining a channel
        print "Joined %s" % channel
        self.logger.log("[JOINED %s]" % channel)

    def userJoined(self, user, channel):
        #Called when another user joins a channel
        print "%s has joined %s" % (user, channel)

        chance = random.random()

        if chance >= 0.4:
                print "Welcomed %s. Chance: %s" % (user, chance)
                msg = "Welcome to %s, %s" % (channel, user)
                self.msg(channel, msg)
        if chance <= 0.4:
            print "Chance:", chance
        self.logger.log("%s has joined %s" % (user, channel))

    def userLeft(self, user, channel):
        self.logger.log("%s has left %s channel. Bubye." % (user, channel))

    def kickedFrom(self, channel, kicker, message):
        self.logger.log("%s kicked me from %s, the nerve!" % (kicker, channel))

    def privmsg(self, user, channel, msg):
        #user = user.split('!', 1)[0]
        self.logger.log("<%s> %s" % (user, msg))

        if not user:
            return
        if self.nickname in msg:
            msg = re.compile(self.nickname + "[:,]* ?", re.I).sub('', msg)
            prefix = "%s: " % (user.split('!', 1)[0], )
        else:
            prefix = ''
        add_to_brain(msg, self.factory.chain_length, write_to_file=True)
        if prefix or random.random() <= self.factory.chattiness:
            sentence = generate_sentence(msg, self.factory.chain_length, self.factory.max_words)
            if sentence:
                self.msg(self.factory.channel, prefix + sentence)

        if msg.startswith("!i"):
            #If called, states owner and nickname(completely redundant, but rather cool)
            nickname = cfg.get('Bot Settings', 'nickname')
            owner = cfg.get('Users', 'owner')
            msg = "Hello, %s. I am %s, a bot belonging to %s" % (user, nickname, owner)
            self.msg(channel, msg)

        if msg.startswith("!leave %s" % channel):
            #Leaves the channel(can be called outside said channel?)
            self.leave(channel)

        if msg == ("!join %s" % channel):
            #Joins designated channel.
            print "Joining %s" % channel
            self.join(channel)

        if msg.startswith("!nick %s" % str()):
            #Changes nickname
            new_nick = str()
            self.setNick(nickname=new_nick)

        if channel == self.nickname:
            msg = "I don't reply to whispers."
            self.msg(user, msg)
            return

        if msg.startswith(self.nickname + ": Talk!"):
            msg = "%s: No, go duck yourself, foo'" % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))

    def action(self, user, channel, message):
        user = user.split('!', 1)[0]
        self.logger.log("* %s %s" % (user, message))

    #IRC CALLBACKS

    def irc_NICK(self, prefix, params):
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.logger.log("%s has changed nick to %s" % (old_nick, new_nick))

    def alterCollidedNick(self, nickname):
        return nickname + 'Clone'