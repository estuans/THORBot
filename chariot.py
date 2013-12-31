__author__ = 'Platinum'

# Factory, launches and configures the bot and attaches it to the IRC network/channel.
# All settings can be configured in hammer.ini

from thor import ThorBot
import thor
import sys
import os
from twisted.internet import protocol, reactor
from twisted.python import log
import ConfigParser

cfg = ConfigParser.RawConfigParser()
cfg.read("hammer.ini")
server = cfg.get('Connection', 'Server')
port = cfg.getint('Connection', 'Port')
__channels = cfg.get('Connection', 'Channels')
logfile = cfg.get('Connection', 'Logfile')


class ThorBotFactory(protocol.ClientFactory):
    protocol = ThorBot

    def __init__(self, channel, filename, chain_length, chattiness, max_words):
        self.channel = channel
        self.filename = filename
        self.logfile = logfile
        self.chain_length = chain_length
        self.chattiness = chattiness
        self.max_words = max_words

    def buildProtocol(self, addr):
        p = ThorBot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        print "connection lost:", reason
        connector.connect()
        reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        print "failed to connect:", reason
        reactor.stop()

if __name__ == '__main__':
    chain_length = cfg.getint('Bot Settings', 'Chain Length')
    chattiness = cfg.getfloat('Bot Settings', 'Chattiness')
    max_words = cfg.getint('Bot Settings', 'Max Words')
    if os.path.exists('brain.txt'):
        f = open('brain.txt', 'r')
        for line in f:
            thor.add_to_brain(line, chain_length)
        print 'Brain Loaded'
        f.close()
    log.startLogging(sys.stdout)
    reactor.connectTCP(server, port, ThorBotFactory(__channels, logfile, chain_length, chattiness, max_words))
    reactor.run()