import os
import logging
import logging.handlers

from django.conf import settings

import datetime

logs_dir = settings.PROJECT_DIR + '/logs/'

today_cat = datetime.datetime.now().strftime("%Y-%m-%d")
# try:
# os.stat(logs_dir + str(today_cat))
# except OSError:
# os.mkdir(logs_dir + str(today_cat), 0777)

class SMTPHandlerWithAuth(logging.handlers.SMTPHandler):
    def emit(self, record):
        """
        Emit a record.

        Format the record and send it to the specified addressees.
        """
        try:
            import smtplib

            try:
                from email.Utils import formatdate
            except:
                formatdate = self.date_time
            # port = self.mailport
            # if not port:
            # 	port = smtplib.SMTP_PORT
            # smtp = smtplib.SMTP(self.mailhost, port)
            msg = self.format(record)
            msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                self.fromaddr,
                ",".join(self.toaddrs),
                self.getSubject(record),
                formatdate(), msg)

            # smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            # smtp.sendmail(self.fromaddr, self.toaddrs, msg)
            # smtp.quit()

            from django.core.mail import send_mail

            send_mail(self.getSubject(record), msg, 'Pick Score <robot@madfb.com>', self.toaddrs, fail_silently=True)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


def create_logger(name=None):
    if name is None:
        logger = logging.getLogger('')
        name = settings.SITE_DIR
    else:
        logger = logging.getLogger(name)

    # hdlr = logging.FileHandler(logs_dir + str(today_cat) + "/%s.log" % (name))
    path = logs_dir + str(today_cat) + ".log"
    if not os.path.exists(path):
        f = open(path, 'w', 0777)
        f.writelines('')
        f.close()

    hdlr = logging.FileHandler(path)
    # formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s',)
    formatter = logging.Formatter('%(asctime)-11s | %(levelname)-6s | %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    if settings.DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return logger


def set_email_logger(logger, subject="Log message"):
    rootLogger = create_logger(logger)
    smtpHandler = SMTPHandlerWithAuth((settings.EMAIL_HOST, settings.EMAIL_PORT), settings.DEFAULT_FROM_EMAIL,
                                      settings.ADMINS[0][1], subject)
    rootLogger.addHandler(smtpHandler)
    return rootLogger


debug_logger = create_logger('debug')
info_logger = create_logger('info')
warning_logger = create_logger('warning')
error_logger = set_email_logger('error', "Error message from " + settings.PROJECT_NAME)
critical_logger = set_email_logger('critical', "CRITICAL message from " + settings.PROJECT_NAME)


def debug(msg):
    debug_logger.debug(msg)


def info(msg):
    info_logger.info(msg)


def warning(msg):
    warning_logger.warning(msg)


def error(msg):
    error_logger.error(msg)


def critical(msg):
    critical_logger.critical(msg)
