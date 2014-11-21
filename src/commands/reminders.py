from base import BaseCommand

from operator import itemgetter
import shelve
from datetime import datetime

class FetchReminder(BaseCommand):
    help_message = "Checks for reminders for the user that just spoke, and reminds them!"
    #listen = "remind"

    def test_message(self):
        self.perform_action()
        return True

    def perform_action(self):
        sh = shelve.open('reminders')
        rfor = self.user
        check = sh.has_key(rfor)

        if check is True:
            #Checks if key exists
            reminder = sh[rfor]
            reply = "[%s] %s" % (self.user, reminder)
            self.respond(reply)

            #And deletes them
            del sh[rfor]

        elif check is False:
            pass


# Reminder
class RemindUser(BaseCommand):
    listen = "remind"

    def perform_action(self):
        dt = datetime
        msg = self.message

        str_check = "Smek"

        if msg.__contains__(str_check.lower()):
            return

        #Open the shelf
        sh = shelve.open('reminders')
        spl = msg.split(' ')

        #Get user, datetime, key(target) and data(reminder)
        _from = self.user
        timestamp = dt.today()
        target = itemgetter(1)(spl)
        reminder = itemgetter(slice(2, None))(spl)
        reminder_ = ' '.join(reminder)

        #Alter data to include timestamp and user
        data = '(%s) %s reminds you: %s' % (timestamp, _from, reminder_)

        #Throw it into the shelf
        sh[target] = data
        msg = "I'll remind %s about that, %s" % (target, self.user)
        self.respond(msg)

        if IndexError:
            pass

class DebugReminders(BaseCommand):
    listen = ".debugreminders"

    def perform_action(self):
        sh = shelve.open('reminders')
        klist = sh.keys()
        print klist
        self.respond(klist)