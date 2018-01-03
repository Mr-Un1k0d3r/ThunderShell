"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/gui.py
"""
from core.apis import CliApi
from appJar import gui
import hashlib

class ThunderShellGUI:
    GUI_VERSION = "1.0"
    
    def __init__(self):
        self.config = {}
        self.app = None
        
    def launch(self):
        self.init_main_ui()
        
    def init_login_ui(self):
        self.app.startSubWindow("login", modal=True)
        self.app.setGeometry("420x200")
        self.app.setLocation("CENTER")
        self.app.startLabelFrame("Connect to a ThunderShell server")
        self.app.setLabelFramePadding("Connect to a ThunderShell server", 15, 15)
        self.app.setSticky("ew")
        self.app.addLabelEntry("Server  ")
        self.app.addLabelSecretEntry("Password")   
        self.app.addEmptyLabel("login_msg")
        self.app.setLabelFg("login_msg", "red")
        
        login_event = self.login_click  
        self.app.addButtons(["Login"], login_event)
        self.app.stopLabelFrame()
        self.app.setFocus("Server  ")
        self.app.stopSubWindow()
        self.app.showSubWindow("login")
        
    def init_main_ui(self):
        self.app = gui("ThunderShell GUI" , "1500x900")
        self.app.setLocation("CENTER")
        self.app.setGuiPadding(15, 15)
        self.app.setFont(size=10, font="Consolas")
        self.init_login_ui()
        self.app.go()

    def init_tabs(self):
        self.app.startTabbedFrame("main_tabs")
        self.app.startTab("Tab1")
        self.app.addLabel("l1", "Tab 1 Label")
        self.app.stopTab()

    def init_data(self):
        self.init_tabs()
        self.init_menu()
        self.init_status_bar()
        
    def init_menu(self):
        self.app.createMenu("main_menu", tearable=False)
        fileMenus = ["Refresh", "-", "Close"]
        self.app.addMenuList("File", fileMenus, self.login_click)
    
    def init_status_bar(self):
        self.app.addStatusbar(fields=3)
        self.app.setStatusbar("Connected on %s" % self.config["server"], 0)
        self.app.setStatusbar("Active shells: 0", 1)
     
    def login_click(self, action):           
        self.config["server"] = self.app.getEntry("Server  ")
        self.config["password"] = hashlib.sha512(self.app.getEntry("Password")).hexdigest()
        self.config["version"] = self.GUI_VERSION
        
        cliapi = CliApi(self.config)
        if not cliapi.ping():
            self.app.setLabel("login_msg", "Login Failed. Server error.")
        
        if not cliapi.login():
            self.app.setLabel("login_msg", "Login Failed. Wrong password.")
        else:
            self.app.hideSubWindow("login")
            self.init_data()