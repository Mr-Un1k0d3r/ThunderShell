#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: launcher
"""

import os
import sys

from core.utils import Utils
from core.ui import UI

# Make sure all the dependencies are installed

UI.banner()
Utils.check_dependencies()

from core.config import CONFIG
from core.redisquery import RedisQuery
from core.httpd import init_httpd_thread
from core.gui import init_gui_thread
from core.cli import Cli

if __name__ == '__main__':

    if len(sys.argv) < 3:
        UI.error('''Missing configuration file path or username\n\n Usage: %s config username (optional -nohttpd, -nogui)''' % sys.argv[0], True)

    config = CONFIG(sys.argv[1])
    if config.reload_config():
        config = CONFIG(sys.argv[1])

    profile = config.get('http-profile')
    if not profile == '':
        Utils.file_exists(profile, True)
        profile = CONFIG(profile)
        config.set('profile', profile)

    uid = Utils.guid()
    config.set('uid', uid)
    config.set('username', '%s' % sys.argv[2])
    config.set('payload-callback', '%s:%s' % (config.get('http-fqdn'), config.get('http-port')))  # Temporary
    db = RedisQuery(config)

    config.set('redis', db)

    db.update_config(config).init_sql()
    UI.warn('Current Active CLI session UUID is %s' % config.get('uid'))

    cli = Cli(config)

    # Launch the GUI
    if not '-nogui' in sys.argv:
        webui_thread = init_gui_thread(config, cli)

    # Launch the HTTPD daemon
    if not '-nohttpd' in sys.argv:
        httpd_thread = init_httpd_thread(config)

    while True:
        try:
            cmd = cli.prompt()
            cli.parse_cmd(cmd)
        except KeyboardInterrupt, e:
            UI.error('*** You really want to exit the application? *** (yes/no)')
            if UI.prompt('Exit').lower() == 'yes':
                os._exit(0)
                sql.shutdown()
