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
__channel = cfg.get('Connection', 'Channel')
logfile = cfg.get('Connection', 'Logfile')


class ThorBotFactory(protocol.ClientFactory):
    protocol = ThorBot

    def __init__(self, channel, filename, chain_length=3, chattiness=1.0, max_words=10000):
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
    chain_length = 2
    if os.path.exists('brain.txt'):
        f = open('brain.txt', 'r')
        for line in f:
            thor.add_to_brain(line, chain_length)
        print 'Brain Loaded'
        f.close()
    log.startLogging(sys.stdout)
    reactor.connectTCP(server, port, ThorBotFactory(__channel, logfile, chain_length, chattiness=0.05))
    reactor.run()