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


class WorkTimeModule:
    def __init__(self, confile=None):
        self.__confile = confile
        self.__timelist = list()
        self.__dayrange = list()
        self.__employeelist = list()
        self.__hostname = None
        self.__smtphostname = None
        self.__username = None
        self.__password = None

    def processing(self):
        self.__get_param()
        self.__get_mail()
        if self.__sendmail == "True":
            self.__send_mail()

    def __get_param(self):
        if self.__confile == None:
            return
        config = configparser.ConfigParser()
        try:
            config.read([os.path.expanduser(self.__confile)])
            self.__imaphostname = config.get('mailaccountinfo', 'imaphostname')
            self.__imapusername = config.get('mailaccountinfo', 'imapusername')
            self.__imappassword = config.get('mailaccountinfo', 'imappassword')
            self.__smtphostname = config.get('mailaccountinfo', 'smtphostname')
            self.__smtpusername = config.get('mailaccountinfo', 'smtpusername')
            self.__smtppassword = config.get('mailaccountinfo', 'smtppassword')
            self.__mailfolder = config.get('mailaccountinfo', 'mailfolder')
            self.__employeelist = config.get('employees', 'namelist').split(",")
            self.__mailtolist = config.get('mailtolist', 'namelist').split(",")
            self.__timelist.append(config.get('time', 'time1'))
            self.__timelist.append(config.get('time', 'time2'))
            self.__dayrange.append(config.get('time', 'day_start'))
            self.__dayrange.append(config.get('time', 'day_end'))
            self.__sendmail = config.get('sendmail', 'sendmail')

            # file handler.
            self.__output_filename = "output.csv"
            self.__output_file_hdl = file(self.__output_filename, "w")
            self.__write_results("Employee", "Time", "Mail subject", "Counts")
        except Exception as e:
            print(e)
            return

    def __my_unicode(self, s, encoding):
        if encoding:
            return unicode(s, encoding)
        else:
            return unicode(s)

    def __get_charset(self, message, default='ascii'):
        return message.get_charset

    def __get_mail(self, port=993, ssl=1):  # 获取邮件
        if ssl == 1:
            imap_server = imaplib.IMAP4_SSL(self.__imaphostname, port)
        else:
            imap_server = imaplib.IMAP4(self.__imaphostname, port)
        imap_server.login(self.__imapusername, self.__imappassword)
        s = imap_server.select(self.__mailfolder)
        resp, items = imap_server.search(None, 'ALL')
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
                times = self.__check_work_overtime(msg['Date'], self.__timelist)
                if times:
                    if self.__check_name(strfrom):
                        print(strfrom, ",", strdate[5:25], ",", subject[0][0], ",", times)
                        self.__write_results(strfrom, strdate[5:25], subject[0][0], str(times))
            except Exception as e:
                print(e)

        # close imap server.
        self.__output_file_hdl.close()
        imap_server.close()
        imap_server.logout()

    def __check_work_overtime(self, str_date=None, time_list=None):
        if str_date == None or time_list == None:
            return False
        date_for_compare = time.strptime(str_date[5:24], '%d %b %Y %H:%M:%S')
        month_begin = time.strptime(self.__dayrange[0], "%Y-%m-%d")
        month_end = time.strptime(self.__dayrange[1], "%Y-%m-%d")
        date_string = (re.search("\d+:\d+:\d+", str_date)).group(0)
        if date_for_compare > month_begin and date_for_compare < month_end:
            time1 = time.strptime(self.__timelist[0], "%H:%M:%S")
            time2 = time.strptime(self.__timelist[1], "%H:%M:%S")
            time_list = time.strptime(date_string, "%H:%M:%S")
            if time_list >= time2:
                return 2
            elif time_list >= time1 and time_list < time2:
                return 1
            else:
                return 0

    def __check_name(self, name):
        for single_name in self.__employeelist:
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
        smtp.connect(self.__smtphostname)
        smtp.login(self.__smtpusername, self.__smtppassword)
        smtp.sendmail(self.__smtpusername, self.__mailtolist, msgRoot.as_string())
        smtp.quit()

    def __del__(self):
        pass


if __name__ == '__main__':
    confile = ".configuration.cfg"
    print('begin processing...')
    mailobj = WorkTimeModule(confile)
    mailobj.processing()
    print("Completed. ")

