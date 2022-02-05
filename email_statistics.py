#!/usr/bin/env python
# coding:utf-8

import imaplib
import email
import sys
import configparser
import os
import datetime
import time
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header
import smtplib
import logging
import json


def logging_settings():
    log_format = '%(asctime)s %(name)s %(levelname)s %(module)s: %(message)s'
    logging.basicConfig(filename='email_statistics.log',
                        format=log_format,
                        datefmt='%Y-%m-%d %H:%M:%S %p',
                        level=10)


class ConfigInfo:
    def __init__(self, config_file='./.configuration.cfg'):
        self._config = configparser.ConfigParser()
        self._config.read([os.path.expanduser(config_file)])

    @property
    def imap_hostname(self):
        return self._config.get('mailaccountinfo', 'imaphostname')

    @property
    def imap_username(self):
        return self._config.get('mailaccountinfo', 'imapusername')

    @property
    def imap_password(self):
        return self._config.get('mailaccountinfo', 'imappassword')

    @property
    def smtp_hostname(self):
        return self._config.get('mailaccountinfo', 'smtphostname')

    @property
    def smtp_username(self):
        return self._config.get('mailaccountinfo', 'smtpusername')

    @property
    def smtp_password(self):
        return self._config.get('mailaccountinfo', 'smtppassword')

    @property
    def mail_folder(self):
        return self._config.get('mailaccountinfo', 'mailfolder')

    @property
    def employee_list(self):
        return self._config.get('employees', 'namelist').split(",")

    @property
    def receivers_list(self):
        return self._config.get('mailtolist', 'namelist').split(",")

    @property
    def time_list(self):
        time_list = []
        time_list.append(self._config.get('time', 'time1'))
        time_list.append(self._config.get('time', 'time2'))
        return time_list

    @property
    def day_range(self):
        day_range = []
        day_range.append(self._config.get('time', 'day_start'))
        day_range.append(self._config.get('time', 'day_end'))
        return day_range

    @property
    def is_send_email(self):
        return True if self._config.get('sendmail', 'sendmail') == 'True' else False

    def __str__(self):
        imap_info, smtp_info, mail_info = {}, {}, {}

        # imap info
        imap_info['hostname'] = self.imap_hostname
        imap_info['username'] = self.imap_username
        imap_info['password'] = self.imap_password

        # smtp info
        smtp_info['hostname'] = self.smtp_hostname
        smtp_info['username'] = self.smtp_hostname
        smtp_info['password'] = self.smtp_password

        # mail info
        mail_info['mail_folder'] = self.mail_folder
        mail_info['employee_list'] = self.employee_list
        mail_info['receivers_list'] = self.receivers_list
        mail_info['time_range'] = self.time_list
        mail_info['day_range'] = self.day_range
        mail_info['is_send'] = self.is_send_email

        config_info = {'imap_info': imap_info,
                       'smtp_info': smtp_info,
                       'mail_info': mail_info}
        return json.dumps(config_info)


