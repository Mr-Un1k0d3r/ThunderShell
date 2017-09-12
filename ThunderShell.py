"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: launch
"""
import os
import sys
from core.config import CONFIG
from core.redisquery import RedisQuery
from core.httpd import init_httpd_thread
from core.cli import Cli
from core.ui import UI

if __name__ == "__main__":
    UI.banner()
    
    if len(sys.argv) < 2:
        UI.error("Missing configuration file path\n\nUsage: %s config (optional -nohttpd)" % sys.argv[0], True)
        
    config = CONFIG(sys.argv[1])
    db = RedisQuery(config)
    config.set("redis", db)
    
    
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
            