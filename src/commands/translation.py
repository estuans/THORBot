
import goslate
from operator import itemgetter

from base import BaseCommand

class TranslateTo(BaseCommand):
    listen = "tr"
    help_message = "Translates the source language into the target language"

    def perform_action(self):
        gs = goslate.Goslate()

        wlist = self.message.split(' ')

        slang = itemgetter(1)(wlist)
        tlang = itemgetter(2)(wlist)

        slangrep = '%s' % slang
        tlangrep = '%s' % tlang

        phrase = itemgetter(slice(3, None))(wlist)

        phrase_ = ' '.join(phrase)
        reply = gs.translate(phrase_, tlangrep, slangrep)

        self.respond(reply.encode('UTF-8'))

class ToEnglish(BaseCommand):

    listen = "dt"
    help_message = "Translates the detected string to English"

    def perform_action(self):
        gs = goslate.Goslate()

        wlist = self.message.split(' ')

        trans = itemgetter(slice(1, None))(wlist)

        trans = ' '.join(trans)

        source = gs.detect(trans)
        reply = gs.translate(trans, 'en', source)

        self.respond(reply.encode('UTF-8'))