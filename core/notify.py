#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/notify.py
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailNotify:

    def __init__(self, config):
        self.config = config
        self.init_config()

    def init_config(self):
        self.source = self.config.get("notify-email-username")
        self.password = self.config.get("notify-email-password")
        self.server = self.config.get("notify-email-server")
        self.server_port = int(self.config.get("notify-email-server-port"))
        self.subject = self.config.get("notify-email-subject")
        self.destination = self.config.get("notify-list")
        self.tls = self.config.get("notify-email-server-tls")

    def send_notification(self, data):
        if self.config.get("notify-new-shell") == "on":
            for to in self.destination:
                self.send_email(to, self.format_message(to, data))

    def format_message(self, to, data):
        message = MIMEMultipart()
        message["From"] = self.source
        message["To"] = to
        message["Subject"] = self.subject
        message.attach(MIMEText(data, "plain"))
        return message.as_string()

    def send_email(self, to, data):
        connector = smtplib.SMTP(self.server, self.server_port)
        if self.tls == "on":
            connector.starttls()

        connector.login(self.source, self.password)
        connector.sendmail(self.source, to, data)
        connector.quit()
