"""
Permissions module for keeping track of channel permissions
"""

#Import Twisted Words IRC for good measure
from twisted.words.protocols import irc

#Import database handler
import sqlite3

i = irc
ic = irc.IRCClient
conn = sqlite3.connect('databases/permissions.db')
c = conn.cursor()


class Permissions():

    def __init__(self):
        return

    @staticmethod
    def createtable():
        """
        An 'in-case-of' function that can be called if datacheck somehow fails.
        """

        c.execute('''CREATE TABLE permissions(user, level, channel)''')
        c.execute('''CREATE TABLE illegal_channels(channel, state)''')

        conn.commit()
        conn.close()

    @staticmethod
    def datacheck():
        """
        Checks if table 'permissions' exists, and if not creates it. To be run alongside SignedOn.
        """

        tab_check = c.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='permissions' ''')

        res1 = "Database Already Exists."
        res2 = "Database Created."

        if tab_check == 1:
            print res1

        if tab_check == 0:
            c.execute('''CREATE TABLE permissions(user, level, channel)''')
            conn.commit()
            print res2

    @staticmethod
    def permop(user, channel):
        """
        Applies 'operator' condition to user. (Level 3)
        """

        sqin = '''INSERT INTO permissions(user,level,channel) VALUES (?,?,?)'''
        params = (user, 3, channel)
        c.execute(sqin, params)
        conn.commit()

        conn.close()

    @staticmethod
    def permhop(user, channel):
        """
        Applies 'half-operator' condition to user. (Level 2)
        """

        sqin = '''INSERT INTO permissions(user,level,channel) VALUES (?,?,?)'''
        params = (user, 2, channel)
        c.execute(sqin, params)
        conn.commit()

        conn.close()

    @staticmethod
    def permvoice(user, channel):
        """
        Applied 'voiced' condition to user. (Level 1)
        """

        sqin = '''INSERT INTO permissions(user,level,channel) VALUES (?,?,?)'''
        params = (user, 1, channel)
        c.execute(sqin, params)
        conn.commit()

        conn.close()

    @staticmethod
    def chckvoice(self):
        """
        Checks if user is voiced
        """

        sqin = '''SELECT FROM permissions(level,channel)'''

    def illegalchannel(self, channel, state):

        allowed = 1
        disallowed = 0

    def add_illegal(self, channel, state):

        check = '''SELECT FROM illegal_channels(channel,state)'''
        if check is 1:
            return "Invalid"
        if check is 0:
            sqin = '''INSERT INTO illegal_channels(channel,state) VALUES (?,?,?)'''
            params = (channel, 0)
            c.execute(sqin, params)


        conn.commit()
        conn.close()