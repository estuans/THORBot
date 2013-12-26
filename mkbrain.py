__author__ = 'Platinum'

import redis
import random
import ConfigParser

cfg = ConfigParser.RawConfigParser()
cfg.read("hammer.ini")


def split_message(self, message):
    words = message.split()

    if len(words) > self.chain_length:
        #Append stopword
        words.append(self.stop_word)

        for i in range(len(words) - self.chain_length):
            yield words[i:i + self.chain_length + 1]


def generate_message(self, seed):
    key = seed

    gen_words = []

    for i in xrange(self.max_words):

        words = key.split(self.separator)

        gen_words.append(words[0])

        next_word = self.redis_conn.srandmember(self.make_key(key))
        if not next_word:
            break

        key = self.separator.join(words[1:] + [next_word])

    return ' '.join(gen_words)


def log(self, sender, message, channel):
    channel = cfg.get('Connection', 'channel')
    say_something = self.is_ping(message) or (sender != self.conn.nick and random.random() < self.chattiness)

    messages = []

    if self.is_ping(message):
        message = self.fix_ping(message)

    if message.startswith('/'):
        return

    for words in self.split_message(self.sanitize_message(message)):

        key = self.separator.join(words[:-1])

        self.redis_conn.sadd(self.make_key(key), words[-1])

    if say_something:
        best_message = ''
        for i in range(self.messages_to_generate):
            generated = self.generate_message(seed=key)
            if len(generated) > len(best_message):
                best_message = generated

        if best_message:
            messages.append(best_message)

    if len(messages):
        return random.choice(messages)