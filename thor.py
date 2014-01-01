#!/usr/bin/python
'''
THOR connects to an IRC network, joins a channel, and keeps a log of everything that goes on.
WolframAlpha integration will come later.
'''

#TWISTED Imports

from twisted.words.protocols import irc

#INTERNAL Imports
from modules.marthor import generate_sentence
from modules.marthor import add_to_brain
from modules import observer

#SYS Imports
import time
import random
import re

#OTHER Imports
import ConfigParser
import wolframalpha

#Basic Inf
versionName = "Baktu"
versionNumber = "0.0402a"

#Config parser. Could be replaced in the future?

cfg = ConfigParser.RawConfigParser()
cfg.read("hammer.ini")

logfile = cfg.get('Connection', 'Logfile')

# WOLFRAMALPHA implementation

#api_id = wolframalpha.Client('YT6T34-E7L5L5YWWK')

#Globals(These are ABSOLUTELY necessary to declare here, otherwise the code won't work.
#Don't sue me. I'm just making sure it won't throw syntax warnings at me.)
icl = irc.IRCClient
i = irc.IRC
chttb = True


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
        password = cfg.get('Bot Settings', 'NickPass')
        owner = cfg.get('Users', 'Owner')
        admins = cfg.get('Users', 'Admins')
        ignored = cfg.get('Users', 'Ignorelist')
        self.nickname = nickname
        self.realname = realname
        self.password = password
        self.owner = owner
        self.admins = admins
        self.ignored = ignored

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
        self.logger.log("[JOINED %s]" % channel)

    def userJoined(self, user, channel):
        #Called when another user joins a channel
        print "%s has joined %s" % (user, channel)

        chance = random.random()

        if chance >= 0.2:
            print "Welcomed %s. Chance: %s" % (user, chance)
            msg = "Welcome to %s, %s" % (channel, user)
            self.logger.log(msg)
            self.msg(channel, msg)
        if chance <= 0.2:
            print "Chance:", chance
        self.logger.log("%s has joined %s" % (user, channel))

    def userLeft(self, user, channel):
        self.logger.log("%s has left %s channel. Bubye." % (user, channel))

    def kickedFrom(self, channel, kicker, message):
        self.logger.log("%s kicked me from %s, the nerve!" % (kicker, channel))

    def userKicked(self, kickee, channel, kicker, message):
        self.logger.log("{us} was kicked from {ch} by {ki}".format(us=kickee, ch=channel, ki=kicker))
        msg = "{us} must have pissed {ki} off!".format(us=kickee, ki=kicker)
        self.msg(channel, msg)

    def irc_unknown(self, prefix, command, params):
        if command == "INVITE":
            self.join(params[1])

    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]
        self.logger.log("[{c}] {u}: {m}".format(c=channel, u=user, m=msg))

        #Globals
        global chttb

        #Used by the Markov command
        prefix = "%s: " % user

        #PRIVMSG Configuration parameters
        chain_length = cfg.getint('Bot Settings', 'Chain Length')
        max_words = cfg.getint('Bot Settings', 'Max Words')
        owner = cfg.get('Users', 'Owner')
        admins = cfg.get('Users', 'Admins')
        ignored = cfg.get('Users', 'Ignorelist')

       #Thor's markov implementation wasn't playing ball, so I had
       #To alter the vast majority of the code. Instead of replying randomly,
       #He now only generates when prompted by the !markov command.
       #It's not the best way, but it's the least intrusive.

        if msg:
            #Logs all messages
            self.logger.log("[{c}] {u}: {m}".format(c=channel, u=user, m=msg))

        if self.msg:
            #Logs own messages, so long as self.msg() is called
            self.logger.log("[{c}] {u}: {m}".format(c=channel, u=self.nickname, m=self.msg))

        if msg == "!reload":
            msg = "Reloading..."
            self.msg(channel, msg)
            observer.remodule()

        if msg == "!chatterbot":
            #Checks what the status of the chttb variable is and provides it in place of {st}
            msg = "Chatterbot variable status: {st}".format(st=chttb)
            self.msg(channel, msg)

        if msg == "!chatterbot off":
            #Checks if chttb is true, and if it is, changes it to False.
            if chttb is True:
                chttb = False
                msg = "Chatterbot replies turned off."
                self.msg(channel, msg)
            else:
                msg = "Chatterbot replies already off."
                self.msg(channel, msg)

        if msg == "!chatterbot on":
            #Inverse of the above
            if chttb is False:
                chttb = True
                msg = "Chatterbot replies turned on."
                self.msg(channel, msg)
            else:
                msg = "Chatterbot replies already on."
                self.channel(channel, msg)

        if msg.__contains__(self.nickname) and chttb is True and user != ignored:
            #Silly command that just produces a bunch of garbled text from brain.txt
            #Might be expanded upon at a later time, but in all likelihood
            #I'll try to replace it with a natural learning/machine learning command.
            #msg = re.compile(self.nickname + "[:,]* ?").sub('', msg)
            #msg = re.compile(self.nickname + "[a-z$1][A-Z$1]+[\s^$]$1").sub("", msg)
            msg = re.compile(self.nickname + "[A-Z][a-z'\-]+[, ]([a-zA-Z'\-]+[;,]? ){15,25}[a-zA-Z'\-]+[.?!]").sub("",
                                                                                                                   msg)
            sentence = generate_sentence(msg, chain_length, max_words)
            if sentence:
                #' '.join(sentence.split("[:,]* ?"))
                ' '.join(sentence.split("[A-Z][a-z'\-]+[, ]([a-zA-Z'\-]+[;,]? ){15,25}[a-zA-Z'\-]+[.?!]"))
                re.split(msg, sentence)
                if sentence.endswith(""):
                    self.msg(channel, prefix + sentence + ".")
                    print "!!!DEBUG: Replaced WHITESPACE!!!"
                elif sentence.endswith(","):
                    sentence.replace(",", ".")
                    self.msg(channel, prefix + sentence)
                    print "!!!DEBUG: Replaced COMMA!!!"
                elif sentence.endswith(",."):
                    sentence.replace(",.", ".")
                    self.msg(channel, prefix + sentence)
                    print "!!!DEBUG: Replaced COMMA PERIOD!!!"
                else:
                    self.msg(channel, prefix + sentence)
                self.logger.log("[{c}] {u}: {m}".format(c=channel, u=self.nickname, m=self.msg))
                print sentence
            else:
                print "Markov function called, but failed to generate sentence."
                self.logger.log("Markov function was called, but failed to generate a sentence.")

        add_to_brain(msg, chain_length, write_to_file=True)

        if msg == "!version":
            #Passes version and version number to channel
            msg = "Version: {vnam}(NUMBER {vnum})".format(vnam=versionName, vnum=versionNumber)
            self.msg(channel, msg)

        if msg == "!inv {user} {chan}":
            #Broken. Meant to invite person.
            user = user
            chan = channel
            self.invite(user, chan)
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
            owner = cfg.get('Users', 'Owner')
            msg = "Hello, {u}. I am {n}, a bot belonging to {o}".format(u=user, n=self.nickname, o=owner)
            self.logger.log("[{c}] {u}: {m}".format(c=channel, u=user, m=msg))
            self.msg(channel, msg)

        if msg.startswith("!leave {c} {r}".format(c=channel, r=str)) and user == (owner or admins):
            #Leaves the channel(can be called outside said channel?)
            self.logger.log("[{c}] {u}: {m}".format(c=channel, u=user, m=msg))
            self.leave(channel, reason=reason)

        if msg == "!disconnect" and user == (owner or admins):
            self.quit(message="Disconnected per request")
            self.logger.log("Disconnected per request of %s" % user)

        if channel == self.nickname:
            if user != owner:
                msg = "I don't reply to whispers."
                self.logger.log("<{t}> {m}".format(t=self.nickname, m=self.msg))
                self.msg(user, msg)
            elif user == owner:
                if msg == "!s {ch} ".format(ch=channel):
                    self.say(channel, msg)
                    self.logger.log("[{c}] <{t}> {m}".format(c=channel, t=self.nickname, m=self.msg))
            return

    def action(self, user, channel, message):
        user = user.split('!', 1)[0]
        self.logger.log("[{c}] * {u} {m}".format(c=channel, u=user, m=message))

    #IRC CALLBACKS

    def irc_NICK(self, prefix, params):
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.logger.log("{on} has changed nick to {nn}".format(on=old_nick, nn=new_nick))

    def alterCollidedNick(self, nickname):
        return nickname + 'Clone'