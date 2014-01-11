#!/usr/bin/python

'''
THOR connects to an IRC network, joins a channel, and keeps a log of everything that goes on.
WolframAlpha integration will come later.
'''

#TWISTED Imports
from twisted.words.protocols import irc

#INTERNAL Imports
from modules.logger import Bin
from modules import perm

#SYS Imports
import time
import random
import re

#OTHER Imports
import ConfigParser
import urllib2
import urllib
import json
from operator import itemgetter
from cobe.brain import Brain

#Version Information

#None of the following lines down to the config parser are of any consequence
#to the code itself, and were merely added to poke fun at the sometimes
#arbitrary nature of version numbers in software today.

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
gobblenumber = random.choice(alphabet) + str(random.randrange(0, 2000)) + "." + str(random.randint(0, 1))

versionName = "DreadFish"
versionNumber = "{g}".format(g=gobblenumber)

#Config parser. Could be replaced in the future?

cfg = ConfigParser.RawConfigParser(allow_no_value=True)
cfg.read("hammer.ini")

#Globals(These are ABSOLUTELY necessary to declare here, otherwise the code won't work.
#Don't sue me. I'm just making sure it won't throw syntax warnings at me.)
p = perm.Permissions
chttb = True
randrep = False

realname = "THORBot @ VALHALLA"

br = Brain("databases/valhalla.brain")

illegal_channels = ['#welcome', '#jacoders', '#ircrpg', '#tiramisu', '#tribes']


