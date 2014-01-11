THORBot
=======

An IRC bot under development.

Currently supports a variety of commands, with more modules on the drawing board.




Connecting
======

Before you can start using THORBot, you need to configure a few settings in the configuration file provided with the bot. You'll find these settings in the "hammer.ini" file, and most revisions should include a clean file for you to use. Everything from the nickname, nickserver pass, to the channels it connects to can be configured from there.



Usage
======

As of the current revision, the bot isn't set up to accept more than a !leave [channel] command. There are certain
commands that will print a message to the console for debugging, but mostly it just logs and leaves.

Todo
======

- Improve the way THORBot handles messages being sent to valhalla.brain.
- Add additional support for Google API.
- Add support for WolframAlpha API.
- Work on the permissions database and how they're handled.


Dependencies
======

To speed up things and streamline the code, THORBot relies on a few dependencies to be present.

- Twisted - http://twistedmatrix.com/trac/wiki/TwistedWords
- COBE - https://github.com/pteichman/cobe/wiki

Attribution
=======

- The goslate.py module belongs to ZHUO QIANG ( http://pythonhosted.org/goslate/ ) and is used in accordance to the MIT license


Commands
======

For information on the available, and usage thereof, commands, please check the THORBot wiki on GitHub.
