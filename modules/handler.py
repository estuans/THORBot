__author__ = 'Platinum'


def action(self, user, channel, message):
    user = user.split('!', 1)[0]
    self.logger.log("[{c}] * {u} {m}".format(c=channel, u=user, m=message))