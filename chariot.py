__author__ = 'Platinum'

# Factory, launches and configures the bot and attaches it to the IRC network/channel.
# All settings can be configured in hammer.ini

from thor import *
import ConfigParser

cfg = ConfigParser.RawConfigParser()
cfg.read("hammer.ini")
server = cfg.get('Connection', 'server')
port = cfg.getint('Connection', 'port')
__channel = cfg.get('Connection', 'channel')


class ThorBotFactory(protocol.ClientFactory):
    protocol = ThorBot

    def __init__(self, channel, filename):
        self.channel = channel
        self.filename = filename

    def buildProtocol(self, addr):
        p = ThorBot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        print "connection lost:", reason
        self.logger.log("Connection Lost:", reason)
        connector.connect()
        reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        print "failed to connect:", reason
        self.logger.log("Failed to connect:", reason)
        reactor.stop()

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    reactor.connectTCP(server, port, ThorBotFactory(__channel, logfile))
    reactor.run()