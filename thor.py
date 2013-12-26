'''
THOR connects to an IRC network, joins a channel, and keeps a log of everything that goes on.
WolframAlpha integration will come later.
'''

#TWISTED Imports

from twisted.words.protocols import irc

#INTERNAL Imports

#SYS Imports
import time

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


#server = cfg.get('Connection', 'server')
#port = cfg.getint('Connection', 'port')
#__channel = cfg.get('Connection', 'channel')
#owner = cfg.get('Users', 'owner')
#admins = cfg.get('Users', 'admins')
logfile = cfg.get('Connection', 'logfile')
#realname = cfg.get('Bot Settings', 'realname')

# WOLFRAMALPHA implementation

client = wolframalpha.Client('YT6T34-E7L5L5YWWK')


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
        nickname = cfg.get('Bot Settings', 'nickname')
        realname = cfg.get('Bot Settings', 'realname')
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
        self.join(self.factory.channel)

    def joined(self, channel):
        self.logger.log("[JOINED %s]" % channel)

    def userJoined(self, user, channel):
        self.logger.log("%s has joined %s" % (user, channel))

    def userLeft(self, user, channel):
        self.logger.log("%s has left %s channel. Bubye." % (user, channel))
        channel.message("Goodbye, %s" % user)

    def kickedFrom(self, channel, kicker, message):
        self.logger.log("%s kicked me from %s, the nerve!" % (kicker, channel))

    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]
        self.logger.log("<%s> %s" % (user, msg))

        if msg.startswith("!test"):
            print "Test Successful"

    #    if message.startswith("!leave"):
    #        print "!leave was called"
    #        self.leave(channel)

        if msg.startswith(self.nickname + ":" or "," or " "):
            print "Was mentioned."
            msg = "You called?"

        if msg.startswith("!leave %s" % channel):
            self.leave(channel)

        if msg.startswith("!join %s" % channel):
            print "Joining %s" % channel
            self.join(channel)

        if msg.startswith("!nick %s" % str):
            self.setNick(nickname=str)

        if channel == self.nickname:
            msg = "I don't reply to whispers."
            self.msg(user, msg)
            return

        if msg.startswith(self.nickname + ": Talk!"):
            msg = "%s: No, go duck yourself, foo'" % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))

        if msg.startswith(self.nickname + ":"):
            msg = "%s: I am a log bot" % user
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