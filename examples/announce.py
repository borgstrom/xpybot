#!/usr/bin/env python
#
# This is a bot that is used to announce things into a chat room
#
# It does so by creating a unix socket and sending the messages
# it receives over the socket into the chat room.
#
# To send messages to the bot you'll need something that can connect
# to a UNIX socket, here's a simple python implementation that sends
# what it receives on STDIN but you can also use tools like socat.
#
# #!/usr/bin/env python
# import socket
# import sys
#
# s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
# s.connect(sys.argv[1])
# for line in sys.stdin:
#        s.send(line)
#        s.close()
#
#

from xpybot import XPyBot

import logging
import logging.handlers

import select
import socket
import sys
import Queue

import os

class Announce(XPyBot):
    def __init__(self, sock, logs):
        # setup the parameters needed for your xmpp server
        self.server = ('your-xmpp-server.yourdomain.com', 5222)
        self.require_tls = True

        # this is the ID your bot will use to connect
        self.jid = 'announcebot@yourdomain.com/announcebot'
        self.password = 'shhh-this-is-secret'

        # this is the room to join & send our messages to
        self.room = 'chatroom@conference.yourdomain.com'
        self.room_password = None

        print "Announce Bot - Starting up..."

        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            os.remove(sock)
        except OSError:
            pass

        print "Binding to socket: %s" % sock

        self.socket.bind(sock)
        self.socket.listen(1)
        self.socket.setblocking(0)
        self.message_queues = {}

        self.epoll = select.epoll()
        self.epoll.register(self.socket.fileno(), select.EPOLLIN)
        self.connections = {}
        self.incoming = {}

    def process(self):
        """
        Check for incoming data from the announce socket
        """
        events = self.epoll.poll(0.5)
        for fileno, event in events:
            if fileno == self.socket.fileno():
                conn, addr = self.socket.accept()
                conn.setblocking(0)
                self.epoll.register(conn.fileno(), select.EPOLLIN)
                self.connections[conn.fileno()] = conn
                self.incoming[conn.fileno()] = ''
            else:
                if event & select.EPOLLIN:
                    self.incoming[fileno] += self.connections[fileno].recv(1024)
                if event & select.EPOLLHUP:
                    self.groupchat(self.room, self.incoming[fileno])
                    self.epoll.unregister(fileno)
                    self.connections[fileno].close()
                    del self.incoming[fileno]
                    del self.connections[fileno]

    def startup(self):
        self.status('Surly')
        self.join_muc(self.room, self.room_password)
        self.groupchat(self.room, 'I know it\'s exciting that I\'m back. But please hold your applause.')

    def handle_subscribe(self, msg):
        who = msg.getFrom()
        if msg.getType() == 'subscribe':
            self.presence(to=who, typ='subscribed')
            self.presence(to=who, typ='subscribe')

if __name__ == '__main__':
    import getopt, sys
    try:
        opts, args = getopt.getopt(sys.argv[1:], "s:", ["socket="])
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(1)

    sock = None
    for o, a in opts:
        if o in ('-s', '--socket'):
            sock = a
        else:
            assert False, "unhandled option"

    if sock is None:
        assert False, "need socket"

    bot = Announce(sock, logs)
    bot.run()
