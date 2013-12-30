THORBot
=======

An experimental IRC bot running Python
with Twisted.Words and various other
small libraries tacked on.

Currently connects and does random debugging stuff.

=======

Connecting
=======

In order to connect to a server, use the hammer.ini provided to set the appropriate server, port, and nickname.
You can alter the nickname of ThorBot easily through the ini, as well as certain messages provided.

=======

Usage
=======

As of the current revision, the bot isn't set up to accept more than a !leave [channel] command. There are certain
commands that will print a message to the console for debugging, but mostly it just logs and leaves.

Todo
=======

- Need to create a database function that stores permissions, channels, etc.

- Fix !invite and !join

Dependencies
=======

Due to Thor's nature, he requires certain things to be present for him to function.

Twisted - http://twistedmatrix.com/trac/wiki/TwistedWords