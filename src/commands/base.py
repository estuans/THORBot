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

class OneLiner(BaseCommand):
    msg = "One Liner"

    def perform_action(self):
        user = self.user.split('!', 1)[0]
        self.respond(user + ": " + self.msg)

class EchoTest(BaseCommand):
    help_message = "Repeats the message that's just been heard."
    listen = "echo"

    def perform_action(self):
        self.respond("Echo test: " + self.message)


class DiceRoll(BaseCommand):
    listen = "roll"

    def perform_action(self):
        dice = random.randint(1, 100)
        dice = str(dice)
        self.respond(dice)
