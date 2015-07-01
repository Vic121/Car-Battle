#!/usr/bin/python
# -*- coding: utf-8 -*-
# echobot.py -- echo messages back to sender

import msnp
import time


class MsnChatListener(msnp.ChatCallbacks):
    def message_received(self, passport_id, display_name, text, charset):
        print '%s: %s' % (passport_id, text)
        self.chat.send_message(text, charset)


class MsnListener(msnp.SessionCallbacks):
    def chat_started(self, chat):
        callbacks = MsnChatListener()
        chat.callbacks = callbacks
        callbacks.chat = chat


msn = msnp.Session(MsnListener())
msn.login('trinity@hotmail.com', 'Z10N0101')

while True:
    msn.process(chats=True)
    time.sleep(1)
