import logging
import platform
import sys
import time
import xmpp

from exceptions import *

from optparse import OptionParser

class XPyBot(object):
    parser = None

    server = None
    jid = None
    password = None
    resource = None
    require_tls = True

    client = None

    connected = False
    connect_retry = None

    authenticated = False

    def run(self):
        """
        Start the bot
        """
        while True:
            try:
                if not self.connected or not self.authenticated:
                    self.connect()
                else:
                    self.client.Process(1)
                    self.process()
            except BotConnectionException:
                if self.connect_retry and int(self.connect_retry) > 0:
                    time.sleep(self.connect_retry)
                else:
                    break
            except BotAuthenticationException:
                break
            except KeyboardInterrupt:
                break

        if self.client:
            self.client.disconnect()

    def startup(self):
        """
        Called to allow bots to preform commands once authenticated
        """
        pass

    def process(self):
        """
        Called to allow bots to process data outside of the main loop
        """
        pass

    def send(self, *args, **kwargs):
        """
        Sends arbitrary data with the current client
        """
        if self.client:
            return self.client.send(*args, **kwargs)

    def message(self, *args, **kwargs):
        """
        Sends a Message object
        """
        return self.send(xmpp.protocol.Message(*args, **kwargs))

    def chat(self, *args, **kwargs):
        """
        Sends a Message object with the type preset to 'chat'
        """
        kwargs['typ'] = 'chat'
        return self.message(*args, **kwargs)

    def groupchat(self, *args, **kwargs):
        """
        Sends a Message object with the type preset to 'groupchat'
        """
        kwargs['typ'] = 'groupchat'
        return self.message(*args, **kwargs)

    def handle_message(self, session, message):
        if message.getType() == 'chat':
            self.handle_chat(message)
        elif message.getType() == 'groupchat':
            self.handle_groupchat(message)
        else:
            print message

    def handle_chat(self, message):
        pass

    def handle_groupchat(self, message):
        pass

    def handle_presence(self, session, message):
        if message.getType() == 'subscribe':
            self.handle_subscribe(message)
        else:
            print message

    def handle_subscribe(self, message):
        pass

    def connect(self):
        if isinstance(self.jid, basestring):
            self.jid = xmpp.JID(self.jid)

        if self.client is None:
            self.client = xmpp.Client(self.jid.getDomain(), debug=[])

        print self.server
        self.connected = self.client.connect(self.server)
        if not self.connected:
            raise BotConnectionException("Could not connect to server")
        if self.connected != 'tls' and self.require_tls:
            raise BotConnectionException("Connection does not use TLS")

        # setup handlers
        self.client.RegisterHandler('message', self.handle_message)
        self.client.RegisterHandler('presence', self.handle_presence)

        # authenticate
        if not self.resource:
            self.resource = platform.node()
        self.authenticated = self.client.auth(self.jid.getNode(), self.password, self.resource)
        if not self.authenticated:
            raise BotAuthenticationException("Failed to authenticate")

        # set initial presence
        self.client.sendInitPresence()

        # fetch the roster
        self.roster = self.client.getRoster()

        # do custom startup
        self.startup()

    def join_muc(self, room, password=None):
        """
        Join a conference room
        """
        if self.authenticated:
            # join the conference room
            presence = xmpp.Presence(to="%s/%s" % (room, self.jid.getResource()))
            if password:
                presence.setTag('x', namespace=xmpp.NS_MUC).setTagData('password', password)
            presence.getTag('x').addChild('history', {'maxchars': '0', 'maxstanzas': '0'})
            self.client.send(presence)
