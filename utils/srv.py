import sys

from twisted.cred import checkers, portal
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.python import log
from twisted.words import service


ROOM = 'room'
USERS = dict(
    Estuans='test',
    Mothi='test',
    user3='pass3',
    user4='pass4')


if __name__ == '__main__':
    log.startLogging(sys.stdout)

    # Initialize the Cred authentication system used by the IRC server.
    realm = service.InMemoryWordsRealm('testrealm')
    realm.addGroup(service.Group(ROOM))
    user_db = checkers.InMemoryUsernamePasswordDatabaseDontUse(**USERS)
    portal = portal.Portal(realm, [user_db])

    # IRC server factory.
    ircfactory = service.IRCFactory(realm, portal)

    # Connect a server to the TCP port 6667 endpoint and start listening.
    endpoint = TCP4ServerEndpoint(reactor, 6667)
    endpoint.listen(ircfactory)
    reactor.run()