class WorkTimeModule:
    def __init__(self, confile=None):
        self._config_info = ConfigInfo(confile)
        self.__hostname = None
        self.__username = None
        self.__password = None

    def processing(self):
        self.__get_param()
        self.__get_mail()
        if self._config_info.is_send_email:
            logging.info('Send info to specified email.')
            self.__send_mail()

    def __str__(self):
        imap_info, smtp_info, mail_info = {}, {}, {}

        # imap info
        imap_info['hostname'] = self._config_info.imap_hostname
        imap_info['username'] = self._config_info.imap_username
        imap_info['password'] = self._config_info.imap_password

        # smtp info
        smtp_info['hostname'] = self._config_info.smtp_hostname
        smtp_info['username'] = self._config_info.smtp_username
        smtp_info['password'] = self._config_info.smtp_password

        # mail info
        mail_info['mail_folder'] = self._config_info.mail_folder
        mail_info['employee_list'] = self._config_info.employee_list
        mail_info['receivers_list'] = self._config_info.receivers_list
        mail_info['time_range'] = self._config_info.time_list
        mail_info['day_range'] = self._config_info.day_range
        mail_info['is_send'] = self._config_info.is_send_email

        config_info = {'imap_info': imap_info,
                       'smtp_info': smtp_info,
                       'mail_info': mail_info}
        return json.dumps(config_info)

    def __get_param(self):
        logging.info("Get configuration info.")
        try:
            # file handler.
            self.__output_filename = "output.csv"
            self.__output_file_hdl = file(self.__output_filename, "w")
            self.__write_results("Employee", "Time", "Mail subject", "Counts")
        except Exception as e:
            logging.critical(e)

    def __my_unicode(self, s, encoding):
        if encoding:
            return unicode(s, encoding)
        else:
            return unicode(s)

    def __get_charset(self, message, default='ascii'):
        return message.get_charset

    def __get_mail(self, port=993, ssl=1):  # 获取邮件
        if ssl == 1:
            imap_server = imaplib.IMAP4_SSL(self._config_info.imap_hostname, port)
        else:
            imap_server = imaplib.IMAP4(self._config_info.imap_hostname, port)

        logging.info('Login email.')
        imap_server.login(self._config_info.imap_username, self._config_info.imap_password)
        s = imap_server.select(self._config_info.mail_folder)
        resp, items = imap_server.search(None, 'ALL')
        logging.info('Loop all sended emails.')
        for i in items[0].split():
            resp, data = imap_server.fetch(i, '(RFC822.SIZE BODY[HEADER.FIELDS (SUBJECT FROM DATE)])')
            msg = email.message_from_string(data[0][1])
            try:
                whosend = msg['From'].split(' ')
                if (len(whosend) == 2):
                    fromname = email.Header.decode_header((whosend[0]).strip('\"'))
                    strfrom = (whosend[1].strip("<")).strip(">")
                else:
                    strfrom = msg['From']
                strdate = msg['Date']
                subject = email.Header.decode_header(msg['Subject'])  # 得到一个list

                # output contents
                times = self.__check_work_overtime(msg['Date'], self._config_info.time_list)
                if times:
                    if self.__check_name(strfrom):
                        print(strfrom, ",", strdate[5:25], ",", subject[0][0], ",", times)
                        self.__write_results(strfrom, strdate[5:25], subject[0][0], str(times))
            except Exception as e:
                print(e)

        # close imap server.
        self.__output_file_hdl.close()
        logging.info("Close email connection.")
        imap_server.close()
        imap_server.logout()

    def __check_work_overtime(self, str_date=None, time_list=None):
        if str_date == None or time_list == None:
            return False
        date_for_compare = time.strptime(str_date[5:24], '%d %b %Y %H:%M:%S')
        month_begin = time.strptime(self._config_info.day_range[0], "%Y-%m-%d")
        month_end = time.strptime(self._config_info.day_range[1], "%Y-%m-%d")
        date_string = (re.search("\d+:\d+:\d+", str_date)).group(0)
        if date_for_compare > month_begin and date_for_compare < month_end:
            time1 = time.strptime(self._config_info.receivers_list[0], "%H:%M:%S")
            time2 = time.strptime(self._config_info.receivers_list[1], "%H:%M:%S")
            time_list = time.strptime(date_string, "%H:%M:%S")
            if time_list >= time2:
                return 2
            elif time_list >= time1 and time_list < time2:
                return 1
            else:
                return 0

    def __check_name(self, name):
        for single_name in self._config_info.employee_list:
            name_match_pattern = re.search(r"{0}".format(single_name), name)
            if name_match_pattern:
                return True
        return False

    def __write_results(self, employee_name, work_date, mail_subject, times):
        self.__output_file_hdl.write(employee_name + "," + work_date + "," + mail_subject + "," + times + "\n")

    def __send_mail(self):
        att = MIMEApplication(open(self.__output_filename, 'rb').read())
        att.add_header('Content-Disposition', 'attachment', filename=self.__output_filename)

        msg = MIMEText("Please check attachment")

        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = "working time summary"
        msgRoot.attach(att)
        msgRoot.attach(msg)

        smtp = smtplib.SMTP_SSL()
        smtp.connect(self._config_info.smtp_hostname)
        smtp.login(self._config_info.smtp_username, self._config_info.smtp_password)
        smtp.sendmail(self._config_info.smtp_username, self._config_info.receivers_list, msgRoot.as_string())
        smtp.quit()

    def __del__(self):
        pass


if __name__ == '__main__':
    confile = ".configuration.cfg"
    logging.info('begin processing...')
    logging_settings()
    mail_hdl = WorkTimeModule(confile)
    print(mail_hdl)
    # mailobj.processing()
    # logging.info("Completed. ")

