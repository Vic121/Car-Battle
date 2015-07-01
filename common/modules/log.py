# -*- coding: utf-8 -*-
import logging

import datetime


class Log(object):
    def __init__(self, engine):
        self.engine = engine
        self.stat = None

    def message(self, message, is_error=False, is_success=False):
        from django.contrib import messages

        if not is_error and not is_success:
            messages.add_message(self.engine.request, messages.INFO, message)
        elif is_success:
            messages.add_message(self.engine.request, messages.SUCCESS, message)
        else:
            messages.add_message(self.engine.request, messages.ERROR, message)

    def add_log(self, log_type='', log_type_id=0, log='', ip=''):
        from django.db import connection

        try:
            sql = """
				INSERT INTO
					archive.garage_user_log
				VALUES (
					'%s', '%s', '%s', '%s', '%s', '%s'
				)
			""" % (str(self.engine.user.user.id), log_type, log_type_id, log, datetime.datetime.now(), str(ip))

            cursor = connection.cursor()
            cursor.execute(sql)
        except:
            logging.warning('Error inserting log to archive')
