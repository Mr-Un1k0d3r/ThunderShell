#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: launcher
"""

import os
import platform 
import sys

# Make sure we are running Python 3
if int(platform.python_version().split(".")[0]) < 3:
    sys.stdout.write("\n\033[31m[-] %s\033[00m\n" % "*** Warning Python 3 is required ***")
    sys.exit(0)

from core.ui import UI
from core.utils import Utils
from core.vars import THUNDERSHELL

# Make sure all of the dependencies are installed
UI.banner()
Utils.check_dependencies()
Utils.check_pyver()
#Utils.check_version()
Utils.start_redis()

from core.cli import Cli
from core.config import CONFIG
from core.httpd import init_httpd_thread
from core.redisquery import RedisQuery
from core.webserver import init_flask_thread

if __name__ == '__main__':

    if len(sys.argv) < 3:
        UI.error('''Missing the config file or username\n\n Usage: %s config username (optional -nohttpd, -nogui)''' % sys.argv[0], True)

    config = CONFIG(sys.argv[1])
    if config.reload_config():
        config = CONFIG(sys.argv[1])

    Utils.suppress_ssl_errors()

    profile = config.get('http-profile')
    if not profile == '':
        Utils.file_exists(profile, True)
        profile = CONFIG(profile)
        config.set('profile', profile)

    uid = Utils.guid()
    config.set('uid', uid)
    config.set('username', '%s' % sys.argv[2])
    db = RedisQuery(config)

    config.set('redis', db)

    UI.warn('Current active CLI session UUID is %s' % config.get('uid'))

    cli = Cli(config)

    # Launch the GUI
    if not '-nogui' in sys.argv:
        webui_thread = init_flask_thread(config, cli)

    # Launch the HTTPD daemon
    if not '-nohttpd' in sys.argv:
        httpd_thread = init_httpd_thread(config)

    while True:
        try:
            cmd = cli.prompt()
            cli.parse_cmd(cmd)
        except KeyboardInterrupt as e:
            UI.error('[*] Are you sure you want to quit? (yes/no)')
            if UI.prompt('Exit').lower() == 'yes':
                os._exit(0)
                sql.shutdown()
