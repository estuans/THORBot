"""
The Observer Class, in this instance, is a custom module designed with the express purpose of
keeping an eye out for commands that alter entire modules or files within THOR BOT.
"""

import time
import thor


def remodule():
            print "RELOAD requested"
            time.sleep(2)
            reload(thor)