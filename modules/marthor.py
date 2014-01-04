from collections import defaultdict
import re
import random

#MARKOV integration
markov = defaultdict(list)
STOP_WORD = ""


def add_to_brain(msg, chain_length, write_to_file=False):
    if write_to_file:
        f = open('brain.txt', 'a')
        f.write(msg + '\r')
        f.close()
    buf = [STOP_WORD] * chain_length
    for word in msg.split():
        markov[tuple(buf)].append(word)
        del buf[0]
        buf.append(word)
    markov[tuple(buf)].append(STOP_WORD)


def generate_sentence(msg, chain_length, max_words):
    buf = msg.split()[:chain_length]
    if len(msg.split()) > chain_length:
        msg = buf[:chain_length]
    else:
        msg = []
        for i in xrange(chain_length):
            msg.append(random.choice(markov[random.choice(markov.keys())]))
        for i in xrange(max_words):
            try:
                next_word = random.choice(markov[tuple(buf)])
            except IndexError:
                continue
            if next_word == STOP_WORD:
                return
            msg.append(next_word)
            del buf[0]
            buf.append(next_word)
            re.sub("\[(.*?)\] <(.*?)>", '', '')
        return ' '.join(msg)