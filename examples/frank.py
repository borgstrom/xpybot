#!/usr/bin/env python
"""
Frank. The XPyBot test bot.

Frank's a nice guy, he likes to do things for his friends.

First you need to introduce yourself to Frank.
- Add Frank to your roster
- Msg Frank and say "Hi"
- Answer Frank's questions
- He'll authorize & add you back
- Have fun together
"""

from xpybot import XPyBot

STATUS_INTRO = 1
STATUS_QUESTION = 2
STATUS_FRIEND = 3

class Frank(XPyBot):
    require_tls = True
    resource = 'Frank'

    friends = {}
    answers = {}

    def __init__(self, jid, password, server=None):
        self.jid = jid
        self.password = password
        self.server = server

    def startup(self):
        # get the roster and add our existing friends
        pass

    def handle_subscribe(self, msg):
        who = msg.getFrom()
        print "Got a subscribe message from %s" % who
        self.friends[who] = STATUS_INTRO

    def handle_chat(self, msg):
        who = msg.getFrom().getStripped()
        print "Got a chat message from %s" % who
        if who not in self.friends:
            return self.chat(who, 'No thanks.')

        if self.friends[who] == STATUS_INTRO:
            if str(msg.getBody()) == "Hi":
                print "Questioning %s" % who
                self.friends[who] = STATUS_QUESTION
                self.chat(who, 'Well hi there. I\'m Frank')
                self.chat(who, 'Wanna be friends?')

                import random
                op = random.randint(1, 3)
                dig1 = random.randint(5, 15)
                dig2 = random.randint(2, 5)
                if op == 1:
                    self.answers[who] = dig1 + dig2
                    op = "+"
                elif op == 2:
                    self.answers[who] = dig1 - dig2
                    op = "-"
                elif op == 3:
                    self.answers[who] = dig1 * dig2
                    op = "*"

                question = 'What is %d %s %d?' % (dig1, op, dig2)
                print "The question: %s" % question
                print "The answer: %s" % self.answers[who]

                return self.chat(who, question)

        if self.friends[who] == STATUS_QUESTION:
            if who not in self.answers:
                self.friends[who] = STATUS_INTRO
                return

            if str(msg.getBody()) == str(self.answers[who]):
                del self.answers[who]
                self.friends[who] = STATUS_FRIEND
                return self.chat(who, "Correct! We're friends now")

        if self.friends[who] == STATUS_FRIEND:
            return self.chat(who, "Friend said: %s" % msg.getBody())

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print "Usage: frank.py <user> <pass> [server]"
        sys.exit(1)

    server = None
    if len(sys.argv) == 4:
        server = (sys.argv[3], 5222)
    frank = Frank(sys.argv[1], sys.argv[2], server)
    frank.run()
