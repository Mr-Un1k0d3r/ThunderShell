"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: launch
"""
import os
import sys

from core.utils import Utils
# Make sure all the dependencies are installed
Utils.check_dependencies()

from core.config import CONFIG
from core.redisquery import RedisQuery
from core.httpd import init_httpd_thread
from core.cli import Cli
from core.ui import UI
from core.mysqlquery import MySQLQuery

if __name__ == "__main__":
    UI.banner()
    
    if len(sys.argv) < 3:
        UI.error("Missing configuration file path or username\n\nUsage: %s config username (optional -nohttpd)" % sys.argv[0], True)
        
    config = CONFIG(sys.argv[1])
    uid = Utils.guid()
    config.set("uid", uid)
    config.set("username", "(CLI)%s" % sys.argv[2])
    db = RedisQuery(config)
    sql = MySQLQuery(config)
    sql.install_db().init_uid()

    config.set("redis", db)
    config.set("mysql", sql)

    db.update_config(config).init_sql()

    UI.success("Current Active session UUID is %s" % config.get("uid"))
    
    # Launch the HTTPD daemon
    if not "-nohttpd" in sys.argv:
        httpd_thread = init_httpd_thread(config)
    
    cli = Cli(config)
    
    while True:
        try:
            cmd = cli.prompt()
            cli.parse_cmd(cmd)
            
        except KeyboardInterrupt as e:
            UI.error("*** You really want to exit the application? *** (yes/no)")
            if UI.prompt("Exit").lower() == "yes":
                os._exit(0)
            
