import thor

__author__ = 'Platinum'

# Factory, launches and configures the bot and attaches it to the IRC network/channel.
# All settings can be configured in hammer.ini

from thor import ThorBot
from modules import perm
import sys
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

    def __init__(self, channel, filename):
        self.channel = channel
        self.filename = filename
        self.logfile = logfile

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
    log.startLogging(sys.stdout)
    reactor.connectTCP(server, port, ThorBotFactory(__channels, logfile))
    reactor.run()