"""
Permissions module for keeping track of channel permissions
"""

#Import Twisted Words IRC for good measure
from twisted.words.protocols import irc

#Import database handler
import sqlite3

i = irc
ic = irc.IRCClient
conn = sqlite3.connect('permissions.db')
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

        sqin = '''INSERT INTO permissions VALUES(user=? AND level=? AND channel=?)'''
        params = (user, 3, channel)
        c.execute(sqin, params)
        conn.commit()

    @staticmethod
    def permhop(user, channel):
        """
        Applies 'half-operator' condition to user. (Level 2)
        """

        sqin = '''INSERT INTO permissions VALUES(user=? AND level=? AND channel=?)'''
        params = (user, 2, channel)
        c.execute(sqin, params)
        conn.commit()

    @staticmethod
    def permvoice(user, channel):
        """
        Applied 'voiced' condition to user. (Level 1)
        """

        sqin = '''INSERT INTO permissions VALUES(user=? AND level=? AND channel=?)'''
        params = (user, 1, channel)
        c.execute(sqin, params)
        conn.commit()