"""
Various IRC games.
"""

from twisted.words.protocols import irc
import random


class Logic():

    def __init__(self, msg):
        self.msg = msg(self)
        return

    @staticmethod
    def player(self, user):
        ply = user

        ply_score = []

    @staticmethod
    def qholder(self, msg, channel):

        #Question block 1
        a1 = "Can a blue pattern can be checkered if it's striped?"
        a2 = "Can you smelt a piece of plastic if it's blue?"
        a3 = "Can you overvalue a piece of jewelry if it's fake?"
        a4 = "Can a blue sky be clear if it's sunny?"
        a5 = "Can an old man be retired if he's active?"
        a6 = "Can a purple checkered tie be rugged if it's blue?"
        a7 = "Can a die-hard fan be active if he's a doctor?"

        #Question block 2
        b1 = "Can a purple checkered tie be patterned if it's green?"
        b2 = "Can a hot oven be warm if it's on?"
        b3 = "Can a glove with holes be warm if it's green?"
        b4 = "Can a bald man shave his beard if he's active?"
        b5 = "Can a weird man be healthy if he's sick?"
        b6 = "Can a black car have four wheels if it runs on diesel?"
        b7 = "Can a blue ship with holes sink if it's colourful?"

        qbl1 = [a1, a2, a3, a4, a5, a6, a7]
        qbl2 = [b1, b2, b3, b4, b5, b6, b7]
        qblo = [qbl1, qbl2]

        if msg == "!logic":
            msg = "In the 'logic' game, you're asked to either agree or disagree(with a 'Yes' or a 'No')" \
                  " on a randomly select question. There are no poits. It's all for fun. Let the game begin!"
            self.msg(channel, msg)

            qt = random.choice(qblo)
            msg = qt

        ans = msg
        ct = "Yes"
        cf = "False!"
        fa = "No"
        ca = "Correct!"

        if qbl1 in (a1, a6):
            if ans == ct:
                msg = fa
                self.msg(channel, msg)
            if ans == cf:
                msg = ca
                self.msg(channel, msg)
        elif qbl1 in (a2, a3, a4, a5, a7):
            if ans == ct:
                msg = ca
                self.msg(channel, msg)
            if ans == cf:
                msg = fa
                self.msg(channel, msg)

        if qbl2 in (b1, b5, b7):
            if ans == ct:
                msg = fa
                self.msg(channel, msg)
            if ans == cf:
                msg = ca
                self.msg(channel, msg)

        if qbl2 in (b2, b3, b4, b6):
            if ans == ct:
                msg = ca
                self.msg(channel, msg)
            if ans == cf:
                msg = fa
                self.msg(channel, msg)
