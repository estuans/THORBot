import logging


class BaseCommand(object):
    help_message = "This the base command class, does nothing."
    predicate = "!"
    listen = "base"

    def _help(self):
        return self.help_message

    @property
    def trigger(self):
        return self.predicate + self.listen

    def __init__(self,*args,**kwargs):
        self.bot = kwargs.get('instance')
        self.user = kwargs.get('user')
        self.channel = kwargs.get('chan')
        self.message = kwargs.get('message')


    def test_message(self):
        #Override this if you need more complex triggers.
        if self.message.split(" ")[0] == self.trigger:
            self.perform_action()
            return True

    def perform_action(self):
        return True

    def respond(self,message):
        self.bot.msg(self.channel,message)


class EchoTest(BaseCommand):
    help_message = "Repeats the message that's just been heard."
    listen = "echo"

    def perform_action(self):
        self.respond("Echo test: " + self.message)


class Reminder(BaseCommand):
    help_message = "Checks for reminders for the user that just spoke, and reminds them!"
    listen = "remind"

    def perform_action(self):
        sh = shelve.open('reminders')
        rfor = self.user
        check = sh.has_key(rfor)

        if check is True:
            #Checks if key exists
            reminder = sh[rfor]
            reply = "[%s] %s" % (user, reminder)
            self.respond(reply)

            #And deletes them
            del sh[rfor]

        elif check is False:
            pass
