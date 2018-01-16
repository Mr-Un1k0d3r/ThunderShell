"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/gui.py
"""

from core.apis import CliApi
from appJar import gui
import threading
import hashlib
import time
import os
import base64

class ThunderShellGUI:
    GUI_VERSION = "1.0"
    
    def __init__(self):
        self.config = {}
        self.app = None
        self.cliapi = None
        self.current_shell_id = None
        self.current_data_hash = None
        
    def launch(self):
        self.init_main_ui()
        
    def init_login_ui(self):
        self.app.startSubWindow("login", modal=True)
        self.app.setGeometry("420x200")
        self.app.setLocation("CENTER")
        self.app.startLabelFrame("Connect to a ThunderShell server")
        self.app.setLabelFramePadding("Connect to a ThunderShell server", 15, 15)
        self.app.setSticky("ew")
        self.app.addLabel("server", "Server:", 0, 0)
        self.app.addEntry("Server", 0, 1)
        self.app.setLabelAlign("server", "left")
        self.app.addLabel("password", "Password:", 2, 0)
        self.app.addEmptyLabel("padding", 1, 0)     
        self.app.addSecretEntry("Password", 2, 1)   
        self.app.addEmptyLabel("login_msg", colspan=2)
        self.app.setLabelFg("login_msg", "red")
        self.app.addButtons(["Login"], self.login_click, colspan=2)
        self.app.stopLabelFrame()
        self.app.setFocus("Server")
        self.app.stopSubWindow()
        self.app.showSubWindow("login")
        
    def init_main_ui(self):
        self.app = gui("ThunderShell GUI" , "1500x900")
        self.app.setLocation("CENTER")
        self.app.setFont(size=10, font="Consolas")
        self.init_login_ui()
        self.app.go()

    def init_data(self):
        self.init_shell_ui()
        self.init_menu()
        self.init_status_bar()
        self.refresh_shell()
        self.refresh_active_shell_data()

    def init_shell_ui(self):
        self.app.startPanedFrame("left_pane")
        self.app.addListBox("shell_list", [], 0, 0, 0, 2)
        self.app.setListBoxSubmitFunction("shell_list", self.get_shell_from_list)
        self.app.setListBoxWidth("shell_list", 45)
        self.app.startPanedFrame("right_pane")
        self.app.addScrolledTextArea("shell_output", 0, 0, 0, 2)
        #self.app.disableTextArea("shell_output")
        self.app.setTextAreaBg("shell_output", "black")
        self.app.setTextAreaFg("shell_output", "green")
        self.app.setSticky("sw")
        self.app.setStretch("both")
        self.app.addLabelEntry(">>>")
        self.app.setLabelBg(">>>", "black")
        self.app.setLabelFg(">>>", "green")
        self.app.setEntryBg(">>>", "black")
        self.app.setEntryFg(">>>", "green")
        self.app.setEntryWidth(">>>", 300)
        self.app.setEntrySubmitFunction(">>>", self.get_input)
        self.app.stopPanedFrame()
        self.app.stopPanedFrame()
        
    def init_menu(self):
        tools = ["Refresh Shells", "Save Current", "Exit"]
        self.app.addToolbar(tools, self.menu_click, findIcon=False)
        
    def init_status_bar(self):
        self.app.addStatusbar(fields=3)
        self.app.setStatusbar("Connected to %s" % self.config["server"], 0)
        self.app.setStatusbarWidth(30, 0)
        self.app.setStatusbarWidth(75, 1)
        self.app.registerEvent(self.init_event_functions)
        
    def init_event_functions(self):
        self.app.setStatusbar(time.strftime("%d-%m-%Y %H:%M"), 2)
        
    def refresh_shell(self):
        self.app.clearListBox("shell_list")
        shells = self.cliapi.list_shell()
        for shell in shells["shells"]:
            self.app.addListItem("shell_list", str(shell))
            
        self.app.addListItem("shell_list", "Select a session")
        self.app.after(60000, self.refresh_shell) # Refresh shell every 60 seconds

    def refresh_active_shell_data(self):
        data = self.cliapi.get_shell_data(self.current_shell_id)
        try:
            data = base64.b64decode(data["data"])
            new_data_hash = hashlib.md5(data).hexdigest()
            if not new_data_hash == self.current_data_hash:
                self.app.clearTextArea("shell_output")
                self.app.setTextArea("shell_output", data)
                self.current_data_hash = new_data_hash
        except:
            self.app.setStatusbar("Failed to fetch data for %s" % self.current_shell_id, 1)
            self.app.setTextArea("shell_output", "Nothing to display")
        self.app.after(3000, self.refresh_active_shell_data) # Refresh shell output every 3 seconds
        
    def get_input(self, widget):
        data = self.app.getEntry(widget)
        self.app.clearEntry(widget)
        self.cliapi.send_shell_cmd(self.current_shell_id, {"data": base64.b64decode(data)})
        
    def get_shell_from_list(self, shell):
        data = self.app.getListBox(shell)
        if len(data) == 1:
            id = data[0].split(" ")[0]
            self.current_shell_id = id
            self.refresh_active_shell_data()
            
    def menu_click(self, tab):
        if tab == "Refresh Shells":
            self.refresh_shell()
        elif tab == "Save Current":
            self.app.setStatusbar("Not implemented", 1)
        else:
            os._exit(0)
            
    def login_click(self, action):           
        self.config["server"] = self.app.getEntry("Server").strip()
        self.config["password"] = hashlib.sha512(self.app.getEntry("Password")).hexdigest()
        self.config["version"] = self.GUI_VERSION
        self.cliapi = CliApi(self.config)
        
        if not self.cliapi.ping():
            self.app.setLabel("login_msg", "Login Failed. Server error.")
        elif not self.cliapi.login():
            self.app.setLabel("login_msg", "Login Failed. Wrong password.")
        else:
            self.app.hideSubWindow("login")
            self.init_data()