class ThorBot(irc.IRCClient):
    """
    Primary IRC class. Controls just about everything that isn't a module. Logging is handled by logger.py.
    Below you'll find a bunch of options that are handled by hammer.ini.
    """

    def __init__(self):
        nickname = cfg.get('Bot Settings', 'Nickname')
        password = cfg.get('Bot Settings', 'NickPass')
        self.nickname = nickname
        self.password = password
        self.lineRate = 1

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
        self.join(channel)
        msg = "How fucking dare you, {ki}".format(ki=kicker)
        self.msg(channel, msg)

    def userKicked(self, kickee, channel, kicker, message):
        self.logger.log("{us} was kicked from {ch} by {ki}".format(us=kickee, ch=channel, ki=kicker))
        msg = "{us} must have pissed {ki} off!".format(us=kickee, ki=kicker)
        self.msg(channel, msg)

    def irc_unknown(self, prefix, command, params):
        if command == "INVITE":
            if params[1] in illegal_channels[:]:
                print "INVITED BUT NOT ALLOWED TO JOIN"

            else:
                self.join(params[1])

    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]
        self.logger.log("[{c}] {u}: {m}".format(c=channel, u=user, m=msg))

        #Globals
        global chttb
        global randrep

        #PRIVMSG Configuration parameters
        owner = cfg.get('Users', 'Owner')
        admins = cfg.get('Users', 'Admins')

        #COBE Integration starts here!
        #I had to study the brain of the COBE bot example, but
        #managed to conjure up a way to better format messages.

        if msg:

            #Format
            text = msg.decode('utf-8')
            msg = re.sub('<\S>\s', '', msg)

            #Learn text
            br.learn(text)

        if self.nickname in msg and chttb is True:

            #Strip pasted nicknames and timecodes from message, as well as own nickname
            msg = re.sub('<\S>\s', '', msg)

            #Format
            text = msg.decode('utf-8')

            #Learn text
            br.learn(text)

            #Create reply
            reply = br.reply(text).encode('utf-8')

            self.msg(channel, "%s: " % user + reply.replace(self.nickname + ' ', ''))

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
                self.msg(channel, msg)

        #URL Fetchers & Integrated Utilities

        if msg == "!qdb":
            if re.match('[0-9]', msg) is True:
                re.split(' ', msg)
                qn = re.compile('[0-9]', msg)
                url = "http://www.arloria.net/qdb/"
                params = urllib.urlencode(qn)
                url2 = (url + params)
                msg = url2
                self.msg(channel, msg)
            else:
                msg = "No QDB # supplied."
                self.msg(channel, msg)

        if msg == "!j":
            #Fetches an ol' fashioned Chuck Norris joke and prints it

            rq = urllib2.Request("http://api.icndb.com/jokes/random?")
            joke = urllib2.urlopen(rq).read()
            data = json.loads(joke)
            msg = data['value']['joke']
            self.msg(channel, msg.encode('utf-8', 'ignore'))

        #Logging Things

        if self.msg:
            #Logs own messages, so long as self.msg() is called

            self.logger.log("[{c}] {u}: {m}".format(c=channel, u=self.nickname, m=msg))

        #Database things

        if msg == "!ctab":
            p.createtable()
            msg = "SQL - SUCCESS"
            self.msg(channel, msg)
            print "Table created!"

        if msg == "!dchck":
            p.datacheck()
            msg = "Running dataCheck. . ."
            self.msg(channel, msg)
            if p.datacheck() == 1:
                msg = "Tables existed. No further action required."
                self.msg(channel, msg)
            if p.datacheck() == 0:
                msg = "Data insufficient. Tables invalid. Creating tables. . ."
                self.msg(channel, msg)

        if msg == "!chv {user}".format(user=user):
            p.chckvoice(user)

        if msg == "!v {user}".format(user=user):
            p.permvoice(user, channel)
            msg = "Voiced {user}".format(user=user)
            self.msg(channel, msg)

        if msg == "!h {user}".format(user=user):
            p.permhop(user, channel)
            msg = "Half-opped {user}".format(user=user)
            self.msg(channel, msg)

        if msg == "!o {user}".format(user=user):
            p.permop(user, channel)
            msg = "Opped {user}".format(user=user)
            self.msg(channel, msg)

        #Misc

        if msg.startswith("!s"):

            #Sends message to target channel

            wlist = msg.split(' ')
            targ = itemgetter(1)(wlist)

            #Slice 'n dice the message we want to send
            tsay = itemgetter(slice(2, None))(wlist)

            #Piece it back together
            tsay = ' '.join(tsay)

            self.sendLine('PRIVMSG {targ} {tsay}'.format(targ=targ, tsay=tsay))

        if msg.startswith("!inv"):

            #Invites target user into present channel.
            #May be expanded upon in the future.

            invchan = channel
            wlist = msg.split(' ')
            targ = itemgetter(1)(wlist)

            print wlist, targ, invchan

            self.sendLine('INVITE {t} {c}'.format(c=invchan, t=targ))

            pending = "Inviting {t} into {c}".format(t=targ, c=channel)

            self.msg(channel, pending)

        if msg.startswith("!join"):

            #Joins designated channel.

            wlist = msg.split(' ')
            targ = itemgetter(1)(wlist)

            if targ in illegal_channels[:]:
                #If target is found in illegal channels list,
                #cancels operation and apologises in a polite manner.

                msg = "Sorry, {u}, I'm not allowed to join {t}".format(u=user, t=targ)
                self.msg(channel, msg)

            else:
                #Checks target against illegal channels list.
                #If not present, will join the channel.

                self.sendLine('join {c}'.format(c=targ))
                msg = "Joining {c}".format(c=targ)

                self.msg(channel, msg)

        if msg.startswith("!leave"):
            #Sends a part message to the server,
            #leaving the designated channel(even if not sent from aforementioned channel)

            wlist = msg.split(' ')
            targ = itemgetter(1)(wlist)

            msg = "Leaving {c}".format(c=targ)
            self.msg(channel, msg)

            self.sendLine('part {c}'.format(c=targ))

        if msg == "!dance":
            msg = "<(o.o<)\r\n" \
                  "(>o.o)>\r\n" \
                  "^(o.o)^\r\n" \
                  "v(o.o)v\r\n" \
                  "<(o.o)>\r\n"
            self.msg(channel, msg)

        if msg == "!help":
            msg = "Commands: !dance, !join [channel], !leave [channel], !disconnect, !rickroll, !j, " \
                  "!chatterbot [on/off], !rejoin, !version, !info, !inv [user], !s [channel] [message]"
            self.msg(channel, msg)

        if msg == "!randrep on" and randrep is False:
            msg = "Random replies turned on."
            self.msg(channel, msg)
            randrep = True

        if msg == "!randrep off" and randrep is True:
            msg = "Random replies turned off."
            self.msg(channel, msg)
            randrep = False

        if msg == "!randrep":
            if randrep is True:
                msg = "Random replies currently on."
                self.msg(channel, msg)
            if randrep is False:
                msg = "Random replies currently off."
                self.msg(channel, msg)

        if msg == "!rejoin":
            #Rejoins channel
            self.leave(channel, reason="Cycling")
            time.sleep(1)
            self.join(channel)
            time.sleep(1)
            msg = "Rejoined successfully"
            self.msg(channel, msg)

        if msg == "!version":
            #Passes version and version number to channel
            msg = "Version | {vnam} | {vnum} |".format(vnam=versionName, vnum=versionNumber)
            self.msg(channel, msg)

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

        if msg == "!disconnect" and user == (owner or admins):
            msg = "Severing connection..."
            self.msg(channel, msg)
            time.sleep(2)
            self.quit(message="Disconnected per request")
            self.logger.log("Disconnected per request of %s" % user)
            print "Disconnected."

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