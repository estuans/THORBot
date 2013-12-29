#!/usr/bin/python
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
from collections import defaultdict

#OTHER Imports
import ConfigParser
import wolframalpha

#Basic Inf
versionName = "Apple"
versionNumber = "0.0223b"

#Config parser. Could be replaced in the future?

cfg = ConfigParser.RawConfigParser()
cfg.read("hammer.ini")

logfile = cfg.get('Connection', 'Logfile')

# WOLFRAMALPHA implementation

api_id = wolframalpha.Client('YT6T34-E7L5L5YWWK')

#MARKOV integration
markov = defaultdict(list)
STOP_WORD = ""


def add_to_brain(msg, chain_length, write_to_file=False):
    if write_to_file:
        f = open('brain', 'a')
        f.write(msg + '')
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
                return
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
        owner = cfg.get('Users', 'Owner')
        admins = cfg.get('Users', 'Admins')
        self.nickname = nickname
        self.realname = realname
        self.owner = owner
        self.admins = admins

    def connectionMade(self):
        #First we connect
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
                self.logger.log(msg)
                self.msg(channel, msg)
        if chance <= 0.4:
            print "Chance:", chance
        self.logger.log("%s has joined %s" % (user, channel))

    def userLeft(self, user, channel):
        self.logger.log("%s has left %s channel. Bubye." % (user, channel))

    def kickedFrom(self, channel, kicker, message):
        self.logger.log("%s kicked me from %s, the nerve!" % (kicker, channel))

    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]
        self.logger.log("<%s> %s" % (user, msg))

        #Used by the Markov command
        prefix = "%s: " % user

        #PRIVMSG Configuration parameters
        chain_length = cfg.getint('Bot Settings', 'Chain Length')
        max_words = cfg.getint('Bot Settings', 'Max Words')
        owner = cfg.get('Users', 'Owner')
        admins = cfg.get('Users', 'Admins')

       #Thor's markov implementation wasn't playing ball, so I had
       #To alter the vast majority of the code. Instead of replying randomly,
       #He now only generates when prompted by the !markov command.
       #It's not the best way, but it's the least intrusive.

        if msg == "!markov":
            #Silly command that just produces a bunch of garbled text from brain.txt
            #Might be expanded upon at a later time, but in all likelihood
            #I'll try to replace it with a natural learning/machine learning command.
            msg = re.compile(self.nickname + "[:,]* ?", re.I).sub('', msg)
            sentence = generate_sentence(msg, chain_length, max_words)
            if sentence:
                self.msg(channel, prefix + sentence)
                self.logger.log("[%s] <%s> %s" % (channel, self.nickname, sentence))
            else:
                print "Markov function called, but failed to generate sentence."
                self.logger.log("Markov function was called, but failed to generate a sentence.")

        add_to_brain(msg, chain_length, write_to_file=True)

        if msg == "!version":
            #Passes version and version number to channel
            msg = "Version: {vnam}(NUMBER {vnum})".format(vnam=versionName, vnum=versionNumber)
            self.msg(channel, msg)

        if msg == "!inv {user} {chan}".format(user=str, chan=channel):
            #Broken. Meant to invite person.
            self.invite(str, channel)
            msg = "Inviting {user} into {chan}".format(user=user, chan=channel)
            self.msg(channel, msg)
            self.logger.log("Invited {user} into {chan}".format(user=user, chan=channel))

        if msg == "!rickroll":
            #... It was a silly idea, okay?
            msg = "Never gonna give you up,\nNever gonna let you down,\n" \
                  "Never gonna run around and desert you.\n" \
                  "Never gonna make you cry,\nNever gonna say goodbye,\nNever gonna tell a lie and hurt you.\n"
            self.msg(channel, msg)

        if msg.startswith("!info"):
            #If called, states owner and nickname
            nickname = cfg.get('Bot Settings', 'Nickname')
            owner = cfg.get('Users', 'Owner')
            msg = "Hello, %s. I am %s, a bot belonging to %s" % (user, nickname, owner)
            self.logger.log("[%s] <%s> %s" % (channel, self.nickname, self.msg))
            self.msg(channel, msg)

        if msg.startswith("!leave %s" % channel) and user == (owner or admins):
            #Leaves the channel(can be called outside said channel?)
            self.logger.log("[%s] <%s> %s" % (channel, user, msg))
            self.leave(channel)

        if msg == "!disconnect" and user == (owner or admins):
            self.quit(message="Disconnected per request")
            self.logger.log("Disconnected per request of %s" % user)



        if msg == ("!join %s" % str) and user == (owner or admins):
            #Joins designated channel.
            channel = str
            self.join(channel)

        if msg == "!nick %s" % str():
            #Changes nickname
            self.setNick(str())

        if channel == self.nickname:
            msg = "I don't reply to whispers."
            self.logger.log("<%s> %s" % (self.nickname, self.msg))
            self.msg(user, msg)
            return

        if msg.startswith(self.nickname + ": Talk!"):
            msg = "%s: No, go duck yourself, foo'" % user
            self.msg(channel, msg)
            self.logger.log("[%s] <%s> %s" % (channel, self.nickname, self.msg))

    def action(self, user, channel, message):
        user = user.split('!', 1)[0]
        self.logger.log("[%s] * %s %s" % (channel, user, message))

    #IRC CALLBACKS

    def irc_NICK(self, prefix, params):
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.logger.log("%s has changed nick to %s" % (old_nick, new_nick))

    def alterCollidedNick(self, nickname):
        return nickname + 'Clone'