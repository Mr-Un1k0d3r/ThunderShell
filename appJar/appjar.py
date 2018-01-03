# -*- coding: utf-8 -*-
"""appJar.py: Provides a GUI class, for making simple tkinter GUIs."""
# Nearly everything I learnt came from: http://effbot.org/tkinterbook/
# with help from: http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/index.html
# with snippets from stackexchange.com

# make print & unicode backwards compatible
from __future__ import print_function
from __future__ import unicode_literals

try:
    # for Python2
    from Tkinter import *
    import tkMessageBox as MessageBox
    from tkColorChooser import askcolor
    import tkFileDialog as filedialog
    import ScrolledText as scrolledtext
    import tkFont as font
    PYTHON2 = True
    PY_NAME = "Python"
except ImportError:
    # for Python3
    from tkinter import *
    from tkinter import messagebox as MessageBox
    from tkinter.colorchooser import askcolor
    from tkinter import filedialog
    from tkinter import scrolledtext
    from tkinter import font
    PYTHON2 = False
    PY_NAME = "python3"

import os, sys, locale
import re
import imghdr   # images
import time     # splashscreen
import webbrowser   # links
import calendar # datepicker
import datetime # datepicker & image
import logging  # python's logger
import inspect  # for logging
import argparse # argument parser
from contextlib import contextmanager # generators

import __main__ as theMain
from platform import system as platform

# modules to be imported on demand
ttk = None
hashlib = None
ToolTip = None
nanojpeg = PngImageTk = array = None # extra image support
EXTERNAL_DND = None
INTERNAL_DND = None
types = None            # used to register dnd functions
winsound = None
FigureCanvasTkAgg = Figure = None # matplotlib
parseString = TreeItem = TreeNode = None # ajTree
ajTreeNode = ajTreeData = None
base64 = urlencode = urlopen = urlretrieve = quote_plus = json = None # GoogleMap
ConfigParser = codecs = ParsingError = None # used to parse language files
Thread = Queue = None
frameBase = Frame
labelBase = Label

# details
__author__ = "Richard Jarvis"
__copyright__ = "Copyright 2016-2017, Richard Jarvis"
__credits__ = ["Graham Turner", "Sarah Murch"]
__license__ = "Apache 2.0"
__version__ = "0.82.1"
__maintainer__ = "Richard Jarvis"
__email__ = "info@appJar.info"
__status__ = "Development"
__url__ = "http://appJar.info"
try:
    __locale__ = locale.getdefaultlocale()[0]
except ValueError:
    __locale__ = None

# class to allow simple creation of tkinter GUIs
class gui(object):
    """ Class to represent the GUI
        - Create one of these
        - add some widgets
        - call the go() function
    """

    # ensure only one instance of gui is created
    instantiated = False

    # static variables
    exe_file = None
    exe_path = None
    lib_file = None
    lib_path = None

    @staticmethod
    def CLEAN_CONFIG_DICTIONARY(**kw):
        """ Used by all Classes to tidy up dictionaries passed into config functions
            Allows us to more quickly process the dictionaries when overriding config
        """
        try:
            kw['bg'] = kw.pop('background')
        except:
            pass
        try:
            kw['fg'] = kw.pop('foreground')
        except:
            pass
        kw = dict((k.lower().strip(), v) for k, v in kw.items())
        return kw

    # globals for supported platforms
    WINDOWS = 1
    MAC = 2
    LINUX = 3

    @staticmethod
    def GET_PLATFORM():
        # get the platform
        if platform() in ["win32", "Windows"]:
            return gui.WINDOWS
        elif platform() == "Darwin":
            return gui.MAC
        elif platform() in ["Linux", "FreeBSD"]:
            return gui.LINUX
        else:
            raise Exception("Unsupported platform: " + platform())

    @staticmethod
    def SHOW_VERSION():
        verString = \
            "appJar: " + str(__version__) \
            + "\nPython: " + str(sys.version_info[0]) \
            + "." + str(sys.version_info[1]) + "." + str(sys.version_info[2]) \
            + "\nTCL: " + str(TclVersion) \
            + ", TK: " + str(TkVersion) \
            + "\nPlatform: " + str(platform()) \
            + "\npid: " + str(os.getpid()) \
            + "\nlocale: " + str(__locale__)

        return verString

    @staticmethod
    def SHOW_PATHS():
        pathString = \
            "File Name: " + (gui.exe_file if gui.exe_file is not None else "") \
            + "\nFile Location: " + (gui.exe_path if gui.exe_path is not None else "") \
            + "\nLib Location: " + (gui.lib_path if gui.lib_path is not None else "")

        return pathString

    @staticmethod
    def CENTER(win, up=0):
        """ Centers a tkinter window
        http://stackoverflow.com/questions/3352918/
        :param win: the root or Toplevel window to center
        """
        scr_width = win.winfo_screenwidth()
        scr_height = win.winfo_screenheight()

        if gui.GET_PLATFORM() != gui.LINUX:
            trans = win.attributes('-alpha')
            win.attributes('-alpha', 0.0)

        win.update_idletasks()
        width = win.winfo_reqwidth()
        height = win.winfo_reqheight()

        if hasattr(win, 'geom'):
            geom = win.geom.split("x")
            if len(geom) == 2:
                width=int(geom[0])
                height=int(geom[1])

        outer_frame_width = win.winfo_rootx() - win.winfo_x()
        titlebar_height = win.winfo_rooty() - win.winfo_y()

        actual_width = width + (outer_frame_width * 2)
        actual_height = height + titlebar_height + outer_frame_width

        x = (scr_width // 2) - (actual_width // 2)
        y = (scr_height // 2) - (actual_height // 2)

        # move the window up a bit if requested
        if up < y:
            y = y - up
        else:
            y = 0

        gui.debug("Setting location: " +str(x)+","+str(y) + " - " + str(width)+","+str(height))
        win.geometry("+%d+%d" % (x, y))

        if gui.GET_PLATFORM() != gui.LINUX:
            win.attributes('-alpha', trans)

    # figure out where the cursor is with respect to a widget
    @staticmethod
    def MOUSE_POS_IN_WIDGET(widget, event, findRoot=True):
        # subtract the widget's top left corner from the root window's top corner

        # first we have to get the real master
        master = widget
        while findRoot:
            if isinstance(master, (SubWindow, Tk)):
                break
            master = master.master

        x = event.x_root - master.winfo_rootx()
        y = event.y_root - master.winfo_rooty()
        gui.debug("<<MOUSE_POS_IN_WIDGET>> " + str(widget) + str(x) + "," + str(y))
        return (x, y)

    built = False

    # used to identify widgets in component configurations
    WINDOW = 0
    LABEL = 1
    ENTRY = 2
    FILE_ENTRY = 24
    DIRECTORY_ENTRY = 25
    BUTTON = 3
    CHECKBOX = 4
    SCALE = 5
    RADIOBUTTON = 6
    LISTBOX = 7
    MESSAGE = 8
    SPIN = 9
    SPINBOX = 9
    OPTION = 10
    OPTIONBOX = 10
    TEXTAREA = 11
    LINK = 12
    METER = 13
    IMAGE = 14
    PIECHART = 15
    PROPERTIES = 16
    GRID = 17
    PLOT = 18
    MICROBIT = 19
    WIDGET = 20
    MAP = 21
    TREE = 22
    TOOLBAR = 23

    RB = 60
    CB = 40
    LB = 70

    LABELFRAME = 30
    FRAME = 36
    TABBEDFRAME = 31
    NOTEBOOK = 37
    PANEDFRAME = 32
    SCROLLPANE = 33
    PAGEDWINDOW = 34
    TOGGLEFRAME = 35

    # positioning
    N = N
    NE = NE
    E = E
    SE = SE
    S = S
    SW = SW
    W = W
    NW = NW
    CENTER = CENTER
    LEFT = LEFT
    RIGHT = RIGHT

    # reliefs
    SUNKEN = SUNKEN
    RAISED = RAISED
    GROOVE = GROOVE
    RIDGE = RIDGE
    FLAT = FLAT

    # containers
    C_ROOT = 'rootPage'
    C_LABELFRAME = 'labelFrame'
    C_FRAME = 'frame'
    C_TOGGLEFRAME = 'toggleFrame'

    # 2 containers for pagedWindow
    C_PAGEDWINDOW = 'pagedWindow'
    C_PAGE = 'page'
    # 2 containers for tabbedFrame
    C_TABBEDFRAME = 'tabbedFrame'
    C_TAB = 'tab'
    C_NOTEBOOK = 'notebook'
    C_NOTE = 'note'
    # 2 containers for panedFrame
    C_PANEDFRAME = 'panedFrame'
    C_PANE = 'pane'

    C_SUBWINDOW = 'subWindow'
    C_SCROLLPANE = 'scrollPane'

    # names for each of the widgets defined above
    # used for defining functions
    WIDGETS = {
#        WINDOW: "Window",
        LABEL: "Label",
        ENTRY: "Entry",
        BUTTON: "Button",
        CB: "Cb",
        CHECKBOX: "CheckBox",
        SCALE: "Scale",
        RB: "Rb",
        RADIOBUTTON: "RadioButton",
        LB: "Lb",
        LISTBOX: "ListBox",
        MESSAGE: "Message",
        SPIN: "SpinBox",
        OPTION: "OptionBox",
        TEXTAREA: "TextArea",
        LINK: "Link",
        METER: "Meter",
        IMAGE: "Image",
        MAP: "Map",
        PIECHART: "PieChart",
        PROPERTIES: "Properties",
        GRID: "Grid",
        PLOT: "Plot",
        MICROBIT: "MicroBit",
        LABELFRAME: "LabelFrame",
        FRAME: "Frame",
        TABBEDFRAME: "TabbedFrame",
        NOTEBOOK: "Notebook",
        FILE_ENTRY: "FileEntry",
        DIRECTORY_ENTRY: "DirectoryEntry",
#       TAB:"Tab",
        PANEDFRAME: "PanedFrame",
        WIDGET: "Widget",
#       PANE:"Pane",
#       SCROLLPANE: "ScrollPane",
#       PAGEDWINDOW: "PagedWindow",
#       PAGE:"Page",
#       SUBWINDOW:"SubWindow",
        TOGGLEFRAME: "ToggleFrame"}


    # music stuff
    BASIC_NOTES = {
        "A": 440,
        "B": 493,
        "C": 261,
        "D": 293,
        "E": 329,
        "F": 349,
        "G": 392}
    NOTES = {
        'f8': 5587,
        'c#6': 1108,
        'f4': 349,
        'c7': 2093,
        'd#2': 77,
        'g8': 6271,
        'd4': 293,
        'd7': 2349,
        'd#7': 2489,
        'g#4': 415,
        'e7': 2637,
        'd9': 9397,
        'b8': 7902,
        'a#4': 466,
        'b5': 987,
        'b2': 123,
        'g#9': 13289,
        'g9': 12543,
        'f#2': 92,
        'c4': 261,
        'e1': 41,
        'e6': 1318,
        'a#8': 7458,
        'c5': 523,
        'd6': 1174,
        'd3': 146,
        'g7': 3135,
        'd2': 73,
        'd#3': 155,
        'g#6': 1661,
        'd#4': 311,
        'a3': 219,
        'g2': 97,
        'c#5': 554,
        'd#9': 9956,
        'a8': 7040,
        'a#5': 932,
        'd#5': 622,
        'a1': 54,
        'g#8': 6644,
        'a2': 109,
        'g#5': 830,
        'f3': 174,
        'a6': 1760,
        'e8': 5274,
        'c#9': 8869,
        'f5': 698,
        'b1': 61,
        'c#4': 277,
        'f#9': 11839,
        'e5': 659,
        'f9': 11175,
        'f#5': 739,
        'a#1': 58,
        'f#8': 5919,
        'b7': 3951,
        'c#8': 4434,
        'g1': 48,
        'c#3': 138,
        'f#7': 2959,
        'c6': 1046,
        'c#2': 69,
        'c#7': 2217,
        'c3': 130,
        'e9': 10548,
        'c9': 8372,
        'a#6': 1864,
        'a#7': 3729,
        'g#2': 103,
        'f6': 1396,
        'b3': 246,
        'g#3': 207,
        'b4': 493,
        'a7': 3520,
        'd#6': 1244,
        'd#8': 4978,
        'f2': 87,
        'd5': 587,
        'f7': 2793,
        'f#6': 1479,
        'g6': 1567,
        'e3': 164,
        'f#3': 184,
        'g#1': 51,
        'd8': 4698,
        'f#4': 369,
        'f1': 43,
        'c8': 4186,
        'g4': 391,
        'g3': 195,
        'a4': 440,
        'a#3': 233,
        'd#1': 38,
        'e2': 82,
        'e4': 329,
        'a5': 880,
        'a#2': 116,
        'g5': 783,
        'g#7': 3322,
        'b6': 1975,
        'c2': 65,
        'f#1': 46}

    DURATIONS = {
        "BREVE": 2000,
        "SEMIBREVE": 1000,
        "MINIM": 500,
        "CROTCHET": 250,
        "QUAVER": 125,
        "SEMIQUAVER": 63,
        "DEMISEMIQUAVER": 32,
        "HEMIDEMISEMIQUAVER": 16}


#####################################
# CONSTRUCTOR - creates the GUI
#####################################
    def __init__(self, title=None, geom=None, warn=None, debug=None, handleArgs=True, language=None, startWindow=None, useTtk=False):

        if self.__class__.instantiated:
            raise Exception("You cannot have more than one instance of gui, try using a subWindow.")
        else:
            self.__class__.instantiated = True

        self.alive = True

        # first up, set the logger
        logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(name)s:%(levelname)s %(message)s')

        # check any command line arguments
        self.language = language
        self.startWindow = startWindow
        args = self.__handleArgs() if handleArgs else None

        # warn if we're in an untested mode
        self.__checkMode()
        self.ttkFlag = False
        if useTtk:
            self.useTtk()
        self.ttkStyle = None

        # first out, verify the platform
        self.platform = gui.GET_PLATFORM()

        if warn is not None or debug is not None:
            self.warn("Cannot set logging level in __init__. You should use .setLogLevel()")

        # process any command line arguments
        if handleArgs:
            if args.c: gui.setLogLevel("CRITICAL")
            elif args.e: gui.setLogLevel("ERROR")
            elif args.w: gui.setLogLevel("WARNING")
            elif args.i: gui.setLogLevel("INFO")
            elif args.d: gui.setLogLevel("DEBUG")

            if args.l: self.language = args.l
            if args.f: gui.setLogFile(args.f)
            if args.ttk:
                self.useTtk()
                if args.ttk is not True:
                    self.ttkStyle = args.ttk

        # a stack to hold containers as being built
        # done here, as initArrays is called elsewhere - to reset the gubbins
        self.containerStack = []

        self.translations = {"POPUP":{}, "SOUND":{}, "EXTERNAL":{}}

        # first up, set up all the data stores
        self.__initArrays()

        # dynamically create lots of functions for configuring stuff
        self.__buildConfigFuncs()

        # language parser
        self.config = None

        # set up some default path locations

        # this fails if in interactive mode....
        try:
            gui.exe_file = str(os.path.basename(theMain.__file__))
            gui.exe_path = str(os.path.dirname(theMain.__file__))
        except:
            pass

        gui.lib_file = os.path.abspath(__file__)
        gui.lib_path = os.path.dirname(gui.lib_file)

        # location of appJar
        self.resource_path = os.path.join(gui.lib_path, "resources")
        self.icon_path = os.path.join(self.resource_path, "icons")
        self.sound_path = os.path.join(self.resource_path, "sounds")
        self.appJarIcon = os.path.join(self.icon_path, "favicon.ico")

        # user configurable
        self.userImages = gui.exe_path
        self.userSounds = gui.exe_path

        # create the main window - topLevel
        self.topLevel = Tk()
        self.topLevel.bind('<Configure>', self.__windowEvent)
        # override close button
        self.topLevel.protocol("WM_DELETE_WINDOW", self.stop)
        # temporarily hide it
        self.topLevel.withdraw()
        self.topLevel.locationSet = False

        # used to keep a handle on the last pop-up dialog
        # allows the dialog to be closed remotely
        # mainly for test-automation
        self.topLevel.POP_UP = None

        # create a frame to store all the widgets
        # now a canvas to allow animation...
        self.appWindow = CanvasDnd(self.topLevel)
        self.appWindow.pack(fill=BOTH, expand=True)
        self.topLevel.canvasPane = self.appWindow

        # set the windows title
        if title is None:
            title = "appJar" if gui.exe_file is None else gui.exe_file

        self.setTitle(title)

        # configure the geometry of the window
        self.topLevel.escapeBindId = None  # used to exit fullscreen
        self.topLevel.stopFunction = None  # used to exit fullscreen
        self.setGeom(geom)

        # set the resize status - default to True
        self.setResizable(True)

        # set up fonts
        self.buttonFont = font.Font(family="Helvetica", size=12,)
        self.labelFont = font.Font(family="Helvetica", size=12)
        self.entryFont = font.Font(family="Helvetica", size=12)
        self.messageFont = font.Font(family="Helvetica", size=12)
        self.rbFont = font.Font(family="Helvetica", size=12)
        self.cbFont = font.Font(family="Helvetica", size=12)
        self.tbFont = font.Font(family="Helvetica", size=12)
        self.scaleFont = font.Font(family="Helvetica", size=12)
        self.statusFont = font.Font(family="Helvetica", size=12)
        self.spinFont = font.Font(family="Helvetica", size=12)
        self.optionFont = font.Font(family="Helvetica", size=12)
        self.lbFont = font.Font(family="Helvetica", size=12)
        self.taFont = font.Font(family="Helvetica", size=12)
        self.meterFont = font.Font(family="Helvetica", size=12, weight='bold')
        self.linkFont = font.Font(
            family="Helvetica",
            size=12,
            weight='bold',
            underline=1)
        self.labelFrameFont = font.Font(family="Helvetica", size=12)
        self.frameFont = font.Font(family="Helvetica", size=12)
        self.toggleFrameFont = font.Font(family="Helvetica", size=12)
        self.tabbedFrameFont = font.Font(family="Helvetica", size=12)
        self.panedFrameFont = font.Font(family="Helvetica", size=12)
        self.scrollPaneFont = font.Font(family="Helvetica", size=12)
        self.propertiesFont = font.Font(family="Helvetica", size=12)
        self.gridFont = font.Font(family="Helvetica", size=12)

#        self.fgColour = self.topLevel.cget("foreground")
#        self.buttonFgColour = self.topLevel.cget("foreground")
#        self.labelFgColour = self.topLevel.cget("foreground")

        # create a menu bar - only shows if populated
        # now created in menu functions, as it generated a blank line...
        self.hasMenu = False
        self.hasStatus = False
        self.hasTb = False
        self.tbPinned = True
        self.copyAndPaste = CopyAndPaste(self.topLevel)

        # won't pack, if don't pack it here
        self.tb = Frame(self.appWindow, bd=1, relief=RAISED)
        self.tb.pack(side=TOP, fill=X)
        self.tbMinMade = False

        # create the main container for this GUI
        container = frameBase(self.appWindow)
        # container = Label(self.appWindow) # made as a label, so we can set an
        # image
        if not self.ttkFlag:
            container.config(padx=2, pady=2, background=self.topLevel.cget("bg"))
        container.pack(fill=BOTH, expand=True)
        self.__addContainer("root", self.C_ROOT, container, 0, 1)

        # set up the main container to be able to host an image
        self.__configBg(container)

        if self.platform == self.WINDOWS:
            try:
                self.setIcon(self.appJarIcon)
            except: # file not found
                self.debug("Error setting Windows default icon")

        if self.ttkStyle is not None:
            self.setTtkTheme(self.ttkStyle)

        # for configuting event processing
        self.EVENT_SIZE = 1000
        self.EVENT_SPEED = 100
        self.preloadAnimatedImageId = None
        self.processQueueId = None

        # an array to hold any threaded events....
        self.events = []
        self.pollTime = 250
        self.built = True

    def __handleArgs(self):
        parser = argparse.ArgumentParser(
            description="appJar - the easiest way to create GUIs in python",
            epilog="For more information, go to: http://appJar.info"
        )
        parser.add_argument("-v", "--version", action="version", version=gui.SHOW_VERSION(), help="show version information and exit")
        logGroup = parser.add_mutually_exclusive_group()
        logGroup.add_argument("-c", action="store_const", const=True, help="only log CRITICAL messages")
        logGroup.add_argument("-e", action="store_const", const=True, help="log ERROR messages and above")
        logGroup.add_argument("-w", action="store_const", const=True, help="log WARNING messages and above")
        logGroup.add_argument("-i", action="store_const", const=True, help="log INFO messages and above")
        logGroup.add_argument("-d", action="store_const", const=True, help="log DEBUG messages and above")
        parser.add_argument("-l", metavar="LANGUAGE.ini", help="set a language file to use")
        parser.add_argument("-f", metavar="file.log", help="set a log file to use")
        parser.add_argument("--ttk", metavar="THEME", const=True, nargs="?", help="enable ttk, with an optional theme")
        return parser.parse_args()

    # function to check on mode
    def __checkMode(self):
        # detect if we're in interactive mode
        if hasattr(sys, 'ps1'):
            self.warn("Interactive mode is not fully tested, some features might not work.")
        else:
            if sys.flags.interactive:
                self.warn("Postmortem Interactive mode is not fully tested, some features might not work.")
        # also, check for iPython
        try:
            __IPYTHON__
        except NameError:
            #no iPython - ignore
            pass
        else:
            self.warn("iPython is not fully tested, some features might not work.")

    def __configBg(self, container):
        # set up a background image holder
        # alternative to label option above, as label doesn't update widgets
        # properly

        if not self.ttkFlag:
            self.bgLabel = Label(
                container, anchor=CENTER,
                font=self.labelFont,
                background=self.__getContainerBg())
        else:
            self.bgLabel = ttk.LabelFrame(container)
        self.bgLabel.place(x=0, y=0, relwidth=1, relheight=1)
        container.image = None


#####################################
# library loaders
#####################################

    def useTtk(self):
        global ttk, frameBase, labelBase
        try:
            import ttk
        except:
            try: 
                from tkinter import ttk
            except:
                gui.error("ttk not available")
                return
        self.ttkFlag = True
        frameBase = ttk.Frame
        labelBase = ttk.Label
        gui.debug("Mode switched to ttk")

    # only call this after the main tk has been created
    # otherwise we get two windows!
    def setTtkTheme(self, theme=None):
        self.ttkStyle = ttk.Style()
        if theme is not None:
            try:
                self.ttkStyle.theme_use(theme)
            except:
                self.error("ttk theme: " + str(theme) + " unavailable. Try one of: " + str(self.ttkStyle.theme_names()))
                return

        gui.debug("ttk theme switched to: " + str(self.ttkStyle.theme_use()))

    # internationalisation
    def __loadConfigParser(self):
        global ConfigParser, ParsingError, codecs
        if ConfigParser is None:
            try:
                from configparser import ConfigParser
                from configparser import ParsingError
                import codecs
            except:
                try:
                    from ConfigParser import ConfigParser
                    from ConfigParser import ParsingError
                    import codecs
                except:
                    ConfigParser = ParsingError = codecs = False
                    self.config = None
                    return
            self.config = ConfigParser()
            self.config.optionxform = str

    # textarea
    def __loadHashlib(self):
        global hashlib
        if hashlib is None:
            try:
                import hashlib
            except:
                hashlib = False

    def __loadTooltip(self):
        global ToolTip
        if ToolTip is None:
            try:
                from appJar.lib.tooltip import ToolTip
            except:
                ToolTip = False

    def __loadMatplotlib(self):
        global FigureCanvasTkAgg, Figure

        if FigureCanvasTkAgg is None:
            try:
                from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
                from matplotlib.figure import Figure
            except:
                FigureCanvasTkAgg = Figure = False

    def __loadExternalDnd(self):
        global EXTERNAL_DND
        if EXTERNAL_DND is None:
            try:
                tkdndlib = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib", "tkdnd2.8")
                os.environ['TKDND_LIBRARY'] = tkdndlib
                from appJar.lib.TkDND_wrapper import TkDND as EXTERNAL_DND
                self.dnd = EXTERNAL_DND(self.topLevel)
            except:
                EXTERNAL_DND = False

    def __loadInternalDnd(self):
        global INTERNAL_DND, types
        if INTERNAL_DND is None:
            try:
                import Tkdnd as INTERNAL_DND
                import types as types
            except:
                try:
                    from tkinter import dnd as INTERNAL_DND
                    import types as types
                except:
                    INTERNAL_DND = False
                    types = False

    def __loadURL(self):
        global base64, urlencode, urlopen, urlretrieve, quote_plus, json, Queue
        self.__loadThreading()
        if Queue:
            if urlencode is None:
                try: # python 2
                    from urllib import urlencode, urlopen, urlretrieve, quote_plus
                    import json
                    import base64
                except ImportError: # python 3
                    try:
                        from urllib.parse import urlencode
                        from urllib.parse import quote_plus
                        from urllib.request import urlopen
                        from urllib.request import urlretrieve
                        import json
                        import base64
                    except:
                        base64 = urlencode = urlopen = urlretrieve = quote_plus = json = Queue = False
        else:
            base64 = urlencode = urlopen = urlretrieve = quote_plus = json = Queue = False

    def __loadThreading(self):
        global Thread, Queue
        if Thread is None:
            try:
                from threading import Thread
                import Queue
            except ImportError: # python 3
                try:
                    from threading import Thread
                    import queue as Queue
                except:
                    Thread = Queue = False
                    return

            self.eventQueue = Queue.Queue(maxsize=self.EVENT_SIZE)
            self.__processEventQueue()

    def __loadNanojpeg(self):
        global nanojpeg, array
        if nanojpeg is None:
            try:
                from appJar.lib import nanojpeg
                import array
            except:
                nanojpeg = False
                array = False

    def __loadWinsound(self):
        # only try to import winsound if we're on windows
        global winsound
        if winsound is None:
            if platform() in ["win32", "Windows"]:
                import winsound
            else:
                winsound = False

    def __importPngimagetk(self):
        global PngImageTk
        if PngImageTk is None:
            try:
                from appJar.lib.tkinter_png import PngImageTk
            except:
                PngImageTk = False

    def __importAjtree(self):
        global parseString, TreeItem, TreeNode
        global ajTreeNode, ajTreeData

        if TreeNode is None:
            try:
                from idlelib.TreeWidget import TreeItem, TreeNode
            except:
                try:
                    from idlelib.tree import TreeItem, TreeNode
                except:
                    gui.warning("no trees")
                    TreeItem = TreeNode = parseString = False
                    ajTreeNode = ajTreeData = False

            if TreeNode is not False:
                try:
                    from xml.dom.minidom import parseString
                except:
                    gui.warning("no parse string")
                    TreeItem = TreeNode = parseString = False
                    ajTreeNode = ajTreeData = False
                    return

                #####################################
                # Tree Widget Class
                # https://www.safaribooksonline.com/library/view/python-cookbook-2nd/0596007973/ch11s11.html
                # idlelib -> TreeWidget.py
                # modify minidom - https://wiki.python.org/moin/MiniDom
                #####################################
                class ajTreeNode(TreeNode):

                    def __init__(self, canvas, parent, item):

                        TreeNode.__init__(self, canvas, parent, item)

                        self.bgColour = None
                        self.fgColour = None
                        self.bgHColour = None
                        self.fgHColour = None
                        # called (if set) when a leaf is edited
                        self.editEvent = None

                        if self.parent:
                            self.bgColour = self.parent.bgColour
                            self.fgColour = self.parent.fgColour
                            self.bgHColour = self.parent.bgHColour
                            self.fgHColour = self.parent.fgHColour
                            self.editEvent = self.parent.editEvent

                    def registerEditEvent(self, func):
                        self.editEvent = func
                        for c in self.children:
                            c.registerEditEvent(func)

                    def setBgColour(self, colour):
                        self.canvas.config(background=colour)
                        self.bgColour = colour
                        self.__doUpdateColour()

                    def setFgColour(self, colour):
                        self.fgColour = colour
                        self.__doUpdateColour()

                    def setBgHColour(self, colour):
                        self.bgHColour = colour
                        self.__doUpdateColour()

                    def setFgHColour(self, colour):
                        self.fgHColour = colour
                        self.__doUpdateColour()

                    def setAllColours(self, bg, fg, bgH, fgH):
                        self.canvas.config(background=bg)
                        self.bgColour = bg
                        self.fgColour = fg
                        self.bgHColour = bgH
                        self.fgHColour = fgH
                        self.__doUpdateColour()

                    def __doUpdateColour(self):
                        self.__updateColours(
                            self.bgColour,
                            self.bgHColour,
                            self.fgColour,
                            self.fgHColour)
                        self.update()

                    def __updateColours(self, bgCol, bgHCol, fgCol, fgHCol):
                        self.bgColour = bgCol
                        self.fgColour = fgCol
                        self.bgHColour = bgHCol
                        self.fgHColour = fgHCol
                        for c in self.children:
                            c.__updateColours(bgCol, bgHCol, fgCol, fgHCol)

                    # override parent function, so that we can change the label's background
                    # colour
                    def drawtext(self):
                        if PYTHON2:
                            TreeNode.drawtext(self)
                        else:
                            super(__class__, self).drawtext()

                        self.colourLabels()

                    # override parent function, so that we can generate an event on finish
                    # editing
                    def edit_finish(self, event=None):
                        if PYTHON2:
                            TreeNode.edit_finish(self, event)
                        else:
                            super(__class__, self).edit_finish(event)
                        if self.editEvent is not None:
                            self.editEvent()

                    def colourLabels(self):
                        try:
                            if not self.selected:
                                self.label.config(background=self.bgColour, fg=self.fgColour)
                            else:
                                self.label.config(background=self.bgHColour, fg=self.fgHColour)
                        except:
                            pass

                    def getSelectedText(self):
                        item = self.getSelected()
                        if item is not None:
                            return item.GetText()
                        else:
                            return None

                    def getSelected(self):
                        if self.selected:
                            return self.item
                        else:
                            for c in self.children:
                                val = c.getSelected()
                                if val is not None:
                                    return val
                            return None

                # implementation of container for XML data
                # functions implemented as specified in skeleton
                class ajTreeData(TreeItem):

                    def __init__(self, node):
                        self.node = node
                        self.dblClickFunc = None
                        self.canEdit = True

                # REQUIRED FUNCTIONS

                    # called whenever the tree expands
                    def GetText(self):
                        node = self.node
                        if node.nodeType == node.ELEMENT_NODE:
                            return node.nodeName
                        elif node.nodeType == node.TEXT_NODE:
                            return node.nodeValue

                    def IsEditable(self):
                        return self.canEdit and not self.node.hasChildNodes()

                    def SetText(self, text):
                        self.node.replaceWholeText(text)

                    def IsExpandable(self):
                        return self.node.hasChildNodes()

                    def GetIconName(self):
                        if not self.IsExpandable():
                            return "python"  # change to file icon

                    def GetSubList(self):
                        children = self.node.childNodes
                        prelist = [ajTreeData(node) for node in children]
                        itemList = [item for item in prelist if item.GetText().strip()]
                        for item in itemList:
                            item.registerDblClick(self.dblClickFunc)
                            item.canEdit = self.canEdit
                        return itemList

                    def OnDoubleClick(self):
                        if self.IsEditable():
                            # TO DO: start editing this node...
                            pass
                        if self.dblClickFunc is not None:
                            self.dblClickFunc()

                #  EXTRA FUNCTIONS

                    # TODO: can only set before calling go()
                    def setCanEdit(self, value=True):
                        self.canEdit = value

                    # TODO: can only set before calling go()
                    def registerDblClick(self, func):
                        self.dblClickFunc = func

                    # not used - for DEBUG
                    def getSelected(self, spaces=1):
                        if spaces == 1:
                            gui.debug(str(self.node.tagName))
                        for c in self.node.childNodes:
                            if c.__class__.__name__ == "Element":
                                gui.debug(str(" " * spaces) + " >> "+ str(c.tagName))
                                node = ajTreeData(c)
                                node.getSelected(spaces + 2)
                            elif c.__class__.__name__ == "Text":
                                val = c.data.strip()
                                if len(val) > 0:
                                    gui.debug(str(" " * spaces) + " >>>> "+ str(val))


#####################################
# FUNCTIONS FOR UNIVERSAL DND
#####################################

    def __registerExternalDragSource(self, title, widget, function=None):
        self.__loadExternalDnd()

        if EXTERNAL_DND is not False:
            try:
                self.dnd.bindsource(widget, self.__startExternalDrag, 'text/uri-list')
                self.dnd.bindsource(widget, self.__startExternalDrag, 'text/plain')
                widget.dndFunction = function
                widget.dragData = None
            except:
                # dnd not working on this platform
                raise Exception("Failed to register external Drag'n Drop for: " + str(title))
        else:
            raise Exception("External Drag'n Drop not available on this platform")

    def __registerExternalDropTarget(self, title, widget, function=None, replace=True):
        self.__loadExternalDnd()

        if EXTERNAL_DND is not False:
            try:
                self.dnd.bindtarget(widget, self.__receiveExternalDrop, 'text/uri-list')
                self.dnd.bindtarget(widget, self.__receiveExternalDrop, 'text/plain')
                widget.dndFunction = function
                widget.dropData = None
                widget.dropReplace = replace
            except:
                # dnd not working on this platform
                raise Exception("Failed to register external Drag'n Drop for: " + str(title))
        else:
            raise Exception("External Drag'n Drop not available on this platform")

    def __registerInternalDragSource(self, kind, title, widget, function=None):
        self.__loadInternalDnd()

        name = None
        if kind == self.LABEL:
            name = self.getLabel(title)

        if INTERNAL_DND is not False:
            try:
                widget.bind('<ButtonPress>', lambda e: self.__startInternalDrag(e, title, name, widget))
                widget.dnd_canvas = self.__getCanvas().canvasPane
                self.debug("DND drag source created: " + str(widget) + " on canvas " + str(widget.dnd_canvas))
            except:
                raise Exception("Failed to register internal Drag'n Drop for: " + str(title))
        else:
            raise Exception("Internal Drag'n Drop not available on this platform")

    def __registerInternalDropTarget(self, widget, function):
        self.debug("<<WIDGET.__registerInternalDropTarget>> " + str(widget))
        self.__loadInternalDnd()
        if not INTERNAL_DND:
            raise Exception("Internal Drag'n Drop not available on this platform")

        # called by DND class, when looking for a DND target
        def dnd_accept(self, source, event):
            gui.debug("<<WIDGET.dnd_accept>> " + str(widget) + " - " + str(self.dnd_canvas))
            return self

        # This is called when the mouse pointer goes from outside the
        # Target Widget to inside the Target Widget.
        def dnd_enter(self, source, event):
            gui.debug("<<WIDGET.dnd_enter>> " + str(widget))
            XY = gui.MOUSE_POS_IN_WIDGET(self,event)
            source.appear(self, XY)

        # This is called when the mouse pointer goes from inside the
        # Target Widget to outside the Target Widget.
        def dnd_leave(self, source, event):
            gui.debug("<<WIDGET.dnd_leave>> " + str(widget))
            # hide the dragged object
            source.vanish()

        #This is called if the DraggableWidget is being dropped on us.
        def dnd_commit(self, source, event):
            source.vanish(all=True)
            gui.debug("<<WIDGET.dnd_commit>> " + str(widget) + " Object received=" + str(source))

        #This is called when the mouse pointer moves within the TargetWidget.
        def dnd_motion(self, source, event):
            gui.debug("<<WIDGET.dnd_motion>> " + str(widget))
            XY = gui.MOUSE_POS_IN_WIDGET(self,event)
            # move the dragged object
            source.move(self, XY)

        def keepWidget(self, title, name):
            if self.drop_function is not None:
                return self.drop_function(title, name)
            else:
                self.config(text=name)
                return True

        widget.dnd_accept = types.MethodType(dnd_accept, widget)
        widget.dnd_enter = types.MethodType(dnd_enter, widget)
        widget.dnd_leave = types.MethodType(dnd_leave, widget)
        widget.dnd_commit = types.MethodType(dnd_commit, widget)
        widget.dnd_motion = types.MethodType(dnd_motion, widget)
        widget.keepWidget = types.MethodType(keepWidget, widget)
        # save the underlying canvas
        widget.dnd_canvas = self.__getCanvas().canvasPane
        widget.drop_function = function

        self.debug("DND target created: " + str(widget) + " on canvas " + str(widget.dnd_canvas))

    # called when the user initiates an internal drag event
    def __startInternalDrag(self, event, title, name, widget):
        self.debug("Internal drag started for " + title + " on " + str(widget))

        x, y = gui.MOUSE_POS_IN_WIDGET(widget, event, False)
        width = x / widget.winfo_width()
        height = y / widget.winfo_height()

        thingToDrag = DraggableWidget(widget.dnd_canvas, title, name, (width, height))
        INTERNAL_DND.dnd_start(thingToDrag, event)

    # function to receive DnD events
    def __startExternalDrag(self, event):
        widgType = event.widget.__class__.__name__
        self.warn("Unable to initiate drag events: " + str(widgType))

    def __receiveExternalDrop(self, event):
        widgType = event.widget.__class__.__name__
        event.widget.dropData = event.data
        if not hasattr(event.widget, 'dndFunction'):
            self.warn("Error - external drop target not correctly configured: " + str(widgType))
        elif event.widget.dndFunction is not None:
            event.widget.dndFunction(event.data)
        else:
            if widgType in ["Entry", "AutoCompleteEntry"]:
                if event.widget.dropReplace:
                    event.widget.delete(0, END)
                event.widget.insert(END, event.data)
                event.widget.focus_set()
                event.widget.icursor(END)
            elif widgType in ["TextArea", "AjText", "ScrolledText", "AjScrolledText"]:
                if event.widget.dropReplace:
                    event.widget.delete(1.0, END)
                event.widget.insert(END, event.data)
                event.widget.focus_set()
                event.widget.see(END)
            elif widgType in ["Label"]:
                for k, v in self.n_images.items():
                    if v == event.widget:
                        try:
                            imgTemp = self.userImages
                            image = self.__getImage(event.data, False)
                            self.__populateImage(k, image)
                            self.userImages = imgTemp
                        except:
                            self.errorBox("Error loading image", "Unable to load image: " + str(event.data))
                        return
                for k, v in self.n_labels.items():
                    if v == event.widget:
                        self.setLabel(k, event.data)
                        return
            elif widgType in ["Listbox"]:
                for k, v in self.n_lbs.items():
                    if v == event.widget:
                        self.addListItem(k, event.data)
                        return
            elif widgType in ["Message"]:
                for k, v in self.n_messages.items():
                    if v == event.widget:
                        self.setMessage(k, event.data)
                        return
            else:
                self.warn("Unable to receive drop events: " + str(widgType))

#####################################
# set the arrays we use to store everything
#####################################
    def __initArrays(self):
        # set up a row counter - used to auto add rows
        # breaks once user sets own row

        # set up a minimum label width for label combos
        self.labWidth = 1

        # validate function callbacks - used by numeric texts
        # created first time a widget is used
        self.validateNumeric = None
        self.validateSpinBox = None

        # set up flash variable
        self.doFlash = False

        # used to hide/show title bar
        self.hasTitleBar = True
        # records if we're in fullscreen - stops hideTitle from breaking
        self.isFullscreen = False

        # splash screen?
        self.splashConfig = None

        # store the path to any icon
        self.winIcon = None

        # collections of widgets, widget name is key
        self.n_frames = []  # un-named, so no direct access
        self.n_labels = {}
        self.n_buttons = {}
        self.n_entries = {}
        self.n_messages = {}
        self.n_scales = {}
        self.n_cbs = {}
        self.n_rbs = {}
        self.n_lbs = {}
        self.n_tbButts = {}
        self.n_spins = {}
        self.n_props = {}
        self.n_plots = {}
        self.n_microbits = {}
        self.n_options = {}
        self.n_frameLabs = {}
        self.n_textAreas = {}
        self.n_links = {}
        self.n_meters = {}
        self.n_subWindows = {}
        self.n_labelFrames = {}
        self.n_ajFrame = {}
        self.n_tabbedFrames = {}
        self.n_notebooks = {}
        self.n_panedFrames = {}
        self.n_panes = {}
        self.n_pagedWindows = {}
        self.n_toggleFrames = {}
        self.n_scrollPanes = {}
        self.n_trees = {}
        self.n_flashLabs = []
        self.n_pieCharts = {}
        self.n_separators = []
        self.n_widgets = {}
        self.n_dps = {}

        # completed containers - in case we want to open them again
        self.n_usedContainers = {}

        # variables associated with widgets
        self.n_entryVars = {}
        self.n_optionVars = {}
        self.n_optionTicks = {} # to store tick option items
        self.n_boxVars = {}
        self.n_rbVars = {}
        self.n_rbVals = {}
        self.n_images = {}        # image label widgets
        self.n_maps = {}        # GoogleMap widgets
        self.n_imageCache = {}    # image file objects
        self.n_imageAnimationIds = {} # stores after ids

        # for simple grids
        self.n_grids = {}

        # menu stuff
        self.n_menus = {}
        self.n_menuVars = {}
        self.n_accelerators = []

        # the dnd manager
        self.dnd = None

    def translate(self, key, default=None):
        return self.__translate(key, "EXTERNAL", default)

    def __translateSound(self, key):
        return self.__translate(key, "SOUND", key)

    def __translatePopup(self, key, value):
        pop = self.__translate(key, "POPUP")
        if pop is None:
            return (key, value)
        else:
            return (pop[0], pop[1])

    def __translate(self, key, section, default=None):
        if key in self.translations[section]:
            return self.translations[section][key]
        else:
            return default

    def setLanguage(self, language):
        self.changeLanguage(language)

    # function to update languages
    def changeLanguage(self, language):
        self.__loadConfigParser()
        if not ConfigParser:
            self.error("Internationalisation not supported")
            return

        language = language.upper() + ".ini"
        if not PYTHON2:
            try:
                with codecs.open(language, "r", "utf8") as langFile:
                    self.config.read_file(langFile)
            except FileNotFoundError:
                self.error("Invalid language, file not found: " + language)
                return
        else:
            try:
                try:
                    with codecs.open(language, "r", "utf8") as langFile:
                        self.config.read_file(langFile)
                except AttributeError:
                    with codecs.open(language, "r", "utf8") as langFile:
                        self.config.readfp(langFile)
            except IOError:
                self.error("Invalid language, file not found: " + language)
                return
            except ParsingError:
                self.error("Translation failed - language file contains errors, ensure there is no whitespace at the beginning of any lines.")
                return

        self.debug("Switching to: " + language)
        self.translations = {"POPUP":{}, "SOUND":{}, "EXTERNAL":{}}
        # loop through each section, get the relative set of widgets
        # change the text
        for section in self.config.sections():
            getWidgets = True
            section = section.upper()
            self.debug("\tSection: " + section)

            # convert the section title to its code
            if section == "CONFIG":
                # skip the config section (for now)
                self.debug("\tSkipping CONFIG")
                continue
            elif section == "TITLE":
                kind = self.C_SUBWINDOW
            elif section.startswith("TOOLTIP-"):
                kind = "TOOLTIP"
                getWidgets = False
            elif section in ["SOUND", "EXTERNAL", "POPUP"]:
                for (key, val) in self.config.items(section):
                    if section == "POPUP": val = val.strip().split("\n")
                    self.translations[section][key] = val
                    self.debug("\t\t" + str(key) + ": " + str(val))
                continue
            elif section == "MENUBAR":
                for (key, val) in self.config.items(section):
                    key = key.strip().split("-")
                    self.debug("\t\t" + str(key) + ": " + str(val))
                    if len(key) == 1:
                        try:
                            self.renameMenu(key[0], val)
                        except:
                            self.warn("Invalid key")
                    elif len(key) == 2:
                        try:
                            self.renameMenuItem(key[0], key[1], val)
                        except:
                            self.warn("Invalid key")
                continue
            else:
                try:
                    kind = vars(gui)[section]
                except KeyError:
                    self.warn("Invalid config section: " + section)
                    continue

            # if necessary, use the code to get the widget list
            if getWidgets:
                widgets = self.__getItems(kind)

            if kind in [self.SCALE]:
                self.warn("No text is displayed in " + section + ". Maybe it has a Label?")
                continue
            elif kind in [self.TEXTAREA, self.METER, self.PIECHART, self.TREE]:
                self.warn("No text is displayed in " + section)
                continue
            elif kind in [self.C_SUBWINDOW]:
                for (key, val) in self.config.items(section):
                    self.debug("\t\t" + key + ": " +  val)

                    if key.lower() == "appjar":
                        self.setTitle(val)
                    elif key.lower() == "splash":
                        if self.splashConfig is not None:
                            self.debug("\t\t Updated SPLASH to: " + str(val))
                            self.splashConfig['text'] = val
                        else:
                            self.debug("\t\t No SPLASH to update")
                    elif key.lower() == "statusbar":
                        self.debug("\tSetting STATUSBAR: " + str(val))
                        self.setStatusbarHeader(val)
                    else:
                        try:
                            widgets[key].title(val)
                        except KeyError:
                            self.warn("Invalid SUBWINDOW: " + str(key))

            elif kind in [self.LISTBOX]:
                for k in widgets.keys():
                    lb = widgets[k]

                    # convert data to a list
                    if self.config.has_option(section, k):
                        data = self.config.get(section, k)
                    else:
                        data = lb.DEFAULT_TEXT
                    data = data.strip().split("\n")

                    # tidy up the list
                    data = [item.strip() for item in data if len(item.strip()) > 0]
                    self.updateListBox(k, data)

            elif kind in [self.SPIN, self.SPINBOX]:
                for k in widgets.keys():
                    sb = widgets[k]

                    # convert data to a list
                    if self.config.has_option(section, k):
                        data = self.config.get(section, k)
                    else:
                        data = sb.DEFAULT_TEXT
                    data = data.strip().split("\n")

                    # tidy up the list
                    data = [item.strip() for item in data if len(item.strip()) > 0]
                    self.changeSpinBox(k, data)

            elif kind in [self.OPTION, self.OPTIONBOX]:
                for k in widgets.keys():
                    ob = widgets[k]

                    # convert data to a list
                    if self.config.has_option(section, k):
                        data = self.config.get(section, k)
                    else:
                        data = ob.DEFAULT_TEXT
                    data = data.strip().split("\n")

                    # tidy up the list
                    data = [item.strip() for item in data if len(item.strip()) > 0]
                    self.changeOptionBox(k, data)

            elif kind in [self.RADIOBUTTON]:
                for (key, val) in self.config.items(section):
                    self.debug("\t\t" + key + ": " +  val)
                    keys = key.split("-")
                    if len(keys) != 2:
                        self.warn("Invalid RADIOBUTTON key:" + key)
                    else:
                        try:
                            rbs = self.n_rbs[keys[0]]
                        except KeyError:
                            self.warn("Invalid RADIOBUTTON key: " + keys[0])
                            continue
                        for rb in rbs:
                            if rb.DEFAULT_TEXT == keys[1]:
                                rb["text"] = val
                                break

            elif kind in [self.TABBEDFRAME]:
                for (key, val) in self.config.items(section):
                    self.debug("\t\t" + key + ": " +  val)
                    keys = key.split("-")
                    if len(keys) != 2:
                        self.warn("Invalid TABBEDFRAME key: " + key)
                    else:
                        try:
                            self.setTabText(keys[0], keys[1], val)
                        except ItemLookupError:
                            self.warn("Invalid TABBEDFRAME: " + str(keys[0]) + " with TAB: " + str(keys[1]))

            elif kind in [self.PROPERTIES]:
                for (key, val) in self.config.items(section):
                    self.debug("\t\t" + key + ": " +  val)
                    keys = key.split("-")
                    if len(keys) != 2:
                        self.warn("Invalid PROPERTIES key: " + key)
                    else:
                        try:
                            self.setPropertyText(keys[0], keys[1], val)
                        except ItemLookupError:
                            self.warn("Invalid PROPERTIES: " + keys[0])
                        except KeyError:
                            self.warn("Invalid PROPERTY: " + keys[1])

            elif kind == self.GRID:
                for (key, val) in self.config.items(section):
                    self.debug("\t\t" + key + ": " +  val)
                    keys = key.split("-")
                    if len(keys) != 2:
                        self.warn("Invalid GRID key: " + key)
                    else:
                        if keys[1] not in ["actionHeading", "actionButton", "addButton"]:
                            self.warn("Invalid GRID label: " + str(keys[1]) + " for GRID: " + str(keys[0]))
                        else:
                            try:
                                self.confGrid(keys[0], keys[1], val)
                            except ItemLookupError:
                                self.warn("Invalid GRID: " + str(keys[0]))

            elif kind == self.PAGEDWINDOW:
                for (key, val) in self.config.items(section):
                    self.debug("\t\t" + key + ": " +  val)
                    keys = key.split("-")
                    if len(keys) != 2:
                        self.warn("Invalid PAGEDWINDOW key: " + key)
                    else:
                        if keys[1] not in ["prevButton", "nextButton", "title"]:
                            self.warn("Invalid PAGEDWINDOW label: " + str(keys[1]) + " for PAGEDWINDOW: " + str(keys[0]))
                        else:
                            try:
                                widgets[keys[0]].config(**{keys[1]:val})
                            except KeyError:
                                self.warn("Invalid PAGEDWINDOW: " + str(keys[0]))

            elif kind == self.ENTRY:
                for k in widgets.keys():
                    ent = widgets[k]

                    if self.config.has_option(section, k):
                        data = self.config.get(section, k)
                    else:
                        data = ent.DEFAULT_TEXT

                    self.debug("\t\t" + k + ": " +  str(data))
                    self.updateEntryDefault(k, data)

            elif kind in [self.IMAGE]:
                for k in widgets.keys():
                    if self.config.has_option(section, k):
                        data = str(self.config.get(section, k))

                        try:
                            self.setImage(k, data)
                            self.debug("\t\t" + k + ": " +  data)
                        except:
                            self.error("Failed to update image: " + str(k) + " to: " + str(data))
                    else:
                        self.debug("No translation for: " + str(k))

            elif kind in [self.LABEL, self.BUTTON, self.CHECKBOX, self.MESSAGE,
                            self.LINK, self.LABELFRAME, self.TOGGLEFRAME]:
                for k in widgets.keys():
                    widg = widgets[k]

                    # skip validation labels - we don't need to translate them
                    try:
                        if kind == self.LABEL and widg.isValidation:
                            self.debug("\t\t" + k + ": skipping, validation label")
                            continue
                    except:
                        pass

                    if self.config.has_option(section, k):
                        data = str(self.config.get(section, k))
                    else:
                        data = widg.DEFAULT_TEXT

                    self.debug("\t\t" + k + ": " +  data)
                    widg.config(text=data)

            elif kind == self.TOOLBAR:
                for k in widgets.keys():
                    but = widgets[k]
                    if but.image is None:
                        if self.config.has_option(section, k):
                            data = str(self.config.get(section, k))
                        else:
                            data = but.DEFAULT_TEXT

                        self.debug("\t\t" + k + ": " +  data)
                        but.config(text = data)

            elif kind == "TOOLTIP":
                try:
                    kind = self.WIDGETS[vars(gui)[section.split("-")[1]]]
                    func = getattr(self, "set"+kind+"Tooltip")
                except KeyError:
                    self.warn("Invalid config section: TOOLTIP-" + section)
                    return
                self.debug("Parsing TOOLTIPs for: " + str(kind))

                for (key, val) in self.config.items(section):
                    try:
                        func(key, val)
                    except ItemLookupError:
                        self.warn("Invalid TOOLTIP for: " + kind + ", with key: " + key)
                        continue
            else:
                self.warn("Unsupported widget: " + section)
                continue

    # function to turn on the splash screen
    def showSplash(self, text="appJar", fill="#FF0000", stripe="#000000", fg="#FFFFFF", font=44):
        self.splashConfig= {'text':text, 'fill':fill, 'stripe':stripe, 'fg':fg, 'font':font}

    #########################
    ### Stuff for logging
    #########################
                
    @staticmethod
    def setLogFile(fileName):
        # Remove all handlers associated with the root logger object.
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(level=logging.INFO, filename=fileName, format='%(asctime)s %(name)s:%(levelname)s: %(message)s')
        gui.info("Switched to logFile: " + str(fileName))

    # function to turn off warning messages
    def disableWarnings(self):
        self.warn("Using old debug setter, should use gui.setLogLevel()")
        gui.setLogLevel("ERROR")

    def enableWarnings(self):
        self.warn("Using old debug setter, should use gui.setLogLevel()")
        gui.setLogLevel("WARNING")

    # function to turn on debug messages
    def enableDebug(self):
        self.warn("Using old debug setter, should use gui.setLogLevel()")
        gui.setLogLevel("DEBUG")

    def disableDebug(self):
        self.warn("Using old debug setter, should use gui.setLogLevel()")
        gui.setLogLevel("INFO")

    @staticmethod
    def setLogLevel(level):
        logging.getLogger("appJar").setLevel(getattr(logging, level.upper()))
        gui.info("Log level changed to: " + str(level))

    @staticmethod
    def exception(message): gui.logMessage(message, "EXCEPTION")
    @staticmethod
    def critical(message): gui.logMessage(message, "CRITICAL")
    @staticmethod
    def error(message): gui.logMessage(message, "ERROR")
    @staticmethod
    def warn(message): gui.logMessage(message, "WARNING")
    @staticmethod
    def debug(message): gui.logMessage(message, "DEBUG")
    @staticmethod
    def info(message): gui.logMessage(message, "INFO")

    @staticmethod
    def logMessage(msg, level):
        frames = inspect.stack()
        # try to ensure we only log extras if we're called from above functions
        if frames[1][3] in ("exception", "critical", "error", "warn", "debug", "info"):

            callFrame = ""
            try:
                progName = gui.exe_file
                for s in frames:
                    if progName in s[1]:
                        callFrame = s
                        break
            except: pass

            if callFrame != "":
                callFrame = "Line " + str(callFrame[2])

            # user generated call
            if "appjar.py" not in frames[2][1] or frames[2][3] == "handlerFunction":
                if callFrame != "":
                    msg = "[" + callFrame + "]: "+str(msg)

            # appJar logging
            else:
                if callFrame != "":
                    msg = "["+callFrame + "->" + str(frames[2][2]) +"/"+str(frames[2][3])+"]: "+str(msg)
                else:
                    msg = "["+str(frames[2][2]) +"/"+str(frames[2][3])+"]: "+str(msg)

        logger = logging.getLogger("appJar")
        level = level.upper()

        if level == "EXCEPTION": logger.exception(msg)
        elif level == "CRITICAL": logger.critical(msg)
        elif level == "ERROR": logger.error(msg)
        elif level == "WARNING": logger.warning(msg)
        elif level == "INFO": logger.info(msg)
        elif level == "DEBUG": logger.debug(msg)

#####################################
# Event Loop - must always be called at end
#####################################
    def __enter__(self):
        self.debug("ContextManager: initialised")
        return self

    def __exit__(self, eType, eValue, eTrace):
        if eType is not None:
            self.error("ContextManager: failed")
            return False
        else:
            self.debug("ContextManager: starting")
            self.go(startWindow=self.startWindow)
            return True

    def go(self, language=None, startWindow=None):
        """ Most important function! Start the GUI """

        # check if we have a command line language
        if self.language is not None:
            language = self.language

        # if language is populated, we are in internationalisation mode
        # call the changeLanguage function - to re-badge all the widgets
        if language is not None:
            self.changeLanguage(language)

        if self.splashConfig is not None:
            self.debug("SPLASH:" + str(self.splashConfig))
            splash = SplashScreen(
                            self.topLevel,
                            self.splashConfig['text'],
                            self.splashConfig['fill'],
                            self.splashConfig['stripe'],
                            self.splashConfig['fg'],
                            self.splashConfig['font']
                            )
            self.topLevel.withdraw()
            self.__bringToFront(splash)

        # check the containers have all been stopped
        if len(self.containerStack) > 1:
            self.warn("You didn't stop all containers")
            for i in range(len(self.containerStack) - 1, 0, -1):
                kind = self.containerStack[i]['type']
                if kind not in [self.C_PANE]:
                    self.warn("STOP: " + kind)

        if len(self.n_trees) > 0:
            for k in self.n_trees:
                self.n_trees[k].update()
                self.n_trees[k].expand()

        # create appJar menu, if no menuBar created
        if not self.hasMenu:
            self.addAppJarMenu()

        if self.platform == self.WINDOWS:
            self.menuBar.add_cascade(menu=self.n_menus["WIN_SYS"])
        self.topLevel.config(menu=self.menuBar)

        # pack it all in & make sure it's drawn
        self.appWindow.pack(fill=BOTH)
        self.topLevel.update_idletasks()

        # check geom is set and set a minimum size, also positions the window
        # if necessary
        self.__dimensionWindow()

        if self.splashConfig is not None:
            time.sleep(3)
            splash.destroy()

        # bring to front
        if startWindow is None:
            self.__bringToFront()
            self.topLevel.deiconify()
        else:
            self.hide()
            sw = self.__verifyItem(self.n_subWindows, startWindow)
            if sw.blocking:
                raise Exception("Unable to start appjar with a blocking subWindow")

            self.showSubWindow(startWindow)

        # required to make the gui reopen after minimising
        if self.GET_PLATFORM() == self.MAC:
            self.topLevel.createcommand(
                'tk::mac::ReopenApplication',
                self.topLevel.deiconify)

        # start the call back & flash loops
        self.__poll()
        self.__flash()

        # start the main loop
        try:
            self.topLevel.mainloop()
        except(KeyboardInterrupt, SystemExit) as e:
            self.debug("appJar stopped through ^c or exit()")
            self.stop()
        except Exception as e:
            self.exception(e)
            self.stop()

    def setStopFunction(self, function):
        """ Set a function to call when the GUI is quit. Must return True or False """
        tl = self.__getTopLevel()
        tl.stopFunction = function
        # link to exit item in topMenu
        # only if in root
        if self.containerStack[-1]['type'] != self.C_SUBWINDOW:
            tl.createcommand('exit', self.stop)

    def saveSettings(self):
        props = {}
        # get geometry: widthxheight+x+y
        props["geom"] = self.topLevel.geometry()
        props["fullscreen"] = self.topLevel.attributes('-fullscreen')

        # get toolbar setting
        props["tbPinned"] = self.tbPinned

        # get container settings
        props["togs"] = {}
        for k, v in self.n_toggleFrames.items():
            props["togs"][k] = v.isShowing()

        props["tabs"] = {}
        for k, v in self.n_tabbedFrames.items():
            props["tabs"][k] = v.getSelectedTab()

        props["pages"] = {}
        for k, v in self.n_pagedWindows.items():
            props["pages"][k] = v.getPageNumber()

        # pane positions?
        # sub windows geom & visibility
        # scrollpane x & y positions

        return props

    def stop(self, event=None):
        """ Closes the GUI. If a stop function is set, will only close the GUI if True """
        theFunc = self.__getTopLevel().stopFunction
        if theFunc is None or theFunc():
            # stop the after loops
            self.alive = False
            self.topLevel.after_cancel(self.pollId)
            self.topLevel.after_cancel(self.flashId)
            if self.preloadAnimatedImageId:
                self.topLevel.after_cancel(self.preloadAnimatedImageId)
            if self.processQueueId:
                self.topLevel.after_cancel(self.processQueueId)

            # stop any animations
            for key in self.n_imageAnimationIds:
                self.topLevel.after_cancel(self.n_imageAnimationIds[key])

            # stop any maps
            for key in self.n_maps:
                self.n_maps[key].stopUpdates()

            # stop any sounds, ignore error when not on Windows
            try:
                self.stopSound()
            except:
                pass

            self.topLevel.quit()
            self.topLevel.destroy()
            self.__class__.instantiated = False

#####################################
# Functions for configuring polling events
#####################################
    # events will fire in order of being added, after sleeping for time
    def setPollTime(self, time):
        """ Set a frequency for executing queued functions """
        self.pollTime = time

    # register events to be called by the sleep timer
    def registerEvent(self, func):
        """ Queue a function, to be executed every poll time """
        self.events.append(func)

    # wrapper for tkinter event callers
    def after(self, delay_ms, callback=None, *args):
        return self.topLevel.after(delay_ms, callback, *args)

    def afterIdle(self, callback, *args):
        return self.after_idle(callback, *args)

    def after_idle(self, callback, *args):
        return self.topLevel.after_idle(callback, *args)

    def afterCancel(self, afterId):
        return self.after_cancel(afterId)

    def after_cancel(self, afterId):
        return self.topLevel.after_cancel(afterId)

    def queueFunction(self, func, *args, **kwargs):
        """ adds the specified function & arguments to the event queue
        Functions in the event queue are actioned by the gui's main thread

        :param func: the function to call
        :param *args: any number of ordered arguments
        :param **kwargs: any number of named arguments
        :raises Full: if unable to add the function to the queue
        """
        self.__loadThreading()
        if Queue is False:
            gui.warn("Unable to queueFunction - threading not possible.")
        else:
            self.eventQueue.put((5, func, args, kwargs), block=False)

    def queuePriorityFunction(self, func, *args, **kwargs):
        self.__loadThreading()
        if Queue is False:
            gui.warn("Unable to queueFunction - threading not possible.")
        else:
            self.eventQueue.put((1, func, args, kwargs), block=False)

    def __processEventQueue(self):
        if not self.alive: return
        if not self.eventQueue.empty():
            priority, func, args, kwargs = self.eventQueue.get()
            gui.debug("FUNCTION: " + str(func) + "(" + str(args) + ")")
            func(*args, **kwargs)

        self.processQueueId = self.after(self.EVENT_SPEED, self.__processEventQueue)

    def thread(self, func, *args):
        """ will run the supplied function in a separate thread

        param func: the function to run
        """
        self.__loadThreading()
        if Queue is False:
            gui.warn("Unable to queueFunction - threading not possible.")
        else:
            t = Thread(target=func, args=args)
            t.daemon = True
            t.start()

    # internal function, called by 'after' function, after sleeping
    def __poll(self):
        if not self.alive: return
        # run any registered actions
        for e in self.events:
            # execute the event
            e()
        self.pollId = self.topLevel.after(self.pollTime, self.__poll)

    # not used now, but called every time window is resized
    # may be used in the future...
    def __windowEvent(self, event):
        new_width = self.topLevel.winfo_width()
        new_height = self.topLevel.winfo_height()
        #self.debug("Window resized: " + str(new_width) + "x" + str(new_height))

    # will call the specified function when enter key is pressed
    def enableEnter(self, func):
        """ Binds <Return> to the specified function - all widgets """
        self.bindKey("<Return>", func)

    def disableEnter(self):
        """ unbinds <enter> from all widgets """
        self.unbindKey("<Return>")

    def bindKey(self, key, func):
        """ bind the specified key, to the specified function, for all widgets """
        # for now discard the Event...
        myF = self.MAKE_FUNC(func, key, True)
        self.__getTopLevel().bind(key, myF)

    def unbindKey(self, key):
        """ unbinds the specified key from whatever functions it os bound to """
        self.__getTopLevel().unbind(key)

    # helper - will see if the mouse is in the specified widget
    def __isMouseInWidget(self, w):
        l_x = w.winfo_rootx()
        l_y = w.winfo_rooty()

        if l_x <= w.winfo_pointerx() <= l_x + \
                w.winfo_width() and l_y <= w.winfo_pointery() <= l_y + w.winfo_height():
            return True
        else:
            return False

    # function to give a clicked widget the keyboard focus
    def __grabFocus(self, e):
        e.widget.focus_set()

#####################################
# FUNCTIONS for configuring GUI settings
#####################################
    # set a minimum size
    def __dimensionWindow(self):
        self.topLevel.update_idletasks()
        if self.__getTopLevel().geom != "fullscreen":
            # ISSUES HERE:
            # on MAC & LINUX, w_width/w_height always 1
            # on WIN, w_height is bigger then r_height - leaving empty space

            # show the tb if needed
            toggleTb = False
            if self.hasTb and not self.tbPinned:
                self.__toggletb()
                toggleTb = True

            # get the apps requested width & height
            r_width = self.__getTopLevel().winfo_reqwidth()
            r_height = self.__getTopLevel().winfo_reqheight()

            # get the current width & height
            w_width = self.__getTopLevel().winfo_width()
            w_height = self.__getTopLevel().winfo_height()

            # get the window's width & height
            m_width = self.topLevel.winfo_screenwidth()
            m_height = self.topLevel.winfo_screenheight()

            # determine best geom for OS
            if self.platform in [self.MAC, self.LINUX]:
                b_width = r_width
                b_height = r_height
            elif self.platform == self.WINDOWS:
                b_height = min(r_height, w_height)
                b_width = min(r_width, w_width)
                h_height = max(r_height, w_height)
                h_width = max(r_width, w_width)

            # if a geom has not ben set
            if self.__getTopLevel().geom is None:
                width = b_width
                height = b_height
                # store it in the app's geom
                self.__getTopLevel().geom = str(width) + "x" + str(height)
            else:
                # now split the app's geom
                width = int(self.__getTopLevel().geom.lower().split("x")[0])
                height = int(self.__getTopLevel().geom.lower().split("x")[1])
                # warn the user that their geom is not big enough
                if width < b_width or height < b_height:
                    self.warn(
                        "Specified dimensions (" +
                        self.__getTopLevel().geom +
                        "), less than requested dimensions (" +
                        str(b_width) +
                        "x" +
                        str(b_height) +
                        ")")

            # and set it as the minimum size
            self.__getTopLevel().minsize(width, height)

            # remove the tb again if needed
            if toggleTb:
                self.__toggletb()

            # if window hasn't been positioned by the user, put in the middle
            if not self.__getTopLevel().locationSet:
                self.CENTER(self.__getTopLevel())

    # called to update screen geometry
    def setGeometry(self, geom, height=None):
        self.setGeom(geom, height)

    def setGeom(self, geom, height=None):
        if height is not None:
            geom = str(geom) + "x" + str(height)
        container = self.__getTopLevel()
        container.geom = geom
        if container.geom == "fullscreen":
            self.setFullscreen()
        else:
            self.exitFullscreen()
            if container.geom is not None:
                container.geometry(container.geom)

    # called to set screen position
    def setLocation(self, x, y=None):

        if y is None:
            self.debug("Set location called with no params - CENTERING")
            self.CENTER(self.__getTopLevel())
        else:
            # get the window's width & height
            m_width = self.topLevel.winfo_screenwidth()
            m_height = self.topLevel.winfo_screenheight()

            if x < 0 or x > m_width or y < 0 or y > m_height:
                self.warn( "Invalid location: " + str(x) + ", " + str(y) + " - ignoring")
                return

            self.debug("Setting location to: " + str(x) + "," + str(y))
            self.__getTopLevel().geometry("+%d+%d" % (x, y))
        self.__getTopLevel().locationSet = True

    # called to make sure this window is on top
    def __bringToFront(self, win=None):
        if win is None: win = self.topLevel
        if self.platform == self.MAC:
            import subprocess
            tmpl = 'tell application "System Events" to set frontmost of every process whose unix id is {0} to true'
            script = tmpl.format(os.getpid())
            subprocess.check_call(['/usr/bin/osascript', '-e', script])
            win.after( 0, lambda: win.attributes("-topmost", False))
#            val=os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "''' + PY_NAME + '''" to true' ''')
            win.lift()
        elif self.platform == self.WINDOWS:
            win.lift()
        elif self.platform == self.LINUX:
            win.lift()

    def setFullscreen(self, container=None):
        if not self.isFullscreen:
            self.isFullscreen = True
            if container is None:
                container = self.__getTopLevel()
            container.attributes('-fullscreen', True)
            container.escapeBindId = container.bind(
                '<Escape>', self.MAKE_FUNC(
                    self.exitFullscreen, container, True), "+")

    # function to turn off fullscreen mode
    def exitFullscreen(self, container=None):
        if self.isFullscreen:
            self.isFullscreen = False
            if container is None:
                container = self.__getTopLevel()
            container.attributes('-fullscreen', False)
            if container.escapeBindId is not None:
                container.unbind('<Escape>', container.escapeBindId)
            with PauseLogger():
                self.__doTitleBar()
            return True
        else:
            return False

    # set the current container's external grid padding
    def setPadX(self, x=0):
        self.containerStack[-1]['padx'] = x

    def setPadY(self, y=0):
        self.containerStack[-1]['pady'] = y

    # sets the padding around the border of the root container
    def setPadding(self, x, y=None):
        if y is None:
            if isinstance(x, list):
                self.containerStack[-1]['padx'] = x[0]
                self.containerStack[-1]['pady'] = x[1]
        else:
            self.containerStack[-1]['padx'] = x
            self.containerStack[-1]['pady'] = y

    def setGuiPadding(self, x, y=None):
        if y is None:
            if isinstance(x, list):
                self.containerStack[0]['container'].config(padx=x[0], pady=x[1])
        else:
            self.containerStack[0]['container'].config(padx=x, pady=y)

    # sets the current containers internal padding
    def setIPadX(self, x=0):
        self.setInPadX(x)

    def setIPadY(self, y=0):
        self.setInPadY(y)

    def setIPadding(self, x, y=None):
        self.setInPadding(x, y)

    def setInPadX(self, x=0):
        self.containerStack[-1]['ipadx'] = x

    def setInPadY(self, y=0):
        self.containerStack[-1]['ipady'] = y

    def setInPadding(self, x, y=None):
        if y is None:
            if isinstance(x, list):
                self.containerStack[-1]['ipadx'] = x[0]
                self.containerStack[-1]['ipady'] = x[1]
        else:
            self.containerStack[-1]['ipadx'] = x
            self.containerStack[-1]['ipady'] = y


    # set an override sticky for this container
    def setSticky(self, sticky):
        self.containerStack[-1]['sticky'] = sticky

    # this tells widgets what to do when GUI is resized
    def setStretch(self, exp):
        self.setExpand(exp)

    def setExpand(self, exp):
        if exp.lower() == "none":
            self.containerStack[-1]['expand'] = "NONE"
        elif exp.lower() == "row":
            self.containerStack[-1]['expand'] = "ROW"
        elif exp.lower() == "column":
            self.containerStack[-1]['expand'] = "COLUMN"
        else:
            self.containerStack[-1]['expand'] = "ALL"

    def getFonts(self):
        return list(font.families()).sort()

    def increaseButtonFont(self):
        self.setButtonFont(self.buttonFont['size'] + 1)

    def decreaseButtonFont(self):
        self.setButtonFont(self.buttonFont['size'] - 1)

    def setButtonFont(self, size, font=None):
        if font is None:
            font = self.buttonFont['family']
        self.buttonFont.config(family=font, size=size)

    def increaseLabelFont(self):
        self.setLabelFont(self.labelFont['size'] + 1)

    def decreaseLabelFont(self):
        self.setLabelFont(self.labelFont['size'] - 1)

    def setLabelFont(self, size, font=None):
        if font is None:
            font = self.labelFont['family']
        self.labelFont.config(family=font, size=size)
        self.entryFont.config(family=font, size=size)
        self.rbFont.config(family=font, size=size)
        self.cbFont.config(family=font, size=size)
        self.scaleFont.config(family=font, size=size)
        self.messageFont.config(family=font, size=size)
        self.spinFont.config(family=font, size=size)
        self.optionFont.config(family=font, size=size)
        self.lbFont.config(family=font, size=size)
        self.taFont.config(family=font, size=size)
        self.linkFont.config(family=font, size=size)
        self.meterFont.config(family=font, size=size)
        self.propertiesFont.config(family=font, size=size)
        self.labelFrameFont.config(family=font, size=size)
        self.frameFont.config(family=font, size=size)
        self.toggleFrameFont.config(family=font, size=size)
        self.tabbedFrameFont.config(family=font, size=size)
        self.panedFrameFont.config(family=font, size=size)
        self.scrollPaneFont.config(family=font, size=size)
        self.gridFont.config(family=font, size=size)

        # need tbetter way to register font change events on grids
        for grid in self.n_grids:
            self.n_grids[grid].config(font=self.gridFont)

    def increaseFont(self):
        self.increaseLabelFont()
        self.increaseButtonFont()

    def decreaseFont(self):
        self.decreaseLabelFont()
        self.decreaseButtonFont()

    def setFont(self, size, font=None):
        self.setLabelFont(size, font)
        self.setButtonFont(size, font)

    # need to set a default colour for container
    # then populate that field
    # then use & update that field accordingly
    # all widgets will then need to use it
    # and here we update all....
    def setFg(self, colour, override=False):
        if not self.ttkFlag:
            self.containerStack[-1]['fg']=colour
            gui.SET_WIDGET_FG(self.containerStack[-1]['container'], colour, override)

            for child in self.containerStack[-1]['container'].winfo_children():
                if not self.__isWidgetContainer(child):
                    gui.SET_WIDGET_FG(child, colour, override)
        else:
            gui.warn("In ttk mode - can't set FG to " + str(colour))

    # self.topLevel = Tk()
    # self.appWindow = CanvasDnd, fills all of self.topLevel
    # self.tb = Frame, at top of appWindow
    # self.container = Frame, at bottom of appWindow => C_ROOT container
    # self.bglabel = Label, filling all of container
    def setBg(self, colour, override=False, tint=False):
        if not self.ttkFlag:
            if self.containerStack[-1]['type'] == self.C_ROOT:
                self.appWindow.config(background=colour)
                self.bgLabel.config(background=colour)

            self.containerStack[-1]['container'].config(background=colour)

            for child in self.containerStack[-1]['container'].winfo_children():
                if not self.__isWidgetContainer(child):

                    # horrible hack to deal with weird ScrolledText
                    # winfo_children returns ScrolledText as a Frame
                    # therefore can;t call some functions
                    # this gets the ScrolledText version
                    if child.__class__.__name__ == "Frame":
                        for val in self.n_textAreas.values():
                            if str(val) == str(child):
                                child = val
                                break

                    gui.SET_WIDGET_BG(child, colour, override, tint)
        else:
            gui.warn("In ttk mode - can't set BG to " + str(colour))

    @staticmethod
    def __isWidgetContainer(widget):
        try:
            if widget.isContainer:
                return True
        except:
            pass
        return False

    def setResizable(self, canResize=True):
        self.__getTopLevel().isResizable = canResize
        if self.__getTopLevel().isResizable:
            self.__getTopLevel().resizable(True, True)
        else:
            self.__getTopLevel().resizable(False, False)

    def getResizable(self):
        return self.__getTopLevel().isResizable

    def __doTitleBar(self):
        if self.platform == self.MAC:
            self.warn(
                "Title bar hiding doesn't work on MAC - app may become unresponsive.")
        elif self.platform == self.LINUX:
            self.warn(
                "Title bar hiding doesn't work on LINUX - app may become unresponsive.")
        self.__getTopLevel().overrideredirect(not self.hasTitleBar)

    def hideTitleBar(self):
        self.hasTitleBar = False
        self.__doTitleBar()

    def showTitleBar(self):
        self.hasTitleBar = True
        self.__doTitleBar()

    # function to set the window's title
    def setTitle(self, title):
        self.__getTopLevel().title(title)

    # set an icon
    def setIcon(self, image):
        self.winIcon = image
        container = self.__getTopLevel()
        if image.endswith('.ico'):
            container.wm_iconbitmap(image)
        else:
            icon = self.__getImage(image)
            container.iconphoto(True, icon)

    def __getCanvas(self, param=-1):
        if len(self.containerStack) > 1 and self.containerStack[param]['type'] == self.C_SUBWINDOW:
            return self.containerStack[param]['container']
        elif len(self.containerStack) > 1:
            return self.__getCanvas(param-1)
        else:
            return self.topLevel

    def __getTopLevel(self):
        if len(self.containerStack) > 1 and self.containerStack[-1]['type'] == self.C_SUBWINDOW:
            return self.containerStack[-1]['container']
        else:
            return self.topLevel

    # make the window transparent (between 0 & 1)
    def setTransparency(self, percentage):
        if self.platform == self.LINUX:
            self.warn("Transparency not supported on LINUX")
        else:
            if percentage > 1:
                percentage = float(percentage) / 100
            self.__getTopLevel().attributes("-alpha", percentage)

##############################
# functions to deal with tabbing and right clicking
##############################
    def __focusNextWindow(self, event):
        event.widget.tk_focusNext().focus_set()
        nowFocus = self.topLevel.focus_get()
        if isinstance(nowFocus, Entry):
            nowFocus.select_range(0, END)
        return("break")

    def __focusLastWindow(self, event):
        event.widget.tk_focusPrev().focus_set()
        nowFocus = self.topLevel.focus_get()
        if isinstance(nowFocus, Entry):
            nowFocus.select_range(0, END)
        return("break")

    # creates relevant bindings on the widget
    def __addRightClickMenu(self, widget):
        widget.bind("<FocusIn>", self.__checkCopyAndPaste, add="+")
        widget.bind("<FocusOut>", self.__checkCopyAndPaste, add="+")

        if widget.var is None:  # TEXT:
            widget.bind('<KeyRelease>', self.__checkCopyAndPaste)
            widget.bind('<<Paste>>', self.__checkCopyAndPaste)

        else:
            widget.var.trace("w", lambda name, index, mode,
                e=None, w=widget: self.__checkCopyAndPaste(e, w))  # ENTRY/OPTION

        if self.platform in [self.WINDOWS, self.LINUX]:
            widget.bind('<Button-3>', self.__rightClick)
        else:
            widget.bind('<Button-2>', self.__rightClick)

    def __rightClick(self, event, menu="EDIT"):
        event.widget.focus()
        if menu == "EDIT":
            if self.__checkCopyAndPaste(event):
                self.n_menus[menu].tk_popup(event.x_root - 10, event.y_root - 10)
        else:
            self.n_menus[menu].tk_popup(event.x_root - 10, event.y_root - 10)
        return "break"

#####################################
# FUNCTION to configure widgets
#####################################
    def __getItems(self, kind):
        if kind == self.LABEL:
            return self.n_labels
        elif kind == self.MESSAGE:
            return self.n_messages
        elif kind == self.BUTTON:
            return self.n_buttons
        elif kind in [self.ENTRY, self.FILE_ENTRY, self.DIRECTORY_ENTRY]:
            return self.n_entries
        elif kind == self.SCALE:
            return self.n_scales
        elif kind in [self.CB, self.CHECKBOX]:
            return self.n_cbs
        elif kind in [self.RB, self.RADIOBUTTON]:
            return self.n_rbs
        elif kind in [self.LB, self.LISTBOX]:
            return self.n_lbs
        elif kind in [self.SPIN, self.SPINBOX]:
            return self.n_spins
        elif kind in [self.OPTION, self.OPTIONBOX]:
            return self.n_options
        elif kind == self.TEXTAREA:
            return self.n_textAreas
        elif kind == self.LINK:
            return self.n_links
        elif kind == self.METER:
            return self.n_meters
        elif kind == self.IMAGE:
            return self.n_images
        elif kind == self.MAP:
            return self.n_maps
        elif kind == self.PIECHART:
            return self.n_pieCharts
        elif kind == self.PROPERTIES:
            return self.n_props
        elif kind == self.PLOT:
            return self.n_plots
        elif kind == self.MICROBIT:
            return self.n_microbits
        elif kind == self.GRID:
            return self.n_grids
        elif kind == self.WIDGET:
            return self.n_widgets
        elif kind == self.TREE:
            return self.n_trees
        elif kind == self.TOOLBAR:
            return self.n_tbButts

        elif kind in [ self.LABELFRAME, self.C_LABELFRAME ]:
            return self.n_labelFrames
        elif kind in [ self.FRAME, self.C_FRAME ]:
            return self.n_ajFrame
        elif kind in [ self.TOGGLEFRAME, self.C_TOGGLEFRAME ]:
            return self.n_toggleFrames

        elif kind in [ self.PAGEDWINDOW, self.C_PAGEDWINDOW ]:
            return self.n_pagedWindows
        elif kind in [ self.C_PAGE ]:
            # no dict of pages - the container manages them...
            return self.n_pagedWindows

        elif kind in [ self.TABBEDFRAME, self.C_TABBEDFRAME ]:
            return self.n_tabbedFrames
        elif kind in [ self.C_TAB ]:
            # no dict of tabs - the container manages them...
            return self.n_tabbedFrames
        elif kind in [ self.NOTEBOOK, self.C_NOTEBOOK, self.C_NOTE ]:
            return self.n_notebooks

        elif kind in [ self.PANEDFRAME ]:
            return self.n_panedFrames
        elif kind in [ self.C_PANE ]:
            return self.n_panes

        elif kind in [ self.C_SUBWINDOW ]:
            return self.n_subWindows
        elif kind in [ self.SCROLLPANE, self.C_SCROLLPANE ]:
            return self.n_scrollPanes
        else:
            raise Exception("Unknown widget type: " + str(kind))

    def configureAllWidgets(self, kind, option, value):
        items = list(self.__getItems(kind))
        self.configureWidgets(kind, items, option, value)

    def configureWidgets(self, kind, names, option, value):
        if not isinstance(names, list):
            self.configureWidget(kind, names, option, value)
        else:
            for widg in names:
                # incase 2D array, eg. buttons
                if isinstance(widg, list):
                    for widg2 in widg:
                        self.configureWidget(kind, widg2, option, value)
                else:
                    self.configureWidget(kind, widg, option, value)

    def getWidget(self, kind, name):
        # get the list of items for this type, and validate the widget is in
        # the list
        items = self.__getItems(kind)
        return self.__verifyItem(items, name, False)

    def addWidget(self, title, widg, row=None, column=0, colspan=0, rowspan=0):
        self.__verifyItem(self.n_widgets, title, True)
        self.__positionWidget(widg, row, column, colspan, rowspan)
        self.n_widgets[title] = widg

    def configureWidget(
            self,
            kind,
            name,
            option,
            value,
            key=None,
            deprecated=False):

        self.debug("Configuring: " + str(name) + " of " + str(kind) + " with: " + str(option))

        # warn about deprecated functions
        if deprecated:
            self.warn(
                "Deprecated config function (" +
                option +
                ") used for: " +
                self.WIDGETS[kind] +
                "->" +
                name +
                " use " +
                deprecated +
                " instead")
        if kind in [self.RB, self.LB, self.CB]:
            self.warn(
                "Deprecated config function (" +
                option +
                ") used for: " +
                self.WIDGETS[kind] +
                "->" +
                name +
                " use " +
                self.WIDGETS[
                    kind /
                    10] +
                " instead")
        # get the list of items for this type, and validate the widgetis in the
        # list
        items = self.__getItems(kind)
        self.__verifyItem(items, name)

        if kind in [self.RB, self.RADIOBUTTON] and option not in ["change"]:
            items = items[name]
        else:
            items = [items[name]]

        # loop through each item, and try to reconfigure it
        # this will often fail - widgets have varied config options
        for item in items:
            try:
                if option == 'background':
                    gui.SET_WIDGET_BG(item, value, True)
                elif option == 'foreground':
                    gui.SET_WIDGET_FG(item, value, True)
                elif option == 'disabledforeground':
                    item.config(disabledforeground=value)
                elif option == 'disabledbackground':
                    item.config(disabledbackground=value)
                elif option == 'activeforeground':
                    item.config(activeforeground=value)
                elif option == 'activebackground':
                    item.config(activebackground=value)
                elif option == 'inactiveforeground':
                    if kind == self.TABBEDFRAME:
                        item.config(inactiveforeground=value)
                    else:
                        self.warn("Error configuring " + name +
                                  ": can't set inactiveforeground")
                elif option == 'inactivebackground':
                    if kind == self.TABBEDFRAME:
                        item.config(inactivebackground=value)
                    else:
                        self.warn("Error configuring " + name +
                                  ": can't set inactivebackground")
                elif option == 'width':
                    item.config(width=value)
                elif option == 'height':
                    item.config(height=value)
                elif option == 'state':
                    # make entries readonly - can still copy/paste
                    if value == "disabled" and kind == self.ENTRY:
                        value = "readonly"
                    item.config(state=value)
                elif option == 'relief':
                    item.config(relief=value)
                elif option == 'align':
                    if kind == self.ENTRY:
                        if value == W or value == LEFT:
                            value = LEFT
                        elif value == E or value == RIGHT:
                            value = RIGHT
                        item.config(justify=value)
                    else:
                        if value == LEFT:
                            value = "w"
                        elif value == RIGHT:
                            value = "e"
                        item.config(anchor=value)
                elif option == 'anchor':
                    if kind == self.LABELFRAME:
                        item.config(labelanchor=value)
                    else:
                        item.config(anchor=value)
                elif option == 'cursor':
                    item.config(cursor=value)
                elif option == 'tooltip':
                    self.__addTooltip(item, value)
                elif option == 'disableTooltip':
                    self.__disableTooltip(item)
                elif option == 'enableTooltip':
                    self.__enableTooltip(item)
                elif option == "focus":
                    item.focus_set()
                    if kind == self.ENTRY:
                        item.icursor(END)
                        item.xview(END)

                # event bindings
                elif option == 'over':
                    self.__bindOverEvent(kind, name, item, value, option, key)
                elif option == 'drag':
                    self.__bindDragEvent(kind, name, item, value, option, key)
                elif option in ['command', "change", "submit"]:
                    self.__bindEvent(kind, name, item, value, option, key)

                elif option == 'sticky':
                    info = {}
                    # need to reposition the widget in its grid
                    if self.__widgetHasContainer(kind, item):
                        # pack uses LEFT & RIGHT & BOTH
                        info["side"] = value
                        if value.lower() == "both":
                            info["expand"] = 1
                            info["side"] = "right"
                        else:
                            info["expand"] = 0
                    else:
                        # grid uses E+W
                        if value.lower() == "left":
                            side = W
                        elif value.lower() == "right":
                            side = E
                        elif value.lower() == "both":
                            side = W + E
                        else:
                            side = value.upper()
                        info["sticky"] = side
                    self.__repackWidget(item, info)
                elif option == 'padding':
                    if value[1] is None:
                        item.config(padx=value[0][0], pady=value[0][1])
                    else:
                        item.config(padx=value[0], pady=value[1])
                elif option == 'ipadding':
                    if value[1] is None:
                        item.config(ipadx=value[0][0], ipady=value[0][1])
                    else:
                        item.config(ipadx=value[0], ipady=value[1])
                elif option == 'rightClick':
                    if self.platform in [self.WINDOWS, self.LINUX]:
                        item.bind(
                            '<Button-3>',
                            lambda e,
                            menu=value: self.__rightClick(
                                e,
                                menu))
                    else:
                        item.bind(
                            '<Button-2>',
                            lambda e,
                            menu=value: self.__rightClick(
                                e,
                                menu))
                elif option == 'internalDrop':
                    self.__registerInternalDropTarget(item, value)

                elif option == 'internalDrag':
                    self.__registerInternalDragSource(kind, name, item, value)

                elif option == 'externalDrop':
                    self.__registerExternalDropTarget(name, item, value[0], value[1])

                elif option == 'externalDrag':
                    self.__registerExternalDragSource(name, item, value)

            except TclError as e:
                self.warn("Error configuring " + name + ": " + str(e))

    # generic function for over events
    def __validateFunctionList(self, functions, mode):
        if not isinstance(functions, list):
            functions = [functions]
        if len(functions) == 1:
            functions.append(None)
        if len(functions) != 2:
            raise Exception("Invalid arguments, set<widget>" + mode + "Function requires 1 or 2 functions to be passed in.")

        return functions

    def __bindOverEvent(self, kind, name, widget, functions, eventType, key=None):
        functions = self.__validateFunctionList(functions, "Over")

        if functions[0] is not None:
            widget.bind("<Enter>", self.MAKE_FUNC(functions[0], name, True), add="+")
        if functions[1] is not None:
            widget.bind("<Leave>", self.MAKE_FUNC(functions[1], name, True), add="+")

    # generic function for over events
    def __bindDragEvent(self, kind, name, widget, functions, eventType, key=None):
        functions = self.__validateFunctionList(functions, "Drag")

        if kind == self.LABEL:
            widget.config(cursor="fleur")

            def getLabel(f):
                # loop through all labels
                items = self.__getItems(kind)
                for key, value in items.items():
                    if self.__isMouseInWidget(value):
                        f(key)
                        return

            if functions[0] is not None:
                widget.bind("<ButtonPress-1>", self.MAKE_FUNC(functions[0], name, True), add="+")
            if functions[1] is not None:
                widget.bind("<ButtonRelease-1>", self.MAKE_FUNC(getLabel, functions[1], True), add="+")
        else:
            self.warn("Only able to bind drag events to labels")

    # generic function for change/submit/events
    def __bindEvent(self, kind, name, widget, function, eventType, key=None):
        # this will discard the scale value, as default function
        # can't handle it
        if kind == self.SCALE:
            cmd = self.MAKE_FUNC(function, name, True)
            widget.cmd_id = widget.var.trace('w', cmd)
            widget.cmd = cmd
        elif kind == self.OPTION:
            if widget.kind == "ticks":
                vals = self.__verifyItem(self.n_optionTicks, name)
                for o in vals:
                    cmd = self.MAKE_FUNC(function, str(o), True)
                    vals[o].cmd_id = vals[o].trace('w', cmd)
                    vals[o].cmd = cmd
            else:
                cmd = self.MAKE_FUNC(function, name, True)
                # need to trace the variable??
                widget.cmd_id = widget.var.trace('w', cmd)
                widget.cmd = cmd
        elif kind in [self.ENTRY, self.FILE_ENTRY, self.DIRECTORY_ENTRY]:
            if eventType == "change":
                # not populated by change/submit
                if key is None:
                    key = name
                cmd = self.MAKE_FUNC(function, key, True)
                # get Entry variable
                var = self.__verifyItem(self.n_entryVars, name)
                var.cmd_id = var.trace('w', cmd)
                var.cmd = cmd
            else:
                # not populated by change/submit
                if key is None:
                    key = name
                sbm = self.MAKE_FUNC(function, key, True)
                widget.sbm_id = widget.bind('<Return>', sbm)
                widget.sbm = sbm
        elif kind == self.TEXTAREA:
            if eventType == "change":
                # get Entry variable
                cmd = self.MAKE_FUNC(function, name, True)
                widget.bindChangeEvent(cmd)
        elif kind == self.BUTTON:
            if eventType == "change":
                self.warn("Error configuring " + name +
                            ": can't set a change function")
            else:
                widget.config(command=self.MAKE_FUNC(function, name))
                widget.bind(
                    '<Return>', self.MAKE_FUNC(
                        function, name, True))
        # make labels clickable, add a cursor, and change the look
        elif kind == self.LABEL or kind == self.IMAGE:
            if eventType in ["command", "submit"]:
                if self.platform == self.MAC:
                    widget.config(cursor="pointinghand")
                elif self.platform in [self.WINDOWS, self.LINUX]:
                    widget.config(cursor="hand2")

                cmd = self.MAKE_FUNC(function, name, True)
                widget.bind("<Button-1>", cmd, add="+")
                widget.cmd = cmd
                # these look good, but break when dialogs take focus
                #up = widget.cget("relief").lower()
                # down="sunken"
                # make it look like it's pressed
                #widget.bind("<Button-1>",lambda e: widget.config(relief=down), add="+")
                #widget.bind("<ButtonRelease-1>",lambda e: widget.config(relief=up))
            elif eventType == "change":
                self.warn("Error configuring " + name +
                            ": can't set a change function")
        elif kind == self.LISTBOX:
            cmd = self.MAKE_FUNC(function, name, True)
            widget.bind('<<ListboxSelect>>', cmd)
            widget.cmd = cmd
        elif kind in [self.RB, self.RADIOBUTTON]:
            cmd = self.MAKE_FUNC(function, name, True)
            # get rb variable
            var = self.__verifyItem(self.n_rbVars, name)
            var.cmd_id = var.trace('w', cmd)
            var.cmd = cmd
        elif kind == self.PROPERTIES:
            cmd = self.MAKE_FUNC(function, name, True)
            widget.setChangeFunction(cmd)
        else:
            if kind not in [self.SPIN, self.CHECKBOX, self.CB]:
                self.warn("Unmanaged binding of " + str(eventType) + " to " + str(name))
            cmd = self.MAKE_FUNC(function, name)
            widget.config(command=cmd)
            widget.cmd = cmd

    # dynamic way to create the configuration functions
    def __buildConfigFuncs(self):
        # loop through all the available widgets
        # and make all the below functons for each one
        for k, v in self.WIDGETS.items():
            exec( "def set" + v +
                "Bg(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'background', val)")
            exec("gui.set" + v + "Bg=set" + v + "Bg")
            exec( "def set" + v +
                "Fg(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'foreground', val)")
            exec("gui.set" + v + "Fg=set" + v + "Fg")

            exec( "def set" + v +
                "DisabledFg(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'disabledforeground', val)")
            exec("gui.set" + v + "DisabledFg=set" + v + "DisabledFg")
            exec( "def set" + v +
                "DisabledBg(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'disabledbackground', val)")
            exec("gui.set" + v + "DisabledBg=set" + v + "DisabledBg")

            exec( "def set" + v +
                "ActiveFg(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'activeforeground', val)")
            exec("gui.set" + v + "ActiveFg=set" + v + "ActiveFg")
            exec( "def set" + v +
                "ActiveBg(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'activebackground', val)")
            exec("gui.set" + v + "ActiveBg=set" + v + "ActiveBg")

            exec( "def set" + v +
                "InactiveFg(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'inactiveforeground', val)")
            exec("gui.set" + v + "InactiveFg=set" + v + "InactiveFg")
            exec( "def set" + v +
                "InactiveBg(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'inactivebackground', val)")
            exec("gui.set" + v + "InactiveBg=set" + v + "InactiveBg")

            exec( "def set" + v +
                "Width(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'width', val)")
            exec("gui.set" + v + "Width=set" + v + "Width")
            exec( "def set" + v +
                "Height(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'height', val)")
            exec("gui.set" + v + "Height=set" + v + "Height")
            exec( "def set" + v +
                "State(self, name, val): self.configureWidgets(" +
                str(k) + ", name, 'state', val)")
            exec("gui.set" + v + "State=set" + v + "State")
            exec( "def set" + v +
                "Padding(self, name, x, y=None): self.configureWidgets(" +
                str(k) + ", name, 'padding', [x, y])")
            exec("gui.set" + v + "Padding=set" + v + "Padding")

            exec( "def set" + v +
                "IPadding(self, name, x, y=None): self.configureWidgets(" +
                str(k) + ", name, 'ipadding', [x, y])")
            exec("gui.set" + v + "IPadding=set" + v + "IPadding")

            exec( "def set" + v +
                "InPadding(self, name, x, y=None): self.configureWidgets(" +
                str(k) + ", name, 'ipadding', [x, y])")
            exec("gui.set" + v + "InPadding=set" + v + "InPadding")

            # drag and drop stuff
            exec( "def set" + v +
                "DropTarget(self, name, function=None, replace=True): self.configureWidgets(" +
                str(k) + ", name, 'externalDrop', [function, replace])")
            exec("gui.set" + v + "DropTarget=set" + v + "DropTarget")

            exec( "def set" + v +
                "DragSource(self, name, function=None): self.configureWidgets(" +
                str(k) + ", name, 'externalDrag', function)")
            exec("gui.set" + v + "DragSource=set" + v + "DragSource")

            exec( "def register" + v +
                "Draggable(self, name, function=None): self.configureWidgets(" +
                str(k) + ", name, 'internalDrag', function)")
            exec("gui.register" + v + "Draggable=register" + v + "Draggable")

            exec( "def register" + v +
                "Droppable(self, name, function=None): self.configureWidgets(" +
                str(k) + ", name, 'internalDrop', function)")
            exec("gui.register" + v + "Droppable=register" + v + "Droppable")

            # might not all be necessary, could make exclusion list
            exec( "def set" + v +
                "Relief(self, name, val): self.configureWidget(" +
                str(k) + ", name, 'relief', val)")
            exec("gui.set" + v + "Relief=set" + v + "Relief")
            exec( "def set" + v +
                "Align(self, name, val): self.configureWidget(" +
                str(k) + ", name, 'align', val)")
            exec("gui.set" + v + "Align=set" + v + "Align")
            exec( "def set" + v +
                "Anchor(self, name, val): self.configureWidget(" +
                str(k) + ", name, 'anchor', val)")
            exec("gui.set" + v + "Anchor=set" + v + "Anchor")

            exec( "def set" + v +
                "Tooltip(self, name, val): self.configureWidget(" +
                str(k) + ", name, 'tooltip', val)")
            exec("gui.set" + v + "Tooltip=set" + v + "Tooltip")

            exec( "def disable" + v +
                "Tooltip(self, name): self.configureWidget(" +
                str(k) + ", name, 'disableTooltip', None)")
            exec("gui.disable" + v + "Tooltip=disable" + v + "Tooltip")

            exec( "def enable" + v +
                "Tooltip(self, name): self.configureWidget(" +
                str(k) + ", name, 'enableTooltip', None)")
            exec("gui.enable" + v + "Tooltip=enable" + v + "Tooltip")

            # function setters
            exec( "def set" + v +
                "ChangeFunction(self, name, val): self.configureWidget(" +
                str(k) + ", name, 'change', val)")
            exec("gui.set" + v + "ChangeFunction=set" + v + "ChangeFunction")
            exec( "def set" + v +
                "SubmitFunction(self, name, val): self.configureWidget(" +
                str(k) + ", name, 'submit', val)")
            exec("gui.set" + v + "SubmitFunction=set" + v + "SubmitFunction")
            exec( "def set" + v +
                "DragFunction(self, name, val): self.configureWidget(" +
                str(k) + ", name, 'drag', val)")
            exec("gui.set" + v + "DragFunction=set" + v + "DragFunction")
            exec( "def set" + v +
                "OverFunction(self, name, val): self.configureWidget(" +
                str(k) + ", name, 'over', val)")
            exec("gui.set" + v + "OverFunction=set" + v + "OverFunction")

# deprecated, but left in for backwards compatability
            exec( "def set" + v +
                "Function(self, name, val, key=None): self.configureWidget(" +
                str(k) + ", name, 'command', val, key, deprecated='Submit or Change')")
            exec("gui.set" + v + "Function=set" + v + "Function")
            exec( "def set" + v +
                "Command(self, name, val, key=None): self.configureWidget(" +
                str(k) + ", name, 'command', val, key, deprecated='Submit or Change')")
            exec("gui.set" + v + "Command=set" + v + "Command")

            exec( "def set" + v +
                "Func(self, name, val, key=None): self.configureWidget(" +
                str(k) + ", name, 'command', val, key, deprecated='Submit or Change')")
            exec("gui.set" + v + "Func=set" + v + "Func")
# end deprecated
            # http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/cursors.html
            exec( "def set" + v +
                "Cursor(self, name, val): self.configureWidget(" +
                str(k) + ", name, 'cursor', val)")
            exec("gui.set" + v + "Cursor=set" + v + "Cursor")
            exec( "def set" + v +
                "Focus(self, name): self.configureWidget(" +
                str(k) + ", name, 'focus', None)")
            exec("gui.set" + v + "Focus=set" + v + "Focus")

            # change the stickyness
            exec( "def set" + v +
                "Sticky(self, name, pos): self.configureWidget(" +
                str(k) + ", name, 'sticky', pos)")
            exec("gui.set" + v + "Sticky=set" + v + "Sticky")

            # add right click
            exec( "def set" + v +
                "RightClick(self, name, menu): self.configureWidget(" +
                str(k) + ", name, 'rightClick', menu)")
            exec("gui.set" + v + "RightClick=set" + v + "RightClick")

            # functions to manage widgets
            exec( "def show" + v +
                "(self, name): self.showWidgetType(" +
                str(k) + ", name)")
            exec("gui.show" + v + "=show" + v)
            exec( "def hide" + v +
                "(self, name): self.hideWidgetType(" +
                str(k) + ", name)")
            exec("gui.hide" + v + "=hide" + v)
            exec( "def remove" + v +
                "(self, name): self.removeWidgetType(" +
                str(k) + ", name)")
            exec("gui.remove" + v + "=remove" + v)

            # convenience functions for enable/disable
            # might not all be necessary, could make exclusion list
            exec( "def enable" + v +
                "(self, name): self.configureWidget(" +
                str(k) + ", name, 'state', 'normal')")
            exec("gui.enable" + v + "=enable" + v)
            exec( "def disable" + v +
                "(self, name): self.configureWidget(" +
                str(k) + ", name, 'state', 'disabled')")
            exec("gui.disable" + v + "=disable" + v)

            # group functions
            exec( "def set" + v +
                "Widths(self, names, val): self.configureWidgets(" +
                str(k) + ", names, 'width', val)")
            exec("gui.set" + v + "Widths=set" + v + "Widths")
            exec( "def setAll" + v +
                "Widths(self, val): self.configureAllWidgets(" +
                str(k) + ", 'width', val)")
            exec("gui.setAll" + v + "Widths=setAll" + v + "Widths")

            exec( "def set" + v +
                "Heights(self, names, val): self.configureWidgets(" +
                str(k) + ", names, 'height', val)")
            exec("gui.set" + v + "Heights=set" + v + "Heights")
            exec( "def setAll" + v +
                "Heights(self, val): self.configureAllWidgets(" +
                str(k) + ", 'height', val)")
            exec("gui.setAll" + v + "Heights=setAll" + v + "Heights")

            exec( "def get" + v +
                "Widget(self, name): return self.getWidget(" +
                str(k) + ", name)")
            exec("gui.get" + v + "Widget=get" + v + "Widget")

#####################################
#  FUNCTION to hide/show/remove widgets
#####################################
    def __widgetHasContainer(self, kind, item):
        if kind in [
                self.SCALE,
                self.ENTRY,
                self.SPIN,
                self.OPTION,
                self.LABEL] and item.inContainer:
            return True
        else:
            return False

    def hideWidgetType(self, kind, name):
        # get the dictionary of items, and find the item in it
        items = self.__getItems(kind)
        item = self.__verifyItem(items, name)

        if self.__widgetHasContainer(kind, item):
            widget = item.master
            self.n_frameLabs[name].hidden = True
        else:
            if kind in [self.RB, self.RADIOBUTTON]:
                for rb in item:
                    if rb.text == name:
                        widget = rb
            widget = item

        if "in" in widget.grid_info():
            widget.grid_remove()
#                  self.__updateLabelBoxes(name)

    def showWidgetType(self, kind, name):
        # get the dictionary of items, and find the item in it
        items = self.__getItems(kind)
        item = self.__verifyItem(items, name)

        if self.__widgetHasContainer(kind, item):
            widget = item.master
            self.n_frameLabs[name].hidden = False
        else:
            widget = item

        # only show the widget, if it's not already showing
        if "in" not in widget.grid_info():
            widget.grid()
#                  self.__updateLabelBoxes(name)

    def removeWidgetType(self, kind, name):
        # get the dictionary of items, and find the item in it
        items = self.__getItems(kind)
        item = self.__verifyItem(items, name)

        # if it's a flasher, remove it
        if item in self.n_flashLabs:
            self.n_flashLabs.remove(item)
            if len(self.n_flashLabs) == 0:
                self.doFlash = False

        # animated images...

        if self.__widgetHasContainer(kind, item):
            # destroy the parent
            parent = item.master
            parent.grid_forget()
            parent.destroy()
            # remove frame, label & widget from lists
            self.n_labels.pop(name)
            self.n_frameLabs.pop(name)
            self.n_frames.remove(parent)
        else:
            item.grid_forget()
            item.destroy()

        # finally remove it from the dictionary
        items.pop(name)

    def removeAllWidgets(self):
        for child in self.containerStack[0]['container'].winfo_children():
            child.destroy()
        self.__configBg(self.containerStack[0]['container'])
        self.__initArrays()
        self.setGeom(None)

#####################################
# FUNCTION for managing commands
#####################################
    # function to wrap up lambda
    # if the thing calling this generates parameters - then set discard=True
    @staticmethod
    def MAKE_FUNC(funcName, param, discard=False):
        # make sure we get a function
        if not callable(funcName) and not hasattr(funcName, '__call__'):
            raise Exception("Invalid function: " + str(funcName))
        
        if discard:
            return lambda *args: funcName(param)
        else:
            return lambda: funcName(param)

    def __checkFunc(self, names, funcs):
        singleFunc = None
        if funcs is None:
            return None
        elif callable(funcs):
            singleFunc = funcs
        elif len(names) != len(funcs):
            raise Exception("List sizes don't match")
        return singleFunc

#####################################
# FUNCTION to position a widget
#####################################
    # checks if the item already exists
    def __verifyItem(self, items, item, newItem=False):
        if not newItem and item not in items:
            raise ItemLookupError("Invalid key: " + item + " does not exist")
        elif not newItem and item in items:
            return items[item]
        elif newItem and item in items:
            raise ItemLookupError(
                "Duplicate key: '" + item + "' already exists")

    def getRow(self):
        return self.containerStack[-1]['emptyRow']

    def gr(self):
        return self.getRow()

    def __repackWidget(self, widget, params):
        if widget.winfo_manager() == "grid":
            ginfo = widget.grid_info()
            ginfo.update(params)
            widget.grid(ginfo)
        elif widget.winfo_manager() == "pack":
            pinfo = widget.pack_info()
            pinfo.update(params)
            widget.pack(pinfo)
        else:
            raise Exception(
                "Unknown geometry manager: " +
                widget.winfo_manager())

    # convenience function to set RCS, referencing the current container's
    # settings
    def __getRCS(self, row, column, colspan, rowspan):
        if row is None:
            row = self.containerStack[-1]['emptyRow']
        self.containerStack[-1]['emptyRow'] = row + 1

        if column >= self.containerStack[-1]['colCount']:
            self.containerStack[-1]['colCount'] = column + 1
        # if column == 0 and colspan == 0 and self.containerStack[-1]['colCount'] > 1:
        #      colspan = self.containerStack[-1]['colCount']

        return row, column, colspan, rowspan

    @staticmethod
    def SET_WIDGET_FG(widget, fg, external=False):
        widgType = widget.__class__.__name__
        gui.debug("SET_WIDGET_FG: " + str(widgType) + " - " + str(fg))

        # only configure these widgets if external
        if widgType == "Link":
            if external:
                widget.fg = fg
                widget.overFg = gui.TINT(widget, fg)
                widget.config(foreground=fg)
        elif widgType in ["Entry", "AutoCompleteEntry"]:
            if external:
                widget.oldFg = fg
                if not widget.showingDefault:
                    widget.config(foreground=fg)
        elif widgType in ["Spinbox", "AjText", "AjScrolledText", "Button"]:
            if external:
                widget.config(fg=fg)
        elif widgType == "OptionMenu":
            if external:
                widget.config(fg=fg)
                widget["menu"].config(fg=fg)
        # handle flash labels
        elif widgType == "Label":
            widget.config(fg=fg)
            widget.origFg=fg
            try: widget.config(bg=widget.origBg)
            except: pass # not a flash label

        # deal with generic groupers
        elif widgType in ["Frame", "LabelFrame", "PanedFrame", "Pane", "ajFrame"]:
            for child in widget.winfo_children():
                gui.SET_WIDGET_FG(child, fg, external)

        # deal with specific containers
        elif widgType == "LabelBox":
            try:
                if not widget.isValidation:
                    gui.SET_WIDGET_FG(widget.theLabel, fg, external)
            except Exception as e:
                gui.SET_WIDGET_FG(widget.theLabel, fg, external)
            gui.SET_WIDGET_FG(widget.theWidget, fg, external)
        elif widgType == "ButtonBox":
            gui.SET_WIDGET_FG(widget.theWidget, fg, external)
            gui.SET_WIDGET_FG(widget.theButton, fg, external)
        elif widgType == "WidgetBox":
            for child in widget.theWidgets:
                gui.SET_WIDGET_FG(child, fg, external)
        elif widgType == "ListBoxContainer":
            if external:
                gui.SET_WIDGET_FG(widget.lb, fg, external)

        # skip these widgets
        elif widgType in ["PieChart", "MicroBitSimulator", "Scrollbar"]:
            pass

        # always try these widgets
        else:
            try:
                widget.config(fg=fg)
            except Exception as e:
                pass

    @staticmethod
    def TINT(widget, colour):
        col = []
        for a, b in enumerate(widget.winfo_rgb(colour)):
            t = int(min(max(0, b / 256 + (255 - b / 256) * .3), 255))
            t = str(hex(t))[2:]
            if len(t) == 1:
                t = '0' + t
            elif len(t) == 0:
                t = '00'
            col.append(t)

        if int(col[0], 16) > 210 and int(col[1], 16) > 210 and int(col[2], 16) > 210:
            if gui.GET_PLATFORM() == gui.LINUX:
                return "#c3c3c3"
            else:
                return "systemHighlight"
        else:
            return "#" + "".join(col)

    # convenience method to set a widget's bg
    @staticmethod
    def SET_WIDGET_BG(widget, bg, external=False, tint=False):

        if bg is None: # ignore empty colours
            return  

        widgType = widget.__class__.__name__
        isDarwin = gui.GET_PLATFORM() == gui.MAC
        isLinux = gui.GET_PLATFORM() == gui.LINUX

        gui.debug("Config " + str(widgType) + " BG to " + str(bg))

        # these have a highlight border to remove
        hideBorders = [ "Text", "AjText",
            "ScrolledText", "AjScrolledText",
            "Scale", "ajScale",
            "OptionMenu",
            "Entry", "AutoCompleteEntry",
            "Radiobutton", "Checkbutton",
            "Button"]

        # these shouldn't have their BG coloured by default
        noBg = [ "Button",
            "Scale", "ajScale",
            "Spinbox", "Listbox", "OptionMenu",
            "SplitMeter", "DualMeter", "Meter",
            "Entry", "AutoCompleteEntry",
            "Text", "AjText",
            "ScrolledText", "AjScrolledText",
            "ToggleFrame"]

        # remove the highlight borders
        if widgType in hideBorders:
            if widgType == "Entry" and widget.isValidation:
                pass
            elif widgType == "OptionMenu":
                widget["menu"].config(borderwidth=0)
                widget.config(highlightbackground=bg)
                if isDarwin:
                    widget.config(background=bg)
            elif widgType in ["Radiobutton", "Checkbutton"]:
                widget.config(activebackground=bg, highlightbackground=bg)
            else:
                widget.config(highlightbackground=bg)

        # do some fancy tinting
        if external or tint:
            if widgType in ["Button", "Scale", "ajScale"]:
                widget.config(activebackground=gui.TINT(widget, bg))
            elif widgType in ["Entry", "Text", "AjText", "ScrolledText", "AjScrolledText", "AutoCompleteEntry", "Spinbox"]:
                widget.config(selectbackground=gui.TINT(widget, bg))
                widget.config(highlightcolor=gui.TINT(widget, bg))
                if widgType in ["Text", "AjText", "ScrolledText", "AjScrolledText"]:
                    widget.config(inactiveselectbackground=gui.TINT(widget, bg))
                elif widgType == "Spinbox":
                    widget.config(buttonbackground=bg)
            elif widgType == "Listbox":
                widget.config(selectbackground=gui.TINT(widget, bg))
            elif widgType == "OptionMenu":
                widget.config(activebackground=gui.TINT(widget, bg))
                widget["menu"].config(activebackground=gui.TINT(widget, bg))
            elif widgType in ["Radiobutton", "Checkbutton"]:
                widget.config(activebackground=gui.TINT(widget, bg))

        # if this is forced - change everything
        if external:
            widget.config(bg=bg)
            if widgType == "OptionMenu":
                widget["menu"].config(bg=bg)
        # otherwise only colour un-excluded widgets
        elif widgType not in noBg:
            widget.config(bg=bg)

        # deal with flash labels
        if widgType == "Label":
            widget.origBg=bg
            try: widget.config(fg=widget.origFg)
            except: pass # not a flash label

        # now do any of the below containers
        if widgType in ["LabelFrame", "PanedFrame", "Pane", "ajFrame"]:
            for child in widget.winfo_children():
                gui.SET_WIDGET_BG(child, bg, external, tint)
        elif widgType == "LabelBox": # widget with label, in frame
            if widget.theLabel is not None:
                gui.SET_WIDGET_BG(widget.theLabel, bg, external, tint)
            gui.SET_WIDGET_BG(widget.theWidget, bg, external, tint)
        elif widgType == "ButtonBox": # widget with button, in frame
            gui.SET_WIDGET_BG(widget.theWidget, bg, external, tint)
            gui.SET_WIDGET_BG(widget.theButton, bg, external, tint)
        elif widgType == "ListBoxContainer": # list box container
            gui.SET_WIDGET_BG(widget.lb, bg, external, tint)
        elif widgType == "WidgetBox": # group of buttons or labels
            for widg in widget.theWidgets:
                gui.SET_WIDGET_BG(widg, bg, external, tint)

    def __getContainerBg(self):
        return self.getContainer()["bg"]

    def __getContainerFg(self):
        try:
            return self.containerStack[-1]['fg']
        except:
            return "#000000"

    # two important things here:
    # grid - sticky: position of widget in its space (side or fill)
    # row/columns configure - weight: how to grow with GUI
    def __positionWidget(
            self,
            widget,
            row,
            column=0,
            colspan=0,
            rowspan=0,
            sticky=W + E):
        # allow item to be added to container
        container = self.getContainer()
        if not self.ttkFlag:
            gui.SET_WIDGET_FG(widget, self.__getContainerFg())
            gui.SET_WIDGET_BG(widget, self.__getContainerBg())

        # alpha paned window placement
        if self.containerStack[-1]['type'] == self.C_PANEDFRAME:
            container.add(widget)
            self.containerStack[-1]['widgets'] = True
            return

        # else, add to grid
        row, column, colspan, rowspan = self.__getRCS(
            row, column, colspan, rowspan)

        # build a dictionary for the named params
        iX = self.containerStack[-1]['ipadx']
        iY = self.containerStack[-1]['ipady']
        cX = self.containerStack[-1]['padx']
        cY = self.containerStack[-1]['pady']
        params = {
            "row": row,
            "column": column,
            "ipadx": iX,
            "ipady": iY,
            "padx": cX,
            "pady": cY}

        # if we have a column span, apply it
        if colspan != 0:
            params["columnspan"] = colspan
        # if we have a rowspan, apply it
        if rowspan != 0:
            params["rowspan"] = rowspan

        # 1) if param has sticky, use that
        # 2) if container has sticky - override
        # 3) else, none
        if self.containerStack[-1]["sticky"] is not None:
            params["sticky"] = self.containerStack[-1]["sticky"]
        elif sticky is not None:
            params["sticky"] = sticky
        else:
            pass

        # make colspanned widgets expand to fill height of cell
        if rowspan != 0:
            if "sticky" in params:
                if "n" not in params["sticky"]:
                    params["sticky"] += "n"
                if "s" not in params["sticky"]:
                    params["sticky"] += "s"
            else:
                params["sticky"] = "ns"

        # expand that dictionary out as we pass it as a value
        widget.grid(**params)
        self.containerStack[-1]['widgets'] = True
        # if we're in a PANEDFRAME - we need to set parent...
        if self.containerStack[-1]['type'] == self.C_PANE:
            self.containerStack[-2]['widgets'] = True

        # configure the row/column to expand equally
        if self.containerStack[-1]['expand'] in ["ALL", "COLUMN"]:
            Grid.columnconfigure(container, column, weight=1)
        else:
            Grid.columnconfigure(container, column, weight=0)
        if self.containerStack[-1]['expand'] in ["ALL", "ROW"]:
            Grid.rowconfigure(container, row, weight=1)
        else:
            Grid.rowconfigure(container, row, weight=0)

#        self.containerStack[-1]['container'].columnconfigure(0, weight=1)
#        self.containerStack[-1]['container'].rowconfigure(0, weight=1)


#####################################
# FUNCTION to manage containers
#####################################
    # adds the container to the container stack - makes this the current
    # working container
    def __addContainer(self, cTitle, cType, container, row, col, sticky=None):
        containerData = {'type': cType,
                    'title': cTitle,
                    'container': container,
                    'emptyRow': row,
                    'colCount': col,
                    'sticky': sticky,
                    'padx': 0,
                    'pady': 0,
                    'ipadx': 0,
                    'ipady': 0,
                    'expand': "ALL",
                    'widgets': False,
                    "fg": self.__getContainerFg()}
        self.containerStack.append(containerData)

    def openRootPage(self, title):
        self.__openContainer(self.C_ROOT, title)

    def openLabelFrame(self, title):
        self.__openContainer(self.C_LABELFRAME, title)

    def openFrame(self, title):
        self.__openContainer(self.C_FRAME, title)

    def openToggleFrame(self, title):
        self.__openContainer(self.C_TOGGLEFRAME, title)

    def openPagedWindow(self, title):
        self.__openContainer(self.C_PAGEDWINDOW, title)

    def openPage(self, windowTitle, pageNumber):
        self.__openContainer(self.C_PAGE, windowTitle+"__"+str(pageNumber))

    def openTabbedFrame(self, title):
        self.__openContainer(self.C_TABBEDFRAME, title)

    def openTab(self, frameTitle, tabTitle):
        self.__openContainer(self.C_TAB, frameTitle+"__"+tabTitle)

    def openNotebook(self, title):
        self.__openContainer(self.C_NOTEBOOK, title)

    def openNote(self, frameTitle, tabTitle):
        self.__openContainer(self.C_NOTEBOOK, frameTitle+"__"+tabTitle)

    def openPanedFrame(self, title):
        self.__openContainer(self.C_PANEDFRAME, title)

    def openPane(self, title):
        self.__openContainer(self.C_PANE, title)

    def openSubWindow(self, title):
        self.__openContainer(self.C_SUBWINDOW, title)

    def openScrollPane(self, title):
        self.__openContainer(self.C_SCROLLPANE, title)

    # function to reload the specified container
    def __openContainer(self, kind, title):

        # get the cached container config for this container
        cName = kind + "__" + title
        try:
            cConf = self.n_usedContainers[cName]
        except KeyError:
            raise Exception("Attempted to open invalid " + kind + ": " + str(title))

        self.containerStack.append(cConf)

    # returns the current working container
    def __getContainer(self):
        self.warn(".__getContainer() has been deprecated. Please use .getContainer()")
        return self.getContainer()

    def getContainer(self):
        container = self.containerStack[-1]['container']
        if self.containerStack[-1]['type'] == self.C_SCROLLPANE:
            return container.interior
        elif self.containerStack[-1]['type'] == self.C_PAGEDWINDOW:
            return container.getPage()
        elif self.containerStack[-1]['type'] == self.C_TOGGLEFRAME:
            return container.getContainer()
        elif self.containerStack[-1]['type'] == self.C_SUBWINDOW:
            return container.canvasPane
        else:
            return container

    # if possible, removes the current container
    def __removeContainer(self):
        if len(self.containerStack) == 1:
            raise Exception("Can't remove container, already in root window.")
        else:
            container = self.containerStack.pop()
            if not container['widgets']:
                self.warn("Closing empty container: " + container['title'])
#                raise Exception("Put something in the container, before removing it.")

            # store the container so that it can be re-opened later
            name = container["type"] + "__" + container["title"]
            self.n_usedContainers[name] = container
            return container

    # functions to start the various containers
    def startContainer(
            self,
            fType,
            title,
            row=None,
            column=0,
            colspan=0,
            rowspan=0,
            sticky=None):
        if fType == self.C_LABELFRAME:
            # first, make a LabelFrame, and position it correctly
            self.__verifyItem(self.n_labelFrames, title, True)
            if not self.ttkFlag:
                container = LabelFrame(self.getContainer(), text=title, relief="groove")
                container.config(background=self.__getContainerBg(), font=self.labelFrameFont)
            else:
                container = ttk.LabelFrame(self.getContainer(), text=title, relief="groove")

            container.DEFAULT_TEXT = title
            container.isContainer = True
            self.setPadX(5)
            self.setPadY(5)
            self.__positionWidget(container, row, column, colspan, rowspan, "nsew")
            self.n_labelFrames[title] = container

            # now, add to top of stack
            self.__addContainer(title, self.C_LABELFRAME, container, 0, 1, sticky)
            return container
        elif fType == self.C_FRAME:
            # first, make a Frame, and position it correctly
            self.__verifyItem(self.n_ajFrame, title, True)
            container = ajFrame(self.getContainer())
            container.isContainer = True
#            container.config(background=self.__getContainerBg(), font=self.frameFont, relief="groove")
            container.config(background=self.__getContainerBg())
            self.__positionWidget(
                container, row, column, colspan, rowspan, "nsew")
            self.n_ajFrame[title] = container

            # now, add to top of stack
            self.__addContainer(title, self.C_FRAME, container, 0, 1, sticky)
            return container
        elif fType == self.C_TABBEDFRAME:
            self.__verifyItem(self.n_tabbedFrames, title, True)
            tabbedFrame = TabbedFrame(self.getContainer(), bg=self.__getContainerBg())
#            tabbedFrame.isContainer = True
            self.__positionWidget(
                tabbedFrame,
                row,
                column,
                colspan,
                rowspan,
                sticky=sticky)
            self.n_tabbedFrames[title] = tabbedFrame

            # now, add to top of stack
            self.__addContainer(title, self.C_TABBEDFRAME, tabbedFrame, 0, 1, sticky)
            return tabbedFrame
        elif fType == self.C_TAB:
            # add to top of stack
            self.containerStack[-1]['widgets'] = True
            tabTitle = self.containerStack[-1]['title'] + "__" + title
            self.__addContainer(tabTitle,
                self.C_TAB, self.containerStack[-1]['container'].addTab(title), 0, 1, sticky)
        elif fType == self.C_NOTEBOOK:
            self.__verifyItem(self.n_notebooks, title, True)
            notebook = ttk.Notebook(self.getContainer())
#            tabbedFrame.isContainer = True
            self.__positionWidget(
                notebook,
                row,
                column,
                colspan,
                rowspan,
                sticky=sticky)
            self.n_notebooks[title] = notebook

            # now, add to top of stack
            self.__addContainer(title, self.C_NOTEBOOK, notebook, 0, 1, sticky)
            return notebook
        elif fType == self.C_NOTE:
            # add to top of stack
            self.containerStack[-1]['widgets'] = True
            noteTitle = self.containerStack[-1]['title'] + "__" + title
            frame = ttk.Frame(self.containerStack[-1]['container'])
            self.containerStack[-1]['container'].add(frame, text=title)
            self.__addContainer(noteTitle, self.C_NOTE, frame, 0, 1, sticky)
        elif fType == self.C_PANEDFRAME:
            # if we previously put a frame for widgets
            # remove it
            if self.containerStack[-1]['type'] == self.C_PANE:
                self.stopContainer()

            # now, add the new pane
            self.__verifyItem(self.n_panedFrames, title, True)
            pane = PanedWindow(
                self.getContainer(),
                showhandle=True,
                sashrelief="groove",
                bg=self.__getContainerBg())
            pane.isContainer = True
            self.__positionWidget(
                pane, row, column, colspan, rowspan, sticky=sticky)
            self.n_panedFrames[title] = pane

            # now, add to top of stack
            self.__addContainer(title, self.C_PANEDFRAME, pane, 0, 1, sticky)

            # now, add a frame to the pane
            self.startContainer(self.C_PANE, title)
            return pane
        elif fType == self.C_PANE:
            # create a frame, and add it to the pane
            pane = Pane(self.getContainer(), bg=self.__getContainerBg())
            pane.isContainer = True
            self.containerStack[-1]['container'].add(pane)
            self.n_panes[title] = pane

            # now, add to top of stack
            self.__addContainer(title, self.C_PANE, pane, 0, 1, sticky)
            return pane
        elif fType == self.C_SCROLLPANE:
            self.__verifyItem(self.n_scrollPanes, title, True)
            scrollPane = ScrollPane(self.getContainer(), bg=self.__getContainerBg())#, width=100, height=100)
            scrollPane.isContainer = True
#                self.containerStack[-1]['container'].add(scrollPane)
            self.__positionWidget(
                scrollPane,
                row,
                column,
                colspan,
                rowspan,
                sticky=sticky)
            self.n_scrollPanes[title] = scrollPane

            # now, add to top of stack
            self.__addContainer(title, self.C_SCROLLPANE, scrollPane, 0, 1, sticky)
            return scrollPane
        elif fType == self.C_TOGGLEFRAME:
            self.__verifyItem(self.n_toggleFrames, title, True)
            toggleFrame = ToggleFrame(self.getContainer(), title=title, bg=self.__getContainerBg())
            toggleFrame.configure(font=self.toggleFrameFont)
            toggleFrame.isContainer = True
            self.__positionWidget(
                toggleFrame,
                row,
                column,
                colspan,
                rowspan,
                sticky=sticky)
            self.__addContainer(title, self.C_TOGGLEFRAME, toggleFrame, 0, 1, "nw")
            self.n_toggleFrames[title] = toggleFrame
            return toggleFrame
        elif fType == self.C_PAGEDWINDOW:
            # create the paged window
            pagedWindow = PagedWindow(
                self.getContainer(),
                title=title,
                bg=self.__getContainerBg(),
                width=200,
                height=400)
            # bind events
            self.topLevel.bind("<Left>", pagedWindow.showPrev)
            self.topLevel.bind("<Control-Left>", pagedWindow.showFirst)
            self.topLevel.bind("<Right>", pagedWindow.showNext)
            self.topLevel.bind("<Control-Right>", pagedWindow.showLast)
            # register it as a container
            pagedWindow.isContainer = True
            self.__positionWidget(
                pagedWindow,
                row,
                column,
                colspan,
                rowspan,
                sticky=sticky)
            self.__addContainer(title, self.C_PAGEDWINDOW, pagedWindow, 0, 1, "nw")
            self.n_pagedWindows[title] = pagedWindow
            return pagedWindow
        elif fType == self.C_PAGE:
            page = self.containerStack[-1]['container'].addPage()
            page.isContainer = True
            self.__addContainer(title, self.C_PAGE, page, 0, 1, sticky)
            self.containerStack[-1]['expand'] = "None"
            return page
        else:
            raise Exception("Unknown container: " + fType)

    def startNotebook(
            self,
            title,
            row=None,
            column=0,
            colspan=0,
            rowspan=0,
            sticky="NSEW"):
        return self.startContainer(
            self.C_NOTEBOOK,
            title,
            row,
            column,
            colspan,
            rowspan,
            sticky)

    @contextmanager
    def notebook(self, title, row=None, column=0, colspan=0, rowspan=0, sticky="NSEW"):
        try:
            note = self.startNotebook(title, row, column, colspan, rowspan, sticky)
        except ItemLookupError:
            note = self.openNotebook(title)
        try: yield note
        finally: self.stopNotebook()

    def stopNotebook(self):
        # auto close the existing TAB - keep it?
        if self.containerStack[-1]['type'] == self.C_NOTE:
            self.warn("You didn't STOP the previous NOTE")
            self.stopContainer()
        self.stopContainer()

    @contextmanager
    def note(self, title, tabTitle=None):
        if tabTitle is None:
            note = self.startNote(title)
        else:
            self.openNote(title, tabTitle)
        try: yield note
        finally: self.stopNote()

    def startNote(self, title):
        # auto close the previous TAB - keep it?
        if self.containerStack[-1]['type'] == self.C_NOTE:
            self.warn("You didn't STOP the previous NOTE")
            self.stopContainer()
        elif self.containerStack[-1]['type'] != self.C_NOTEBOOK:
            raise Exception(
                "Can't add a Note to the current container: ", self.containerStack[-1]['type'])
        self.startContainer(self.C_NOTE, title)

    def stopNote(self):
        if self.containerStack[-1]['type'] != self.C_NOTE:
            raise Exception("Can't stop a NOTE, currently in:",
                            self.containerStack[-1]['type'])
        self.stopContainer()


    ####### Tabbed Frames ########

    @contextmanager
    def tabbedFrame(self, title, row=None, column=0, colspan=0, rowspan=0, sticky="NSEW"):
        try:
            tabs = self.startTabbedFrame(title, row, column, colspan, rowspan, sticky)
        except ItemLookupError:
            tabs = self.openTabbedFrame(title)
        try: yield tabs
        finally: self.stopTabbedFrame()

    def startTabbedFrame(
            self,
            title,
            row=None,
            column=0,
            colspan=0,
            rowspan=0,
            sticky="NSEW"):
        return self.startContainer(
            self.C_TABBEDFRAME,
            title,
            row,
            column,
            colspan,
            rowspan,
            sticky)

    def stopTabbedFrame(self):
        # auto close the existing TAB - keep it?
        if self.containerStack[-1]['type'] == self.C_TAB:
            self.warn("You didn't STOP the previous TAB")
            self.stopContainer()
        self.stopContainer()

    def setTabbedFrameTabExpand(self, title, expand=True):
        nb = self.__verifyItem(self.n_tabbedFrames, title)
        nb.expandTabs(expand)

    def setTabbedFrameSelectedTab(self, title, tab):
        nb = self.__verifyItem(self.n_tabbedFrames, title)
        nb.changeTab(tab)

    def setTabbedFrameDisabledTab(self, title, tab, disabled=True):
        nb = self.__verifyItem(self.n_tabbedFrames, title)
        nb.disableTab(tab, disabled)

    def setTabbedFrameDisableAllTabs(self, title, disabled=True):
        nb = self.__verifyItem(self.n_tabbedFrames, title)
        nb.disableAllTabs(disabled)

    def setTabText(self, title, tab, newText=None):
        nb = self.__verifyItem(self.n_tabbedFrames, title)
        nb.renameTab(tab, newText)

    def setTabBg(self, title, tab, colour):
        nb = self.__verifyItem(self.n_tabbedFrames, title)
        tab = nb.getTab(tab)
        gui.SET_WIDGET_BG(tab, colour)
        # tab.config(bg=colour)
        #gui.SET_WIDGET_BG(tab, colour)
        for child in tab.winfo_children():
            gui.SET_WIDGET_BG(child, colour)

    @contextmanager
    def tab(self, title, tabTitle=None):
        if tabTitle is None:
            tab = self.startTab(title)
        else:
            tab = self.openTab(title, tabTitle)
        try: yield tab
        finally: self.stopTab()

    def startTab(self, title):
        # auto close the previous TAB - keep it?
        if self.containerStack[-1]['type'] == self.C_TAB:
            self.warn("You didn't STOP the previous TAB")
            self.stopContainer()
        elif self.containerStack[-1]['type'] != self.C_TABBEDFRAME:
            raise Exception(
                "Can't add a Tab to the current container: ", self.containerStack[-1]['type'])
        self.startContainer(self.C_TAB, title)

    def getTabbedFrameSelectedTab(self, title):
        nb = self.__verifyItem(self.n_tabbedFrames, title)
        return nb.getSelectedTab()

    def stopTab(self):
        if self.containerStack[-1]['type'] != self.C_TAB:
            raise Exception("Can't stop a TAB, currently in:",
                            self.containerStack[-1]['type'])
        self.stopContainer()

    ###### END Tabbed Frames ########

    #####################################
    # FUNCTION for simple grids
    #####################################
    def addGrid(
            self,
            title,
            data,
            row=None,
            column=0,
            colspan=0,
            rowspan=0,
            action=None,
            addRow=None,
            actionHeading="Action",
            actionButton="Press",
            addButton="Add"):
        self.__verifyItem(self.n_grids, title, True)
        grid = SimpleGrid(
            self.getContainer(),
            title,
            data,
            action,
            addRow,
            actionHeading,
            actionButton,
            addButton,
            buttonFont=self.buttonFont)
        grid.config(font=self.gridFont, background=self.__getContainerBg())
        self.__positionWidget(
            grid,
            row,
            column,
            colspan,
            rowspan,
            N + E + S + W)
        self.n_grids[title] = grid
        return grid

    def getGridEntries(self, title):
        return self.__verifyItem(self.n_grids, title).getEntries()

    def getGridSelectedCells(self, title):
        return self.__verifyItem(self.n_grids, title).getSelectedCells()

    def addGridRow(self, title, data):
        grid=self.__verifyItem(self.n_grids, title)
        grid.addRow(data)

    def confGrid(self, title, field, value):
        grid=self.__verifyItem(self.n_grids, title)
        kw={field:value}
        grid.config(**kw)

    ########################################

    @contextmanager
    def panedFrame(self, title, row=None, column=0, colspan=0, rowspan=0, sticky="NSEW"):
        reOpen = False
        try:
            pane = self.startPanedFrame(title, row, column, colspan, rowspan, sticky)
        except ItemLookupError:
            reOpen = True
            pane = self.openPane(title)
        try: yield pane
        finally:
            if reOpen:
                self.stopContainer()
            else:
                self.stopPanedFrame()

    def startPanedFrame(
            self,
            title,
            row=None,
            column=0,
            colspan=0,
            rowspan=0,
            sticky="NSEW"):
        self.startContainer(
            self.C_PANEDFRAME,
            title,
            row,
            column,
            colspan,
            rowspan,
            sticky)

    @contextmanager
    def panedFrameVertical(self, title, row=None, column=0, colspan=0, rowspan=0, sticky="NSEW"):
        reOpen = False
        try:
            pane = self.startPanedFrameVertical(title, row, column, colspan, rowspan, sticky)
        except ItemLookupError:
            reOpen = True
            pane = self.openPane(title)
        try: yield pane
        finally:
            if reOpen:
                self.stopContainer()
            else:
                self.stopPanedFrame()

    def startPanedFrameVertical(
            self,
            title,
            row=None,
            column=0,
            colspan=0,
            rowspan=0,
            sticky="NSEW"):
        self.startPanedFrame(title, row, column, colspan, rowspan, sticky)
        self.setPanedFrameVertical(title)

    @contextmanager
    def labelFrame(self, title, row=None, column=0, colspan=0, rowspan=0, sticky=W, hideTitle=False):
        try:
            lf = self.startLabelFrame(title, row, column, colspan, rowspan, sticky, hideTitle)
        except ItemLookupError:
            lf = self.openLabelFrame(title)
        try: yield lf
        finally: self.stopLabelFrame()

    # sticky is alignment inside frame
    # frame will be added as other widgets
    def startLabelFrame(self, title, row=None, column=0, colspan=0, rowspan=0, sticky=W, hideTitle=False):
        lf = self.startContainer(self.C_LABELFRAME, title, row, column, colspan, rowspan, sticky)
        if hideTitle:
            self.setLabelFrameTitle(title, "")

        return lf

    @contextmanager
    def toggleFrame(self, title, row=None, column=0, colspan=0, rowspan=0):
        try:
            tog = self.startToggleFrame(title, row, column, colspan, rowspan)
        except ItemLookupError:
            tog = self.openToggleFrame(title)
        try: yield tog
        finally: self.stopToggleFrame()

    ###### TOGGLE FRAMES #######
    def startToggleFrame(self, title, row=None, column=0, colspan=0, rowspan=0):
        return self.startContainer(self.C_TOGGLEFRAME, title, row, column, colspan, rowspan, sticky="new")

    def stopToggleFrame(self):
        if self.containerStack[-1]['type'] != self.C_TOGGLEFRAME:
            raise Exception("Can't stop a TOGGLEFRAME, currently in:",
                            self.containerStack[-1]['type'])
        self.containerStack[-1]['container'].stop()
        self.stopContainer()

    def toggleToggleFrame(self, title):
        toggle = self.__verifyItem(self.n_toggleFrames, title)
        toggle.toggle()

    def setToggleFrameText(self, title, newText):
        toggle = self.__verifyItem(self.n_toggleFrames, title)
        toggle.config(text=newText)

    def getToggleFrameState(self, title):
        toggle = self.__verifyItem(self.n_toggleFrames, title)
        return toggle.isShowing()

    @contextmanager
    def pagedWindow(self, title, row=None, column=0, colspan=0, rowspan=0):
        try:
            pw = self.startPagedWindow(title, row, column, colspan, rowspan)
        except ItemLookupError:
            pw = self.openPagedWindow(title)
        try: yield pw
        finally: self.stopPagedWindow()

    ###### PAGED WINDOWS #######
    def startPagedWindow(
            self,
            title,
            row=None,
            column=0,
            colspan=0,
            rowspan=0):
        self.startContainer(
            self.C_PAGEDWINDOW,
            title,
            row,
            column,
            colspan,
            rowspan,
            sticky="nsew")

    def setPagedWindowPage(self, title, page):
        pager = self.__verifyItem(self.n_pagedWindows, title)
        pager.showPage(page)

    def setPagedWindowButtonsTop(self, title, top=True):
        pager = self.__verifyItem(self.n_pagedWindows, title)
        pager.setNavPositionTop(top)

    def setPagedWindowButtons(self, title, buttons):
        pager = self.__verifyItem(self.n_pagedWindows, title)
        if not isinstance(buttons, list) or len(buttons) != 2:
            raise Exception(
                "You must provide a list of two strings fot setPagedWinowButtons()")
        pager.setPrevButton(buttons[0])
        pager.setNextButton(buttons[1])

    def setPagedWindowFunction(self, title, func):
        pager = self.__verifyItem(self.n_pagedWindows, title)
        command = self.MAKE_FUNC(func, title)
        pager.registerPageChangeEvent(command)

    def getPagedWindowPageNumber(self, title):
        pager = self.__verifyItem(self.n_pagedWindows, title)
        return pager.getPageNumber()

    def showPagedWindowPageNumber(self, title, show=True):
        pager = self.__verifyItem(self.n_pagedWindows, title)
        pager.showPageNumber(show)

    def showPagedWindowTitle(self, title, show=True):
        pager = self.__verifyItem(self.n_pagedWindows, title)
        pager.showTitle(show)

    def setPagedWindowTitle(self, title, pageTitle):
        pager = self.__verifyItem(self.n_pagedWindows, title)
        pager.setTitle(pageTitle)

    @contextmanager
    def page(self, windowTitle=None, pageNumber=None, sticky="nw"):
        if windowTitle is None:
            pg = self.startPage(sticky)
        else:
            pg = self.openPage(windowTitle, pageNumber)
        try: yield pg
        finally: self.stopPage()


    def startPage(self, sticky="nw"):
        if self.containerStack[-1]['type'] == self.C_PAGE:
            self.warn("You didn't STOP the previous PAGE")
            self.stopPage()
        elif self.containerStack[-1]['type'] != self.C_PAGEDWINDOW:
            raise Exception("Can't start a PAGE, currently in:",
                            self.containerStack[-1]['type'])

        self.containerStack[-1]['widgets'] = True

        # generate a page title
        pageNum = len(self.containerStack[-1]['container'].frames) + 1
        pageTitle = self.containerStack[-1]['title'] + "__" + str(pageNum)

        self.startContainer(
            self.C_PAGE,
            pageTitle,
            row=None,
            column=None,
            colspan=None,
            rowspan=None,
            sticky=sticky)

    def stopPage(self):
        # get a handle on the page object
        page = self.containerStack[-1]['container']

        if self.containerStack[-1]['type'] == self.C_PAGE:
            self.stopContainer()
        else:
            raise Exception("Can't stop PAGE, currently in:",
                            self.containerStack[-1]['type'])

        # call the stopPage function on the paged window
        if self.containerStack[-1]['type'] == self.C_PAGEDWINDOW:
            self.containerStack[-1]['container'].stopPage()
        else:
            # we need to find the container and call stopPage
            page.container.stopPage()

    def stopPagedWindow(self):
        if self.containerStack[-1]['type'] == self.C_PAGE:
            self.warn("You didn't STOP the previous PAGE")
            self.stopPage()

        if self.containerStack[-1]['type'] != self.C_PAGEDWINDOW:
            raise Exception("Can't stop a PAGEDWINDOW, currently in:",
                            self.containerStack[-1]['type'])
        self.stopContainer()

    ###### PAGED WINDOWS #######
    @contextmanager
    def scrollPane(self, title, row=None, column=0, colspan=0, rowspan=0, sticky="NSEW"):
        try:
            sp = self.startScrollPane(title, row, column, colspan, rowspan, sticky)
        except ItemLookupError:
            sp = self.openScrollPane(title)
        try: yield sp
        finally: self.stopScrollPane()


    def startScrollPane(
            self,
            title,
            row=None,
            column=0,
            colspan=0,
            rowspan=0,
            sticky="NSEW"):
        self.startContainer(
            self.C_SCROLLPANE,
            title,
            row,
            column,
            colspan,
            rowspan,
            sticky)

    # functions to stop the various containers
    def stopContainer(self): self.__removeContainer()

    def stopFrame(self):
        if self.containerStack[-1]['type'] != self.C_FRAME:
            raise Exception("Can't stop a FRAME, currently in:",
                            self.containerStack[-1]['type'])
        self.stopContainer()

    def stopLabelFrame(self):
        if self.containerStack[-1]['type'] != self.C_LABELFRAME:
            raise Exception("Can't stop a LABELFRAME, currently in:",
                            self.containerStack[-1]['type'])
        self.stopContainer()

    def stopPanedFrame(self):
        if self.containerStack[-1]['type'] == self.C_PANE:
            self.stopContainer()
        if self.containerStack[-1]['type'] != self.C_PANEDFRAME:
            raise Exception("Can't stop a PANEDFRAME, currently in:",
                            self.containerStack[-1]['type'])
        self.stopContainer()

    def stopScrollPane(self):
        if self.containerStack[-1]['type'] != self.C_SCROLLPANE:
            raise Exception("Can't stop a SCROLLPANE, currently in:",
                            self.containerStack[-1]['type'])
        self.stopContainer()

    def stopAllPanedFrames(self):
        while True:
            try:
                self.stopPanedFrame()
            except:
                break

    @contextmanager
    def frame(self, title, row=None, column=0, colspan=0, rowspan=0, sticky="NSEW"):
        try:
            fr = self.startFrame(title, row, column, colspan, rowspan, sticky)
        except ItemLookupError:
            fr = self.openFrame(title)
        try: yield fr
        finally: self.stopFrame()

    def startFrame(
            self,
            title,
            row=None,
            column=0,
            colspan=0,
            rowspan=0,
            sticky="NSEW"):
        return self.startContainer(
            self.C_FRAME,
            title,
            row,
            column,
            colspan,
            rowspan,
            sticky)

    ### SUB WINDOWS ###

    @contextmanager
    def subWindow(self, name, title=None, modal=False, blocking=False, transient=False, grouped=True):
        try:
            sw = self.startSubWindow(name, title, modal, blocking, transient, grouped)
        except ItemLookupError:
            sw = self.openSubWindow(name)
        try: yield sw
        finally: self.stopSubWindow()

    def startSubWindow(self, name, title=None, modal=False, blocking=False, transient=False, grouped=True):
        self.__verifyItem(self.n_subWindows, name, True)
        if title is None:
            title = name
        top = SubWindow()
        top.withdraw()
        top.locationSet = False
        top.modal = modal
        top.blocking = blocking
        top.title(title)
        top.protocol("WM_DELETE_WINDOW", self.MAKE_FUNC(self.hideSubWindow, name))
        top.win = self

        # have this respond to topLevel window style events
        if transient:
            top.transient(self.topLevel)

        # group this with the topLevel window
        if grouped:
            top.group(self.topLevel)

        if blocking:
            top.killLab = None

        self.n_subWindows[name] = top

        # now, add to top of stack
        self.__addContainer(name, self.C_SUBWINDOW, top, 0, 1, "")
        if self.winIcon is not None:
            self.setIcon(self.winIcon)

        return top

    def stopSubWindow(self):
        if self.containerStack[-1]['type'] == self.C_SUBWINDOW:
            self.stopContainer()
        else:
            raise Exception("Can't stop a SUBWINDOW, currently in:",
                            self.containerStack[-1]['type'])

    def setSubWindowLocation(self, title, x, y):
        tl = self.__verifyItem(self.n_subWindows, title)
        tl.geometry("+%d+%d" % (x, y))
        tl.locationSet = True

    # functions to show/hide/destroy SubWindows
    def showSubWindow(self, title):
        tl = self.__verifyItem(self.n_subWindows, title)
        if not tl.locationSet:
            self.CENTER(tl)
            tl.locationSet = True
        tl.deiconify()
        tl.config(takefocus=True)

        # stop other windows receiving events
        if tl.modal:
            tl.grab_set()

        tl.focus_set()
        self.__bringToFront(tl)

        # block here - wait for the subwindow to close
        if tl.blocking and tl.killLab is None:
            tl.killLab = Label(tl)
            self.topLevel.wait_window(tl.killLab)

        return tl

    def hideSubWindow(self, title):
        tl = self.__verifyItem(self.n_subWindows, title)
        theFunc = tl.stopFunction
        if theFunc is None or theFunc():
            tl.withdraw()
            if tl.blocking and tl.killLab is not None:
                tl.killLab.destroy()
                tl.killLab = None
            if tl.modal:
                tl.grab_release()
                self.topLevel.focus_set()

    def destroySubWindow(self, title):
        tl = self.__verifyItem(self.n_subWindows, title)
        theFunc = tl.stopFunction
        if theFunc is None or theFunc():
            if tl.blocking and tl.killLab is not None:
                tl.killLab.destroy()
                tl.killLab = None
            tl.withdraw()
            tl.grab_release()
            self.topLevel.focus_set()

            # get rid of all the kids!
            self.cleanseWidgets(tl)

    # function to destroy widget & all children
    # will also attempt to remove all trace from config dictionaries
    def cleanseWidgets(self, widget):
        for child in widget.winfo_children():
            self.cleanseWidgets(child)
        widgType = widget.__class__.__name__
        for k, v in self.WIDGETS.items():
            if widgType == v:
                widgets = self.__getItems(k)
                if self.destroyWidget(widget, widgets):
                    break
                break
        else:
            if widgType in ["Tab", "Page"]:
                pass # managed by container
            elif widgType in ["Pane", "ScrollPane", "PagedWindow", "SubWindow", "WidgetBox", "LabelBox", "ButtonBox"]:
                if widgType == "Pane": widgets = self.n_panes
                elif widgType == "ScrollPane": widgets = self.n_scrollPanes
                elif widgType == "PagedWindow": widgets = self.n_pagedWindows
                elif widgType == "SubWindow": widgets = self.n_subWindows
                elif widgType in ["WidgetBox", "LabelBox", "ButtonBox"]: widgets = self.n_frames

                if not self.destroyWidget(widget, widgets):
                    self.warn("Unable to destroy " + str(widgType) + ", during cleanse")
            else:
                self.warn("Unable to destroy " + str(widgType) + ", during cleanse")

    # function to loop through a config dict/list and remove matching object
    def destroyWidget(self, widget, widgets):
        if type(widgets) in [list, tuple]:
            for obj in widgets:
                if widget == obj:
                    obj.destroy()
                    widgets.remove(obj)
                    return True
        else:
            for name, obj in widgets.items():
                if widget == obj:
                    obj.destroy()
                    del widgets[name]
                    return True
        return False

    #### END SUB WINDOWS ####

    # make a PanedFrame align vertically
    def setPanedFrameVertical(self, window):
        pane = self.__verifyItem(self.n_panedFrames, window)
        pane.config(orient=VERTICAL)

    # function to set position of title for label frame
    def setLabelFrameTitle(self, title, newTitle):
        frame = self.__verifyItem(self.n_labelFrames, title)
        frame.config(text=newTitle)

    # functions to hide & show the main window
    def hide(self, btn=None):
        self.topLevel.withdraw()

    def show(self, btn=None):
        self.topLevel.deiconify()


#####################################
# warn when bad functions called...
#####################################
    def __getattr__(self, name):
        def handlerFunction(*args, **kwargs):
            self.warn(
                "Unknown function: <" + name +
                "> Check your spelling, do you need more camelCase?"
            )
        return handlerFunction

    def __setattr__(self, name, value):
        # would this create a new attribute?
        if self.built and not hasattr(self, name):
            raise AttributeError("Creating new attributes is not allowed!")
        if PYTHON2:
            object.__setattr__(self, name, value)
        else:
            super(__class__, self).__setattr__(name, value)

#####################################
# FUNCTION to add labels before a widget
#####################################
    # this will build a frame, with a label on the left hand side
    def __getLabelBox(self, title):
        self.__verifyItem(self.n_labels, title, True)

        # first, make a frame
        frame = LabelBox(self.getContainer())
        if not self.ttkFlag:
            frame.config(background=self.__getContainerBg())
        self.n_frames.append(frame)

        # if this is a big label, update the others to match...
        if len(title) > self.labWidth:
            self.labWidth = len(title)
            # loop through other labels and resize
#            for na in self.n_frameLabs:
#                self.n_frameLabs[na].config(width=self.labWidth)

        # next make the label
        if self.ttkFlag:
            lab = ttk.Label(frame)
        else:
            lab = Label(frame, background=self.__getContainerBg())
        frame.theLabel = lab
        lab.hidden = False
        lab.inContainer = True
        lab.config(
            text=title,
            anchor=W,
            justify=LEFT,
            font=self.labelFont,
        )
#            lab.config( width=self.labWidth)
        lab.DEFAULT_TEXT = title

        self.n_labels[title] = lab
        self.n_frameLabs[title] = lab

        # now put the label in the frame
        lab.pack(side=LEFT, fill=Y)
        #lab.grid( row=0, column=0, sticky=W )
        #Grid.columnconfigure(frame, 0, weight=1)
        #Grid.rowconfigure(frame, 0, weight=1)

        return frame

    # this is where we add the widget to the frame built above
    def __packLabelBox(self, frame, widget):
        widget.pack(side=LEFT, fill=BOTH, expand=True)
        widget.inContainer = True
        frame.theWidget = widget
        #widget.grid( row=0, column=1, sticky=W+E )
        #Grid.columnconfigure(frame, 1, weight=1)
        #Grid.rowconfigure(frame, 0, weight=1)

    # function to resize labels, if they are hidden or shown
    def __updateLabelBoxes(self, title):
        if len(title) >= self.labWidth:
            self.labWidth = 0
            # loop through other labels and resize
            for na in self.n_frameLabs:
                size = len(self.n_frameLabs[na].cget("text"))
                if not self.n_frameLabs[na].hidden and size > self.labWidth:
                    self.labWidth = size
            for na in self.n_frameLabs:
                self.n_frameLabs[na].config(width=self.labWidth)

#####################################
# FUNCTION for check boxes
#####################################
    def addCheckBox(self, title, row=None, column=0, colspan=0, rowspan=0, name=None):
        self.__verifyItem(self.n_cbs, title, True)
        var = IntVar(self.topLevel)
        if name is None:
            name = title

        if not self.ttkFlag:
            cb = Checkbutton(self.getContainer(), text=name, variable=var)
            cb.config(
                font=self.cbFont,
                background=self.__getContainerBg(),
                activebackground=self.__getContainerBg(),
                anchor=W)
        else:
            cb = ttk.Checkbutton(self.getContainer(), text=name, variable=var)

        cb.DEFAULT_TEXT = name
        cb.bind("<Button-1>", self.__grabFocus)
        self.n_cbs[title] = cb
        self.n_boxVars[title] = var
        self.__positionWidget(cb, row, column, colspan, rowspan, EW)
        return cb

    def addNamedCheckBox(self, name, title, row=None, column=0, colspan=0, rowspan=0):
        return self.addCheckBox(title, row, column, colspan, rowspan, name)

    def getCheckBox(self, title):
        bVar = self.__verifyItem(self.n_boxVars, title)
        if bVar.get() == 1:
            return True
        else:
            return False

    def getAllCheckBoxes(self):
        cbs = {}
        for k in self.n_cbs:
            cbs[k] = self.getCheckBox(k)
        return cbs

    def setCheckBox(self, title, ticked=True, callFunction=True):
        cb = self.__verifyItem(self.n_cbs, title)
        if ticked:
            cb.select()
        else:
            cb.deselect()
        # now call function
        if callFunction:
            if hasattr(cb, 'cmd'):
                cb.cmd()

    def clearAllCheckBoxes(self, callFunction=False):
        for cb in self.n_cbs:
            self.setCheckBox(cb, ticked=False, callFunction=callFunction)

#####################################
# FUNCTION for scales
#####################################

    def __buildScale(self, title, frame):
        self.__verifyItem(self.n_scales, title, True)
        var = DoubleVar(self.topLevel)
        if not self.ttkFlag:
            scale = ajScale(frame, increment=10, variable=var, repeatinterval=10, orient=HORIZONTAL)
            scale.config(digits=1, showvalue=False, highlightthickness=1)
        else:
            scale = ajScale(frame, increment=10, variable=var, repeatinterval=10, orient=HORIZONTAL)

        scale.bind("<Button-1>", self.__grabFocus, "+")
        scale.var = var
        scale.inContainer = False
        self.n_scales[title] = scale
        return scale

    def addScale(self, title, row=None, column=0, colspan=0, rowspan=0):
        scale = self.__buildScale(title, self.getContainer())
        self.__positionWidget(scale, row, column, colspan, rowspan)
        return scale

    def addLabelScale(self, title, row=None, column=0, colspan=0, rowspan=0):
        frame = self.__getLabelBox(title)
        scale = self.__buildScale(title, frame)
        self.__packLabelBox(frame, scale)
        self.__positionWidget(frame, row, column, colspan, rowspan)
        return scale

    def getScale(self, title):
        sc = self.__verifyItem(self.n_scales, title)
        return sc.get()

    def getAllScales(self):
        scales = {}
        for k in self.n_scales:
            scales[k] = self.getScale(k)
        return scales

    def setScale(self, title, pos, callFunction=True):
        sc = self.__verifyItem(self.n_scales, title)
        with PauseCallFunction(callFunction, sc):
            sc.set(pos)

    def clearAllScales(self, callFunction=False):
        for sc in self.n_scales:
            self.setScale(sc, self.n_scales[sc].cget("from"), callFunction=callFunction)

    def setScaleIncrement(self, title, increment):
        sc = self.__verifyItem(self.n_scales, title)
        sc.increment = increment

    def setScaleLength(self, title, length):
        sc = self.__verifyItem(self.n_scales, title)
        sc.config(sliderlength=length)

    # this will make the scale show interval numbers
    # set to 0 to remove
    def showScaleIntervals(self, title, intervals):
        sc = self.__verifyItem(self.n_scales, title)
        sc.config(tickinterval=intervals)

    # this will make the scale show its value
    def showScaleValue(self, title, show=True):
        sc = self.__verifyItem(self.n_scales, title)
        sc.config(showvalue=show)

    # change the orientation (Hor or Vert)
    def orientScaleHor(self, title, hor=True):
        self.warn(
            ".orientScaleHor() is deprecated. Please use .setScaleHorizontal() or .setScaleVertical()")
        sc = self.__verifyItem(self.n_scales, title)
        if hor:
            sc.config(orient=HORIZONTAL)
        else:
            sc.config(orient=VERTICAL)

    def setScaleVertical(self, title):
        sc = self.__verifyItem(self.n_scales, title)
        sc.config(orient=VERTICAL)

    def setScaleHorizontal(self, title):
        sc = self.__verifyItem(self.n_scales, title)
        sc.config(orient=HORIZONTAL)

    def setScaleRange(self, title, start, end, curr=None):
        if curr is None:
            curr = start
        sc = self.__verifyItem(self.n_scales, title)
        sc.config(from_=start, to=end)
        self.setScale(title, curr)

        # set the increment as 10%
        res = sc.cget("resolution")
        diff = int((((end - start)/res)/10)+0.99) # add 0.99 to round up...
        sc.increment = diff

#####################################
# FUNCTION for optionMenus
#####################################
    def __buildOptionBox(self, frame, title, options, kind="normal"):
        """ Internal wrapper, used for building OptionBoxes.
        It will use the kind to choose either a standard OptionBox or a TickOptionBox.
        ref: http://stackoverflow.com/questions/29019760/how-to-create-a-combobox-that-includes-checkbox-for-each-item

        :param frame: this should be a container, used as the parent for the OptionBox
        :param title: the key used to reference this OptionBox
        :param options: a list of values to put in the OptionBox, can be len 0
        :param kind: the style of OptionBox: notmal or ticks
        :returns: the created OptionBox
        :raises ItemLookupError: if the title is already in use
        """
        self.__verifyItem(self.n_options, title, True)

        # create a string var to hold selected item
        var = StringVar(self.topLevel)
        self.n_optionVars[title] = var

        maxSize, options = self.__configOptionBoxList(title, options, kind)

        if len(options) > 0 and kind == "normal":
            option = OptionMenu(frame, var, *options)
            var.set(options[0])
            option.kind = "normal"

        elif kind == "ticks":
            option = OptionMenu(frame, variable=var, value="")
            self.__buildTickOptionBox(title, option, options)
        else:
            option = OptionMenu(frame, var, [])
            option.kind = "normal"

        option.config(
            justify=LEFT,
            font=self.optionFont,
#            background=self.__getContainerBg(),
            highlightthickness=0,
            width=maxSize,
            takefocus=1)
        option.bind("<Button-1>", self.__grabFocus)

        # compare on windows & mac
        #option.config(highlightthickness=12, bd=0, highlightbackground=self.__getContainerBg())
        option.var = var
        option.maxSize = maxSize
        option.inContainer = False
        option.options = options

        option.DEFAULT_TEXT=""
        if options is not None:
            option.DEFAULT_TEXT='\n'.join(str(x) for x in options)

        # configure the drop-down too
        dropDown = option.nametowidget(option.menuname)
        dropDown.configure(font=self.optionFont)
#        dropDown.configure(background=self.__getContainerBg())

#        if self.platform == self.MAC:
#            option.config(highlightbackground=self.__getContainerBg())

        option.bind("<Tab>", self.__focusNextWindow)
        option.bind("<Shift-Tab>", self.__focusLastWindow)

        # add a right click menu
        self.__addRightClickMenu(option)

        # disable any separators
        self.__disableOptionBoxSeparators(option)

        # add to array list
        self.n_options[title] = option
        return option

    def __buildTickOptionBox(self, title, option, options):
        """ Internal wrapper, used for building TickOptionBoxes.
        Called by __buildOptionBox & changeOptionBox.
        Will add each of the options as a tick box, and use the title as a disabled header.

        :param title: the key used to reference this OptionBox
        :param option: an existing OptionBox that will be emptied & repopulated
        :param options: a list of values to put in the OptionBox, can be len 0
        :returns: None - the option param is modified
        :raises ItemLookupError: if the title can't be found
        """
        # delete any items - either the initial one when created, or any existing ones if changing
        option['menu'].delete(0, 'end')
        var = self.__verifyItem(self.n_optionVars, title, False)
        var.set(title)
        vals = {}
        for o in options:
            vals[o] = BooleanVar()
            option['menu'].add_checkbutton(
                label=o, onvalue=True, offvalue=False, variable=vals[o])
        self.n_optionTicks[title] = vals
        option.kind = "ticks"

    def addOptionBox(self, title, options, row=None, column=0, colspan=0, rowspan=0):
        """ Adds a new standard OptionBox.
        Simply calls internal function __buildOptionBox.

        :param title: the key used to reference this OptionBox
        :param options: a list of values to put in the OptionBox, can be len 0
        :returns: the created OptionBox
        :raises ItemLookupError: if the title is already in use
        """
        option = self.__buildOptionBox(self.getContainer(), title, options)
        self.__positionWidget(option, row, column, colspan, rowspan)
        return option

    def addLabelOptionBox(self, title, options, row=None, column=0, colspan=0, rowspan=0):
        """ Adds a new standard OptionBox, with a Label before it.
        Simply calls internal function __buildOptionBox, placing it in a LabelBox.

        :param title: the key used to reference this OptionBox and text for the Label
        :param options: a list of values to put in the OptionBox, can be len 0
        :returns: the created OptionBox (not the LabelBox)
        :raises ItemLookupError: if the title is already in use
        """
        frame = self.__getLabelBox(title)
        option = self.__buildOptionBox(frame, title, options)
        self.__packLabelBox(frame, option)
        self.__positionWidget(frame, row, column, colspan, rowspan)
        return option

    def addTickOptionBox(self, title, options, row=None, column=0, colspan=0, rowspan=0):
        """ Adds a new TickOptionBox.
        Simply calls internal function __buildOptionBox.

        :param title: the key used to reference this TickOptionBox
        :param options: a list of values to put in the TickOptionBox, can be len 0
        :returns: the created TickOptionBox
        :raises ItemLookupError: if the title is already in use
        """
        tick = self.__buildOptionBox(self.getContainer(), title, options, "ticks")
        self.__positionWidget(tick, row, column, colspan, rowspan)
        return tick

    def addLabelTickOptionBox(self, title, options, row=None, column=0, colspan=0, rowspan=0):
        """ Adds a new TickOptionBox, with a Label before it
        Simply calls internal function __buildOptionBox, placing it in a LabelBox

        :param title: the key used to reference this TickOptionBox, and text for the Label
        :param options: a list of values to put in the TickOptionBox, can be len 0
        :returns: the created TickOptionBox (not the LabelBox)
        :raises ItemLookupError: if the title is already in use
        """
        frame = self.__getLabelBox(title)
        tick = self.__buildOptionBox(frame, title, options, "ticks")
        self.__packLabelBox(frame, tick)
        self.__positionWidget(frame, row, column, colspan, rowspan)
        return tick

    def getOptionBox(self, title):
        """ Gets the selected item from the named OptionBox

        :param title: the OptionBox to check
        :returns: the selected item in an OptionBox or a dictionary of all items and their status for a TickOptionBox
        :raises ItemLookupError: if the title can't be found
        """
        box = self.__verifyItem(self.n_options, title)

        if box.kind == "ticks":
            val = self.n_optionTicks[title]
            retVal = {}
            for k, v in val.items():
                retVal[k] = bool(v.get())
            return retVal
        else:
            val = self.n_optionVars[title]
            val = val.get().strip()
            # set to None if it's a divider
            if val.startswith("-") or len(val) == 0:
                val = None
            return val

    def getAllOptionBoxes(self):
        """ Convenience function to get the selected items for all OptionBoxes in the GUI.

        :returns: a dictionary containing the result of calling getOptionBox for every OptionBox/TickOptionBox in the GUI
        """
        boxes = {}
        for k in self.n_options:
            boxes[k] = self.getOptionBox(k)
        return boxes

    def __disableOptionBoxSeparators(self, box):
        """ Loops through all items in box and if they start with a dash, disables them

        :param box: the OptionBox to process
        :returns: None
        """
        for pos, item in enumerate(box.options):
            if item.startswith("-"):
                box["menu"].entryconfigure(pos, state="disabled")
            else:
                box["menu"].entryconfigure(pos, state="normal")

    def __configOptionBoxList(self, title, options, kind):
        """ Tidies up the list provided when an OptionBox is created/changed

        :param title: the title for the OptionBox - only used by TickOptionBox to calculate max size
        :param options: the list to tidy
        :param kind: The type of option box (normal or ticks)
        :returns: a tuple containing the maxSize (width) and tidied list of items
        """

        # deal with a dict_keys object - messy!!!!
        if not isinstance(options, list):
            options = list(options)

        # make sure all options are strings
        options = [str(i) for i in options]

        # check for empty strings, replace first with message, remove rest
        found = False
        newOptions = []
        for pos, item in enumerate(options):
            if str(item).strip() == "":
                if not found:
                    newOptions.append("- options -")
                    found = True
            else:
                newOptions.append(item)

        options = newOptions

        # get the longest string length
        try:
            maxSize = len(str(max(options, key=len)))
        except:
            try:
                maxSize = len(str(max(options)))
            except:
                maxSize = 0

        # increase if ticks
        if kind == "ticks":
            if len(title) > maxSize:
                maxSize = len(title)

        # new bug?!? - doesn't fit anymore!
        if self.platform == self.MAC:
            maxSize += 3
        return maxSize, options

    def changeOptionBox(self, title, options, index=None, callFunction=False):
        """ Changes the entire contents of the named OptionBox
        ref: http://www.prasannatech.net/2009/06/tkinter-optionmenu-changing-choices.html

        :param title: the OptionBox to change
        :param options: the new values to put in the OptionBox
        :param index: an optional initial value to select
        :param callFunction: whether to generate an event to notify that the widget has changed
        :returns: None
        :raises ItemLookupError: if the title can't be found
        """
        # get the optionBox & associated var
        box = self.__verifyItem(self.n_options, title)

        # tidy up list and get max size
        maxSize, options = self.__configOptionBoxList(title, options, "normal")

        # warn if new options bigger
        if maxSize > box.maxSize:
            self.warn("The new options are wider then the old ones. " +
                      str(maxSize) + ">" + str(box.maxSize))

        if box.kind == "ticks":
            self.__buildTickOptionBox(title, box, options)
        else:
            # delete the current options
            box['menu'].delete(0, 'end')

            # add the new items
            for option in options:
                box["menu"].add_command(
                    label=option, command=lambda temp=option: box.setvar(
                        box.cget("textvariable"), value=temp))

            with PauseCallFunction(callFunction, box):
                box.var.set(options[0])

        box.options = options

        # disable any separators
        self.__disableOptionBoxSeparators(box)
        # select the specified option
        self.setOptionBox(title, index, callFunction=False, override=True)

    def deleteOptionBox(self, title, index):
        """ Deleted the specified item from the named OptionBox

        :param title: the OptionBox to change
        :param inde: the value to delete - either a numeric index, or the text of an item
        :returns: None
        :raises ItemLookupError: if the title can't be found
        """
        self.__verifyItem(self.n_optionVars, title)
        self.setOptionBox(title, index, value=None, override=True)

    def renameOptionBoxItem(self, title, item, newName=None, callFunction=False):
        """ Changes the text of the specified item in the named OptionBox
        :param title: the OptionBox to change
        :param item: the item to rename
        :param newName: the value to rename it with
        :param callFunction: whether to generate an event to notify that the widget has changed
        :returns: None
        :raises ItemLookupError: if the title can't be found
        """
        self.__verifyItem(self.n_optionVars, title)
        self.setOptionBox(title, item, value=newName, callFunction=callFunction)

    def clearOptionBox(self, title, callFunction=True):
        """ Deselects any items selected in the named OptionBox
        If a TickOptionBox, all items will be set to False (unticked)

        :param title: the OptionBox to change
        :param callFunction: whether to generate an event to notify that the widget has changed
        :returns: None
        :raises ItemLookupError: if the title can't be found
        """
        box = self.__verifyItem(self.n_options, title)
        if box.kind == "ticks":
            # loop through each tick, set it to False
            ticks = self.__verifyItem(self.n_optionTicks, title)
            for k in ticks:
                self.setOptionBox(title, k, False, callFunction=callFunction)
        else:
            self.setOptionBox(title, 0, callFunction=callFunction, override=True)

    def clearAllOptionBoxes(self, callFunction=False):
        """ Convenience function to clear all OptionBoxes in the GUI
        Will simply call clearOptionBox on each OptionBox/TickOptionBox

        :param callFunction: whether to generate an event to notify that the widget has changed
        :returns: None
        """
        for k in self.n_options:
            self.clearOptionBox(k, callFunction)

    def setOptionBox(self, title, index, value=True, callFunction=True, override=False):
        """ Main purpose is to select/deselect the item at the specified position
        But will also: delete an item if value is set to None or rename an item if value is set to a String

        :param title: the OptionBox to change
        :param index: the position or value of the item to select/delete
        :param value: determines what to do to the item: if set to None, will delete the item, else it sets the items state
        :param callFunction: whether to generate an event to notify that the widget has changed
        :param override: if set to True, allows a disabled item to be selected
        :returns: None
        :raises ItemLookupError: if the title can't be found
        """
        box = self.__verifyItem(self.n_options, title)

        if box.kind == "ticks":
            gui.debug("Updating tickOptionBox")
            ticks = self.__verifyItem(self.n_optionTicks, title)
            if index is None:
                gui.debug("Index empty - nothing to update")
                return
            elif index in ticks:
                gui.debug("Updating: " + str(index))

                tick = ticks[index]
                try:
                    index_num = box.options.index(index)
                except:
                    self.warn("Unknown tick: " + str(index) + " in OptionBox: " + str(title))
                    return

                with PauseCallFunction(callFunction, tick, useVar=False):
                    if value is None: # then we need to delete it
                        self.debug("Deleting tick: " + str(index) + " from OptionBox: " + str(title))
                        box['menu'].delete(index_num)
                        del(box.options[index_num])
                        del self.n_optionTicks[title][index]
                    elif isinstance(value, bool):
                        gui.debug("Updating tick: " + str(index) + " from OptionBox: " + str(title) + " to: " + str(value))
                        tick.set(value)
                    else:
                        gui.debug("Renaming tick: " + str(index) + " from OptionBox: " + str(title) + " to: " + str(value))
                        ticks = self.n_optionTicks[title]
                        ticks[value] = ticks.pop(index)
                        box.options[index_num] = value
                        self.changeOptionBox(title, box.options)
                        for tick in ticks:
                            self.n_optionTicks[title][tick].set(ticks[tick].get())
            else:
                if value is None:
                    self.warn("Unknown tick in deleteOptionBox: " + str(index) +
                            " in OptionBox: " + str(title))
                else:
                    self.warn("Unknown tick in setOptionBox: " + str(index) +
                            " in OptionBox: " + str(title))
        else:
            gui.debug("Updating regular optionBox: " + str(title) + " at: " + str(index) + " to: " + str(value))
            count = len(box.options)
            if count > 0:
                if index is None:
                    index = 0
                if not isinstance(index, int):
                    try:
                        index = box.options.index(index)
                    except:
                        if value is None:
                            self.warn("Unknown option in deleteOptionBox: " + str(index) +
                                    " in OptionBox: " + str(title))
                        else:
                            self.warn("Unknown option in setOptionBox: " + str(index) +
                                    " in OptionBox: " + str(title))
                        return

                gui.debug("--> index now: " + str(index))

                if index < 0 or index > count - 1:
                    self.warn("Invalid option: " + str(index) + ". Should be between 0 and " +
                            str(count - 1) + ".")
                else:
                    if value is None: # then we can delete it...
                        self.debug("Deleting option: " + str(index) + " from OptionBox: " + str(title))
                        box['menu'].delete(index)
                        del(box.options[index])
                        self.setOptionBox(title, 0, callFunction=False, override=override)
                    elif isinstance(value, bool):
                        gui.debug("Updating: " + str(index) + " from OptionBox: " + str(title) + " to: " + str(index))
                        with PauseCallFunction(callFunction, box):
                            if not box['menu'].invoke(index):
                                if override:
                                    self.debug("Setting OptionBox: " + str(title) +
                                            " to disabled option: " + str(index))
                                    box["menu"].entryconfigure(index, state="normal")
                                    box['menu'].invoke(index)
                                    box["menu"].entryconfigure(index, state="disabled")
                                else:
                                    self.warn("Unable to set disabled option: " + str(index) +
                                            " in OptionBox: " + str(title) + ". Try setting 'override=True'")
                            else:
                                gui.debug("Invoked item: " + str(index))
                    else:
                        gui.debug("Renaming: " + str(index) + " from OptionBox: " + str(title) + "to: " + str(value))
                        pos = box.options.index(self.n_optionVars[title].get())
                        box.options[index] = value
                        self.changeOptionBox(title, box.options, pos)

            else:
                self.__verifyItem(self.n_optionVars, title).set("")
                self.warn("No items to select from: " + title)

#####################################
# FUNCTION for GoogleMaps
#####################################

    def addGoogleMap(self, title, row=None, column=0, colspan=0, rowspan=0):
        self.__loadURL()
        if urlencode is False:
            raise Exception("Unable to load GoogleMaps - urlencode library not available")
        self.__loadTooltip()
        self.__verifyItem(self.n_maps, title, True)
        gMap = GoogleMap(self.getContainer(), self)
        self.__positionWidget(gMap, row, column, colspan, rowspan)
        self.n_maps[title] = gMap
        return gMap

    def setGoogleMapLocation(self, title, location):
        self.searchGoogleMap(title, location)

    def searchGoogleMap(self, title, location):
        gMap = self.__verifyItem(self.n_maps, title)
        gMap.changeLocation(location)

    def setGoogleMapTerrain(self, title, terrain):
        gMap = self.__verifyItem(self.n_maps, title)
        if terrain not in gMap.TERRAINS:
            raise Exception("Invalid terrain. Must be one of " + str(gMap.TERRAINS))
        gMap.changeTerrain(terrain)

    def setGoogleMapZoom(self, title, mod):
        self. zoomGoogleMap(title, mod)

    def zoomGoogleMap(self, title, mod):
        gMap = self.__verifyItem(self.n_maps, title)
        if mod in ["+", "-"]:
            gMap.zoom(mod)
        elif isinstance(mod, int) and 0 <= mod <= 22:
            gMap.setZoom(mod)

    def setGoogleMapSize(self, title, size):
        gMap = self.__verifyItem(self.n_maps, title)
        gMap.setSize(size)

    def setGoogleMapMarker(self, title, location):
        gMap = self.__verifyItem(self.n_maps, title)
        if len(location) == 0:
            gMap.removeMarkers()
        else:
            gMap.addMarker(location)

    def getGoogleMapZoom(self, title):
        return self.__verifyItem(self.n_maps, title).params["zoom"]

    def getGoogleMapTerrain(self, title):
        return self.__verifyItem(self.n_maps, title).params["maptype"].title()

    def getGoogleMapLocation(self, title):
        return self.__verifyItem(self.n_maps, title).params["center"]

    def getGoogleMapSize(self, title):
        return self.__verifyItem(self.n_maps, title).params["size"]

    def saveGoogleMap(self, title, fileLocation):
        gMap = self.__verifyItem(self.n_maps, title)
        return gMap.saveTile(fileLocation)
        

#####################################
# FUNCTION for matplotlib
#####################################
    def addPlot(
            self,
            title,
            t, s,
            row=None,
            column=0,
            colspan=0,
            rowspan=0):
        self.__verifyItem(self.n_plots, title, True)

        self.__loadMatplotlib()
        if FigureCanvasTkAgg is False:
            raise Exception("Unable to load MatPlotLib - plots not available")
        else:
            fig = Figure()

            axes = fig.add_subplot(111)
            axes.plot(t,s)

            canvas = FigureCanvasTkAgg(fig, self.getContainer())
            canvas.fig = fig
            canvas.axes = axes
            canvas.show()
    #        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
            canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

            self.__positionWidget(canvas.get_tk_widget(), row, column, colspan, rowspan)
            self.n_plots[title] = canvas
            return axes

    def refreshPlot(self, title):
        canvas = self.__verifyItem(self.n_plots, title)
        canvas.draw()

    def updatePlot(self, title, t, s, keepLabels=False):
        axes = self.__verifyItem(self.n_plots, title).axes

        if keepLabels:
            xLab = axes.get_xlabel()
            yLab = axes.get_ylabel()
            pTitle = axes.get_title()
            handles, legends = axes.get_legend_handles_labels()

        axes.clear()
        axes.plot(t, s)

        if keepLabels:
            axes.set_xlabel(xLab)
            axes.set_ylabel(yLab)
            axes.set_title(pTitle)
            axes.legend(handles, legends)

        self.refreshPlot(title)
        return axes


#####################################
# FUNCTION to manage Properties Widgets
#####################################
    def addProperties(
            self,
            title,
            values=None,
            row=None,
            column=0,
            colspan=0,
            rowspan=0):
        self.__verifyItem(self.n_props, title, True)
        haveTitle = True
        if self.containerStack[-1]['type'] == self.C_TOGGLEFRAME:
            self.containerStack[-1]['sticky'] = "ew"
            haveTitle = False

        props = Properties(
            self.getContainer(),
            title,
            values,
            haveTitle,
            font=self.propertiesFont,
            background=self.__getContainerBg())
        self.__positionWidget(props, row, column, colspan, rowspan)
        self.n_props[title] = props
        return props

    def getProperties(self, title):
        props = self.__verifyItem(self.n_props, title)
        return props.getProperties()

    def getAllProperties(self):
        props = {}
        for k in self.n_props:
            props[k] = self.getProperties(k)
        return props

    def getProperty(self, title, prop):
        props = self.__verifyItem(self.n_props, title)
        return props.getProperty(prop)

    def setProperty(self, title, prop, value=False, callFunction=True):
        props = self.__verifyItem(self.n_props, title)
        props.addProperty(prop, value, callFunction=callFunction)

    def setProperties(self, title, props, callFunction=True):
        p = self.__verifyItem(self.n_props, title)
        p.addProperties(props, callFunction=callFunction)

    def deleteProperty(self, title, prop):
        props = self.__verifyItem(self.n_props, title)
        props.addProperty(prop, None, callFunction=False)

    def setPropertyText(self, title, prop, newText=None):
        props = self.__verifyItem(self.n_props, title)
        props.renameProperty(prop, newText)

    def clearProperties(self, title, callFunction=True):
        self.__verifyItem(self.n_props, title).clearProperties(callFunction)

    def clearAllProperties(self, callFunction=False):
        props = {}
        for k in self.n_props:
            self.clearProperties(k, callFunction)

    def resetProperties(self, title, callFunction=True):
        self.__verifyItem(self.n_props, title).resetProperties(callFunction)

    def resetAllProperties(self, callFunction=False):
        props = {}
        for k in self.n_props:
            self.resetProperties(k, callFunction)

#####################################
# FUNCTION to add spin boxes
#####################################
    def __buildSpinBox(self, frame, title, vals):
        self.__verifyItem(self.n_spins, title, True)
        if type(vals) not in [list, tuple]:
            raise Exception(
                "Can't create SpinBox " +
                title +
                ". Invalid values: " +
                str(vals))

        spin = Spinbox(frame)
        spin.inContainer = False
        spin.isRange = False
        spin.config(font=self.entryFont, highlightthickness=0)

# adds bg colour under spinners
#        if self.platform == self.MAC:
#              spin.config(highlightbackground=self.__getContainerBg())

        spin.bind("<Tab>", self.__focusNextWindow)
        spin.bind("<Shift-Tab>", self.__focusLastWindow)

        # store the vals in DEFAULT_TEXT
        spin.DEFAULT_TEXT=""
        if vals is not None:
            spin.DEFAULT_TEXT='\n'.join(str(x) for x in vals)

        # make sure it's a list
        # reverse it, so the spin box functions properly
        vals = list(vals)
        vals.reverse()
        vals = tuple(vals)
        spin.config(values=vals)

        # prevent invalid entries
        if self.validateSpinBox is None:
            self.validateSpinBox = (
                self.containerStack[0]['container'].register(
                    self.__validateSpinBox), '%P', '%W')

        spin.config(validate='all', validatecommand=self.validateSpinBox)

        self.n_spins[title] = spin
        return spin

    def __addSpinBox(
            self,
            title,
            values,
            row=None,
            column=0,
            colspan=0,
            rowspan=0):
        spin = self.__buildSpinBox(self.getContainer(), title, values)
        self.__positionWidget(spin, row, column, colspan, rowspan)
        self.setSpinBoxPos(title, 0)
        return spin

    def addSpinBox(
            self,
            title,
            values,
            row=None,
            column=0,
            colspan=0,
            rowspan=0):
        return self.__addSpinBox(title, values, row, column, colspan, rowspan)

    def addLabelSpinBox(
            self,
            title,
            values,
            row=None,
            column=0,
            colspan=0,
            rowspan=0):
        frame = self.__getLabelBox(title)
        spin = self.__buildSpinBox(frame, title, values)
        self.__packLabelBox(frame, spin)
        self.__positionWidget(frame, row, column, colspan, rowspan)
        self.setSpinBoxPos(title, 0)
        return spin

    def addSpinBoxRange(
            self,
            title,
            fromVal,
            toVal,
            row=None,
            column=0,
            colspan=0,
            rowspan=0):
        vals = list(range(fromVal, toVal + 1))
        spin = self.__addSpinBox(title, vals, row, column, colspan, rowspan)
        spin.isRange = True
        return spin

    def addLabelSpinBoxRange(
            self,
            title,
            fromVal,
            toVal,
            row=None,
            column=0,
            colspan=0,
            rowspan=0):
        vals = list(range(fromVal, toVal + 1))
        spin = self.addLabelSpinBox(title, vals, row, column, colspan, rowspan)
        spin.isRange = True
        return spin

    def getSpinBox(self, title):
        spin = self.__verifyItem(self.n_spins, title)
        return spin.get()

    def getAllSpinBoxes(self):
        boxes = {}
        for k in self.n_spins:
            boxes[k] = self.getSpinBox(k)
        return boxes

    # validates that an item in the named spinbox starts with the user_input
    def __validateSpinBox(self, user_input, widget_name):
        spin = self.containerStack[0]['container'].nametowidget(widget_name)

        vals = spin.cget("values")  # .split()
        vals = self.__getSpinBoxValsAsList(vals)
        for i in vals:
            if i.startswith(user_input):
                return True

        self.containerStack[0]['container'].bell()
        return False

    # expects a valid spin box widget, and a valid value
    def __setSpinBoxVal(self, spin, val, callFunction=True):
        var = StringVar(self.topLevel)
        var.set(val)
        spin.config(textvariable=var)
        # now call function
        if callFunction:
            if hasattr(spin, 'cmd'):
                spin.cmd()

    # is it going to be a hash or list??
    def __getSpinBoxValsAsList(self, vals):
        vals.replace("{", "")
        vals.replace("}", "")
#        if "{" in vals:
#            vals = vals[1:-1]
#            vals = vals.split("} {")
#        else:
        vals = vals.split()
        return vals

    def setSpinBox(self, title, value, callFunction=True):
        spin = self.__verifyItem(self.n_spins, title)
        vals = spin.cget("values")  # .split()
        vals = self.__getSpinBoxValsAsList(vals)
        val = str(value)
        if val not in vals:
            raise Exception( "Invalid value: " + val + ". Not in SpinBox: " +
                        title + "=" + str(vals))
        self.__setSpinBoxVal(spin, val, callFunction)

    def clearAllSpinBoxes(self, callFunction=False):
        for sb in self.n_spins:
            self.setSpinBoxPos(sb, 0, callFunction=callFunction)

    def setSpinBoxPos(self, title, pos, callFunction=True):
        spin = self.__verifyItem(self.n_spins, title)
        vals = spin.cget("values")  # .split()
        vals = self.__getSpinBoxValsAsList(vals)
        pos = int(pos)
        if pos < 0 or pos >= len(vals):
            raise Exception( "Invalid position: " + str(pos) + ". No position in SpinBox: " +
                        title + "=" + str(vals))
        pos = len(vals) - 1 - pos
        val = vals[pos]
        self.__setSpinBoxVal(spin, val, callFunction)

    def changeSpinBox(self, title, vals):
        spin = self.__verifyItem(self.n_spins, title)
        if spin.isRange:
            self.warn("Can't convert " + title + " RangeSpinBox to SpinBox")
        else:
            vals = list(vals)
            vals.reverse()
            vals = tuple(vals)
            spin.config(values=vals)
            self.setSpinBoxPos(title, 0)

#####################################
# FUNCTION to add images
#####################################
    # looks up label containing image
    def __animateImage(self, title, firstTime=False):
        if not self.alive: return
        try:
            lab = self.__verifyItem(self.n_images, title)
        except ItemLookupError:
            # image destroyed...
            try: del self.n_imageAnimationIds[title]
            except: pass
            return
        if not lab.image.animating:
            del self.n_imageAnimationIds[title]
            return
        if firstTime and lab.image.alreadyAnimated:
            return

        lab.image.alreadyAnimated = True
        try:
            if lab.image.cached:
                pic = lab.image.pics[lab.image.anim_pos]
            else:
                pic = PhotoImage(file=lab.image.path,
                                 format="gif - {0}".format(lab.image.anim_pos))
                lab.image.pics.append(pic)
            lab.image.anim_pos += 1
            lab.config(image=pic)
            anim_id = self.topLevel.after(
                lab.image.anim_speed,
                self.__animateImage,
                title)
            self.n_imageAnimationIds[title] = anim_id
        except Exception as e:
            # will be thrown when we reach end of anim images
            lab.image.anim_pos = 0
            lab.image.cached = True
            self.__animateImage(title)

    def __preloadAnimatedImage(self, img):
        if not self.alive: return
        if img.cached:
            return
        try:
            pic = PhotoImage(file=img.path,
                             format="gif - {0}".format(img.anim_pos))
            img.pics.append(pic)
            img.anim_pos += 1
            self.preloadAnimatedImageId = self.topLevel.after(
                0, self.__preloadAnimatedImage, img)
        # when all frames have been processed
        except TclError as e:
            # expected - when all images cached
            img.anim_pos = 0
            img.cached = True

    def __configAnimatedImage(self, img):
        img.alreadyAnimated = False
        img.isAnimated = True
        img.pics = []
        img.cached = False
        img.anim_pos = 0
        img.anim_speed = 150
        img.animating = True

    # simple way to check if image is animated
    def __checkIsAnimated(self, name):
        if imghdr.what(name) == "gif":
            try:
                PhotoImage(file=name, format="gif - 1")
                return True
            except:
                pass
        return False

    def setAnimationSpeed(self, name, speed):
        img = self.__verifyItem(self.n_images, name).image
        if speed < 1:
            speed = 1
            self.warn("Setting " + str(name) + " speed to 1. Minimum animation speed is 1.")
        img.anim_speed = speed

    def stopAnimation(self, name):
        img = self.__verifyItem(self.n_images, name).image
        img.animating = False

    def startAnimation(self, name):
        img = self.__verifyItem(self.n_images, name).image
        if not img.animating:
            img.animating = True
            anim_id = self.topLevel.after(img.anim_speed, self.__animateImage, name)
            self.n_imageAnimationIds[name] = anim_id

    def addAnimatedImage(
            self,
            name,
            imageFile,
            row=None,
            column=0,
            colspan=0,
            rowspan=0):
        self.warn("addAnimatedImage() is now deprecated - use addImage()")
        return self.addImage(name, imageFile, row, column, colspan, rowspan)

    # function to set an alternative image, when a mouse goes over
    def setImageMouseOver(self, title, overImg):
        lab = self.__verifyItem(self.n_images, title)

        # first check over image & cache it
        fullPath = self.getImagePath(overImg)
        self.topLevel.after(0, self.__getImage, fullPath)

        leaveImg = lab.image.path
        lab.bind("<Leave>", lambda e: self.setImage(title, leaveImg, True))
        lab.bind("<Enter>", lambda e: self.setImage(title, fullPath, True))
        lab.hasMouseOver = True

    # function to set an image location
    def setImageLocation(self, location):
        if os.path.isdir(location):
            self.userImages = location
        else:
            raise Exception("Invalid image location: " + location)

    # get the full path of an image (including image folder)
    def getImagePath(self, imagePath):
        if imagePath is None:
            return None

        if self.userImages is not None:
            imagePath = os.path.join(self.userImages, imagePath)

        absPath = os.path.abspath(imagePath)
        return absPath

    # function to see if an image has changed
    def hasImageChanged(self, originalImage, newImage):
        newAbsImage = self.getImagePath(newImage)

        if originalImage is None:
            return True

        # filename has changed
        if originalImage.path != newAbsImage:
            return True

        # modification time has changed
        if originalImage.modTime != os.path.getmtime(newAbsImage):
            return True

        # no changes
        return False

    # function to remove image objects form cache
    def clearImageCache(self):
        self.n_imageCache = {}

    # internal function to build an image function from a string
    def __getImageData(self, imageData, fmt="gif"):
        if fmt=="png":
            self.__importPngimagetk()
            if PngImageTk is False:
                raise Exception("TKINTERPNG library not found, PNG files not supported: imageData")
            if sys.version_info >= (2, 7):
                self.warn(
                    "Image processing for .PNGs is slow. .GIF is the recommended format")
#                png = PngImageTk(imagePath)
#                png.convert()
#                photo = png.image
            else:
                raise Exception("PNG images only supported in python 3: imageData")

        elif fmt == "gif":
            imgObj = PhotoImage(data=imageData)

        else:
            # expect we already have a PhotoImage object, for example created by PIL
            imgObj = imageData


        imgObj.path = None
        imgObj.modTime = datetime.datetime.now()
        imgObj.isAnimated = False
        imgObj.animating = False
        return imgObj

    # internal function to check/build image object
    def __getImage(self, imagePath, checkCache=True, addToCache=True):
        if imagePath is None:
            return None

        # get the full image path
        imagePath = self.getImagePath(imagePath)

        # if we're caching, and we have a non-None entry in the cache - get it...
        photo = None
        if checkCache and imagePath in self.n_imageCache and self.n_imageCache[imagePath] is not None:
            photo = self.n_imageCache[imagePath]

        # if the image hasn't changed, use the cache
        if not self.hasImageChanged(photo, imagePath):
            pass
        # else load a new one
        elif os.path.isfile(imagePath):
            if os.access(imagePath, os.R_OK):
                imgType = imghdr.what(imagePath)
                if imgType is None:
                    raise Exception( "Invalid file: " + imagePath + " is not a valid image")
                elif not imagePath.lower().endswith(imgType) and not (
                        imgType == "jpeg" and imagePath.lower().endswith("jpg")):
                        # the image has been saved with the wrong extension
                    raise Exception(
                        "Invalid image extension: " +
                        imagePath +
                        " should be a ." +
                        imgType)
                elif imagePath.lower().endswith('.gif'):
                    photo = PhotoImage(file=imagePath)
                elif imagePath.lower().endswith('.ppm') or imagePath.lower().endswith('.pgm'):
                    photo = PhotoImage(file=imagePath)
                elif imagePath.lower().endswith('jpg') or imagePath.lower().endswith('jpeg'):
                    self.warn(
                        "Image processing for .JPGs is slow. .GIF is the recommended format")
                    photo = self.convertJpgToBmp(imagePath)
                elif imagePath.lower().endswith('.png'):
                    # known issue here, some PNGs lack IDAT chunks
                    # also, PNGs seem broken on python<3, maybe around the map
                    # function used to generate pixel maps
                    self.__importPngimagetk()
                    if PngImageTk is False:
                        raise Exception(
                            "TKINTERPNG library not found, PNG files not supported: " + imagePath)
                    if sys.version_info >= (2, 7):
                        self.warn(
                            "Image processing for .PNGs is slow. .GIF is the recommended format")
                        png = PngImageTk(imagePath)
                        png.convert()
                        photo = png.image
                    else:
                        raise Exception("PNG images only supported in python 3: " + imagePath)
                else:
                    raise Exception("Invalid image type: " + imagePath)
            else:
                raise Exception("Can't read image: " + imagePath)
        else:
            raise Exception("Image " + imagePath + " does not exist")

        # store the full poath to this image
        photo.path = imagePath
        # store the modification time
        photo.modTime = os.path.getmtime(imagePath)

        # sort out if it's an animated images
        if self.__checkIsAnimated(imagePath):
            self.__configAnimatedImage(photo)
            self.__preloadAnimatedImage(photo)
        else:
            photo.isAnimated = False
            photo.animating = False
            if addToCache:
                self.n_imageCache[imagePath] = photo

        return photo

    def getImageDimensions(self, name):
        img = self.__verifyItem(self.n_images, name).image
        return img.width(), img.height()

    # force replace the current image, with a new one
    def reloadImage(self, name, imageFile):
        label = self.__verifyItem(self.n_images, name)
        image = self.__getImage(imageFile, False)
        self.__populateImage(name, image)

    def reloadImageData(self, name, imageData, fmt="gif"):
        self.setImageData(name, imageData, fmt)

    def setImageData(self, name, imageData, fmt="gif"):
        label = self.__verifyItem(self.n_images, name)
        image = self.__getImageData(imageData, fmt=fmt)
        self.__populateImage(name, image)

    # replace the current image, with a new one
    def setImage(self, name, imageFile, internal=False):
        label = self.__verifyItem(self.n_images, name)
        imageFile = self.getImagePath(imageFile)

        # only set the image if it's different
        if label.image.path == imageFile:
            self.warn("Not updating " + str(name) + ", " + str(imageFile) + " hasn't changed." )
            return
        elif imageFile is None:
            return
        else:
            image = self.__getImage(imageFile)
            self.__populateImage(name, image, internal)

    # internal function to update the image in a label
    def __populateImage(self, name, image, internal=False):
        label = self.__verifyItem(self.n_images, name)

        label.image.animating = False
        label.config(image=image)
        label.config(
            anchor=CENTER,
            font=self.labelFont,
            background=self.__getContainerBg())
        label.image = image  # keep a reference!

        if image.isAnimated:
            anim_id = self.topLevel.after(
                image.anim_speed + 100,
                self.__animateImage,
                name,
                True)
            self.n_imageAnimationIds[name] = anim_id

        if not internal and label.hasMouseOver:
            leaveImg = label.image.path
            label.bind("<Leave>", lambda e: self.setImage(name, leaveImg, True))

        # removed - keep the label the same size, and crop images
        #h = image.height()
        #w = image.width()
        #label.config(height=h, width=w)
        self.topLevel.update_idletasks()

    # function to configure an image map
    def setImageMap(self, name, func, coords):
        img = self.__verifyItem(self.n_images, name)

        rectangles = []
        if len(coords) > 0:
            for k, v in coords.items():
                rect = AJRectangle(k, Point(v[0], v[1]), v[2]-v[0], v[3]-v[1])
                rectangles.append(rect)

        img.MAP_COORDS = rectangles
        img.MAP_FUNC = func
        img.bind("<Button-1>", lambda e: self.__imageMap(name, e), add="+")

    # function called when an image map is clicked
    def __imageMap(self, name, event):
        img = self.__verifyItem(self.n_images, name)
        for rect in img.MAP_COORDS:
            if rect.contains(Point(event.x, event.y)):
                img.MAP_FUNC(rect.name)
                return

        img.MAP_FUNC("UNKNOWN: " + str(event.x) + ", " + str(event.y))

    # must be GIF or PNG
    def addImage(self, name, imageFile, row=None, column=0, colspan=0, rowspan=0):
        self.__verifyItem(self.n_images, name, True)
        imgObj = self.__getImage(imageFile)
        self.__addImageObj(name, imgObj, row, column, colspan, rowspan)
        self.n_images[name].hasMouseOver = False
        return imgObj

    # uses built-in icons to add an image
    def addIcon(self, name, iconName, row=None, column=0, colspan=0, rowspan=0):
        icon = os.path.join(self.icon_path, iconName.lower()+".png")
        with PauseLogger():
            return self.addImage(name, icon, row, column, colspan, rowspan)

    # load image from base-64 encoded GIF
    # use base64 module to convert binary data to base64
    def addImageData(self, name, imageData, row=None, column=0, colspan=0, rowspan=0, fmt="gif"):
        self.__verifyItem(self.n_images, name, True)
        imgObj = self.__getImageData(imageData, fmt)
        self.__addImageObj(name, imgObj, row, column, colspan, rowspan)
        self.n_images[name].hasMouseOver = False
        return imgObj

    def __addImageObj(self, name, img, row=None, column=0, colspan=0, rowspan=0):
        label = Label(self.getContainer())
        label.config(
            anchor=CENTER,
            font=self.labelFont,
            background=self.__getContainerBg())
        label.config(image=img)
        label.image = img  # keep a reference!

        if img is not None:
            h = img.height()
            w = img.width()
            label.config(height=h, width=w)

        self.n_images[name] = label
        self.__positionWidget(label, row, column, colspan, rowspan)
        if img.isAnimated:
            anim_id = self.topLevel.after(
                img.anim_speed, self.__animateImage, name, True)
            self.n_imageAnimationIds[name] = anim_id

    def setImageSize(self, name, width, height):
        img = self.__verifyItem(self.n_images, name)
        img.config(height=height, width=width)

#      def rotateImage(self, name, image):
#            img = self.__verifyItem(self.n_images, name)

    # if +ve then grow, else shrink...
    def zoomImage(self, name, x, y=''):
        if x <= 0:
            self.shrinkImage(name, x * -1, y * -1)
        else:
            self.growImage(name, x, y)

    # get every nth pixel (must be an integer)
    # 0 will return an empty image, 1 will return the image, 2 will be 1/2 the
    # size ...
    def shrinkImage(self, name, x, y=''):
        img = self.__verifyItem(self.n_images, name)
        image = img.image.subsample(x, y)

        img.config(image=image)
        img.config(
            anchor=CENTER,
            font=self.labelFont,
            background=self.__getContainerBg())
        img.modImage = image  # keep a reference!
        img.config(width=image.width(), height=image.height())

    # get every nth pixel (must be an integer)
    # 0 won't work, 1 will return the original size
    def growImage(self, name, x, y=''):
        label = self.__verifyItem(self.n_images, name)
        image = label.image.zoom(x, y)

        label.config(image=image)
        label.config(
            anchor=CENTER,
            font=self.labelFont,
            background=self.__getContainerBg())
        label.modImage = image  # keep a reference!
        label.config(width=image.width(), height=image.height())

    def convertJpgToBmp(self, image):
        self.__loadNanojpeg()
        if nanojpeg is False:
            raise Exception(
                "nanojpeg library not found, unable to display jpeg files: " + image)
        elif sys.version_info < (2, 7):
            raise Exception(
                "JPG images only supported in python 2.7+: " + image)
        else:
            # read the image into an array of bytes
            with open(image, 'rb') as inFile:
                buf = array.array(str('B'), inFile.read())

            # init the translator, and decode the array of bytes
            nanojpeg.njInit()
            nanojpeg.njDecode(buf, len(buf))

            # determine a file name & type
            if nanojpeg.njIsColor():
#                fileName = image.split('.jpg', 1)[0] + '.ppm'
                param = 6
            else:
#                fileName = image.split('.jpg', 1)[0] + '.pgm'
#                fileName = "test3.pgm"
                param = 5

            # create a string, starting with the header
            val = "P%d\n%d %d\n255\n" % (
                param, nanojpeg.njGetWidth(), nanojpeg.njGetHeight())
            # append the bytes, converted to chars
            val = str(val) + str('').join(map(chr, nanojpeg.njGetImage()))

            # release any stuff
            nanojpeg.njDone()

            photo = PhotoImage(data=val)
            return photo

            # write the chars to a new file, if python3 we need to encode them first
#            with open(fileName, "wb") as outFile:
#                  if sys.version_info[0] == 2: outFile.write(val)
#                  else: outFile.write(val.encode('ISO-8859-1'))
#
#            return fileName

    # function to set a background image
    # make sure this is done before everything else, otherwise it will cover
    # other widgets
    def setBgImage(self, image):
        image = self.__getImage(image, False, False)  # make sure it's not using the cache
        # self.containerStack[0]['container'].config(image=image) # window as a
        # label doesn't work...
        self.bgLabel.config(image=image)
        self.containerStack[0]['container'].image = image  # keep a reference!

    def removeBgImage(self):
        self.bgLabel.config(image="")
        # self.containerStack[0]['container'].config(image=None) # window as a
        # label doesn't work...
        # remove the reference - shouldn't be cached
        self.containerStack[0]['container'].image = None

    def resizeBgImage(self):
        if self.containerStack[0]['container'].image is None:
            return
        else:
            pass

#####################################
# FUNCTION to play sounds
#####################################
    # function to set a sound location
    def setSoundLocation(self, location):
        if os.path.isdir(location):
            self.userSounds = location
        else:
            raise Exception("Invalid sound location: " + location)

    # internal function to manage sound availability
    def __soundWrap(self, sound, isFile=False, repeat=False, wait=False):
        self.__loadWinsound()
        if self.platform == self.WINDOWS and winsound is not False:
            sound = self.__translateSound(sound)
            if self.userSounds is not None and sound is not None:
                sound = os.path.join(self.userSounds, sound)
            if isFile:
                if os.path.isfile(sound) is False:
                    raise Exception("Can't find sound: " + sound)
                if not sound.lower().endswith('.wav'):
                    raise Exception("Invalid sound format: " + sound)
                kind = winsound.SND_FILENAME
                if not wait:
                    kind = kind | winsound.SND_ASYNC
            else:
                if sound is None:
                    kind = winsound.SND_FILENAME
                else:
                    kind = winsound.SND_ALIAS
                    if not wait:
                        kind = kind | winsound.SND_ASYNC

            if repeat:
                kind = kind | winsound.SND_LOOP

            winsound.PlaySound(sound, kind)
        else:
            # sound not available at this time
            raise Exception(
                "Sound not supported on this platform: " +
                platform())

    def playSound(self, sound, wait=False):
        self.__soundWrap(sound, True, False, wait)

    def stopSound(self):
        self.__soundWrap(None)

    def loopSound(self, sound):
        self.__soundWrap(sound, True, True)

    def soundError(self):
        self.__soundWrap("SystemHand")

    def soundWarning(self):
        self.__soundWrap("SystemAsterisk")

    def bell(self):
        self.containerStack[0]['container'].bell()

    def playNote(self, note, duration=200):
        self.__loadWinsound()
        if self.platform == self.WINDOWS and winsound is not False:
            try:
                if isinstance(note, str):
                    freq = self.NOTES[note.lower()]
                else:
                    freq = note
            except KeyError:
                raise Exception("Error: cannot play note - " + note)
            try:
                if isinstance(duration, str):
                    length = self.DURATIONS[duration.upper()]
                else:
                    length = duration
            except KeyError:
                raise Exception("Error: cannot play duration - " + duration)

            try:
                winsound.Beep(freq, length)
            except RuntimeError:
                raise Exception(
                    "Sound not available on this platform: " +
                    platform())
        else:
            # sound not available at this time
            raise Exception(
                "Sound not supported on this platform: " +
                platform())

#####################################
# FUNCTION for radio buttons
#####################################
    def addRadioButton(
            self,
            title,
            name,
            row=None,
            column=0,
            colspan=0,
            rowspan=0):
        var = None
        newRb = False
        # title - is the grouper
        # so, if we already have an entry in n_rbVars - get it
        if (title in self.n_rbVars):
            var = self.n_rbVars[title]
            # also get the list of rbVals
            vals = self.n_rbVals[title]
            # and if we already have the new item in that list - reject it
            if name in vals:
                raise Exception(
                    "Invalid radio button: " +
                    name +
                    " already exists")
            # otherwise - append it to the list of vals
            else:
                vals.append(name)
        else:
            # if this is a new grouper - set it all up
            var = StringVar(self.topLevel)
            vals = [name]
            self.n_rbVars[title] = var
            self.n_rbVals[title] = vals
            newRb = True

        # finally, create the actual RadioButton
        if not self.ttkFlag:
            rb = Radiobutton(self.getContainer(), text=name, variable=var, value=name)
            rb.config(
                anchor=W,
                background=self.__getContainerBg(),
                activebackground=self.__getContainerBg(),
                font=self.rbFont,
                indicatoron=1
            )
        else:
            rb = ttk.Radiobutton(self.getContainer(), text=name, variable=var, value=name)

        rb.bind("<Button-1>", self.__grabFocus)
        rb.DEFAULT_TEXT = name

        # either append to existing widget list
        if (title in self.n_rbs):
            self.n_rbs[title].append(rb)
        # or create a new one
        else:
            self.n_rbs[title] = [rb]
        #rb.bind("<Tab>", self.__focusNextWindow)
        #rb.bind("<Shift-Tab>", self.__focusLastWindow)

        # and select it, if it's the first item in the list
        if newRb:
            rb.select() if not self.ttkFlag else rb.invoke()
            var.startVal = name # so we can reset it...
        self.__positionWidget(rb, row, column, colspan, rowspan, EW)
        return rb

    def getRadioButton(self, title):
        var = self.__verifyItem(self.n_rbVars, title)
        return var.get()

    def getAllRadioButtons(self):
        rbs = {}
        for k in self.n_rbs:
            rbs[k] = self.getRadioButton(k)
        return rbs

    def setRadioButton(self, title, value, callFunction=True):
        vals = self.__verifyItem(self.n_rbVals, title)
        if value not in vals:
            raise Exception("Invalid radio button: '" + value + "' doesn't exist") 

        # now call function
        var = self.n_rbVars[title]
        with PauseCallFunction(callFunction, var, False):
            var.set(value)

    def clearAllRadioButtons(self, callFunction=False):
        for rb in self.n_rbs:
            self.setRadioButton(rb, self.n_rbVars[rb].startVal, callFunction=callFunction)

    def setRadioTick(self, title, tick=True):
        radios = self.__verifyItem(self.n_rbs, title)
        for rb in radios:
            if tick:
                rb.config(indicatoron=1)
            else:
                rb.config(indicatoron=0)

#####################################
# FUNCTION for list box
#####################################
    def addListBox(
            self,
            name,
            values=None,
            row=None,
            column=0,
            colspan=0,
            rowspan=0):
        self.__verifyItem(self.n_lbs, name, True)
        container = ListBoxContainer(self.getContainer())
        vscrollbar = AutoScrollbar(container)
        hscrollbar = AutoScrollbar(container, orient=HORIZONTAL)

        container.lb = Listbox(container,
            yscrollcommand=vscrollbar.set,
            xscrollcommand=hscrollbar.set)

        vscrollbar.grid(row=0, column=1, sticky=N + S)
        hscrollbar.grid(row=1, column=0, sticky=E + W)

        container.lb.grid(row=0, column=0, sticky=N + S + E + W)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        vscrollbar.config(command=container.lb.yview)
        hscrollbar.config(command=container.lb.xview)

        container.lb.config(font=self.lbFont)
        self.n_lbs[name] = container.lb

        container.lb.DEFAULT_TEXT=""
        if values is not None:
            container.lb.DEFAULT_TEXT='\n'.join(str(x) for x in values)
            for name in values:
                container.lb.insert(END, name)

        self.__positionWidget(container, row, column, colspan, rowspan)
        return container.lb

    # enable multiple listboxes to be selected at the same time
    def setListBoxGroup(self, name, group=True):
        lb = self.__verifyItem(self.n_lbs, name)
        group = not group
        lb.config(exportselection=group)

    # set how many rows to display
    def setListBoxRows(self, name, rows):
        lb = self.__verifyItem(self.n_lbs, name)
        lb.config(height=rows)

    # make the list single/multi select
    # default is single
    def setListBoxMulti(self, title, multi=True):
        lb = self.__verifyItem(self.n_lbs, title)
        if multi:
            lb.config(selectmode=EXTENDED)
        else:
            lb.config(selectmode=BROWSE)

    # make the list single/multi select
    # default is single
    def setListBoxSingle(self, title, single=True):
        self.warn(".setListBoxSingle() is deprecated. You should be using .setListBoxMulti()")
        self.setListBoxMulti(title, not single)

    def setListSingle(self, title, single=True):
        self.warn(".setListSingle() is deprecated. You should be using .setListBoxMulti()")
        self.setListBoxMulti(title, not single)

    # select the specified item in the list
    def selectListItem(self, title, item, callFunction=True):
        positions = self.__getListPositions(title, item)
        if len(positions) > 0:
            self.selectListItemAtPos(title, positions[0], callFunction)

    def selectListItemPos(self, title, pos, callFunction=False):
        self.warn(".selectListItemPos() is deprecated. You should be using .selectListItemAtPos()")
        self.selectListItemAtPos(title, pos, callFunction)

    def selectListItemAtPos(self, title, pos, callFunction=False):
        lb = self.__verifyItem(self.n_lbs, title)

        # clear previous selection if we're not multi
        if lb.cget("selectmode") != EXTENDED:
            lb.selection_clear(0, END)

        # show & select this item
        if pos >= 0:
            lb.see(pos)
            lb.activate(pos)
            lb.selection_set(pos)
            # now call function
            if callFunction and hasattr(lb, 'cmd'):
                lb.cmd()
            self.topLevel.update_idletasks()

    # replace the list items in the list box
    def updateListItems(self, title, items, select=False):
        self.warn(".updateListItems() is deprecated. You should be using .updateListBox()")
        self.updateListBox(title, items, select)

    def updateListBox(self, title, items, select=False):
        self.clearListBox(title)
        self.addListItems(title, items, select=select)

    # add the items to the specified list box
    def addListItems(self, title, items, select=True):
        for i in items:
            self.addListItem(title, i, select=select)

    # add the item to the end of the list box
    def addListItem(self, title, item, pos=None, select=True):
        lb = self.__verifyItem(self.n_lbs, title)
        # add it at the end
        if pos is None: pos = END
        lb.insert(pos, item)

        # show & select the newly added item
        if select:
            # clear any selection
            items = lb.curselection()
            if len(items) > 0:
                lb.selection_clear(items)

            self.selectListItemAtPos(title, lb.size() - 1)

    # returns a list containing 0 or more elements
    # all that are in the selected range
    def getListItems(self, title):
        self.warn(".getListItems() is deprecated. You should be using .getListBox()")
        return self.getListBox(title)

    def getListBox(self, title):
        lb = self.__verifyItem(self.n_lbs, title)
        items = lb.curselection()
        values = []
        for loop in range(len(items)):
            values.append(lb.get(items[loop]))
        return values

    def getAllListBoxes(self):
        boxes = {}
        for k in self.n_lbs:
            boxes[k] = self.getListBox(k)
        return boxes

    def getAllListItems(self, title):
        lb = self.__verifyItem(self.n_lbs, title)
        items = lb.get(0, END)
        return list(items)

    def getListItemsPos(self, title):
        self.warn(".getListItemsPos() is deprecated. You should be using .getListBoxPos()")
        return self.getListBoxPos(title)

    def getListBoxPos(self, title):
        lb = self.__verifyItem(self.n_lbs, title)
        # bug in tkinter 1.160 returns these as strings
        items = [int(i) for i in lb.curselection()]

        return items

    def removeListItemAtPos(self, title, pos):
        lb = self.__verifyItem(self.n_lbs, title)
        items = lb.get(0, END)
        if pos >= len(items):
            raise Exception("Invalid position: " + str(pos))
        lb.delete(pos)

        # show & select this item
        if pos >= lb.size():
            pos -= 1
        self.selectListItemAtPos(title, pos)

    # remove a specific item from the listBox
    # will only remove the first item that matches the String
    def removeListItem(self, title, item):
        lb = self.__verifyItem(self.n_lbs, title)
        positions = self.__getListPositions(title, item)
        if len(positions) > 0:
            lb.delete(positions[0])

        # show & select this item
        if positions[0] >= lb.size():
            positions[0] -= 1
        self.selectListItemAtPos(title, positions[0])

    def setListItemAtPos(self, title, pos, newVal):
        lb = self.__verifyItem(self.n_lbs, title)
        lb.delete(pos)
        lb.insert(pos, newVal)

    def setListItem(self, title, item, newVal, first=False):
        for pos in self.__getListPositions(title, item):
            self.setListItemAtPos(title, pos, newVal)
            if first:
                break

    # functions to config
    def setListItemAtPosBg(self, title, pos, col):
        lb = self.__verifyItem(self.n_lbs, title)
        lb.itemconfig(pos, bg=col)

    def setListItemAtPosFg(self, title, pos, col):
        lb = self.__verifyItem(self.n_lbs, title)
        lb.itemconfig(pos, fg=col)

    def __getListPositions(self, title, item):
        lb = self.__verifyItem(self.n_lbs, title)
        if not isinstance(item, list):
            item = [item]
        vals = lb.get(0, END)
        positions = []
        for pos, val in enumerate(vals):
            if val in item:
                positions.append(pos)
        return positions
 
    def setListItemBg(self, title, item, col):
        for pos in self.__getListPositions(title, item):
            self.setListItemAtPosBg(title, pos, col)

    def setListItemFg(self, title, item, col):
        for pos in self.__getListPositions(title, item):
            self.setListItemAtPosFg(title, pos, col)

    def clearListBox(self, title, callFunction=True):
        lb = self.__verifyItem(self.n_lbs, title)
        lb.selection_clear(0, END)
        lb.delete(0, END)  # clear
        if callFunction and hasattr(lb, 'cmd'):
            lb.cmd()

    def clearAllListBoxes(self, callFunction=False):
        for lb in self.n_lbs:
            self.clearListBox(lb, callFunction)

#####################################
# FUNCTION for buttons
#####################################
    def __buildButton(self, title, func, frame, name=None):
        if name is None:
            name = title
        if isinstance(title, list):
            raise Exception("Can't add a button using a list of names: " + str(title) + " - you should use .addButtons()")
        self.__verifyItem(self.n_buttons, title, True)
        if not self.ttkFlag:
            but = Button(frame, text=name)
            but.config(font=self.buttonFont)
            if self.platform in [self.MAC, self.LINUX]:
                but.config(highlightbackground=self.__getContainerBg())
        else:
            but = ttk.Button(frame, text=name)

        but.DEFAULT_TEXT = name

        if func is not None:
            command = self.MAKE_FUNC(func, title)
            bindCommand = self.MAKE_FUNC(func, title, True)
            but.config(command=command)

        #    but.bind('<Return>', bindCommand)


        #but.bind("<Tab>", self.__focusNextWindow)
        #but.bind("<Shift-Tab>", self.__focusLastWindow)
        self.n_buttons[title] = but

        return but

    def addNamedButton(
            self,
            name,
            title,
            func,
            row=None,
            column=0,
            colspan=0,
            rowspan=0):
        but = self.__buildButton(title, func, self.getContainer(), name)
        self.__positionWidget(but, row, column, colspan, rowspan, None)
        return but

    def addButton(self, title, func, row=None, column=0, colspan=0, rowspan=0):
        but = self.__buildButton(title, func, self.getContainer())
        self.__positionWidget(but, row, column, colspan, rowspan, None)
        return but

    def addImageButton(self, title, func, imgFile, row=None, column=0, colspan=0, rowspan=0):
        but = self.__buildButton(title, func, self.getContainer())
        self.__positionWidget(but, row, column, colspan, rowspan, None)
        self.setButtonImage(title, imgFile)
        return but

    def addIconButton(self, title, func, iconName, row=None, column=0, colspan=0, rowspan=0):
        icon = os.path.join(self.icon_path, iconName.lower()+".png")
        with PauseLogger():
            return self.addImageButton(title, func, icon, row, column, colspan, rowspan)

    def setButton(self, name, text):
        but = self.__verifyItem(self.n_buttons, name)
        but.config(text=text)

    def setButtonImage(self, name, imgFile):
        but = self.__verifyItem(self.n_buttons, name)
        image = self.__getImage(imgFile)
        # works on Mac & Windows :)
        but.config(image=image, compound=TOP, text="", justify=LEFT)
        # but.config(image=image, compound=None, text="") # works on Windows,
        # not Mac

        but.image = image

    # adds a set of buttons, in the row, spannning specified columns
    # pass in a list of names & a list of functions (or a single function to
    # use for all)
    def addButtons(
            self,
            names,
            funcs,
            row=None,
            column=0,
            colspan=0,
            rowspan=0):

        if not isinstance(names, list):
            raise Exception(
                "Invalid button: " +
                names +
                ". It must be a list of buttons.")

        singleFunc = self.__checkFunc(names, funcs)

        frame = WidgetBox(self.getContainer())
        frame.config(background=self.__getContainerBg())

        # make them into a 2D array, if not already
        if not isinstance(names[0], list):
            names = [names]
            # won't be used if single func
            if funcs is not None:
                funcs = [funcs]

        for bRow in range(len(names)):
            for i in range(len(names[bRow])):
                t = names[bRow][i]
                if funcs is None:
                    tempFunc = None
                elif singleFunc is None:
                    tempFunc = funcs[bRow][i]
                else:
                    tempFunc = singleFunc
                but = self.__buildButton(t, tempFunc, frame)

                but.grid(row=bRow, column=i)
                Grid.columnconfigure(frame, i, weight=1)
                Grid.rowconfigure(frame, bRow, weight=1)
                frame.theWidgets.append(but)

        self.__positionWidget(frame, row, column, colspan, rowspan)
        self.n_frames.append(frame)

#####################################
# FUNCTIONS for links
#####################################
    def __buildLink(self, title):
        link = Link(self.getContainer())
        link.config(
            text=title,
            font=self.linkFont)
        if not self.ttk:
            link.config(background=self.__getContainerBg())
        self.n_links[title] = link
        return link

    # launches a browser to the specified page
    def addWebLink(
            self,
            title,
            page,
            row=None,
            column=0,
            colspan=0,
            rowspan=0):
        link = self.__buildLink(title)
        link.registerWebpage(page)
        self.__positionWidget(link, row, column, colspan, rowspan)
        return link

    # executes the specified function
    def addLink(self, title, func, row=None, column=0, colspan=0, rowspan=0):
        link = self.__buildLink(title)
        if func is not None:
            myF = self.MAKE_FUNC(func, title, True)
            link.registerCallback(myF)
        self.__positionWidget(link, row, column, colspan, rowspan)
        return link

#####################################
# FUNCTIONS for grips
#####################################
    # adds a simple grip, used to drag the window around
    def addGrip(self, row=None, column=0, colspan=0, rowspan=0):
        grip = Grip(self.getContainer())
        self.__positionWidget(grip, row, column, colspan, rowspan)
        self.__addTooltip(grip, "Drag here to move", True)
        return grip


#####################################
# FUNCTIONS for dnd
#####################################
    def addTrashBin(self, title, row=None, column=0, colspan=0, rowspan=0):
        trash = TrashBin(self.getContainer())
        self.__positionWidget(trash, row, column, colspan, rowspan)
        return trash


#####################################
# FUNCTIONS for Microbits
#####################################
    # adds a simple microbit widget
    # used with permission from Ben Goodwin
    def addMicroBit(self, title, row=None, column=0, colspan=0, rowspan=0):
        self.__verifyItem(self.n_microbits, title, True)
        mb = MicroBitSimulator(self.getContainer())
        self.__positionWidget(mb, row, column, colspan, rowspan)
        self.n_microbits[title] = mb
        return mb

    def setMicroBitImage(self, title, image):
        self.__verifyItem(self.n_microbits, title).show(image)

    def setMicroBitPixel(self, title, x, y, brightness):
        self.__verifyItem(self.n_microbits, title).set_pixel(x, y, brightness)

    def clearMicroBit(self, title):
        self.__verifyItem(self.n_microbits, title).clear()

#####################################
# DatePicker Widget - using Form Container
#####################################
    def addDatePicker(self, name, row=None, column=0, colspan=0, rowspan=0):
        self.__verifyItem(self.n_dps, name, True)
        self.n_dps[name] = name
        # initial DatePicker has these dates
        days = range(1, 32)
        self.MONTH_NAMES = calendar.month_name[1:]
        years = range(1970, 2021)

        # create a frame, and add the widgets
        frame = self.startFrame(name, row, column, colspan, rowspan)
        self.setExpand("none")
        self.addLabel(name + "_DP_DayLabel", "Day:", 0, 0)
        self.setLabelAlign(name + "_DP_DayLabel", "w")
        self.addOptionBox(name + "_DP_DayOptionBox", days, 0, 1)
        self.addLabel(name + "_DP_MonthLabel", "Month:", 1, 0)
        self.setLabelAlign(name + "_DP_MonthLabel", "w")
        self.addOptionBox(name + "_DP_MonthOptionBox", self.MONTH_NAMES, 1, 1)
        self.addLabel(name + "_DP_YearLabel", "Year:", 2, 0)
        self.setLabelAlign(name + "_DP_YearLabel", "w")
        self.addOptionBox(name + "_DP_YearOptionBox", years, 2, 1)
        self.setOptionBoxChangeFunction(
            name + "_DP_MonthOptionBox",
            self.__updateDatePickerDays)
        self.setOptionBoxChangeFunction(
            name + "_DP_YearOptionBox",
            self.__updateDatePickerDays)
        self.stopFrame()
        frame.isContainer = False

    def setDatePickerFg(self, name, fg):
        self.__verifyItem(self.n_dps, name)
        self.setLabelFg(name + "_DP_DayLabel", fg)
        self.setLabelFg(name + "_DP_MonthLabel", fg)
        self.setLabelFg(name + "_DP_YearLabel", fg)

    def setDatePickerChangeFunction(self, title, function):
        self.__verifyItem(self.n_dps, title)
        cmd = self.MAKE_FUNC(self.__datePickerChangeFunction, title, True)
        self.setOptionBoxChangeFunction(title + "_DP_DayOptionBox", cmd)
        self.__verifyItem(self.n_options, title + "_DP_DayOptionBox").function = function

    def __datePickerChangeFunction(self, title):
        box = self.__verifyItem(self.n_options, title + "_DP_DayOptionBox")
        if hasattr(box, 'function'):
            box.function(title)

    # function to update DatePicker dropDowns
    def __updateDatePickerDays(self, title):
        if title.find("_DP_MonthOptionBox") > -1:
            title = title.split("_DP_MonthOptionBox")[0]
        elif title.find("_DP_YearOptionBox") > -1:
            title = title.split("_DP_YearOptionBox")[0]
        else:
            self.warn("Can't update days in DatePicker: " + title)
            return

        day = self.getOptionBox(title + "_DP_DayOptionBox")
        month = self.MONTH_NAMES.index(
            self.getOptionBox(
                title + "_DP_MonthOptionBox")) + 1
        year = int(self.getOptionBox(title + "_DP_YearOptionBox"))
        days = range(1, calendar.monthrange(year, month)[1] + 1)
        self.changeOptionBox(title + "_DP_DayOptionBox", days)

        # keep previous day if possible
        with PauseLogger():
            self.setOptionBox(title + "_DP_DayOptionBox", day, callFunction=False)

        self.__datePickerChangeFunction(title)

    # set a date for the named DatePicker
    def setDatePickerRange(self, title, startYear, endYear=None):
        self.__verifyItem(self.n_dps, title)
        if endYear is None:
            endYear = datetime.date.today().year
        years = range(startYear, endYear + 1)
        self.changeOptionBox(title + "_DP_YearOptionBox", years)

    def setDatePicker(self, title, date=None):
        self.__verifyItem(self.n_dps, title)
        if date is None:
            date = datetime.date.today()
        self.setOptionBox(title + "_DP_YearOptionBox", str(date.year))
        self.setOptionBox(title + "_DP_MonthOptionBox", date.month - 1)
        self.setOptionBox(title + "_DP_DayOptionBox", date.day - 1)

    def clearDatePicker(self, title, callFunction=True):
        self.__verifyItem(self.n_dps, title)
        self.setOptionBox(title + "_DP_YearOptionBox", 0, callFunction)
        self.setOptionBox(title + "_DP_MonthOptionBox", 0, callFunction)
        self.setOptionBox(title + "_DP_DayOptionBox", 0, callFunction)

    def clearAllDatePickers(self, callFunction=False):
        for k in self.n_dps:
            self.clearDatePicker(k, callFunction)

    def getDatePicker(self, title):
        self.__verifyItem(self.n_dps, title)
        day = int(self.getOptionBox(title + "_DP_DayOptionBox"))
        month = self.MONTH_NAMES.index(
            self.getOptionBox(
                title + "_DP_MonthOptionBox")) + 1
        year = int(self.getOptionBox(title + "_DP_YearOptionBox"))
        date = datetime.date(year, month, day)
        return date

    def getAllDatePickers(self):
        dps = {}
        for k in self.n_dps:
            dps[k] = self.getDatePicker(k)
        return dps

#####################################
# FUNCTIONS for labels
#####################################
    def __flash(self):
        if not self.alive: return
        if self.doFlash:
            for lab in self.n_flashLabs:
                bg = lab.cget("background")
                fg = lab.cget("foreground")
                lab.config(background=fg, foreground=bg)
        self.flashId = self.topLevel.after(250, self.__flash)

    def addFlashLabel(
            self,
            title,
            text=None,
            row=None,
            column=0,
            colspan=0,
            rowspan=0):
        self.addLabel(title, text, row, column, colspan, rowspan)
        self.n_flashLabs.append(self.n_labels[title])
        self.doFlash = True
        return self.n_labels[title]

    def addSelectableLabel(
            self,
            title,
            text=None,
            row=None,
            column=0,
            colspan=0,
            rowspan=0):
        return self.addLabel(title, text, row, column, colspan, rowspan, selectable=True)

    def addLabel(
            self,
            title,
            text=None,
            row=None,
            column=0,
            colspan=0,
            rowspan=0,
            selectable = False):
        """Add a label to the GUI.
        :param title: a unique identifier for the Label
        :param text: optional text for the Label
        :param row/column/colspan/rowspan: the row/column to position the label in & how many rows/columns to strecth across
        :raises ItemLookupError: raised if the title is not unique
        """
        self.__verifyItem(self.n_labels, title, True)
        if text is None:
            text = ""

        if not selectable:
            if not self.ttkFlag:
                lab = Label(self.getContainer(), text=text)
                lab.config(justify=LEFT, font=self.labelFont, background=self.__getContainerBg())
                lab.origBg = self.__getContainerBg()
            else:
                lab = ttk.Label(self.getContainer(), text=text)
        else:
            lab = SelectableLabel(self.getContainer(), text=text)
            lab.config(justify=LEFT, font=self.labelFont, background=self.__getContainerBg())
            lab.origBg = self.__getContainerBg()

        lab.inContainer = False
        lab.DEFAULT_TEXT = text

        self.n_labels[title] = lab
        self.__positionWidget(lab, row, column, colspan, rowspan)
        return lab

    def addEmptyLabel(self, title, row=None, column=0, colspan=0, rowspan=0):
        return self.addLabel(title, None, row, column, colspan, rowspan)

    # adds a set of labels, in the row, spannning specified columns
    def addLabels(self, names, row=None, colspan=0, rowspan=0):
        frame = WidgetBox(self.getContainer())
        if not self.ttkFlag:
            frame.config(background=self.__getContainerBg())
        for i in range(len(names)):
            self.__verifyItem(self.n_labels, names[i], True)
            if not self.ttkFlag:
                lab = Label(frame, text=names[i])
                lab.config(font=self.labelFont, justify=LEFT, background=self.__getContainerBg())
            else:
                lab = ttk.Label(frame, text=names[i])
            lab.DEFAULT_TEXT = names[i]
            lab.inContainer = False

            self.n_labels[names[i]] = lab
            lab.grid(row=0, column=i)
            Grid.columnconfigure(frame, i, weight=1)
            Grid.rowconfigure(frame, 0, weight=1)
            frame.theWidgets.append(lab)

        self.__positionWidget(frame, row, 0, colspan, rowspan)
        self.n_frames.append(frame)

    def setLabel(self, name, text):
        lab = self.__verifyItem(self.n_labels, name)
        lab.config(text=text)

    def getLabel(self, name):
        lab = self.__verifyItem(self.n_labels, name)
        return lab.cget("text")

    def clearLabel(self, name):
        self.setLabel(name, "")

#####################################
# FUNCTIONS to add Text Area
#####################################
    def __buildTextArea(self, title, frame, scrollable=False):
        """ Internal wrapper, used for building TextAreas.

        :param title: the key used to reference this TextArea
        :param frame: this should be a container, used as the parent for the OptionBox
        :param scrollable: the key used to reference this TextArea
        :returns: the created TextArea
        :raises ItemLookupError: if the title is already in use
        """
        self.__verifyItem(self.n_textAreas, title, True)
        if scrollable:
            text = AjScrolledText(frame)
        else:
            text = AjText(frame)
        text.config(font=self.taFont, width=20, height=10, undo=True, wrap=WORD)

        if self.platform in [self.MAC, self.LINUX]:
            text.config(highlightbackground=self.__getContainerBg())

        text.bind("<Tab>", self.__focusNextWindow)
        text.bind("<Shift-Tab>", self.__focusLastWindow)

        # add a right click menu
        text.var = None
        self.__addRightClickMenu(text)

        self.n_textAreas[title] = text
        self.logTextArea(title)

        return text

    def addTextArea(self, title, row=None, column=0, colspan=0, rowspan=0):
        """ Adds a TextArea with the specified title
        Simply calls internal __buildTextArea function before positioning the widget

        :param title: the key used to reference this TextArea
        :returns: the created TextArea
        :raises ItemLookupError: if the title is already in use
        """
        text = self.__buildTextArea(title, self.getContainer())
        self.__positionWidget(text, row, column, colspan, rowspan, N+E+S+W)
        return text

    def addScrolledTextArea(self, title, row=None, column=0, colspan=0, rowspan=0):
        """ Adds a Scrollable TextArea with the specified title
        Simply calls internal __buildTextArea functio, specifying a ScrollabelTextArea before positioning the widget

        :param title: the key used to reference this TextArea
        :returns: the created TextArea
        :raises ItemLookupError: if the title is already in use
        """
        text = self.__buildTextArea(title, self.getContainer(), True)
        self.__positionWidget(text, row, column, colspan, rowspan, N+E+S+W)
        return text

    def getTextArea(self, title):
        """ Gets the text in the specified TextArea

        :param title: the TextArea to check
        :returns: the text in the specified TextArea
        :raises ItemLookupError: if the title can't be found
        """
        return self.__verifyItem(self.n_textAreas, title).getText()

    def getAllTextAreas(self):
        """ Convenience function to get the text for all TextAreas in the GUI.

        :returns: a dictionary containing the result of calling getTextArea for every TextArea in the GUI
        """
        areas = {}
        for k in self.n_textAreas:
            areas[k] = self.getTextArea(k)
        return areas

    def setTextArea(self, title, text, end=True, callFunction=True):
        """ Add the supplied text to the specified TextArea

        :param title: the TextArea to change
        :param text: the text to add to the TextArea
        :param end: where to insert the text, by default it is added to the end. Set end to False to add to the beginning.
        :param callFunction: whether to generate an event to notify that the widget has changed
        :returns: None
        :raises ItemLookupError: if the title can't be found
        """
        ta = self.__verifyItem(self.n_textAreas, title)

        ta.pauseCallFunction(callFunction)
        if end:
            ta.insert(END, text)
        else:
            ta.insert('1.0', text)
        ta.resumeCallFunction()

    def clearTextArea(self, title, callFunction=True):
        """ Removes all text from the specified TextArea

        :param title: the TextArea to change
        :param callFunction: whether to generate an event to notify that the widget has changed
        :returns: None
        :raises ItemLookupError: if the title can't be found
        """
        ta = self.__verifyItem(self.n_textAreas, title)
        ta.pauseCallFunction(callFunction)
        ta.delete('1.0', END)
        ta.resumeCallFunction()

    def clearAllTextAreas(self, callFunction=False):
        """ Convenience function to clear all TextAreas in the GUI
        Will simply call clearTextArea on each TextArea

        :param callFunction: whether to generate an event to notify that the widget has changed
        :returns: None
        """
        for ta in self.n_textAreas:
            self.clearTextArea(ta, callFunction=callFunction)

    def logTextArea(self, title):
        """ Creates an md5 hash - can be used later to check if the TextArea has changed
        The hash is stored in the widget

        :param title: the TextArea to hash
        :returns: None
        :raises ItemLookupError: if the title can't be found
        """
        self.__loadHashlib()
        if hashlib is False:
            self.warn("Unable to log TextArea, hashlib library not available")
        else:
            text = self.__verifyItem(self.n_textAreas, title)
            text.__hash = text.getTextAreaHash()

    def textAreaChanged(self, title):
        """ Creates a temporary md5 hash - and compares it with a previously generated & stored hash
        The previous hash has to be generated manually, by calling logTextArea

        :param title: the TextArea to hash
        :returns: bool - True if the TextArea has changed or False if it hasn't
        :raises ItemLookupError: if the title can't be found
        """
        self.__loadHashlib()
        if hashlib is False:
            self.warn("Unable to log TextArea, hashlib library not available")
        else:
            text = self.__verifyItem(self.n_textAreas, title)
            return text.__hash != text.getTextAreaHash()

#####################################
# FUNCTIONS to add Tree Widgets
#####################################
    def addTree(self, title, data, row=None, column=0, colspan=0, rowspan=0):
        self.__verifyItem(self.n_trees, title, True)

        self.__importAjtree()
        if parseString is False:
            self.warn("Unable to parse xml files. .addTree() not available")
            return

        xmlDoc = parseString(data)

        frame = ScrollPane(
            self.getContainer(),
            relief=RAISED,
            borderwidth=2,
            bg="#FFFFFF",
            highlightthickness=0,
            takefocus=1)
        self.__positionWidget(frame, row, column, colspan, rowspan, "NSEW")

        item = ajTreeData(xmlDoc.documentElement)
        node = ajTreeNode(frame.getPane(), None, item)
        self.n_trees[title] = node
        # update() & expand() called in go() function
        return node

    def setTreeEditable(self, title, value=True):
        tree = self.__verifyItem(self.n_trees, title)
        tree.item.setCanEdit(value)

    def setTreeBg(self, title, colour):
        tree = self.__verifyItem(self.n_trees, title)
        tree.setBgColour(colour)

    def setTreeFg(self, title, colour):
        tree = self.__verifyItem(self.n_trees, title)
        tree.setFgColour(colour)

    def setTreeHighlightBg(self, title, colour):
        tree = self.__verifyItem(self.n_trees, title)
        tree.setBgHColour(colour)

    def setTreeHighlightFg(self, title, colour):
        tree = self.__verifyItem(self.n_trees, title)
        tree.setFgHColour(colour)

    def setTreeColours(self, title, fg, bg, fgH, bgH):
        tree = self.__verifyItem(self.n_trees, title)
        tree.setAllColours(bg, fg, bgH, fgH)

    def setTreeDoubleClickFunction(self, title, func):
        if func is not None:
            tree = self.__verifyItem(self.n_trees, title)
            command = self.MAKE_FUNC(func, title)
            tree.item.registerDblClick(command)

    def setTreeEditFunction(self, title, func):
        if func is not None:
            tree = self.__verifyItem(self.n_trees, title)
            command = self.MAKE_FUNC(func, title)
            tree.registerEditEvent(command)

    # get whole tree as XML
    def getTreeXML(self, title):
        tree = self.__verifyItem(self.n_trees, title)
        return tree.item.node.toxml()

    # get selected node as a string
    def getTreeSelected(self, title):
        tree = self.__verifyItem(self.n_trees, title)
        return tree.getSelectedText()

    # get selected node (and children) as XML
    def getTreeSelectedXML(self, title):
        tree = self.__verifyItem(self.n_trees, title)
        item = tree.getSelected()
        if item is not None:
            return item.node.toxml()
        else:
            return None

#####################################
# FUNCTIONS to add Message Box
#####################################
    def addMessage(
            self,
            title,
            text,
            row=None,
            column=0,
            colspan=0,
            rowspan=0):

        self.__verifyItem(self.n_messages, title, True)
        mess = Message(self.getContainer())
        mess.config(font=self.messageFont)
        mess.config(justify=LEFT, background=self.__getContainerBg())

        if text is not None:
            mess.config(text=text)
            mess.DEFAULT_TEXT = text
        else:
            mess.DEFAULT_TEXT = ""

        if self.platform in [self.MAC, self.LINUX]:
            mess.config(highlightbackground=self.__getContainerBg())

        self.n_messages[title] = mess

        self.__positionWidget(mess, row, column, colspan, rowspan)
#            mess.bind("<Configure>", lambda e: mess.config(width=e.width-10))
        return mess

    def addEmptyMessage(self, title, row=None, column=0, colspan=0, rowspan=0):
        return self.addMessage(title, None, row, column, colspan, rowspan)

    def setMessage(self, title, text):
        mess = self.__verifyItem(self.n_messages, title)
        mess.config(text=text)

    def clearMessage(self, title):
        self.setMessage(title, "")

#####################################
# FUNCTIONS for entry boxes
#####################################
    def __buildEntry(self, title, frame, secret=False, words=[]):
        self.__verifyItem(self.n_entries, title, True)

        # if we are an autocompleter
        if len(words) > 0:
            ent = AutoCompleteEntry(words, self.topLevel, frame)
        else:
            var = StringVar(self.topLevel)
            if not self.ttkFlag:
                ent = Entry(frame, textvariable=var)
            else:
                ent = ttk.Entry(frame, textvariable=var)

            ent.var = var
            ent.var.auto_id = None

        if not self.ttkFlag:
            ent.config(font=self.entryFont)
            if self.platform in [self.MAC, self.LINUX]:
                ent.config(highlightbackground=self.__getContainerBg())

        # vars to store any limit traces
        ent.var.uc_id = None
        ent.var.lc_id = None
        ent.var.ml_id = None

        ent.inContainer = False
        ent.showingDefault = False  # current status of entry
        ent.default = ""  # the default value to show (if set)
        ent.DEFAULT_TEXT = ""  # the default value for language support
        ent.myTitle = title  # the title of the entry
        ent.isNumeric = False  # if the entry is numeric
        ent.isValidation = False  # if the entry is validation

        # configure it to be secret
        if secret:
            ent.config(show="*")

        ent.bind("<Tab>", self.__focusNextWindow)
        ent.bind("<Shift-Tab>", self.__focusLastWindow)

        # add a right click menu
        self.__addRightClickMenu(ent)

        self.n_entries[title] = ent
        self.n_entryVars[title] = ent.var
        return ent

    def addEntry(
            self,
            title,
            row=None,
            column=0,
            colspan=0,
            rowspan=0,
            secret=False):
        ent = self.__buildEntry(title, self.getContainer(), secret)
        self.__positionWidget(ent, row, column, colspan, rowspan)
        return ent

    def addFileEntry(self, title, row=None, column=0, colspan=0, rowspan=0):
        ent = self.__buildFileEntry(title, self.getContainer())
        self.__positionWidget(ent, row, column, colspan, rowspan)
        return ent

    def addDirectoryEntry(self, title, row=None, column=0, colspan=0, rowspan=0):
        ent = self.__buildFileEntry(title, self.getContainer(), selectFile=False)
        self.__positionWidget(ent, row, column, colspan, rowspan)
        return ent

    def __getDirName(self, title):
        self.__getFileName(title, selectFile=False)

    def __getFileName(self, title, selectFile=True):
        if selectFile:
            fileName = self.openBox()
        else:
            fileName = self.directoryBox()

        if fileName is not None:
            self.setEntry(title, fileName)

        self.topLevel.after(250, self.setEntryFocus, title)

    def __checkDirName(self, title):
        if len(self.getEntry(title)) == 0:
            self.__getFileName(title, selectFile=False)

    def __checkFileName(self, title):
        if len(self.getEntry(title)) == 0:
            self.__getFileName(title)

    def __buildFileEntry(self, title, frame, selectFile=True):
        vFrame = ButtonBox(frame)
        vFrame.config(background=self.__getContainerBg())

        vFrame.theWidget = self.__buildEntry(title, vFrame)
        vFrame.theWidget.pack(expand=True, fill=X, side=LEFT)

        if selectFile:
            command = self.MAKE_FUNC(self.__getFileName, title)
            click_command = self.MAKE_FUNC(self.__checkFileName, title, True)
            text = "File"
            default = "-- enter a filename --"
        else:
            command = self.MAKE_FUNC(self.__getDirName, title)
            click_command = self.MAKE_FUNC(self.__checkDirName, title, True)
            text = "Directory"
            default = "-- enter a directory --"

        self.setEntryDefault(title, default)
        vFrame.theWidget.bind("<Button-1>", click_command, "+")

        vFrame.theButton = Button(vFrame)
        vFrame.theButton.config(text=text, font=self.buttonFont)
        vFrame.theButton.config(command=command)
        vFrame.theButton.pack(side=RIGHT, fill=X)
        vFrame.theButton.inContainer = True
        vFrame.theWidget.but = vFrame.theButton

        return vFrame

    def addValidationEntry(
            self,
            title,
            row=None,
            column=0,
            colspan=0,
            rowspan=0,
            secret=False):

        ent = self.__buildValidationEntry(title, self.getContainer(), secret)
        self.__positionWidget(ent, row, column, colspan, rowspan)
        return ent

    def __buildValidationEntry(self, title, frame, secret):
        vFrame = LabelBox(frame)
        vFrame.config(background=self.__getContainerBg())
        vFrame.isValidation = True

        ent = self.__buildEntry(title, vFrame, secret)
        ent.config(highlightthickness=2)
        ent.pack(expand=True, fill=X, side=LEFT)
        ent.isValidation = True

        lab = Label(vFrame)
        lab.pack(side=RIGHT, fill=Y)
        lab.config(font=self.labelFont, background=self.__getContainerBg())
        lab.inContainer = True
        lab.isValidation = True
        ent.lab = lab

        self.n_labels[title] = lab
        self.n_frameLabs[title] = lab

        vFrame.theWidget = ent
        vFrame.theLabel = lab
        self.setEntryWaitingValidation(title)

        return vFrame

    def addLabelValidationEntry(
            self,
            title,
            row=None,
            column=0,
            colspan=0,
            rowspan=0,
            secret=False):
        frame = self.__getLabelBox(title)
        ent = self.__buildValidationEntry(title, frame, secret)
        self.__packLabelBox(frame, ent)
        self.__positionWidget(frame, row, column, colspan, rowspan)
        return ent

    def setEntryValid(self, title):
        entry = self.__verifyItem(self.n_entries, title)
        if not entry.isValidation:
            self.warn("Entry " + str(title) + " is not a validation entry. Unable to set VALID.")
            return

        entry.config(highlightbackground="#4CC417", highlightcolor="#4CC417", fg="#4CC417")
        entry.config(highlightthickness=2)
        entry.lab.config(text='\u2714', fg="#4CC417")
        entry.lab.DEFAULT_TEXT = entry.lab.cget("text")

    def setEntryInvalid(self, title):
        entry = self.__verifyItem(self.n_entries, title)
        if not entry.isValidation:
            self.warn("Entry " + str(title) + " is not a validation entry. Unable to set INVALID.")
            return

        entry.config(highlightbackground="#FF0000", highlightcolor="#FF0000", fg="#FF0000")
        entry.config(highlightthickness=2)
        entry.lab.config(text='\u2716', fg="#FF0000")
        entry.lab.DEFAULT_TEXT = entry.lab.cget("text")

    def setEntryWaitingValidation(self, title):
        entry = self.__verifyItem(self.n_entries, title)
        if not entry.isValidation:
            self.warn("Entry " + str(title) + " is not a validation entry. Unable to set WAITING VALID.")
            return

        entry.config(highlightbackground="#000000", highlightcolor="#000000", fg="#000000")
        entry.config(highlightthickness=1)
        entry.lab.config(text='\u2731', fg="#000000")
        entry.lab.DEFAULT_TEXT = entry.lab.cget("text")

    def addAutoEntry(
            self,
            title,
            words,
            row=None,
            column=0,
            colspan=0,
            rowspan=0):
        ent = self.__buildEntry(
            title,
            self.getContainer(),
            secret=False,
            words=words)
        self.__positionWidget(ent, row, column, colspan, rowspan)
        return ent

    def setAutoEntryNumRows(self, title, rows):
        entry = self.__verifyItem(self.n_entries, title)
        entry.setNumRows(rows)

    def addLabelAutoEntry(
            self,
            title,
            words,
            row=None,
            column=0,
            colspan=0,
            rowspan=0,
            secret=False):
        frame = self.__getLabelBox(title)
        ent = self.__buildEntry(title, frame, secret, words=words)
        self.__packLabelBox(frame, ent)
        self.__positionWidget(frame, row, column, colspan, rowspan)
        return ent

    def __validateNumericEntry(
            self,
            action,
            index,
            value_if_allowed,
            prior_value,
            text,
            validation_type,
            trigger_type,
            widget_name):
        if action == "1":
            if text in '0123456789.-+':
                try:
                    if len(value_if_allowed) == 1 and value_if_allowed in '.-':
                        return True
                    elif len(value_if_allowed) == 2 and value_if_allowed == '-.':
                        return True
                    else:
                        float(value_if_allowed)
                        return True
                except ValueError:
                    self.containerStack[0]['container'].bell()
                    return False
            else:
                self.containerStack[0]['container'].bell()
                return False
        else:
            return True

    def addNumericEntry(
            self,
            title,
            row=None,
            column=0,
            colspan=0,
            rowspan=0,
            secret=False):
        ent = self.__buildEntry(title, self.getContainer(), secret)
        self.__positionWidget(ent, row, column, colspan, rowspan)

        if self.validateNumeric is None:
            self.validateNumeric = (self.containerStack[0]['container'].register(
                self.__validateNumericEntry), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        ent.isNumeric = True
        ent.config(validate='key', validatecommand=self.validateNumeric)
        self.setEntryTooltip(title, "Numeric data only.")
        return ent

    def addLabelNumericEntry(
            self,
            title,
            row=None,
            column=0,
            colspan=0,
            rowspan=0,
            secret=False):
        return self.addNumericLabelEntry(
            title, row, column, colspan, rowspan, secret)

    def addNumericLabelEntry(
            self,
            title,
            row=None,
            column=0,
            colspan=0,
            rowspan=0,
            secret=False):
        frame = self.__getLabelBox(title)
        ent = self.__buildEntry(title, frame, secret)
        self.__packLabelBox(frame, ent)
        self.__positionWidget(frame, row, column, colspan, rowspan)

        if self.validateNumeric is None:
            self.validateNumeric = (self.containerStack[0]['container'].register(
                self.__validateNumericEntry), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        ent.isNumeric = True
        ent.config(validate='key', validatecommand=self.validateNumeric)
        self.setEntryTooltip(title, "Numeric data only.")
        return ent

    def addSecretEntry(self, title, row=None, column=0, colspan=0, rowspan=0):
        return self.addEntry(title, row, column, colspan, rowspan, True)

    def addLabelEntry(
            self,
            title,
            row=None,
            column=0,
            colspan=0,
            rowspan=0,
            secret=False):
        frame = self.__getLabelBox(title)
        ent = self.__buildEntry(title, frame, secret)
        self.__packLabelBox(frame, ent)
        self.__positionWidget(frame, row, column, colspan, rowspan)
        return ent

    def addLabelSecretEntry(
            self,
            title,
            row=None,
            column=0,
            colspan=0,
            rowspan=0):
        return self.addSecretLabelEntry(title, row, column, colspan, rowspan)

    def addSecretLabelEntry(
            self,
            title,
            row=None,
            column=0,
            colspan=0,
            rowspan=0):
        return self.addLabelEntry(title, row, column, colspan, rowspan, True)

    def getEntry(self, name):
        self.__verifyItem(self.n_entryVars, name)
        entry = self.__verifyItem(self.n_entries, name)
        if entry.showingDefault:
            if entry.isNumeric:
                return 0
            else:
                return ""
        else:
            val = self.n_entryVars[name].get()
            if entry.isNumeric:
                if len(val) == 0 or (len(val) == 1 and val in '.-') or (len(val) == 2 and val == "-."):
                    return 0
                else:
                    return float(val)
            else:
                return val

    def getAllEntries(self):
        entries = {}
        for k in self.n_entries:
            entries[k] = self.getEntry(k)
        return entries

    def setEntry(self, name, text, callFunction=True):
        var = self.__verifyItem(self.n_entryVars, name)
        self.__updateEntryDefault(name, mode="set")

        # now call function
        with PauseCallFunction(callFunction, var, False):
            var.set(text)

    def setEntryMaxLength(self, name, length):
        var = self.__verifyItem(self.n_entryVars, name)
        var.maxLength = length
        if var.ml_id is not None:
            var.trace_vdelete('w', var.ml_id)
        var.ml_id = var.trace('w', self.MAKE_FUNC(self.__limitEntry, name, True))

    def setEntryUpperCase(self, name):
        var = self.__verifyItem(self.n_entryVars, name)
        if var.uc_id is not None:
            var.trace_vdelete('w', var.uc_id)
        var.uc_id = var.trace('w', self.MAKE_FUNC(self.__upperEntry, name, True))

    def setEntryLowerCase(self, name):
        var = self.__verifyItem(self.n_entryVars, name)
        if var.lc_id is not None:
            var.trace_vdelete('w', var.lc_id)
        var.lc_id = var.trace('w', self.MAKE_FUNC(self.__lowerEntry, name, True))

    def __limitEntry(self, name):
        var = self.__verifyItem(self.n_entryVars, name)
        if len(var.get()) > var.maxLength:
            self.containerStack[0]['container'].bell()
            var.set(var.get()[0:var.maxLength])

    def __upperEntry(self, name):
        var = self.__verifyItem(self.n_entryVars, name)
        chars = var.get().upper()
        var.set(chars)

    def __lowerEntry(self, name):
        var = self.__verifyItem(self.n_entryVars, name)
        chars = var.get().lower()
        var.set(chars)

    def __entryIn(self, name):
        self.__updateEntryDefault(name, "in")

    def __entryOut(self, name):
        self.__updateEntryDefault(name, "out")

    def __updateEntryDefault(self, name, mode=None):
        var = self.__verifyItem(self.n_entryVars, name)
        entry = self.__verifyItem(self.n_entries, name)

        # ignore this if no default to apply
        if entry.default == "":
            return

        # disable any limits
        if var.lc_id is not None:
            var.trace_vdelete('w', var.lc_id)
        if var.uc_id is not None:
            var.trace_vdelete('w', var.uc_id)
        if var.ml_id is not None:
            var.trace_vdelete('w', var.ml_id)

        # disable any auto completion
        if var.auto_id is not None:
            var.trace_vdelete('w', var.auto_id)

        current = self.n_entryVars[name].get()

        # disable any change function
        with PauseCallFunction(False, var, False):

            # clear & remove default
            if mode == "set" or (mode in [ "in", "clear"] and entry.showingDefault):
                var.set("")
                entry.showingDefault = False
                entry.config(justify=entry.oldJustify, foreground=entry.oldFg)
            elif mode == "out" and current == "":
                var.set(entry.default)
                entry.config(justify='center', foreground='grey')
                entry.showingDefault = True
            elif mode == "update" and entry.showingDefault:
                var.set(entry.default)

        # re-enable any limits
        if var.lc_id is not None:
            var.lc_id = var.trace('w', self.MAKE_FUNC(self.__lowerEntry, name, True))
        if var.uc_id is not None:
            var.uc_id = var.trace('w', self.MAKE_FUNC(self.__upperEntry, name, True))
        if var.ml_id is not None:
            var.ml_id = var.trace('w', self.MAKE_FUNC(self.__limitEntry, name, True))

        # re-enable auto completion
        if var.auto_id is not None:
            var.auto_id = var.trace('w', entry.textChanged)

    def updateDefaultText(self, name, text):
        self.warn(".updateDefaultText() is deprecated. You should be using .updateEntryDefault()")
        self.updateEntryDefault(name, text)

    def updateEntryDefault(self, name, text):
        entry = self.__verifyItem(self.n_entries, name)

        entry.default = text
        entry.DEFAULT_TEXT = text
        self.__updateEntryDefault(name, "update")

    def setEntryDefault(self, name, text="default"):
        entry = self.__verifyItem(self.n_entries, name)
        self.__verifyItem(self.n_entryVars, name)

        # remember current settings - to return to
        entry.oldJustify = entry.cget('justify')
        entry.oldFg = entry.cget('foreground')

        # configure default stuff
        entry.showingDefault = False
        entry.default = text
        entry.DEFAULT_TEXT = text

        # only show new text if empty
        self.__updateEntryDefault(name, "out")

        # bind commands to show/remove the default
        in_command = self.MAKE_FUNC(self.__entryIn, name, True)
        out_command = self.MAKE_FUNC(self.__entryOut, name, True)
        entry.bind("<FocusIn>", in_command, add="+")
        entry.bind("<FocusOut>", out_command, add="+")

    def clearEntry(self, name, callFunction=True, setFocus=True):
        var = self.__verifyItem(self.n_entryVars, name)

        # now call function
        with PauseCallFunction(callFunction, var, False):
            var.set("")

        self.__updateEntryDefault(name, mode="clear")
        if setFocus: self.setFocus(name)

    def clearAllEntries(self, callFunction=False):
        for entry in self.n_entryVars:
            self.clearEntry(entry, callFunction=callFunction, setFocus=False)

    def setFocus(self, name):
        self.__verifyItem(self.n_entries, name)
        self.n_entries[name].focus_set()

    def __lookupValue(self, myDict, val):
        for name in myDict:
            if isinstance(myDict[name], type([])):  # array of cbs
                for rb in myDict[name]:
                    if rb == val:
                        return name
            else:
                if myDict[name] == val:
                    return name
        return None

    def __getWidgetName(self, widg):
        name = widg.__class__.__name__
        if name.lower() == "tk":
            return self.__getTopLevel().title()
        elif name == "Listbox":
            return self.__lookupValue(self.n_lbs, widg)
        elif name == "Button":
            # merge together Buttons & Toolbar Buttons
            z = self.n_buttons.copy()
            z.update(self.n_tbButts)
            return self.__lookupValue(z, widg)
        elif name == "Entry":
            return self.__lookupValue(self.n_entries, widg)
        elif name == "Scale":
            return self.__lookupValue(self.n_scales, widg)
        elif name == "Checkbutton":
            return self.__lookupValue(self.n_cbs, widg)
        elif name == "Radiobutton":
            return self.__lookupValue(self.n_rbs, widg)
        elif name == "Spinbox":
            return self.__lookupValue(self.n_spins, widg)
        elif name == "OptionMenu":
            return self.__lookupValue(self.n_options, widg)
        elif name == "Text":
            return self.__lookupValue(self.n_textAreas, widg)
        elif name == "Link":
            return self.__lookupValue(self.n_links, widg)
        else:
            raise Exception("Unknown widget type: " + name)

    def getFocus(self):
        widg = self.topLevel.focus_get()
        return self.__getWidgetName(widg)

#####################################
# FUNCTIONS for progress bars (meters)
#####################################
    def __addMeter(
            self,
            name,
            type="METER",
            row=None,
            column=0,
            colspan=0,
            rowspan=0):
        self.__verifyItem(self.n_meters, name, True)

        if type == "SPLIT":
            meter = SplitMeter(self.getContainer(), font=self.meterFont)
        elif type == "DUAL":
            meter = DualMeter(self.getContainer(), font=self.meterFont)
        else:
            meter = Meter(self.getContainer(), font=self.meterFont)

        self.n_meters[name] = meter
        self.__positionWidget(meter, row, column, colspan, rowspan)
        return meter

    def addMeter(self, name, row=None, column=0, colspan=0, rowspan=0):
        return self.__addMeter(name, "METER", row, column, colspan, rowspan)

    def addSplitMeter(self, name, row=None, column=0, colspan=0, rowspan=0):
        return self.__addMeter(name, "SPLIT", row, column, colspan, rowspan)

    def addDualMeter(self, name, row=None, column=0, colspan=0, rowspan=0):
        return self.__addMeter(name, "DUAL", row, column, colspan, rowspan)

    # update the value of the specified meter
    # note: expects a value between 0 (-100 for split/dual) & 100
    def setMeter(self, name, value=0.0, text=None):
        item = self.__verifyItem(self.n_meters, name)
        item.set(value, text)

    def getMeter(self, name):
        item = self.__verifyItem(self.n_meters, name)
        return item.get()

    def getAllMeters(self):
        meters = {}
        for k in self.n_meters:
            meters[k] = self.getMeter(k)
        return meters

    # a single colour for meters, a list of 2 colours for splits & duals
    def setMeterFill(self, name, colour):
        item = self.__verifyItem(self.n_meters, name)
        item.configure(fill=colour)

#####################################
# FUNCTIONS for seperators
#####################################
    def addSeparator(
            self,
            row=None,
            column=0,
            colspan=0,
            rowspan=0,
            colour=None):
        self.warn(
            ".addSeparator() is deprecated. You should be using .addHorizontalSeparator() or .addVerticalSeparator()")
        return self.addHorizontalSeparator(row, column, colspan, rowspan, colour)

    def addHorizontalSeparator(
            self,
            row=None,
            column=0,
            colspan=0,
            rowspan=0,
            colour=None):
        return self.__addSeparator(
            "horizontal",
            row,
            column,
            colspan,
            rowspan,
            colour)

    def addVerticalSeparator(
            self,
            row=None,
            column=0,
            colspan=0,
            rowspan=0,
            colour=None):
        return self.__addSeparator("vertical", row, column, colspan, rowspan, colour)

    def __addSeparator(
            self,
            orient,
            row=None,
            column=0,
            colspan=0,
            rowspan=0,
            colour=None):
        sep = Separator(self.getContainer(), orient)
        if colour is not None:
            sep.configure(fg=colour)
        self.n_separators.append(sep)
        self.__positionWidget(sep, row, column, colspan, rowspan)
        return sep

#####################################
# FUNCTIONS for pie charts
#####################################
    def addPieChart(
            self,
            name,
            fracs,
            row=None,
            column=0,
            colspan=0,
            rowspan=0):
        self.__verifyItem(self.n_pieCharts, name, True)
        self.__loadTooltip()
        pie = PieChart(self.getContainer(), fracs, self.__getContainerBg())
        self.n_pieCharts[name] = pie
        self.__positionWidget(pie, row, column, colspan, rowspan, sticky=None)
        return pie

    def setPieChart(self, title, name, value):
        pie = self.__verifyItem(self.n_pieCharts, title)
        pie.setValue(name, value)

#####################################
# FUNCTIONS for tool bar
#####################################
    # adds a list of buttons along the top - like a tool bar...
    def addToolbar(self, names, funcs, findIcon=False):
        if not self.hasTb:
            self.hasTb = True

        image = None
        singleFunc = self.__checkFunc(names, funcs)
        if not isinstance(names, list):
            names = [names]

        for i in range(len(names)):
            t = names[i]
            if (t in self.n_tbButts):
                raise Exception(
                    "Invalid toolbar button name: " +
                    t +
                    " already exists")

            if findIcon:
                # turn off warnings about PNGs
                with PauseLogger():
                    imgFile = os.path.join(self.icon_path, t.lower() + ".png")
                    try:
                        image = self.__getImage(imgFile)
                    except Exception as e:
                        image = None

            but = Button(self.tb)
            self.n_tbButts[t] = but

            if singleFunc is not None:
                u = self.MAKE_FUNC(singleFunc, t)
            else:
                u = self.MAKE_FUNC(funcs[i], t)

            but.config(text=t, command=u, relief=FLAT, font=self.tbFont)
            but.image = image
            if image is not None:
                # works on Mac & Windows :)
                but.config(image=image, compound=TOP, text="", justify=LEFT)
            but.pack(side=LEFT, padx=2, pady=2)
            but.tt_var = self.__addTooltip(but, t.title(), True)
            but.DEFAULT_TEXT=t

        # add the pinned image
        self.pinBut = None

    def __setPinBut(self):

        # only call this once
        if self.pinBut is not None:
            return

        # try to get the icon, if none - then set but to None, and ignore from now on
        imgFile = os.path.join(self.icon_path, "pin.gif")
        try:
            imgObj = self.__getImage(imgFile)
            self.pinBut = Label(self.tb)
        except:
            return
            
        # if image found, then set up the label
        if self.pinBut is not None:
            self.pinBut.config(image=imgObj)#, compound=TOP, text="", justify=LEFT)
            self.pinBut.image = imgObj  # keep a reference!
            self.pinBut.pack(side=RIGHT, anchor=NE, padx=0, pady=0)

            if gui.GET_PLATFORM() == gui.MAC:
                self.pinBut.config(cursor="pointinghand")
            elif gui.GET_PLATFORM() in [gui.WINDOWS, gui.LINUX]:
                self.pinBut.config(cursor="hand2")

            self.pinBut.eventId = self.pinBut.bind("<Button-1>", self.__toggletb)
            self.__addTooltip(self.pinBut, "Click here to pin/unpin the toolbar.", True)

    # called by pinBut, to toggle the pin status of the toolbar
    def __toggletb(self, event=None):
        self.setToolbarPinned(not self.tbPinned)

    def setToolbarPinned(self, pinned=True):
        self.tbPinned = pinned
        self.__setPinBut()
        if not self.tbPinned:
            if self.pinBut is not None:
                try:
                    self.pinBut.image = self.__getImage(os.path.join(self.icon_path, "unpin.gif"))
                except:
                    pass
            if not self.tbMinMade:
                self.tbMinMade = True
                self.tbm = Frame(self.appWindow, bd=1, relief=RAISED)
                self.tbm.config(bg="gray", height=3)
                self.tb.bind("<Leave>", self.__minToolbar)
                self.tbm.bind("<Enter>", self.__maxToolbar)
            self.__minToolbar()
        else:
            if self.pinBut is not None:
                try:
                    self.pinBut.image = self.__getImage(os.path.join(self.icon_path, "pin.gif"))
                except:
                    pass
            self.__maxToolbar()

        if self.pinBut is not None:
            self.pinBut.config(image=self.pinBut.image)

    def setToolbarIcon(self, name, icon):
        if (name not in self.n_tbButts):
            raise Exception("Unknown toolbar name: " + name)
        imgFile = os.path.join(self.icon_path, icon.lower() + ".png")
        with PauseLogger():
            self.setToolbarImage(name, imgFile)
        self.n_tbButts[name].tt_var.set(icon)

    def setToolbarImage(self, name, imgFile):
        if (name not in self.n_tbButts):
            raise Exception("Unknown toolbar name: " + name)
        image = self.__getImage(imgFile)
        self.n_tbButts[name].config(image=image)
        self.n_tbButts[name].image = image

    def setToolbarButtonEnabled(self, name):
        self.setToolbarButtonDisabled(name, False)

    def setToolbarButtonDisabled(self, name, disabled=True):
        if (name not in self.n_tbButts):
            raise Exception("Unknown toolbar name: " + name)
        if disabled:
            self.n_tbButts[name].config(state=DISABLED)
        else:
            self.n_tbButts[name].config(state=NORMAL)

    def setToolbarEnabled(self):
        self.setToolbarDisabled(False)

    def setToolbarDisabled(self, disabled=True):
        for but in self.n_tbButts.keys():
            if disabled:
                self.n_tbButts[but].config(state=DISABLED)
            else:
                self.n_tbButts[but].config(state=NORMAL)

        if self.pinBut is not None:
            if disabled:
                # this fails if not bound
                if self.pinBut.eventId:
                    self.pinBut.unbind("<Button-1>", self.pinBut.eventId)
                self.pinBut.eventId = None
                self.__disableTooltip(self.pinBut)
                self.pinBut.config(cursor="")
            else:
                if gui.GET_PLATFORM() == gui.MAC:
                    self.pinBut.config(cursor="pointinghand")
                elif gui.GET_PLATFORM() in [gui.WINDOWS, gui.LINUX]:
                    self.pinBut.config(cursor="hand2")

                self.pinBut.eventId = self.pinBut.bind("<Button-1>", self.__toggletb)
                self.__enableTooltip(self.pinBut)

    def __minToolbar(self, e=None):
        if not self.tbPinned:
            if self.tbMinMade:
                self.tbm.config(width=self.tb.winfo_reqwidth())
                self.tbm.pack(before=self.containerStack[0]['container'], side=TOP, fill=X)
            self.tb.pack_forget()

    def __maxToolbar(self, e=None):
        self.tb.pack(before=self.containerStack[0]['container'], side=TOP, fill=X)
        if self.tbMinMade:
            self.tbm.pack_forget()

    # functions to hide & show the toolbar
    def hideToolbar(self):
        if self.hasTb:
            self.tb.pack_forget()
            if self.tbMinMade:
                self.tbm.pack_forget()

    def showToolbar(self):
        if self.hasTb:
            self.tb.pack(before=self.containerStack[0][
                         'container'], side=TOP, fill=X)
            if self.tbMinMade:
                self.tbm.pack_forget()

#####################################
# FUNCTIONS for menu bar
#####################################
    def __initMenu(self):
        # create a menu bar - only shows if populated
        if not self.hasMenu:
            #            self.topLevel.option_add('*tearOff', FALSE)
            self.hasMenu = True
            self.menuBar = Menu(self.topLevel)
            if self.platform == self.MAC:
                appmenu = Menu(self.menuBar, name='apple')
                self.menuBar.add_cascade(menu=appmenu)
                self.n_menus["MAC_APP"] = appmenu
            elif self.platform == self.WINDOWS:
                # sysMenu must be added last, otherwise other menus vanish
                sysMenu = Menu(self.menuBar, name='system', tearoff=False)
                self.n_menus["WIN_SYS"] = sysMenu

    # add a parent menu, for menu items
    def createMenu(self, title, tearable=False, showInBar=True):
        self.__verifyItem(self.n_menus, title, True)
        self.__initMenu()

        if title == "WIN_SYS" and self.platform != self.WINDOWS:
            self.warn("The WIN_SYS menu is specific to Windows")
            return None

        if self.platform == self.MAC and tearable:
            self.warn("Tearable menus (" + title + ") not supported on MAC")
            tearable = False
        theMenu = Menu(self.menuBar, tearoff=tearable)
        if showInBar:
            self.menuBar.add_cascade(label=title, menu=theMenu)
        self.n_menus[title] = theMenu
        return theMenu

    def createRightClickMenu(self, title, showInBar=False):
        men = self.createMenu(title, False, showInBar)
        if men is not None and gui.GET_PLATFORM() == gui.LINUX:
            self.addMenuSeparator(title)
        return men

    # add items to the named menu
    def addMenuItem(
            self,
            title,
            item,
            func=None,
            kind=None,
            shortcut=None,
            underline=-1,
            rb_id=None,
            createBinding=True):
        # set the initial menubar
        self.__initMenu()

        # get or create an initial menu
        if title is not None:
            try:
                theMenu = self.__verifyItem(self.n_menus, title, False)
            except:
                theMenu = self.createMenu(title)
                if theMenu is None:
                    return

        if underline > -1 and self.platform == self.MAC:
            self.warn("Underlining menu items not available on MAC")

        if func is not None:
            u = self.MAKE_FUNC(func, item, True)
        else:
            u = None

        a = b = None
        if shortcut is not None:
            #            MODIFIERS=["Control", "Ctrl", "Option", "Opt", "Alt", "Shift", "Command", "Cmd", "Meta"]

            # UGLY formatting of accelerator & shortcut
            a = b = shortcut.lower().replace("+", "-")

            a = a.replace("control", "ctrl")
            a = a.replace("command", "cmd")
            a = a.replace("option", "opt")

            b = b.replace("ctrl", "Control")
            b = b.replace("control", "Control")
            b = b.replace("cmd", "Command")
            b = b.replace("command", "Command")
            b = b.replace("option", "Option")
            b = b.replace("opt", "Option")
            b = b.replace("alt", "Alt")
            b = b.replace("shift", "Shift")
            b = b.replace("meta", "Meta")

            if gui.GET_PLATFORM() != gui.MAC:
                a = a.replace("cmd", "ctrl")
                b = b.replace("Command", "Control")

            b = "<" + b + ">"
            a = a.title()

            self.__verifyItem(self.n_accelerators, a, True)
            self.n_accelerators.append(a)
            if u is not None and createBinding:
                self.topLevel.bind_all(b, u)

        if item == "-" or kind == "separator":
            theMenu.add_separator()
        elif kind == "topLevel" or title is None:
            if self.platform == self.MAC:
                self.warn(
                    "Unable to make topLevel menus (" + item + ") on Mac")
            else:
                self.menuBar.add_command(
                    label=item, command=u, accelerator=a, underline=underline)
        elif kind == "rb":
            varName = title + "rb" + item
            newRb = False
            if (varName in self.n_menuVars):
                var = self.n_menuVars[varName]
            else:
                newRb = True
                var = StringVar(self.topLevel)
                self.n_menuVars[varName] = var
            theMenu.add_radiobutton(
                label=rb_id,
                command=u,
                variable=var,
                value=rb_id,
                accelerator=a,
                underline=underline)
            if newRb:
                self.setMenuRadioButton(title, item, rb_id)
        elif kind == "cb":
            varName = title + "cb" + item
            self.__verifyItem(self.n_menuVars, varName, True)
            var = StringVar(self.topLevel)
            self.n_menuVars[varName] = var
            theMenu.add_checkbutton(
                label=item,
                command=u,
                variable=var,
                onvalue=1,
                offvalue=0,
                accelerator=a,
                underline=underline)
        elif kind == "sub":
            self.__verifyItem(self.n_menus, item, True)
            subMenu = Menu(theMenu, tearoff=False)
            self.n_menus[item] = subMenu
            theMenu.add_cascade(menu=subMenu, label=item)
        else:
            theMenu.add_command(
                label=item,
                command=u,
                accelerator=a,
                underline=underline)

    #################
    # wrappers for other menu types

    def addMenuList(self, menuName, names, funcs):
        # deal with a dict_keys object - messy!!!!
        if not isinstance(names, list):
            names = list(names)

        # append some Nones, if it's a list and contains separators
        if funcs is not None:
            if not callable(funcs):
                seps = names.count("-")
                for i in range(seps):
                    funcs.append(None)
            singleFunc = self.__checkFunc(names, funcs)

        # add menu items
        for t in names:
            if funcs is None:
                u = None
            elif singleFunc is not None:
                u = singleFunc
            else:
                u = funcs.pop(0)

            self.addMenuItem(menuName, t, u)

    def __checkCopyAndPaste(self, event, widget=None):
        if self.copyAndPaste.inUse:
            if event is None or not (
                    event.type == "10" and self.GET_PLATFORM() == self.LINUX):
                self.disableMenu("EDIT", 10)

            if event is not None:
                widget = event.widget

            # 9 = ENTER/10 = LEAVE/4=RCLICK/3=PRESS/2=PASTE
            if event is None or event.type in ["9", "3", "4", "2"]:
                self.copyAndPaste.setUp(widget)
                if self.copyAndPaste.canCopy:
                    self.enableMenuItem("EDIT", "Copy")
                if self.copyAndPaste.canCut:
                    self.enableMenuItem("EDIT", "Cut")
                if self.copyAndPaste.canPaste:
                    self.enableMenuItem("EDIT", "Paste")
                    self.enableMenuItem("EDIT", "Clear Clipboard")
                if self.copyAndPaste.canSelect:
                    self.enableMenuItem("EDIT", "Select All")
                    self.enableMenuItem("EDIT", "Clear All")
                if self.copyAndPaste.canUndo:
                    self.enableMenuItem("EDIT", "Undo")
                if self.copyAndPaste.canRedo:
                    self.enableMenuItem("EDIT", "Redo")
            return True
        else:
            return False

    # called when copy/paste menu items are clicked
    def __copyAndPasteHelper(self, menu):
        widget = self.topLevel.focus_get()
        self.copyAndPaste.setUp(widget)

        if menu == "Cut":
            self.copyAndPaste.cut()
        elif menu == "Copy":
            self.copyAndPaste.copy()
        elif menu == "Paste":
            self.copyAndPaste.paste()
        elif menu == "Select All":
            self.copyAndPaste.selectAll()
        elif menu == "Clear Clipboard":
            self.copyAndPaste.clearClipboard()
        elif menu == "Clear All":
            self.copyAndPaste.clearText()
        elif menu == "Undo":
            self.copyAndPaste.undo()
        elif menu == "Redo":
            self.copyAndPaste.redo()

    # add a single entry for a menu
    def addSubMenu(self, menu, subMenu):
        self.addMenuItem(menu, subMenu, None, "sub")

    def addMenu(self, name, func, shortcut=None, underline=-1):
        self.addMenuItem(None, name, func, "topLevel", shortcut, underline)

    def addMenuSeparator(self, menu):
        self.addMenuItem(menu, "-")

    def addMenuCheckBox(
            self,
            menu,
            name,
            func=None,
            shortcut=None,
            underline=-1):
        self.addMenuItem(menu, name, func, "cb", shortcut, underline)

    def addMenuRadioButton(
            self,
            menu,
            name,
            value,
            func=None,
            shortcut=None,
            underline=-1):
        self.addMenuItem(menu, name, func, "rb", shortcut, underline, value)

    #################
    # wrappers for setters

    def __setMenu(self, menu, title, value, kind):
        title = menu + kind + title
        var = self.__verifyItem(self.n_menuVars, title)
        if kind == "rb":
            var.set(value)
        elif kind == "cb":
            if value is True:
                var.set("1")
            elif value is False:
                var.set("0")
            else:
                if var.get() == "1":
                    var.set("0")
                else:
                    var.set("1")

    def setMenuCheckBox(self, menu, name, value=None):
        self.__setMenu(menu, name, value, "cb")

    def setMenuRadioButton(self, menu, name, value):
        self.__setMenu(menu, name, value, "rb")

    # set align = "none" to remove text
    def setMenuImage(self, menu, title, image, align="left"):
        theMenu = self.__verifyItem(self.n_menus, menu)
        imageObj = self.__getImage(image)
        if 16 != imageObj.width() or imageObj.width() != imageObj.height():
            self.warn("Invalid image resolution for menu item " +
                      title + " (" + image + ") - should be 16x16")
            #imageObj = imageObj.subsample(2,2)
        theMenu.entryconfigure(title, image=imageObj, compound=align)

    def setMenuIcon(self, menu, title, icon, align="left"):
        image = os.path.join(self.icon_path, icon.lower() + ".png")
        with PauseLogger():
            self.setMenuImage(menu, title, image, align)

    def disableMenubar(self):
        for theMenu in self.n_menus:
            self.disableMenu(theMenu)

        # loop through top level menus
        # and diable any that got missed
        numMenus = self.menuBar.index("end")
        if numMenus is not None:
            for item in range(numMenus+1):
                self.menuBar.entryconfig(item, state=DISABLED)

    def enableMenubar(self):
        for theMenu in self.n_menus:
            self.enableMenu(theMenu)

        # loop through toplevel menus
        # and enable anythat got missed
        numMenus = self.menuBar.index("end")
        if numMenus is not None:
            for item in range(numMenus+1):
                self.menuBar.entryconfig(item, state=NORMAL)

    def disableMenu( self, title, limit=None):
        self.__changeMenuState(title, DISABLED, limit)

    def enableMenu( self, title, limit=None):
        self.__changeMenuState(title, NORMAL, limit)

    def __changeMenuState(self, title, state, limit=None):
        theMenu = self.__verifyItem(self.n_menus, title)
        numMenus = theMenu.index("end")
        if numMenus is not None:  # MAC_APP (and others?) returns None
            for item in range(numMenus + 1):
                if limit is not None and limit == item:
                    break
                try:
                    theMenu.entryconfigure(item, state=state)
                except:
                    pass  # separator
        # also diable the toplevel menu that matches this one
        try:
            self.menuBar.entryconfig(self.menuBar.index(title), state=state)
        except TclError:
            # ignore if we fail...
            pass

    def disableMenuItem(self, title, item):
        theMenu = self.__verifyItem(self.n_menus, title)
        theMenu.entryconfigure(item, state=DISABLED)

    def enableMenuItem(self, title, item):
        theMenu = self.__verifyItem(self.n_menus, title)
        theMenu.entryconfigure(item, state=NORMAL)

    def renameMenu(self, title, newName):
        theMenu = self.__verifyItem(self.n_menus, title)
        self.menuBar.entryconfigure(title, label=newName)

    def renameMenuItem(self, title, item, newName):
        theMenu = self.__verifyItem(self.n_menus, title)
        theMenu.entryconfigure(item, label=newName)

    #################
    # wrappers for getters

    def __getMenu(self, menu, title, kind):
        title = menu + kind + title
        var = self.__verifyItem(self.n_menuVars, title)
        if kind == "rb":
            return var.get()
        elif kind == "cb":
            if var.get() == "1":
                return True
            else:
                return False

    def getMenuCheckBox(self, menu, title):
        return self.__getMenu(menu, title, "cb")

    def getMenuRadioButton(self, menu, title):
        return self.__getMenu(menu, title, "rb")

    #################
    # wrappers for platform specific menus

    # enables the preferences item in the app menu
    def addMenuPreferences(self, func):
        if self.platform == self.MAC:
            self.__initMenu()
            u = self.MAKE_FUNC(func, "preferences")
            self.topLevel.createcommand('tk::mac::ShowPreferences', u)
        else:
            self.warn("The Preferences Menu is specific to Mac OSX")

    # MAC help menu
    def addMenuHelp(self, func):
        if self.platform == self.MAC:
            self.__initMenu()
            helpMenu = Menu(self.menuBar, name='help')
            self.menuBar.add_cascade(menu=helpMenu, label='Help')
            u = self.MAKE_FUNC(func, "help")
            self.topLevel.createcommand('tk::mac::ShowHelp', u)
            self.n_menus["MAC_HELP"] = helpMenu
        else:
            self.warn("The Help Menu is specific to Mac OSX")

    # Shows a Window menu
    def addMenuWindow(self):
        if self.platform == self.MAC:
            self.__initMenu()
            windowMenu = Menu(self.menuBar, name='window')
            self.menuBar.add_cascade(menu=windowMenu, label='Window')
            self.n_menus["MAC_WIN"] = windowMenu
        else:
            self.warn("The Window Menu is specific to Mac OSX")

    # adds an edit menu - by default only as a pop-up
    # if inMenuBar is True - then show in menu too
    def addMenuEdit(self, inMenuBar=False):
        self.__initMenu()
        editMenu = Menu(self.menuBar, tearoff=False)
        if inMenuBar:
            self.menuBar.add_cascade(menu=editMenu, label='Edit ')
        self.n_menus["EDIT"] = editMenu
        self.copyAndPaste.inUse = True

        if gui.GET_PLATFORM() == gui.LINUX:
            self.addMenuSeparator("EDIT")

        if gui.GET_PLATFORM() == gui.MAC:
            shortcut = "Cmd+"
        else:
            shortcut = "Control-"

        eList = [
            ('Cut',
             lambda e: self.__copyAndPasteHelper("Cut"),
             "X",
             False),
            ('Copy',
             lambda e: self.__copyAndPasteHelper("Copy"),
             "C",
             False),
            ('Paste',
             lambda e: self.__copyAndPasteHelper("Paste"),
             "V",
             False),
            ('Select All',
             lambda e: self.__copyAndPasteHelper("Select All"),
             "A",
             True if gui.GET_PLATFORM() == gui.MAC else False),
            ('Clear Clipboard',
             lambda e: self.__copyAndPasteHelper("Clear Clipboard"),
             "B",
             True)]

        for (txt, cmd, sc, bind) in eList:
            acc = shortcut + sc
            self.addMenuItem(
                "EDIT",
                txt,
                cmd,
                shortcut=acc,
                createBinding=bind)

        # add a clear option
        self.addMenuSeparator("EDIT")
        self.addMenuItem(
            "EDIT",
            "Clear All",
            lambda e: self.__copyAndPasteHelper("Clear All"))

        self.addMenuSeparator("EDIT")
        self.addMenuItem(
            "EDIT",
            'Undo',
            lambda e: self.__copyAndPasteHelper("Undo"),
            shortcut=shortcut + "Z",
            createBinding=False)
        self.addMenuItem("EDIT", 'Redo', lambda e: self.__copyAndPasteHelper(
            "Redo"), shortcut="Shift-" + shortcut + "Z", createBinding=True)
        self.disableMenu("EDIT")

    def appJarAbout(self, menu=None):
        self.infoBox("About appJar",
                        "---\n" +
                        __copyright__ + "\n" +
                        "---\n\t" +
                        gui.SHOW_VERSION().replace("\n", "\n\t") + "\n" +
                        "---\n" +
                        gui.SHOW_PATHS() + "\n" +
                        "---")

    def appJarHelp(self, menu=None):
        self.infoBox("appJar Help", "For help, visit " + __url__)

    def addAppJarMenu(self):
        if self.platform == self.MAC:
            self.addMenuItem("MAC_APP", "About appJar", self.appJarAbout)
            self.addMenuWindow()
            self.addMenuHelp(self.appJarHelp)
        elif self.platform == self.WINDOWS:
            self.addMenuSeparator('WIN_SYS')
            self.addMenuItem("WIN_SYS", "About appJar", self.appJarAbout)
            self.addMenuItem("WIN_SYS", "appJar Help", self.appJarHelp)

#####################################
# FUNCTIONS for status bar
#####################################
    def addStatus(self, header="", fields=1, side=None):
        self.warn("addStatus() is deprecated, please use addStatusbar()")
        self.addStatusbar(header, fields, side)

    def addStatusbar(self, header="", fields=1, side=None):
        self.hasStatus = True
        self.header = header
        self.statusFrame = Frame(self.appWindow)
        self.statusFrame.config(bd=1, relief=SUNKEN)
        self.statusFrame.pack(side=BOTTOM, fill=X, anchor=S)

        self.status = []
        for i in range(fields):
            self.status.append(Label(self.statusFrame))
            self.status[i].config(
                bd=1,
                relief=SUNKEN,
                anchor=W,
                font=self.statusFont,
                width=10)
            self.__addTooltip(self.status[i], "Status bar", True)

            if side == "LEFT":
                self.status[i].pack(side=LEFT)
            elif side == "RIGHT":
                self.status[i].pack(side=RIGHT)
            else:
                self.status[i].pack(side=LEFT, expand=1, fill=BOTH)

    def setStatusbarHeader(self, header):
        if self.hasStatus:
            self.header = header

    def setStatus(self, text, field=0):
        self.warn("setStatus() is deprecated, please use setStatusbar()")
        self.setStatusbar(text, field)

    def setStatusbar(self, text, field=0):
        if self.hasStatus:
            if field is None:
                for status in self.status:
                    status.config(text=self.__getFormatStatus(text))
            elif field >= 0 and field < len(self.status):
                self.status[field].config(text=self.__getFormatStatus(text))
            else:
                raise Exception("Invalid status field: " + str(field) +
                                ". Must be between 0 and " + str(len(self.status) - 1))

    def setStatusBg(self, colour, field=None):
        self.warn("setStatusBg() is deprecated, please use setStatusbarBg()")
        self.setStatusbarBg(colour, field)

    def setStatusbarBg(self, colour, field=None):
        if self.hasStatus:
            if field is None:
                for status in self.status:
                    status.config(background=colour)
            elif field >= 0 and field < len(self.status):
                self.status[field].config(background=colour)
            else:
                raise Exception("Invalid status field: " + str(field) +
                                ". Must be between 0 and " + str(len(self.status) - 1))

    def setStatusbarFg(self, colour, field=None):
        if self.hasStatus:
            if field is None:
                for status in self.status:
                    status.config(foreground=colour)
            elif field >= 0 and field < len(self.status):
                self.status[field].config(foreground=colour)
            else:
                raise Exception("Invalid status field: " + str(field) +
                                ". Must be between 0 and " + str(len(self.status) - 1))

    def setStatusbarWidth(self, width, field=None):
        if self.hasStatus:
            if field is None:
                for status in self.status:
                    status.config(width=width)
            elif field >= 0 and field < len(self.status):
                self.status[field].config(width=width)
            else:
                raise Exception("Invalid status field: " + str(field) +
                                ". Must be between 0 and " + str(len(self.status) - 1))

    def clearStatusbar(self, field=None):
        if self.hasStatus:
            if field is None:
                for status in self.status:
                    status.config(text=self.__getFormatStatus(""))
            elif field >= 0 and field < len(self.status):
                self.status[field].config(text=self.__getFormatStatus(""))
            else:
                raise Exception("Invalid status field: " + str(field) +
                                ". Must be between 0 and " + str(len(self.status) - 1))

    # formats the string shown in the status bar
    def __getFormatStatus(self, text):
        text = str(text)
        if len(text) == 0:
            return ""
        elif len(self.header) == 0:
            return text
        else:
            return self.header + ": " + text
#####################################
# TOOLTIPS
#####################################

    def __addTooltip(self, item, text, hideWarn=False):
        self.__loadTooltip()
        if not ToolTip:
            if not hideWarn:
                self.warn("ToolTips unavailable - check tooltip.py is in the lib folder")
        elif text == "":
            self.__disableTooltip(item)
        else:
            # turn off warnings about tooltips
            with PauseLogger():
                # if there's already  tt, just change it
                if hasattr(item, "tt_var"):
                    item.tt_var.set(text)
                # otherwise create one
                else:
                    var = StringVar(self.topLevel)
                    var.set(text)
                    tip = ToolTip(item, delay=500, follow_mouse=1, textvariable=var)
                    item.tooltip = tip
                    item.tt_var = var

            return item.tt_var

    def __enableTooltip(self, item):
        if hasattr(item, "tooltip"):
            item.tooltip.configure(state="normal")
        else:
            self.warn("Unable to enable tooltip - none present.")

    def __disableTooltip(self, item):
        if hasattr(item, "tooltip"):
            item.tooltip.configure(state="disabled")
        else:
            self.warn("Unable to disable tooltip - none present.")

#####################################
# FUNCTIONS to show pop-up dialogs
#####################################
    # function to access the last made pop_up
    def getPopUp(self):
        return self.topLevel.POP_UP

    def infoBox(self, title, message, parent=None):
        self.topLevel.update_idletasks()
        if parent is None:
            MessageBox.showinfo(title, message)
        else:
            opts = {"parent": self.n_subWindows[parent]}
            MessageBox.showinfo(title, message, **opts)
        self.__bringToFront()

    def errorBox(self, title, message, parent=None):
        self.topLevel.update_idletasks()
        if parent is None:
            MessageBox.showerror(title, message)
        else:
            opts = {"parent": self.n_subWindows[parent]}
            MessageBox.showerror(title, message, **opts)
        self.__bringToFront()

    def warningBox(self, title, message, parent=None):
        self.topLevel.update_idletasks()
        if parent is None:
            MessageBox.showwarning(title, message)
        else:
            opts = {"parent": self.n_subWindows[parent]}
            MessageBox.showwarning(title, message, **opts)
        self.__bringToFront()

    def yesNoBox(self, title, message, parent=None):
        self.topLevel.update_idletasks()
        if parent is None:
            return MessageBox.askyesno(title, message)
        else:
            opts = {"parent": self.n_subWindows[parent]}
            return MessageBox.askyesno(title=title, message=message, **opts)

    def questionBox(self, title, message, parent=None):
        self.topLevel.update_idletasks()
        if parent is None:
            return MessageBox.askquestion(title, message)
        else:
            opts = {"parent": self.n_subWindows[parent]}
            return MessageBox.askquestion(title, message, **opts)

    def okBox(self, title, message, parent=None):
        self.topLevel.update_idletasks()
        title, message = self.__translatePopup(title, message)
        if parent is None:
            return MessageBox.askokcancel(title, message)
        else:
            opts = {"parent": self.n_subWindows[parent]}
            return MessageBox.askokcancel(title, message, **opts)

    def retryBox(self, title, message, parent=None):
        self.topLevel.update_idletasks()
        if parent is None:
            return MessageBox.askretrycancel(title, message)
        else:
            opts = {"parent": self.n_subWindows[parent]}
            return MessageBox.askretrycancel(title, message, **opts)

    def openBox(self, title=None, dirName=None, fileTypes=None, asFile=False, parent=None):

        self.topLevel.update_idletasks()

        # define options for opening
        options = {}

        if title is not None:
            options['title'] = title
        if dirName is not None:
            options['initialdir'] = dirName
        if fileTypes is not None:
            options['filetypes'] = fileTypes
        if parent is not None:
            options["parent"] = self.n_subWindows[parent]

        if asFile:
            return filedialog.askopenfile(mode="r", **options)
        # will return "" if cancelled
        else:
            return filedialog.askopenfilename(**options)

    def saveBox( self, title=None, fileName=None, dirName=None, fileExt=".txt",
            fileTypes=None, asFile=False, parent=None):
        self.topLevel.update_idletasks()
        if fileTypes is None:
            fileTypes = [('all files', '.*'), ('text files', '.txt')]
        # define options for opening
        options = {}
        options['defaultextension'] = fileExt
        options['filetypes'] = fileTypes
        options['initialdir'] = dirName
        options['initialfile'] = fileName
        options['title'] = title
        if parent is not None:
            options["parent"] = self.n_subWindows[parent]

        if asFile:
            return filedialog.asksaveasfile(mode='w', **options)
        # will return "" if cancelled
        else:
            return filedialog.asksaveasfilename(**options)

    def directoryBox(self, title=None, dirName=None, parent=None):
        self.topLevel.update_idletasks()
        options = {}
        options['initialdir'] = dirName
        options['title'] = title
        options['mustexist'] = False
        if parent is not None:
            options["parent"] = self.n_subWindows[parent]

        fileName = filedialog.askdirectory(**options)

        if fileName == "":
            return None
        else:
            return fileName

    def colourBox(self, colour='#ff0000', parent=None):
        self.topLevel.update_idletasks()
        if parent is None:
            col = askcolor(colour)
        else:
            opts = {"parent": self.n_subWindows[parent]}
            col = askcolor(colour, **opts)

        if col[1] is None:
            return None
        else:
            return col[1]

    def textBox(self, title, question, defaultValue=None, parent=None):
        self.topLevel.update_idletasks()
        if defaultValue is not None:
            defaultVar = StringVar(self.topLevel)
            defaultVar.set(defaultValue)
        else:
            defaultVar = None
        if parent is None:
            parent = self.topLevel
        else:
            parent = self.n_subWindows[parent]

        return TextDialog(parent, title, question, defaultVar=defaultVar).result

    def numberBox(self, title, question, parent=None):
        return self.numBox(title, question, parent)

    def numBox(self, title, question, parent=None):
        self.topLevel.update_idletasks()
        if parent is None:
            parent = self.topLevel
        else:
            parent = self.n_subWindows[parent]

        return NumDialog(parent, title, question).result

#####################################
# ProgressBar Class
# from: http://tkinter.unpythonic.net/wiki/ProgressMeter
# A gradient fill will be applied to the Meter
#####################################
class Meter(Frame):

    def __init__(self, master, width=100, height=20,
            bg='#FFFFFF', fillColour='orchid1',
            value=0.0, text=None, font=None,
            fg='#000000', *args, **kw):

        # call the super constructor
        Frame.__init__(self, master, bg=bg,
            width=width, height=height, relief='ridge', bd=3, *args, **kw)

        # remember the starting value
        self._value = value
        self._colour = fillColour
        self._midFill = fg

        # create the canvas
        self._canv = Canvas(self, bg=self['bg'],
            width=self['width'], height=self['height'],
            highlightthickness=0, relief='flat', bd=0)
        self._canv.pack(fill='both', expand=1)

        # create the text
        width, height = self.getWH(self._canv)
        self._text = self._canv.create_text(
            width / 2, height / 2, text='', fill=fg)

        if font:
            self._canv.itemconfigure(self._text, font=font)

        self.set(value, text)
        self.moveText()

        # bind refresh event
        self.bind('<Configure>', self._update_coords)

    # customised config setters
    def config(self, cnf=None, **kw):
        self.configure(cnf, **kw)

    def configure(self, cnf=None, **kw):
        # properties to propagate to CheckBoxes
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)

        if "fill" in kw:
            self._colour = kw.pop("fill")
        if "fg" in kw:
            col = kw.pop("fg")
            self._canv.itemconfigure(self._text, fill=col)
            self._midFill = col
        if "bg" in kw:
            self._canv.config(bg=kw.pop("bg"))

        if "width" in kw:
            self._canv.config(width=kw.pop("width"))
        if "height" in kw:
            self._canv.config(height=kw.pop("height"))
        if "font" in kw:
            self._canv.itemconfigure(self._text, font=kw.pop("fillColour"))

        # propagate anything left
        if PYTHON2:
            Frame.config(self, cnf, **kw)
        else:
            super(__class__, self).config(cnf, **kw)

        self.makeBar()

    # called when resized
    def _update_coords(self, event):
        '''Updates the position of the text and rectangle inside the canvas
            when the size of the widget gets changed.'''
        self.makeBar()
        self.moveText()

    # getter
    def get(self):
        val = self._value
        try:
            txt = self._canv.itemcget(self._text, 'text')
        except:
            txt = None
        return val, txt

    # update the variables, then call makeBar
    def set(self, value=0.0, text=None):
        # make the value failsafe:
        value = value / 100.0
        if value < 0.0:
            value = 0.0
        elif value > 1.0:
            value = 1.0
        self._value = value

        # if no text is specified use the default percentage string:
        if text is None:
            text = str(int(round(100 * value))) + ' %'

        # set the new text
        self._canv.itemconfigure(self._text, text=text)
        self.makeBar()

    # draw the bar
    def makeBar(self):
        width, height = self.getWH(self._canv)
        start = 0
        fin = width * self._value

        self.drawLines(width, height, start, fin, self._value, self._colour)
        self._canv.update_idletasks()

    # move the text
    def moveText(self):
        width, height = self.getWH(self._canv)
        if hasattr(self, "_text"):
            self._canv.coords( self._text, width/2, height/2)

    # draw gradated lines, in given coordinates
    # using the specified colour
    def drawLines(self, width, height, start, fin, val, col, tags="gradient"):
        '''Draw a gradient'''
        # http://stackoverflow.com/questions/26178869/is-it-possible-to-apply-gradient-colours-to-bg-of-tkinter-python-widgets

        # remove the lines & midline
        self._canv.delete(tags)
        self._canv.delete("midline")

        # determine start & end colour
        (r1, g1, b1) = self.tint(col, -30000)
        (r2, g2, b2) = self.tint(col, 30000)

        # determine a direction & range
        if val < 0:
            direction = -1
            limit = int(start - fin)
        else:
            direction = 1
            limit = int(fin - start)

        # if lines to draw
        if limit != 0:
            # work out the ratios
            r_ratio = float(r2 - r1) / limit
            g_ratio = float(g2 - g1) / limit
            b_ratio = float(b2 - b1) / limit

            # loop through the range of lines, in the right direction
            modder = 0
            for i in range(int(start), int(fin), direction):
                nr = int(r1 + (r_ratio * modder))
                ng = int(g1 + (g_ratio * modder))
                nb = int(b1 + (b_ratio * modder))

                colour = "#%4.4x%4.4x%4.4x" % (nr, ng, nb)
                self._canv.create_line(
                    i, 0, i, height, tags=(tags,), fill=colour)
                modder += 1
            self._canv.lower(tags)

        # draw a midline
        self._canv.create_line(start, 0, start, height,
            fill=self._midFill, tags=("midline",))

        self._canv.update_idletasks()

    # function to calculate a tint
    def tint(self, col, brightness_offset=1):
        ''' dim or brighten the specified colour by the specified offset '''
        # http://chase-seibert.github.io/blog/2011/07/29/python-calculate-lighterdarker-rgb-colors.html
        rgb_hex = self._canv.winfo_rgb(col)
        new_rgb_int = [hex_value + brightness_offset for hex_value in rgb_hex]
        # make sure new values are between 0 and 65535
        new_rgb_int = [min([65535, max([0, i])]) for i in new_rgb_int]
        return new_rgb_int

    def getWH(self, widg):
        # ISSUES HERE:
        # on MAC & LINUX, w_width/w_height always 1
        # on WIN, w_height is bigger then r_height - leaving empty space

        self._canv.update_idletasks()

        r_width = widg.winfo_reqwidth()
        r_height = widg.winfo_reqheight()
        w_width = widg.winfo_width()
        w_height = widg.winfo_height()

        max_height = max(r_height, w_height)
        max_width = max(r_width, w_width)

        return (max_width, max_height)


#####################################
# SplitMeter Class extends the Meter above
# Will fill in the empty space with a second fill colour
# Two colours should be provided - left & right fill
#####################################
class SplitMeter(Meter):

    def __init__(self, master, width=100, height=20,
            bg='#FFFFFF', leftfillColour='#FF0000', rightfillColour='#0000FF',
            value=0.0, text=None, font=None, fg='#000000', *args, **kw):

        self._leftFill = leftfillColour
        self._rightFill = rightfillColour

        Meter.__init__(self, master, width=width, height=height,
                    bg=bg, value=value, text=text, font=font,
                    fg=fg, *args, **kw)

    # override the handling of fill
    # list of two colours
    def configure(self, cnf=None, **kw):
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)
        if "fill" in kw:
            cols = kw.pop("fill")
            if not isinstance(cols, list):
                raise Exception("SplitMeter requires a list of two colours")
            else:
                self._leftFill = cols[0]
                self._rightFill = cols[1]

        # propagate any left over confs
        if PYTHON2:
            Meter.configure(self, cnf, **kw)
        else:
            super(SplitMeter, self).configure(cnf, **kw)

    def set(self, value=0.0, text=None):
        # make the value failsafe:
        value = value / 100.0
        if value < 0.0:
            value = 0.0
        elif value > 1.0:
            value = 1.0
        self._value = value
        self.makeBar()

    # override the makeBar function
    def makeBar(self):
        width, height = self.getWH(self._canv)
        mid = width * self._value

        self.drawLines(width, height, 0, mid, self._value, self._leftFill, tags="left")
        self.drawLines(width, height, mid, width, self._value, self._rightFill, tags="right")


#####################################
# SplitMeter Class extends the Meter above
# Used to allow bi-directional metering, starting from a mid point
# Two colours should be provided - left & right fill
# A gradient fill will be applied to the Meter
#####################################
class DualMeter(SplitMeter):

    def __init__(self, master, width=100, height=20, bg='#FFFFFF',
            leftfillColour='#FFC0CB', rightfillColour='#00FF00',
            value=None, text=None,
            font=None, fg='#000000', *args, **kw):

        SplitMeter.__init__(self, master, width=width, height=height,
                    bg=bg, leftfillColour=leftfillColour,
                    rightfillColour=rightfillColour,
                    value=value, text=text, font=font,
                    fg=fg, *args, **kw)

    def set(self, value=[0,0], text=None):
        if value is None:
            value=[0,0]
        if not isinstance(value, list):
            raise Exception("DualMeter.set() requires a list of two arguments")

        # make copy, and reduce to decimal
        vals = [value[0]/100.0, value[1]/100.0]

        # normalise
        if vals[0] < -1: vals[0] = -1.0
        elif vals[0] > 0: vals[0] = vals[0] * -1

        if vals[1] > 1.0: vals[1] = 1.0
        elif vals[1] < 0: vals[1] = 0
        elif vals[1] < -1: vals[1] = -1.0

        self._value = vals

        # if no text is specified use the default percentage string:
        if text is not None:
            # set the new text
            self._canv.itemconfigure(self._text, text=text)

        self.makeBar()

    def makeBar(self):
        # get range to draw lines
        width, height = self.getWH(self._canv)

        start = width / 2
        l_fin = start + (start * self._value[0])
        r_fin = start + (start * self._value[1])

        self.drawLines(width, height, start, l_fin, self._value[0], self._leftFill, tags="left")
        self.drawLines(width, height, start, r_fin, self._value[1], self._rightFill, tags="right")


#################################
# TabbedFrame Class
#################################
class TabbedFrame(Frame):

    def __init__(
            self,
            master,
            bg,
            fill=False,
            changeOnFocus=True,
            *args,
            **kwargs):

        # main frame & tabContainer inherit BG colour
        Frame.__init__(self, master, bg=bg)

        # create two containers
        self.tabContainer = Frame(self, bg=bg)
        self.paneContainer = Frame(self, relief=SUNKEN, bd=2, bg=bg, **kwargs)

        # grid the containers
        Grid.columnconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=1)
        self.fill = fill
        if self.fill:
            self.tabContainer.grid(row=0, sticky=W + E)
        else:
            self.tabContainer.grid(row=0, sticky=W)
        self.paneContainer.grid(row=1, sticky="NESW")

        # nain store dictionary: name = [tab, pane]
        from collections import OrderedDict
        self.widgetStore = OrderedDict()

        self.selectedTab = None
        self.highlightedTab = None
        self.changeOnFocus = changeOnFocus
        self.changeEvent = None

        # selected tab & all panes
        self.activeFg = "#0000FF"
        self.activeBg = "#FFFFFF"

        # other tabs
        self.inactiveFg = "#000000"
        self.inactiveBg = "grey"

        # disabled tabs
        self.disabledFg = "lightGray"
        self.disabledBg = "darkGray"

    def config(self, cnf=None, **kw):
        self.configure(cnf, **kw)

    def configure(self, cnf=None, **kw):
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)
        # configure fgs
        if "activeforeground" in kw:
            self.activeFg = kw.pop("activeforeground")
            for key in list(self.widgetStore.keys()):
                self.widgetStore[key][0].config(highlightcolor=self.activeFg)
        if "activebackground" in kw:
            self.activeBg = kw.pop("activebackground")
            for key in list(self.widgetStore.keys()):
                self.widgetStore[key][1].configure(bg=self.activeBg)
                for child in self.widgetStore[key][1].winfo_children():
                    gui.SET_WIDGET_BG(child, self.activeBg)

        if "fg" in kw:
            self.inactiveFg = kw.pop("fg")
        if "inactivebackground" in kw:
            self.inactiveBg = kw.pop("inactivebackground")
        if "inactiveforeground" in kw:
            self.inactiveFg = kw.pop("inactiveforeground")

        if "disabledforeground" in kw:
            self.disabledFg = kw.pop("disabledforeground")
        if "disabledbackground" in kw:
            self.disabledBg = kw.pop("disabledbackground")

        if "bg" in kw:
            self.tabContainer.configure(bg=kw["bg"])
            self.paneContainer.configure(bg=kw["bg"])

        if "command" in kw:
            self.changeEvent = kw.pop("command")

        # update tabs if we have any
        if self.selectedTab is not None:
            self.__colourTabs(False)

        # propagate any left over confs
        if PYTHON2:
            Frame.config(self, cnf, **kw)
        else:
            super(__class__, self).config(cnf, **kw)

    def addTab(self, text, **kwargs):
        # check for duplicates
        if text in self.widgetStore:
            raise ItemLookupError("Duplicate tabName: " + text)

        # create the tab, bind events, pack it in
        tab = Label(
            self.tabContainer,
            text=text,
            highlightthickness=1,
            highlightcolor=self.activeFg,
            relief=SUNKEN,
            cursor="hand2",
            takefocus=1,
            **kwargs)
        tab.disabled = False
        tab.DEFAULT_TEXT = text

        tab.bind("<Button-1>", lambda *args: self.changeTab(text))
        tab.bind("<Return>", lambda *args: self.changeTab(text))
        tab.bind("<space>", lambda *args: self.changeTab(text))
        tab.bind("<FocusIn>", lambda *args: self.__focusIn(text))
        tab.bind("<FocusOut>", lambda *args: self.__focusOut(text))
        if self.fill:
            tab.pack(side=LEFT, ipady=4, ipadx=4, expand=True, fill=BOTH)
        else:
            tab.pack(side=LEFT, ipady=4, ipadx=4)

        # create the pane
        pane = Frame(self.paneContainer, bg=self.activeBg)
        pane.grid(sticky="nsew", row=0, column=0)
        self.paneContainer.grid_columnconfigure(0, weight=1)
        self.paneContainer.grid_rowconfigure(0, weight=1)

        # log the first tab as the selected tab
        if self.selectedTab is None:
            self.selectedTab = text
            tab.focus_set()
        if self.highlightedTab is None:
            self.highlightedTab = text

        self.widgetStore[text] = [tab, pane]
        self.__colourTabs(self.selectedTab)

        return pane

    def getTab(self, title):
        if title not in self.widgetStore.keys():
            raise ItemLookupError("Invalid tab name: " + title)
        else:
            return self.widgetStore[title][1]

    def expandTabs(self, fill=True):
        self.fill = fill

        # update the tabConatiner
        self.tabContainer.grid_forget()
        if self.fill:
            self.tabContainer.grid(row=0, sticky=W + E)
        else:
            self.tabContainer.grid(row=0, sticky=W)

        for key in list(self.widgetStore.keys()):
            tab = self.widgetStore[key][0]
            tab.pack_forget()
            if self.fill:
                tab.pack(side=LEFT, ipady=4, ipadx=4, expand=True, fill=BOTH)
            else:
                tab.pack(side=LEFT, ipady=4, ipadx=4)

    def __focusIn(self, tabName):
        if self.changeOnFocus:
            self.changeTab(tabName)
        else:
            self.highlightedTab = tabName
            self.__colourTabs(False)

    def __focusOut(self, tabName):
        self.highlightedTab = None
        self.__colourTabs(False)

    def disableAllTabs(self, disabled=True):
        for tab in self.widgetStore.keys():
            self.disableTab(tab, disabled)

    def renameTab(self, tabName, newName=None):
        if tabName not in self.widgetStore.keys():
            raise ItemLookupError("Invalid tab name: " + tabName)
        if newName is None:
            newName = self.widgetStore[tabName][0].DEFAULT_TEXT

        self.widgetStore[tabName][0].config(text=newName)

    def disableTab(self, tabName, disabled=True):
        if tabName not in self.widgetStore.keys():
            raise ItemLookupError("Invalid tab name: " + tabName)

        if not disabled:
            self.widgetStore[tabName][0].disabled = False
            self.widgetStore[tabName][0].config(cursor="hand2", takefocus=1)
        else:
            self.widgetStore[tabName][0].disabled = True
            self.widgetStore[tabName][0].config(cursor="X_cursor", takefocus=0)
            if self.highlightedTab == tabName:
                self.highlightedTab = None

            # difficult if the active tab is disabled
            if self.selectedTab == tabName:
                self.widgetStore[tabName][1].grid_remove()
                # find an enabled tab
                self.selectedTab = None
                for key in list(self.widgetStore.keys()):
                    if not self.widgetStore[key][0].disabled:
                        self.changeTab(key)
                        break

        self.__colourTabs()

    def changeTab(self, tabName):
        # quit changing the tab, if it's already selected
        if self.focus_get() == self.widgetStore[tabName][0]:
            return

        if tabName not in self.widgetStore.keys():
            raise ItemLookupError("Invalid tab name: " + tabName)

        if self.widgetStore[tabName][0].disabled:
            return

        self.selectedTab = tabName
        self.highlightedTab = tabName
        self.widgetStore[tabName][0].focus_set()
        # this will also regrid the appropriate panes
        self.__colourTabs()

        if self.changeEvent is not None:
            self.changeEvent()

    def getSelectedTab(self):
        return self.selectedTab

    def __colourTabs(self, swap=True):
        # clear all tabs & remove if necessary
        for key in list(self.widgetStore.keys()):
            if self.widgetStore[key][0].disabled:
                self.widgetStore[key][0]['bg'] = self.disabledBg
                self.widgetStore[key][0]['fg'] = self.disabledFg
                self.widgetStore[key][0]['relief'] = SUNKEN
            else:
                self.widgetStore[key][0]['bg'] = self.inactiveBg
                self.widgetStore[key][0]['fg'] = self.inactiveFg
                self.widgetStore[key][0]['relief'] = SUNKEN
                if swap:
                    self.widgetStore[key][1].grid_remove()

        # decorate the highlighted tab
        if self.highlightedTab is not None:
            self.widgetStore[self.highlightedTab][0]['fg'] = self.activeFg

        # now decorate the active tab
        if self.selectedTab is not None:
            self.widgetStore[self.selectedTab][0]['bg'] = self.activeBg
            self.widgetStore[self.selectedTab][0]['fg'] = self.activeFg
            self.widgetStore[self.selectedTab][0]['relief'] = RAISED
            # and grid it if necessary
            if swap:
                self.widgetStore[self.selectedTab][1].grid()

#####################################
# Drag Grip Label Class
#####################################


class Grip(Label):

    def __init__(self, *args, **kwargs):
        Label.__init__(self, bitmap="gray25", *args, **kwargs)
        self.config(cursor="fleur")
        self.bind("<ButtonPress-1>", self.StartMove)
        self.bind("<ButtonRelease-1>", self.StopMove)
        self.bind("<B1-Motion>", self.OnMotion)

    def StartMove(self, event):
        self.x = event.x
        self.y = event.y

    def StopMove(self, event):
        self.x = None
        self.y = None

    def OnMotion(self, event):
        parent = self.winfo_toplevel()
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = parent.winfo_x() + deltax
        y = parent.winfo_y() + deltay

        parent.geometry("+%s+%s" % (x, y))

#####################################
# Hyperlink Class
#####################################


class Link(Label):

    def __init__(self, *args, **kwargs):
        Label.__init__(self, *args, **kwargs)
        self.fg = "#0000ff"
        self.overFg="#3366ff"
        self.config(fg=self.fg, takefocus=1, highlightthickness=0)
        self.page = ""
        self.DEFAULT_TEXT = ""

        if gui.GET_PLATFORM() == gui.MAC:
            self.config(cursor="pointinghand")
        elif gui.GET_PLATFORM() in [gui.WINDOWS, gui.LINUX]:
            self.config(cursor="hand2")

        self.bind("<Enter>", self.enter)
        self.bind("<Leave>", self.leave)

    def enter(self, e):
        self.config(fg=self.overFg)

    def leave(self, e):
        self.config(fg=self.fg)

    def registerCallback(self, callback):
        self.bind("<Button-1>", callback)
        self.bind("<Return>", callback)
        self.bind("<space>", callback)

    def launchBrowser(self, event):
        webbrowser.open_new(r"" + self.page)
        # webbrowser.open_new_tab(self.page)

    def registerWebpage(self, page):
        if not page.startswith("http"):
            raise InvalidURLError(
                "Invalid URL: " +
                page +
                " (it should begin as http://)")

        self.page = page
        self.bind("<Button-1>", self.launchBrowser)
        self.bind("<Return>", self.launchBrowser)
        self.bind("<space>", self.launchBrowser)

    def config(self, **kw):
        self.configure(**kw)

    def configure(self, **kw):
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)
        if "text" in kw:
            self.DEFAULT_TEXT = kw["text"]

        if PYTHON2:
            Label.config(self, **kw)
        else:
            super(__class__, self).config(**kw)

#####################################
# Properties Widget
#####################################
class Properties(LabelFrame):

    def __init__(
            self,
            parent,
            text,
            props=None,
            haveLabel=True,
            *args,
            **options):
        if haveLabel:
            LabelFrame.__init__(self, parent, text=text, *args, **options)
        else:
            LabelFrame.__init__(self, parent, text="", *args, **options)
        self.parent = parent
        self.config(relief="groove")
        self.props = {}
        self.cbs = {}
        self.title = text
        self.cmd = None
        self.changingProps = False
        self.addProperties(props)

    def config(self, cnf=None, **kw):
        self.configure(cnf, **kw)

    def configure(self, cnf=None, **kw):
        # properties to propagate to CheckBoxes
        vals = ["bg", "fg", "disabledforeground", "state", "font", "command"]
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)

        # loop through all kw properties received
        for k, v in kw.items():
            if k in vals:
                # and set them on all CheckBoxes if desired
                for prop_key in self.cbs:
                    self.cbs[prop_key][k] = v
                    if k == "bg":# and gui.GET_PLATFORM() == gui.LINUX:
                        gui.SET_WIDGET_BG(self.cbs[prop_key], v, True)

        # remove any props the LabelFrame can't handle
        kw.pop("state", None)
        kw.pop("disabledforeground", None)
        kw.pop("command", None)

        if PYTHON2:
            LabelFrame.config(self, cnf, **kw)
        else:
            super(__class__, self).config(cnf, **kw)

    def addProperties(self, props, callFunction=True):

        if props is not None:
            for k in sorted(props):
                self.addProperty(k, props[k], callFunction=False)

        if self.cmd is not None and callFunction:
            self.cmd()

    def renameProperty(self, prop, newName=None):
        if newName is None:
            newName = prop
        if prop in self.cbs:
            self.cbs[prop].config(text=newName)
        else:
            gui.warn("Unknown property: " + str(prop))

    def addProperty(self, prop, value=False, callFunction=True):
        self.changingProps = True
        if prop in self.props:
            if value is None:
                del self.props[prop]
                self.cbs[prop].pack_forget()
                del self.cbs[prop]
            else:
                self.props[prop].set(value)
                self.cbs[prop].defaultValue = value
        elif prop is not None:
            var = BooleanVar()
            var.set(value)
            var.trace('w', self.__propChanged)
            cb = Checkbutton(self)
            cb.config(
                anchor=W,
                text=prop,
                variable=var,
                bg=self.cget("bg"),
                font=self.cget("font"),
                fg=self.cget("fg"))
            cb.defaultValue = value
            cb.pack(fill="x", expand=1)
            self.props[prop] = var
            self.cbs[prop] = cb
        else:
            self.changingProps = False
            raise Exception("Can't add a None property to: ", prop)
        # if text is not None: lab.config ( text=text )

        if self.cmd is not None and callFunction:
            self.cmd()
        self.changingProps = False

    def __propChanged(self, a,b,c):
        if self.cmd is not None and not self.changingProps:
            self.cmd()

    def getProperties(self):
        vals = {}
        for k, v in self.props.items():
            vals[k] = bool(v.get())
        return vals

    def clearProperties(self, callFunction=False):
        for k, cb in self.cbs.items():
            cb.deselect()

        if self.cmd is not None and callFunction:
            self.cmd()

    def resetProperties(self, callFunction=False):
        for k, cb in self.cbs.items():
            if cb.defaultValue:
                cb.select()
            else:
                cb.deselect()

        if self.cmd is not None and callFunction:
            self.cmd()

    def getProperty(self, prop):
        if prop in self.props:
            return bool(self.props[prop].get())
        else:
            raise Exception(
                "Property: " +
                str(prop) +
                " not found in Properties: " +
                self.title)

    def setChangeFunction(self, cmd):
        self.cmd = cmd

#####################################
# appJar Frame
#####################################


class ajFrame(Frame):

    def __init__(self, parent, *args, **options):
        Frame.__init__(self, parent, *args, **options)

#####################################
# Simple Separator
#####################################


class Separator(frameBase):

    def __init__(self, parent, orient="horizontal", *args, **options):
        frameBase.__init__(self, parent, *args, **options)
        self.line = frameBase(self)
        if orient == "horizontal":
            self.line.config(
                relief="ridge",
                height=2,
                width=100,
                borderwidth=1)
            self.line.pack(padx=5, pady=5, fill="x", expand=1)
        else:
            self.line.config(
                relief="ridge",
                height=100,
                width=2,
                borderwidth=1)
            self.line.pack(padx=5, pady=5, fill="y", expand=1)

    def config(self, cnf=None, **kw):
        self.configure(cnf, **kw)

    def configure(self, cnf=None, **kw):
        if "fg" in kw:
            self.line.config(bg=kw.pop("fg"))

        if PYTHON2:
            frameBase.config(self, cnf, **kw)
        else:
            super(__class__, self).config(cnf, **kw)

#####################################
# Pie Chart Class
#####################################


class PieChart(Canvas):
    # constant for available colours
    COLOURS = [
        "#023fa5",
        "#7d87b9",
        "#bec1d4",
        "#d6bcc0",
        "#bb7784",
        "#8e063b",
        "#4a6fe3",
        "#8595e1",
        "#b5bbe3",
        "#e6afb9",
        "#e07b91",
        "#d33f6a",
        "#11c638",
        "#8dd593",
        "#c6dec7",
        "#ead3c6",
        "#f0b98d",
        "#ef9708",
        "#0fcfc0",
        "#9cded6",
        "#d5eae7",
        "#f3e1eb",
        "#f6c4e1",
        "#f79cd4"]

    def __init__(self, container, fracs, bg="#00FF00"):
        Canvas.__init__(self, container, bd=0, highlightthickness=0, bg=bg)
        self.fracs = fracs
        self.arcs = []
        self.__drawPie()
        self.bind("<Configure>", self.__drawPie)

    def __drawPie(self, event=None):
        # remove the existing arcs
        for arc in self.arcs:
            self.delete(arc)
        self.arcs = []

        # get the width * height
        w = self.winfo_width()
        h = self.winfo_height()

        # scale h&w - so they don't hit the edges
        min_w = w * .05
        max_w = w * .95
        min_h = h * .05
        max_h = h * .95

        # if we're not in a square
        # adjust them to make sure we get a circle
        if w > h:
            extra = (w * .9 - h * .9) / 2.0
            min_w += extra
            max_w -= extra
        elif h > w:
            extra = (h * .9 - w * .9) / 2.0
            min_h += extra
            max_h -= extra

        coord = min_w, min_h, max_w, max_h

        pos = col = 0
        for key, val in self.fracs.items():
            sliceId = "slice" + str(col)
            arc = self.create_arc(
                coord,
                fill=self.COLOURS[
                    col % len(
                        self.COLOURS)],
                start=self.frac(pos),
                extent=self.frac(val),
                activedash=(
                    3,
                    5),
                activeoutline="grey",
                activewidth=3,
                tag=(
                    sliceId,
                ),
                width=1)

            self.arcs.append(arc)

            # generate a tooltip
            if ToolTip is not False:
                frac = int(val / sum(self.fracs.values()) * 100)
                tip = key + ": " + str(val) + " (" + str(frac) + "%)"
                tt = ToolTip(
                    self,
                    tip,
                    delay=500,
                    follow_mouse=1,
                    specId=sliceId)

            pos += val
            col += 1

    def frac(self, curr):
        return 360. * curr / sum(self.fracs.values())

    def setValue(self, name, value):
        if value == 0 and name in self.fracs:
            del self.fracs[name]
        else:
            self.fracs[name] = value

        self.__drawPie()

#####################################
# errors
#####################################


class ItemLookupError(LookupError):
    '''raise this when there's a lookup error for my app'''
    pass


class InvalidURLError(ValueError):
    '''raise this when there's a lookup error for my app'''
    pass

#####################################
# ToggleFrame - collapsable frame
# http://stackoverflow.com/questions/13141259/expandable-and-contracting-frame-in-tkinter
#####################################


class ToggleFrame(Frame):

    def __init__(self, parent, title="", *args, **options):
        Frame.__init__(self, parent, *args, **options)

        self.config(relief="raised", borderwidth=2, padx=5, pady=5)
        self.showing = True

        self.titleFrame = Frame(self)
        self.titleFrame.config(bg="DarkGray")

        self.titleLabel = Label(self.titleFrame, text=title)
        self.DEFAULT_TEXT = title
        self.titleLabel.config(font="-weight bold")

        self.toggleButton = Button(
            self.titleFrame,
            width=2,
            text='-',
            command=self.toggle)

        self.subFrame = Frame(self, relief="sunken", borderwidth=2)

        self.configure(bg="DarkGray")

        self.grid_columnconfigure(0, weight=1)
        self.titleFrame.grid(row=0, column=0, sticky=EW)
        self.titleFrame.grid_columnconfigure(0, weight=1)
        self.titleLabel.grid(row=0, column=0)
        self.toggleButton.grid(row=0, column=1)
        self.subFrame.grid(row=1, column=0, sticky=EW)
        self.firstTime = True

    def config(self, cnf=None, **kw):
        self.configure(cnf, **kw)

    def configure(self, cnf=None, **kw):
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)
        if "font" in kw:
            self.titleLabel.config(font=kw["font"])
            self.toggleButton.config(font=kw["font"])
            del(kw["font"])
        if "bg" in kw:
            self.titleFrame.config(bg=kw["bg"])
            self.titleLabel.config(bg=kw["bg"])
            self.subFrame.config(bg=kw["bg"])
            if gui.GET_PLATFORM() == gui.MAC:
                self.toggleButton.config(highlightbackground=kw["bg"])
        if "state" in kw:
            if kw["state"] == "disabled":
                if self.showing:
                    self.toggle()
            self.toggleButton.config(state=kw["state"])
            del(kw["state"])

        if "text" in kw:
            self.titleLabel.config(text=kw.pop("text"))

        if PYTHON2:
            Frame.config(self, cnf, **kw)
        else:
            super(__class__, self).config(cnf, **kw)


    def cget(self, option):
        if option == "text":
            return self.titleLabel.cget(option)

        if PYTHON2:
            return Frame.cget(self, option)
        else:
            return super(__class__, self).cget(option)

    def toggle(self):
        if not self.showing:
            self.subFrame.grid()
            self.toggleButton.configure(text='-')
        else:
            self.subFrame.grid_remove()
            self.toggleButton.configure(text='+')
        self.showing = not self.showing

    def getContainer(self):
        return self.subFrame

    def stop(self):
        self.update_idletasks()
        self.titleFrame.config(width=self.winfo_reqwidth())
        if self.firstTime:
            self.firstTime = False
            self.toggle()

    def isShowing(self):
        return self.showing

#####################################
# Paged Window
#####################################


class PagedWindow(Frame):

    def __init__(self, parent, title=None, **opts):
        # call the super constructor
        Frame.__init__(self, parent, **opts)
        self.config(width=300, height=400)

        # globals to hold list of frames(pages) and current page
        self.currentPage = -1
        self.frames = []
        self.shouldShowPageNumber = True
        self.shouldShowTitle = True
        self.title = title
        self.navPos = 1
        self.maxX = 0
        self.maxY = 0
        self.pageChangeEvent = None

        # create the 3 components, including a default container frame
        self.titleLabel = Label(self)
        self.prevButton = Button(
            self,
            text="PREVIOUS",
            command=self.showPrev,
            state="disabled",
            width=10)
        self.nextButton = Button(
            self,
            text="NEXT",
            command=self.showNext,
            state="disabled",
            width=10)
        self.prevButton.bind("<Control-Button-1>", self.showFirst)
        self.nextButton.bind("<Control-Button-1>", self.showLast)
        self.posLabel = Label(self, width=8)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # grid the navigation components
        self.prevButton.grid(
            row=self.navPos + 1,
            column=0,
            sticky=N + S + W,
            padx=5,
            pady=(
                0,
                5))
        self.posLabel.grid(
            row=self.navPos + 1,
            column=1,
            sticky=N + S + E + W,
            padx=5,
            pady=(
                0,
                5))
        self.nextButton.grid(
            row=self.navPos + 1,
            column=2,
            sticky=N + S + E,
            padx=5,
            pady=(
                0,
                5))

        # show the title
        if self.title is not None and self.shouldShowTitle:
            self.titleLabel.config(text=self.title, font="-weight bold")
            self.titleLabel.grid(
                row=0, column=0, columnspan=3, sticky=N + W + E)

        self.__updatePageNumber()

    def config(self, cnf=None, **kw):
        self.configure(cnf, **kw)

    def configure(self, cnf=None, **kw):
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)

        if "bg" in kw:
            if gui.GET_PLATFORM() == gui.MAC:
                self.prevButton.config(highlightbackground=kw["bg"])
                self.nextButton.config(highlightbackground=kw["bg"])
            self.posLabel.config(bg=kw["bg"])
            self.titleLabel.config(bg=kw["bg"])
        if "fg" in kw:
            self.poslabel.config(fg=kw["fg"])
            self.titleLabel.config(fg=kw["fg"])
            kw.pop("fg")

        if "prevbutton" in kw:
            self.prevButton.config(text=kw.pop("prevbutton"))

        if "nextbutton" in kw:
            self.nextButton.config(text=kw.pop("nextbutton"))

        if "title" in kw:
            self.title = kw.pop("title")
            self.showTitle()

        if "showtitle" in kw:
            kw.pop("showtitle")

        if "showpagenumber" in kw:
            self.shouldShowPageNumber = kw.pop("showpagenumber")
            self.__updatePageNumber()

        if "command" in kw:
            self.pageChangeEvent = kw.pop("command")

        if PYTHON2:
            Frame.config(self, cnf, **kw)
        else:
            super(__class__, self).config(cnf, **kw)


    # functions to change the labels of the two buttons
    def setPrevButton(self, title):
        self.prevButton.config(text=title)

    def setNextButton(self, title):
        self.nextButton.config(text=title)

    def setNavPositionTop(self, top=True):
        oldNavPos = self.navPos
        pady = (0, 5)
        if top:
            self.navPos = 0
        else:
            self.navPos = 1
        if oldNavPos != self.navPos:
            if self.navPos == 0:
                self.grid_rowconfigure(1, weight=0)
                self.grid_rowconfigure(2, weight=1)
                pady = (5, 0)
            else:
                self.grid_rowconfigure(1, weight=1)
                self.grid_rowconfigure(2, weight=0)
            # grid the navigation components
            self.frames[self.currentPage].grid_remove()
            self.prevButton.grid_remove()
            self.posLabel.grid_remove()
            self.nextButton.grid_remove()

            self.frames[self.currentPage].grid(
                row=int(not self.navPos) + 1,
                column=0,
                columnspan=3,
                sticky=N + S + E + W,
                padx=5,
                pady=5)
            self.prevButton.grid(
                row=self.navPos + 1,
                column=0,
                sticky=S + W,
                padx=5,
                pady=pady)
            self.posLabel.grid(
                row=self.navPos + 1,
                column=1,
                sticky=S + E + W,
                padx=5,
                pady=pady)
            self.nextButton.grid(
                row=self.navPos + 1,
                column=2,
                sticky=S + E,
                padx=5,
                pady=pady)

    # whether to showPageNumber
    def showPageNumber(self, val=True):
        self.shouldShowPageNumber = val
        self.__updatePageNumber()

    def setTitle(self, title):
        self.title = title
        self.showTitle()

    def showTitle(self, val=True):
        self.shouldShowTitle = val
        if self.title is not None and self.shouldShowTitle:
            self.titleLabel.config(text=self.title, font="-weight bold")
            self.titleLabel.grid(
                row=0, column=0, columnspan=3, sticky=N + W + E)
        else:
            self.titleLabel.grid_remove()

    # function to update the contents of the label
    def __updatePageNumber(self):
        if self.shouldShowPageNumber:
            self.posLabel.config(
                text=str(self.currentPage + 1) + "/" + str(len(self.frames)))
        else:
            self.posLabel.config(text="")

    # get the current frame being shown - for adding widgets
    def getPage(self, page=None):
        if page == None: page = self.currentPage
        return self.frames[page]

#    # get the named frame - for adding widgets
#    def getPage(self, num):
#        return self.frames[num]

    # get current page number
    def getPageNumber(self):
        return self.currentPage + 1

    # register a function to call when the page changes
    def registerPageChangeEvent(self, event):
        self.pageChangeEvent = event

    # adds a new page, making it visible
    def addPage(self):
        # if we're showing a page, remove it
        if self.currentPage >= 0:
            self.__updateMaxSize()
            self.frames[self.currentPage].grid_forget()

        # add a new page
        self.frames.append(Page(self))
        self.frames[-1].grid(row=int(not self.navPos) + 1,
                             column=0,
                             columnspan=3,
                             sticky=N + S + E + W,
                             padx=5,
                             pady=5)

        self.currentPage = len(self.frames) - 1

        # update the buttons & labels
        if self.currentPage > 0:
            self.prevButton.config(state="normal")
        self.__updatePageNumber()
        return self.frames[-1]

    def stopPage(self):
        self.__updateMaxSize()
        self.showPage(1)

    def __updateMaxSize(self):
        self.frames[self.currentPage].update_idletasks()
        x = self.frames[self.currentPage].winfo_reqwidth()
        y = self.frames[self.currentPage].winfo_reqheight()
        if x > self.maxX:
            self.maxX = x
        if y > self.maxY:
            self.maxY = y

    # function to display the specified page
    # will re-grid, and disable/enable buttons
    # also updates label
    def showPage(self, page):
        if page < 1 or page > len(self.frames):
            raise Exception("Invalid page number: " + str(page) +
                            ". Must be between 1 and " + str(len(self.frames)))

        self.frames[self.currentPage].grid_forget()
        self.currentPage = page - 1
        self.frames[self.currentPage].grid_propagate(False)
        self.frames[
            self.currentPage].grid(
            row=int(
                not self.navPos) + 1,
            column=0,
            columnspan=3,
            sticky=N + S + E + W,
            padx=5,
            pady=5)
        self.frames[self.currentPage].grid_columnconfigure(0, weight=1)
        self.frames[self.currentPage].config(width=self.maxX, height=self.maxY)
        self.__updatePageNumber()

        # update the buttons
        if len(self.frames) == 1:   # only 1 page - no buttons
            self.prevButton.config(state="disabled")
            self.nextButton.config(state="disabled")
        elif self.currentPage == 0:
            self.prevButton.config(state="disabled")
            self.nextButton.config(state="normal")
        elif self.currentPage == len(self.frames) - 1:
            self.prevButton.config(state="normal")
            self.nextButton.config(state="disabled")
        else:
            self.prevButton.config(state="normal")
            self.nextButton.config(state="normal")

    def showFirst(self, event=None):
        if self.currentPage == 0:
            self.bell()
        else:
            self.showPage(1)
            if self.pageChangeEvent is not None:
                self.pageChangeEvent()

    def showLast(self, event=None):
        if self.currentPage == len(self.frames) - 1:
            self.bell()
        else:
            self.showPage(len(self.frames))
            if self.pageChangeEvent is not None:
                self.pageChangeEvent()

    def showPrev(self, event=None):
        if self.currentPage > 0:
            self.showPage(self.currentPage)
            if self.pageChangeEvent is not None:
                self.pageChangeEvent()
        else:
            self.bell()

    def showNext(self, event=None):
        if self.currentPage < len(self.frames) - 1:
            self.showPage(self.currentPage + 2)
            if self.pageChangeEvent is not None:
                self.pageChangeEvent()
        else:
            self.bell()


class Page(Frame):

    def __init__(self, parent, **opts):
        Frame.__init__(self, parent)
        self.config(relief=RIDGE, borderwidth=2)
        self.container = parent

#########################
# Class to provide auto-completion on Entry boxes
# inspired by: https://gist.github.com/uroshekic/11078820
#########################


class AutoCompleteEntry(Entry):

    def __init__(self, words, tl, *args, **kwargs):
        Entry.__init__(self, *args, **kwargs)
        self.allWords = words
        self.allWords.sort()
        self.topLevel = tl

        # store variable - so we can see when it changes
        self.var = self["textvariable"] = StringVar()
        self.var.auto_id = self.var.trace('w', self.textChanged)

        # register events
        self.bind("<Right>", self.selectWord)
        self.bind("<Return>", self.selectWord)
        self.bind("<Up>", self.moveUp)
        self.bind("<Down>", self.moveDown)
        self.bind("<FocusOut>", self.closeList, add="+")
        self.bind("<Escape>", self.closeList, add="+")

        # no list box - yet
        self.listBoxShowing = False
        self.rows = 10

    def setNumRows(self, rows):
        self.rows = rows

    # function to see if words match
    def checkMatch(self, fieldValue, acListEntry):
        pattern = re.compile(re.escape(fieldValue) + '.*', re.IGNORECASE)
        return re.match(pattern, acListEntry)

    # function to get all matches as a list
    def getMatches(self):
        return [w for w in self.allWords if self.checkMatch(self.var.get(), w)]

    # called when typed in entry
    def textChanged(self, name, index, mode):
        # if no text - close list
        if self.var.get() == '':
            self.closeList()
        else:
            if not self.listBoxShowing:
                self.makeListBox()
            self.popListBox()

    # add words to the list
    def popListBox(self):
        if self.listBoxShowing:
            self.listbox.delete(0, END)
            shownWords = self.getMatches()
            if shownWords:
                for w in shownWords:
                    self.listbox.insert(END, w)
                self.selectItem(0)

    # function to create & show an empty list box
    def makeListBox(self):
        self.listbox = Listbox(self.topLevel, width=self["width"], height=8)
        self.listbox.config(height=self.rows, bg=self.cget("bg"), selectbackground=self.cget("selectbackground"))
        self.listbox.config(fg=self.cget("fg"))
        self.listbox.bind("<Button-1>", self.mouseClickBox)
        self.listbox.bind("<Right>", self.selectWord)
        self.listbox.bind("<Return>", self.selectWord)

        x = self.winfo_rootx() - self.topLevel.winfo_rootx()
        y = self.winfo_rooty() - self.topLevel.winfo_rooty() + self.winfo_height()

        self.listbox.place(x=x, y=y)
        self.listBoxShowing = True

    # function to handle a mouse click in the list box
    def mouseClickBox(self, e=None):
        self.selectItem(self.listbox.nearest(e.y))
        self.selectWord(e)

    # function to close/delete list box
    def closeList(self, event=None):
        if self.listBoxShowing:
            self.listbox.destroy()
            self.listBoxShowing = False

    # copy word from list to entry, close list
    def selectWord(self, event):
        if self.listBoxShowing:
            self.var.set(self.listbox.get(ACTIVE))
            self.icursor(END)
            self.closeList()
        return "break"

    # wrappers for up/down arrows
    def moveUp(self, event):
        return self.arrow("UP")

    def moveDown(self, event):
        return self.arrow("DOWN")

    # function for handling up/down keys
    def arrow(self, direction):
        if not self.listBoxShowing:
            self.makeListBox()
            self.popListBox()
            curItem = 0
            numItems = self.listbox.size()
        else:
            numItems = self.listbox.size()
            curItem = self.listbox.curselection()

            if curItem == ():
                curItem = -1
            else:
                curItem = int(curItem[0])

            if direction == "UP" and curItem > 0:
                curItem -= 1
            elif direction == "UP" and curItem <= 0:
                curItem = numItems - 1
            elif direction == "DOWN" and curItem < numItems - 1:
                curItem += 1
            elif direction == "DOWN" and curItem == numItems - 1:
                curItem = 0

        self.selectItem(curItem)

        # stop the event propgating
        return "break"

    # function to select the specified item
    def selectItem(self, position):
        numItems = self.listbox.size()
        self.listbox.selection_clear(0, numItems - 1)
        self.listbox.see(position)  # Scroll!
        self.listbox.selection_set(first=position)
        self.listbox.activate(position)

#####################################
# Named classes for containing groups
#####################################

class ParentBox(frameBase):

    def __init__(self, parent, **opts):
        frameBase.__init__(self, parent)
        self.setup()

    def setup(self):
        pass

    # customised config setters
    def config(self, cnf=None, **kw):
        self.configure(cnf, **kw)

    def configure(self, cnf=None, **kw):
        # properties to propagate to CheckBoxes
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)

        if "bg" in kw:
            for child in self.winfo_children():
                gui.SET_WIDGET_BG(child, kw["bg"])

        kw = self.processConfig(kw)

        # propagate anything left
        if PYTHON2:
            frameBase.config(self, cnf, **kw)
        else:
            super(__class__, self).config(cnf, **kw)

    def processConfig(self, kw):
        return kw

class LabelBox(ParentBox):
    def setup(self):
        self.theLabel = None
        self.theWidget = None

class ButtonBox(ParentBox):
    def setup(self):
        self.theWidget = None
        self.theButton = None

class WidgetBox(ParentBox):
    def setup(self):
        self.theWidgets = []

class ListBoxContainer(Frame):

    def __init__(self, parent, **opts):
        Frame.__init__(self, parent)

    # customised config setters
    def config(self, cnf=None, **kw):
        self.configure(cnf, **kw)

    def configure(self, cnf=None, **kw):
        # properties to propagate to CheckBoxes
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)

        # propagate anything left
        if PYTHON2:
            Frame.config(self, cnf, **kw)
        else:
            super(__class__, self).config(cnf, **kw)


class Pane(Frame):

    def __init__(self, parent, **opts):
        Frame.__init__(self, parent)

#####################################
# scrollable frame...
# http://effbot.org/zone/tkinter-autoscrollbar.htm
#####################################


class AutoScrollbar(Scrollbar):

    def __init__(self, parent, **opts):
        Scrollbar.__init__(self, parent, **opts)
        self.hidden = None

    # a scrollbar that hides itself if it's not needed
    # only works if you use the grid geometry manager
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
            self.hidden = True
        else:
            self.grid()
            self.hidden = False
        Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise Exception("cannot use pack with this widget")

    def place(self, **kw):
        raise Exception("cannot use place with this widget")

    # customised config setters
    def config(self, cnf=None, **kw):
        self.configure(cnf, **kw)

    def configure(self, cnf=None, **kw):
        # properties to propagate to CheckBoxes
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)

        if "fg" in kw:
            kw.pop("fg")

        # propagate anything left
        if PYTHON2:
            Scrollbar.config(self, cnf, **kw)
        else:
            super(__class__, self).config(cnf, **kw)

#######################
# Upgraded scale - http://stackoverflow.com/questions/42843425/change-trough-increment-in-python-tkinter-scale-without-affecting-slider/
#######################

class ajScale(Scale):
    '''a scale where a trough click jumps by a specified increment instead of the resolution'''
    def __init__(self, master=None, **kwargs):
        self.increment = kwargs.pop('increment',1)
        Scale.__init__(self, master, **kwargs)
        self.bind('<Button-1>', self.jump)

    def jump(self, event):
        clicked = self.identify(event.x, event.y)
        return self.__jump(clicked)

    def __jump(self, clicked):
        if clicked == 'trough1':
            self.set(self.get() - self.increment)
        elif clicked == 'trough2':
            self.set(self.get() + self.increment)
        else:
            return None
        return 'break'

#######################
# Widget to give TextArea extra functionality
# http://code.activestate.com/recipes/464635-call-a-callback-when-a-tkintertext-is-modified/
#######################


class TextParent():
    def _init(self):
        self.clearModifiedFlag()
        self.bind('<<Modified>>', self._beenModified)
        self.__hash = None
        self.callFunction = True
        self.oldCallFunction = True

    def pauseCallFunction(self, callFunction=False):
        self.oldCallFunction = self.callFunction
        self.callFunction = callFunction

    def resumeCallFunction(self):
        self.callFunction = self.oldCallFunction

    def _beenModified(self, event=None):
        # stop recursive calls
        if self._resetting_modified_flag: return
        self.clearModifiedFlag()
        self.beenModified(event)

    def bindChangeEvent(self, function):
        self.function = function

    def beenModified(self, event=None):
        # call the user's function
        if hasattr(self, 'function') and self.callFunction:
            self.function()

    def clearModifiedFlag(self):
        self._resetting_modified_flag = True
        try:
            # reset the modified flag (this raises a modified event!)
            self.tk.call(self._w, 'edit', 'modified', 0)
        finally:
            self._resetting_modified_flag = False

    def getText(self):
        return self.get('1.0', END + '-1c')

    def getTextAreaHash(self):
        text = self.getText()
        m = hashlib.md5()
        if PYTHON2:
            m.update(text)
        else:
            m.update(str.encode(text))
        md5 = m.digest()
#        md5 = hashlib.md5(str.encode(text)).digest()
        return md5

# uses multiple inheritance
class AjText(TextParent, Text):
    def __init__(self, parent, **opts):
        Text.__init__(self, parent, **opts)
        self._init()    # call TextParent initialiser


class AjScrolledText(TextParent, scrolledtext.ScrolledText):
    def __init__(self, parent, **opts):
        scrolledtext.ScrolledText.__init__(self, parent, **opts)
        self._init()    # call TextParent initialiser


#######################
# Widget to look like a label, but allow selection...
#######################


class SelectableLabel(Entry):
    def __init__(self, parent, **opts):
        Entry.__init__(self, parent)
        self.configure(relief=FLAT, state="readonly", readonlybackground='#FFFFFF', fg='#000000', highlightthickness=0)
        self.var = StringVar(parent)
        self.configure(textvariable=self.var)
        self.configure(**opts)

    def cget(self, kw):
        if kw == "text":
            return self.var.get()
        else:
            if PYTHON2:
                return Entry.cget(self, kw)
            else:
                return super(__class__, self).cget(kw)

    def config(self, cnf=None, **kw):
        self.configure(cnf, **kw)

    def configure(self, cnf=None, **kw):
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)
        if "text" in kw:
            self.var.set(kw.pop("text"))

        if "bg" in kw:
            kw["readonlybackground"] = kw.pop("bg")

        # propagate anything left
        if PYTHON2:
            Entry.config(self, cnf, **kw)
        else:
            super(__class__, self).config(cnf, **kw)


#######################
# Frame with built in scrollbars and canvas for placing stuff on
# http://effbot.org/zone/tkinter-autoscrollbar.htm
# Modified with help from idlelib TreeWidget.py
#######################


class ScrollPane(Frame):
    def __init__(self, parent, **opts):
        Frame.__init__(self, parent)
        self.config(padx=5, pady=5)

        # make the ScrollPane expandable
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.vscrollbar = AutoScrollbar(self)
        self.hscrollbar = AutoScrollbar(self, orient=HORIZONTAL)
        opts['yscrollcommand'] = self.vscrollbar.set
        opts['xscrollcommand'] = self.hscrollbar.set

        self.canvas = Canvas(self, **opts)
        self.canvas.config(highlightthickness=0)

        self.vscrollbar.grid(row=0, column=1, sticky=N + S + E)
        self.hscrollbar.grid(row=1, column=0, sticky=E + W + S)
        self.canvas.grid(row=0, column=0, sticky=N + S + E + W)

        self.vscrollbar.config(command=self.canvas.yview)
        self.hscrollbar.config(command=self.canvas.xview)

        self.canvas.bind("<Enter>", self.__mouseEnter)
        self.canvas.bind("<Leave>", self.__mouseLeave)

        self.b_ids = []
        self.canvas.focus_set()

        self.interior = Frame(self.canvas)
        self.interior_id = self.canvas.create_window(
            0, 0, window=self.interior, anchor=NW)

        self.interior.bind('<Configure>', self.__configureInterior)

    def config(self, **kw):
        self.configure(**kw)

    def configure(self, **kw):
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)
        if "bg" in kw:
            self.canvas.config(bg=kw["bg"])
            self.interior.config(bg=kw["bg"])

        if PYTHON2:
            Frame.config(self, **kw)
        else:
            super(__class__, self).config(**kw)

    # track changes to the canvas and frame width and sync them,
    # http://www.scriptscoop2.com/t/35d742299f35/python-tkinter-scrollbar-for-frame.html
    def __configureInterior(self, event):
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)

    # unbind any saved bind ids
    def __unbindIds(self):
        if len(self.b_ids) == 0:
            return

        if gui.GET_PLATFORM() == gui.LINUX:
            self.canvas.unbind("<4>", self.b_ids[0])
            self.canvas.unbind("<5>", self.b_ids[1])
            self.canvas.unbind("<Shift-4>", self.b_ids[2])
            self.canvas.unbind("<Shift-5>", self.b_ids[3])
        else:  # Windows and MacOS
            self.canvas.unbind("<MouseWheel>", self.b_ids[0])
            self.canvas.unbind("<Shift-MouseWheel>", self.b_ids[1])

        self.canvas.unbind("<Key-Prior>", self.b_ids[4])
        self.canvas.unbind("<Key-Next>", self.b_ids[5])
        self.canvas.unbind("<Key-Up>", self.b_ids[6])
        self.canvas.unbind("<Key-Down>", self.b_ids[7])
        self.canvas.unbind("<Key-Left>", self.b_ids[8])
        self.canvas.unbind("<Key-Right>", self.b_ids[9])
        self.canvas.unbind("<Home>", self.b_ids[10])
        self.canvas.unbind("<End>", self.b_ids[11])

        self.b_ids = []

    # bind mouse scroll to this widget only when mouse is over
    def __mouseEnter(self, event):
        self.__unbindIds()
        if gui.GET_PLATFORM() == gui.LINUX:
            self.b_ids.append(self.canvas.bind_all("<4>", self.__vertMouseScroll))
            self.b_ids.append(self.canvas.bind_all("<5>", self.__vertMouseScroll))
            self.b_ids.append(self.canvas.bind_all("<Shift-4>", self.__horizMouseScroll))
            self.b_ids.append(self.canvas.bind_all("<Shift-5>", self.__horizMouseScroll))
        else:  # Windows and MacOS
            self.b_ids.append(self.canvas.bind_all("<MouseWheel>", self.__vertMouseScroll))
            self.b_ids.append(self.canvas.bind_all("<Shift-MouseWheel>", self.__horizMouseScroll))
            self.b_ids.append(None)
            self.b_ids.append(None)

        self.b_ids.append(self.canvas.bind_all("<Key-Prior>", self.__keyPressed))
        self.b_ids.append(self.canvas.bind_all("<Key-Next>", self.__keyPressed))
        self.b_ids.append(self.canvas.bind_all("<Key-Up>", self.__keyPressed))
        self.b_ids.append(self.canvas.bind_all("<Key-Down>", self.__keyPressed))
        self.b_ids.append(self.canvas.bind_all("<Key-Left>", self.__keyPressed))
        self.b_ids.append(self.canvas.bind_all("<Key-Right>", self.__keyPressed))
        self.b_ids.append(self.canvas.bind_all("<Home>", self.__keyPressed))
        self.b_ids.append(self.canvas.bind_all("<End>", self.__keyPressed))

    # remove mouse scroll binding, when mouse leaves
    def __mouseLeave(self, event):
        self.__unbindIds()

    def __horizMouseScroll(self, event):
        if not self.hscrollbar.hidden:
            self.__mouseScroll(True, event)

    def __vertMouseScroll(self, event):
        if not self.vscrollbar.hidden:
            self.__mouseScroll(False, event)

    def __mouseScroll(self, horiz, event):
        direction = 0

        # get direction
        if event.num == 4:
            direction = -1
        elif event.num == 5:
            direction = 1
        elif event.delta > 100:
            direction = int(-1 * (event.delta/120))
        elif event.delta > 0:
            direction = -1 * event.delta
        elif event.delta < -100:
            direction = int(-1 * (event.delta/120))
        elif event.delta < 0:
            direction = -1 * event.delta
        else:
            return  # shouldn't happen

        if horiz:
            self.xscroll(direction, "units")
        else:
            self.yscroll(direction, "units")

    def getPane(self):
        return self.canvas

    def __keyPressed(self, event):
        # work out if alt/ctrl/shift are pressed
        # http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/event-handlers.html
        state = event.state
        ctrl  = (state & 0x4) != 0
        alt   = (state & 0x8) != 0 or (state & 0x80) != 0 # buggy
        shift = (state & 0x1) != 0

        if event.type == "2":
            # up and down arrows
            if event.keysym == "Up": # event.keycode == 38
                if ctrl:
                    self.yscroll(-1, "pages")
                else:
                    self.yscroll(-1, "units")
            elif event.keysym == "Down": # event.keycode == 40
                if ctrl:
                    self.yscroll(1, "pages")
                else:
                    self.yscroll(1, "units")

            # left and right arrows
            elif event.keysym == "Left": # event.keycode == 37
                if ctrl:
                    self.xscroll(-1, "pages")
                else:
                    self.xscroll(-1, "units")
            elif event.keysym == "Right": # event.keycode == 39
                if ctrl:
                    self.xscroll(1, "pages")
                else:
                    self.xscroll(1, "units")

            # page-up & page-down keys
            elif event.keysym == "Prior": # event.keycode == 33
                if ctrl:
                    self.xscroll(-1, "pages")
                else:
                    self.yscroll(-1, "pages")
            elif event.keysym == "Next": # event.keycode == 34
                if ctrl:
                    self.xscroll(1, "pages")
                else:
                    self.yscroll(1, "pages")

            # home & end keys
            elif event.keysym == "Home": # event.keycode == 36
                if ctrl:
                    self.scrollLeft()
                else:
                    self.scrollTop()
            elif event.keysym == "End": # event.keycode == 35
                if ctrl:
                    self.scrollRight()
                else:
                    self.scrollBottom()

            return "break"
        else:
            pass # shouldn't happen

    def xscroll(self, direction, value=None):
        if not self.hscrollbar.hidden:
            if value is not None: self.canvas.xview_scroll(direction, value)
            else: self.canvas.xview_moveto(direction)

    def yscroll(self, direction, value=None):
        if not self.vscrollbar.hidden:
            if value is not None: self.canvas.yview_scroll(direction, value)
            else: self.canvas.yview_moveto(direction)

    # functions to scroll to the beginning or end
    def scrollLeft(self):
        self.xscroll(0.0)
    def scrollRight(self):
        self.xscroll(1.0)

    def scrollTop(self):
        self.yscroll(0.0)
    def scrollBottom(self):
        self.yscroll(1.0)


#################################
# Additional Dialog Classes
#################################
# the main dialog class to be extended

class Dialog(Toplevel):

    def __init__(self, parent, title=None):
        Toplevel.__init__(self, parent)
        gui.CENTER(self, up=150)
        self.transient(parent)
        self.withdraw()
        parent.POP_UP = self

        if title:
            self.title(title)
        self.parent = parent
        self.result = None

        # create a frame to hold the contents
        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        # create the buttons
        self.buttonbox()

        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.deiconify()

        self.initial_focus.focus_set()
        self.wait_window(self)

    # override to create the contents of the dialog
    # should return the widget to give focus to
    def body(self, master):
        pass

    # add standard buttons
    # override if you don't want the standard buttons
    def buttonbox(self):
        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    # called when ok button pressed
    def ok(self, event=None):
        # only continue if validate() returns True
        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        # call the validate function before calling the cancel function
        self.apply()
        self.cancel()

    # called when cancel button pressed
    def cancel(self, event=None):
        self.grab_release()
        self.parent.focus_set()  # give focus back to the parent
        self.destroy()

    # override this to cancel closing the form
    def validate(self):
        return True

    # override this to do something before closing
    def apply(self):
        pass

# a base class for a simple data capture dialog


class SimpleEntryDialog(Dialog):

    def __init__(self, parent, title, question, defaultvar=None):
        self.error = False
        self.question = question
        self.defaultVar=defaultvar
        if PYTHON2:
            Dialog.__init__(self, parent, title)
        else:
            super(__class__, self).__init__(parent, title)

    def clearError(self, e):
        if self.error:
            self.error = False
            self.l1.config(text="")

    def setError(self, message):
        self.parent.bell()
        self.error = True
        self.l1.config(text=message)

    # a label for the question, an entry for the answer
    # a label for an error message
    def body(self, master):
        Label(master, text=self.question).grid(row=0)
        self.e1 = Entry(master)
        if self.defaultVar is not None:
            self.e1.var = self.defaultVar
            self.e1.config(textvariable=self.e1.var)
            self.e1.var.auto_id = None
        self.l1 = Label(master, fg="#FF0000")
        self.e1.grid(row=1)
        self.l1.grid(row=2)
        self.e1.bind("<Key>", self.clearError)
        return self.e1

# captures a string - must not be empty


class TextDialog(SimpleEntryDialog):

    def __init__(self, parent, title, question, defaultVar=None):
        if PYTHON2:
            SimpleEntryDialog.__init__(self, parent, title, question, defaultVar)
        else:
            super(__class__, self).__init__(parent, title, question, defaultVar)

    def validate(self):
        res = self.e1.get()
        if len(res.strip()) == 0:
            self.setError("Invalid text.")
            return False
        else:
            self.result = res
            return True

# captures a number - must be a valid float


class NumDialog(SimpleEntryDialog):

    def __init__(self, parent, title, question):
        if PYTHON2:
            SimpleEntryDialog.__init__(self, parent, title, question)
        else:
            super(__class__, self).__init__(parent, title, question)

    def validate(self):
        res = self.e1.get()
        try:
            self.result = float(res) if '.' in res else int(res)
            return True
        except ValueError:
            self.setError("Invalid number.")
            return False

#####################################
# Toplevel Stuff
#####################################


class SubWindow(Toplevel):

    def __init__(self):
        Toplevel.__init__(self)
        self.escapeBindId = None  # used to exit fullscreen
        self.stopFunction = None  # used to stop
        self.modal = False
        self.blocking = False
        self.canvasPane = CanvasDnd(self)
        self.canvasPane.pack(fill=BOTH, expand=True)


#####################################
# SimpleGrid Stuff
#####################################

# first row is used as a header
# SimpleGrid is a ScrollPane, where a Frame has been placed on the canvas - called GridContainer
class SimpleGrid(ScrollPane):

    rows = []
    addRow = False

    def __init__(self, parent, title, data, action=None, addRow=None,
                    actionHeading="Action", actionButton="Press",
                    addButton="Add", **opts):

        if "buttonFont" in opts:
            self.buttonFont = opts.pop("buttonFont")
        else:
            self.buttonFont = font.Font(family="Helvetica", size=12)

        ScrollPane.__init__(self, parent, **opts)

        if "font" in opts:
            self.gdFont = opts["font"]
            self.ghFont = opts["font"]
            self.ghFont.configure(size=self.ghFont.actual("size") + 2, weight="bold")
        else:
            self.gdFont = font.Font(family="Helvetica", size=12)
            self.ghFont = font.Font(family="Helvetica", size=14, weight="bold")

        # actions
        self.addRowEntries = addRow
        self.action = action

        # lists to store the data in
        self.data = []
        self.entries = []
        self.rightColumn = []
        # a list of any selected cells
        from collections import OrderedDict
        self.selectedCells = OrderedDict()

        # how many rows & columns
        self.numColumns = 0
        # find out the max number of cells in a row
        for row in data:
            if len(row) > self.numColumns:
                self.numColumns = len(row)
        
        # headings
        self.actionHeading = actionHeading
        self.actionButton= actionButton
        self.addButton= addButton
       
        # colours
        self.cellHeadingBg = "#A9A9A9"      # HEADING BG
        self.cellBg = "#E0FFFF"             # CELL BG
        self.cellOverBg = "#C0C0C0"         # mouse over BG
        self.cellSelectedBg = "#D3D3D3"     # selected cell BG

        # add the grid container to the frame
        self.gridContainer = Frame(self.interior)
        self.gridContainer.pack(expand=True, fill='both')
        self.gridContainer.bind("<Configure>", self.__refreshGrids)

        self.addRows(data)

    def config(self, cnf=None, **kw):
        self.configure(cnf, **kw)

    def configure(self, cnf=None, **kw):
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)
        if "bg" in kw:
            bg = kw.pop("bg")
            self.gridContainer.config(bg=bg)
            self.canvas.config(bg=bg)
            self.interior.config(bg=bg)
        if "activebackground" in kw:
            self.cellSelectedBg = kw.pop("activebackground")
        if "inactivebackground" in kw:
            self.cellBg = kw.pop("inactivebackground")
        if "font" in kw:
            font = kw.pop("font")
            self.gdFont.configure(family=font.actual("family"), size=font.actual("size"))
            self.ghFont.configure(family=font.actual("family"), size=font.actual("size") + 2, weight="bold")
        if "buttonFont" in kw:
            buttonFont = kw.pop("buttonFont")
            self.buttonFont.configure(family=buttonFont.actual("family"), size=buttonFont.actual("size"))

        # allow labels to be updated
        if "actionheading" in kw:
            self.actionHeading = kw.pop("actionheading")
            if len(self.rightColumn) > 0:
                self.rightColumn[0].config(text=self.actionHeading)
        if "actionbutton" in kw:
            self.actionButton = kw.pop("actionbutton")
            if len(self.rightColumn) > 1:
                for pos in range(1, len(self.rightColumn)):
                    self.rightColumn[pos].config(text=self.actionButton)
        if "addbutton" in kw:
            self.addButton = kw.pop("addbutton")
            self.ent_but.config(text=self.addButton)

    def addRow(self, rowData, scroll=True):
        self.__hideEntryBoxes()
        self.__addRow(rowData)
        self.__showEntryBoxes()
        if scroll:
            self.scrollBottom()

    def addRows(self, data, scroll=True):
        self.__hideEntryBoxes()
        for row in data:
            self.__addRow(row)
        self.__showEntryBoxes()
        if scroll:
            self.scrollBottom()

    # not finished
    def deleteRow(self, position):
        if 0 > position >= self.numRows:
            raise Exception("Invalid row number.")
        else:
            for loop in range(position, self.numRows -2):
                self.data[position] = self.data[position+1]
            self.numRows -= 1

        #self.rightRow.delete(position)
                
    def __addRow(self, rowData):
        self.data.append(rowData)
        rowNum = len(self.data) - 1
        celContents = []

        for cellNum in range(self.numColumns):

            # get a val ("" if no val)
            if cellNum >= len(rowData):
                val = ""
            else:
                val = rowData[cellNum]
            celContents.append(val)

            lab = Label(self.gridContainer)
            if rowNum == 0: # adding title row
                lab.configure(relief=RIDGE,
                    text=val, font=self.ghFont,
                    background=self.cellHeadingBg
                )
            else:
                lab.configure( relief=RIDGE,
                    text=val, font=self.gdFont,
                    background=self.cellBg
                )
                lab.bind("<Enter>", self.__gridCellEnter)
                lab.bind("<Leave>", self.__gridCellLeave)
                lab.bind("<Button-1>", self.__gridCellClick)
                
                lab.gridPos = str(rowNum - 1) + "-" + str(cellNum)
                self.selectedCells[lab.gridPos] = False

            lab.grid(row=rowNum, column=cellNum, sticky=N+E+S+W)
            Grid.columnconfigure(self.gridContainer, cellNum, weight=1)
            Grid.rowconfigure(self.gridContainer, rowNum, weight=1)

        # add some buttons for each row
        if self.action is not None:
            widg = Label(self.gridContainer, relief=RIDGE, height=2)
            # add the title
            if rowNum == 0:
                widg.configure(text=self.actionHeading,
                    font=self.ghFont, background=self.cellHeadingBg
                )
                self.rightColumn.append(widg)
            # add a button
            else:
                but = Button(widg, font=self.buttonFont,
                    text=self.actionButton,
                    command=gui.MAKE_FUNC(self.action, rowNum-1)
                )
                but.place(relx=0.5, rely=0.5, anchor=CENTER)
                self.rightColumn.append(but)

            widg.grid(row=rowNum, column=cellNum + 1, sticky=N+E+S+W)

    def __hideEntryBoxes(self):
        if self.addRowEntries is None or len(self.entries) == 0:
            return
        for e in self.entries:
            e.lab.grid_forget()
        self.ent_but.lab.grid_forget()

    def __showEntryBoxes(self):
        if self.addRowEntries is None: return
        if len(self.entries) > 0:
            for pos in range(len(self.entries)):
                self.entries[pos].lab.grid(row=len(self.data), column=pos, sticky=N+E+S+W)
            self.ent_but.lab.grid(row=len(self.data), column=len(self.entries), sticky=N+E+S+W)
        else:
            self.__createEntryBoxes()

    def __createEntryBoxes(self):
        if self.addRowEntries is None: return
        for cellNum in range(self.numColumns):
            name = "GR" + str(cellNum)
            lab = Label(self.gridContainer, relief=RIDGE, width=6, height=2)
            lab.grid(row=len(self.data), column=cellNum, sticky=N + E + S + W)

            # self.__buildEntry(name, self.gridContainer)
            ent = Entry(lab, width=5)
            ent.pack(expand=True, fill='both')
            self.entries.append(ent)
            ent.lab = lab

        lab = Label(self.gridContainer, relief=RIDGE, height=2)
        lab.grid(row=len(self.data), column=self.numColumns, sticky=N+E+S+W)

        self.ent_but = Button(
            lab, font=self.buttonFont,
            text=self.addButton,
            command=gui.MAKE_FUNC(self.addRowEntries, "newRow")
        )
        self.ent_but.lab = lab
        self.ent_but.pack(expand=True, fill='both')

    def getEntries(self):
        return [e.get() for e in self.entries]

    def getSelectedCells(self):
        return dict(self.selectedCells)

    def __refreshGrids(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def __gridCellEnter(self, event):
        cell = event.widget
        cell.config(background=self.cellOverBg)

    def __gridCellLeave(self, event):
        cell = event.widget
        gridPos = cell.gridPos
        if self.selectedCells[gridPos]:
            cell.config(background=self.cellSelectedBg)
        else:
            cell.config(background=self.cellBg)

    def __gridCellClick(self, event):
        cell = event.widget
        gridPos = cell.gridPos
        if self.selectedCells[gridPos]:
            self.selectedCells[gridPos] = False
            cell.config(background=self.cellBg)
        else:
            self.selectedCells[gridPos] = True
            cell.config(background=self.cellSelectedBg)


##########################
# MicroBit Simulator
##########################


class MicroBitSimulator(Frame):

    COLOURS = {0:'#000000',1:'#110000',2:'#220000',3:'#440000',4:'#660000',5:'#880000',6:'#aa0000',7:'#cc0000',8:'#ee0000',9:'#ff0000'}
    SIZE = 5
    HEART = "09090:90909:90009:09090:00900"

    def __init__(self, parent, **opts):
        Frame.__init__(self, parent, **opts)

        self.matrix = []
        for i in range(self.SIZE):
            self.matrix.append([])
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                self.matrix[i].append('')

        for y in range(self.SIZE):
            for x in range(self.SIZE):
                self.matrix[x][y] = Label(self, bg='#000000', width=5, height=2)
                self.matrix[x][y].grid(column=x, row=y, padx=5, pady=5)

        self.update_idletasks()

    def set_pixel(self, x, y, brightness):
        self.matrix[x][y].config(bg=self.COLOURS[brightness])
        self.update_idletasks()

    def show(self, image):
        rows = image.split(':')
        for y in range(len(rows)):
            for x in range(len(rows[0])):
                self.matrix[x][y].config(bg=self.COLOURS[int(rows[y][x])])
        self.update_idletasks()

    def clear(self):
        for y in range(self.SIZE):
            for x in range(self.SIZE):
                self.matrix[x][y].config(bg='#000000')
        self.update_idletasks()


##########################
# Simple SplashScreen
##########################


class SplashScreen(Toplevel):
    def __init__(self, parent, text="appJar", fill="#FF0000", stripe="#000000", fg="#FFFFFF", font=44):
        Toplevel.__init__(self, parent)

        lab = Label(self, bg=stripe, fg=fg, text=text, height=3, width=50)
        lab.config(font=("Courier", font))
        lab.place(relx=0.5, rely=0.5, anchor=CENTER)

        width = str(self.winfo_screenwidth())
        height = str(self.winfo_screenheight())
        self.geometry(width+"x"+height)
        self.config(bg=fill)

        self.attributes("-alpha", 0.95)
        self.attributes("-fullscreen", True)
        self.overrideredirect(1)

        self.update()

##########################
# CopyAndPaste Organiser
##########################


class CopyAndPaste():

    def __init__(self, topLevel):
        self.topLevel = topLevel
        self.inUse = False

    def setUp(self, widget):
        self.inUse = True
        # store globals
        self.widget = widget
        self.widgetType = widget.__class__.__name__

        # query widget
        self.canCut = False
        self.canCopy = False
        self.canSelect = False
        self.canUndo = False
        self.canRedo = False

        try:
            self.canPaste = len(self.topLevel.clipboard_get()) > 0
        except:
            self.canPaste = False

        if self.widgetType in ["Entry", "AutoCompleteEntry"]:
            if widget.selection_present():
                self.canCut = self.canCopy = True
            if widget.index(END) > 0:
                self.canSelect = True
        elif self.widgetType in ["ScrolledText", "Text", "AjText", "AjScrolledText"]:
            if widget.tag_ranges("sel"):
                self.canCut = self.canCopy = True
            if widget.index("end-1c") != "1.0":
                self.canSelect = True
            if widget.edit_modified():
                self.canUndo = True
            self.canRedo = True
        elif self.widgetType == "OptionMenu":
            self.canCopy = True
            self.canPaste = False

    def copy(self):
        if self.widgetType == "OptionMenu":
            self.topLevel.clipboard_clear()
            self.topLevel.clipboard_append(self.widget.var.get())
        else:
            self.widget.event_generate('<<Copy>>')
            self.widget.selection_clear()

    def cut(self):
        if self.widgetType == "OptionMenu":
            self.topLevel.bell()
        else:
            self.widget.event_generate('<<Cut>>')
            self.widget.selection_clear()

    def paste(self):
        self.widget.event_generate('<<Paste>>')
        self.widget.selection_clear()

    def undo(self):
        try:
            self.widget.edit_undo()
        except:
            self.topLevel.bell()

    def redo(self):
        try:
            self.widget.edit_redo()
        except:
            self.topLevel.bell()

    def clearClipboard(self):
        self.topLevel.clipboard_clear()

    def clearText(self):
        try:
            self.widget.delete(0.0, END)  # TEXT
        except:
            try:
                self.widget.delete(0, END)  # ENTRY
            except:
                self.topLevel.bell()

    def selectAll(self):
        try:
            self.widget.select_range(0, END)  # ENTRY
        except:
            try:
                self.widget.tag_add("sel", "1.0", "end")  # TEXT
            except:
                self.topLevel.bell()

    # clear the undo/redo stack
    def resetStack(self): self.widget.edit_reset()

#####################################
# class to temporarily pause logging
#####################################
# usage:
# with PauseLogger():
#   doSomething()
#####################################
class PauseLogger():
    def __enter__(self):
        # disable all warning of CRITICAL & below
        logging.disable(logging.CRITICAL)
    def __exit__(self, a, b, c):
        logging.disable(logging.NOTSET)


#####################################
# class to temporarily pause function calling
#####################################
# usage:
# with PauseCallFunction(callFunction, widg):
#   doSomething()
# relies on 3 variables in widg:
# var - the thing being traced
# cmd_id - linking to the trace
# cmd - the function called by the trace
#####################################
class PauseCallFunction():
    def __init__(self, callFunction, widg, useVar=True):
        self.callFunction = callFunction
        self.widg = widg
        if useVar:
            self.tracer = self.widg.var
        else:
            self.tracer = self.widg
        gui.debug("PauseCallFunction: callFunction=" +
                str(callFunction) + ", useVar=" + str(useVar))

    def __enter__(self):
        if not self.callFunction and hasattr(self.widg, 'cmd'):
            self.tracer.trace_vdelete('w', self.widg.cmd_id)
            gui.debug("callFunction paused")

    def __exit__(self, a, b, c):
        if not self.callFunction and hasattr(self.widg, 'cmd'):
            self.widg.cmd_id = self.tracer.trace('w', self.widg.cmd)
            gui.debug("callFunction resumed")

#####################################
# classes to work with image maps
#####################################
class Point(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __str__(self):
        return "({},{})".format(self.x, self.y)

class AJRectangle(object):
    def __init__(self, name, posn, w, h):
        self.name = name
        self.corner = posn
        self.width = w
        self.height = h

    def __str__(self):
        return "{3}:({0},{1},{2})".format(self.corner, self.width, self.height, self.name)

    def contains(self, point):
        return (self.corner.x <= point.x <= self.corner.x + self.width and
                    self.corner.y <= point.y <= self.corner.y + self.height)

class GoogleMap(LabelFrame):
    """ Class to wrap a GoogleMap tile download into a widget"""

    def __init__(self, parent, app, defaultLocation="Marlborough, UK"):
        LabelFrame.__init__(self, parent, text="GoogleMaps")
        self.alive = True
        self.API_KEY = ""
        self.parent = parent
        self.imageQueue = Queue.Queue()
        self.defaultLocation = defaultLocation
        self.currentLocation = None
        self.app = app

        self.TERRAINS = ("Roadmap", "Satellite", "Hybrid", "Terrain")
        self.MAP_URL =  "http://maps.google.com/maps/api/staticmap?"
        self.GEO_URL = "https://maps.googleapis.com/maps/api/geocode/json?"
        self.LOCATION_URL = "http://freegeoip.net/json/"
#        self.LOCATION_URL = "http://ipinfo.io/json"
        self.setCurrentLocation()

        # the parameters that we store
        # keeps getting updated, then sent to GoogleMaps
        self.params = {}
        self.__setMapParams()

        imgObj = None
        self.rawData = None
        self.mapData = None
        self.request = None
        self.app.thread(self.getMapData)

        self.updateMapId = self.parent.after(500, self.updateMap)

        # if we got some map data then load it
        if self.mapData is not None:
            try:
                imgObj = PhotoImage(data=self.mapData)
                self.h = imgObj.height()
                self.w = imgObj.width()
            # python 3.3 fails to load data
            except Exception as e:
                gui.exception(e)

        if imgObj is None:
            self.w = self.params['size'].split("x")[0]
            self.h = self.params['size'].split("x")[1]

        self.canvas = Canvas(self, width=self.w, height=self.h)
        self.canvas.pack()#expand = YES, fill = BOTH)
        self.image_on_canvas = self.canvas.create_image(1, 1, image=imgObj, anchor=NW)
        self.canvas.img = imgObj

        # will store the 3 buttons in an array
        # they are actually labels - to hide border
        # maes it easier to configure them
        self.buttons = [
                    Label(self.canvas, text="-"),
                    Label(self.canvas, text="+"),
                    Label(self.canvas, text="H"),
                    Link(self.canvas, text="@")
                        ]
        B_FONT = font.Font(family='Helvetica', size=10)

        for b in self.buttons:
            b.configure(width=3, activebackground="#D2D2D2", relief=GROOVE, font=B_FONT)

            if gui.GET_PLATFORM() == gui.MAC:
                b.configure(cursor="pointinghand")
            elif gui.GET_PLATFORM() in [gui.WINDOWS, gui.LINUX]:
                b.configure(cursor="hand2")

        #make it look like it's pressed
        self.buttons[0].bind("<Button-1>",lambda e: self.buttons[0].config(relief=SUNKEN), add="+")
        self.buttons[0].bind("<ButtonRelease-1>",lambda e: self.buttons[0].config(relief=GROOVE), add="+")
        self.buttons[0].bind("<ButtonRelease-1>",lambda e: self.zoom("-"), add="+")

        self.buttons[1].bind("<Button-1>",lambda e: self.buttons[1].config(relief=SUNKEN), add="+")
        self.buttons[1].bind("<ButtonRelease-1>",lambda e: self.buttons[1].config(relief=GROOVE), add="+")
        self.buttons[1].bind("<ButtonRelease-1>",lambda e: self.zoom("+"), add="+")

        self.buttons[2].bind("<Button-1>",lambda e: self.buttons[2].config(relief=SUNKEN), add="+")
        self.buttons[2].bind("<ButtonRelease-1>",lambda e: self.buttons[2].config(relief=GROOVE), add="+")
        self.buttons[2].bind("<ButtonRelease-1>",lambda e: self.changeLocation(""), add="+")

        # an optionMenu of terrains
        self.terrainType = StringVar(self.parent)
        self.terrainType.set(self.TERRAINS[0])
        self.terrainOption = OptionMenu(self.canvas, self.terrainType, *self.TERRAINS, command=lambda e: self.changeTerrain(self.terrainType.get().lower()))
        self.terrainOption.config(highlightthickness=0)


        self.terrainOption.config(font=B_FONT)

        # an entry for searching locations
        self.locationEntry = Entry(self.canvas)
        self.locationEntry.bind('<Return>', lambda e: self.changeLocation(self.location.get()))
        self.location = StringVar(self.parent)
        self.locationEntry.config(textvariable=self.location)
        self.locationEntry.config(highlightthickness=0)

        self.__placeControls()

    def destroy(self):
        self.stopUpdates()
        if PYTHON2:
            LabelFrame.destroy(self)
        else:
            super(__class__, self).destroy()

    def __removeControls(self):
        self.locationEntry.place_forget()
        self.terrainOption.place_forget()
        self.buttons[0].place_forget()
        self.buttons[1].place_forget()
        self.buttons[2].place_forget()
        self.buttons[3].place_forget()

    def stopUpdates(self):
        self.alive = False
        self.parent.after_cancel(self.updateMapId)

    def __placeControls(self):
        self.locationEntry.place(rely=0, relx=0, x=8, y=8, anchor=NW)
        self.terrainOption.place(rely=0, relx=1.0, x=-8, y=8, anchor=NE)
        self.buttons[0].place(rely=1.0, relx=1.0, x=-5, y=-20, anchor=SE)
        self.buttons[1].place(rely=1.0, relx=1.0, x=-5, y=-38, anchor=SE)
        self.buttons[2].place(rely=1.0, relx=1.0, x=-5, y=-56, anchor=SE)
        self.buttons[3].place(rely=1.0, relx=1.0, x=-5, y=-74, anchor=SE)

        if self.request is not None:
            self.buttons[3].registerWebpage(self.request)
            self.__addTooltip(self.buttons[3], self.request)

    def __addTooltip(self, but, text):
        # generate a tooltip
        if ToolTip is not False:
            tt = ToolTip(
                but,
                text,
                delay=1000,
                follow_mouse=1)

    def __setMapParams(self):
        if "center" not in self.params or self.params["center"] is None or self.params["center"] == "":
            self.params["center"] = self.currentLocation
        if "zoom" not in self.params:
            self.params["zoom"] = 16
        if "size" not in self.params:
            self.params["size"] = "500x500"
        if "format" not in self.params:
            self.params["format"] = "gif"
        if "maptype" not in self.params:
            self.params["maptype"] = self.TERRAINS[0]

#        self.params["mobile"] = "true" # optional: mobile=true will assume the image is shown on a small screen (mobile device)
        self.params["sensor"] = "false"  # must be given, deals with getting loction from mobile device 

        self.markers = []

    def removeMarkers(self):
        self.markers = []
        self.app.thread(self.getMapData)

    def addMarker(self, location):
        self.markers.append(location)
        self.app.thread(self.getMapData)

    def saveTile(self, location):
        if self.rawData is not None:
            try:
                with open(location, "wb") as fh:
                    fh.write(self.rawData)
                gui.info("Map data written to file: " + str(location))
                return True
            except  Exception as e:
                gui.exception(e)
                return False
        else:
            gui.error("Unable to save map data - no data available")
            return False

    def setSize(self, size):
        if size != self.params["size"]:
            self.params["size"] = size.lower()
            self.app.thread(self.getMapData)

    def changeTerrain(self, terrainType):
        terrainType = terrainType.title()
        if terrainType in self.TERRAINS:
            self.terrainType.set(terrainType)
            if self.params["maptype"] != self.terrainType.get().lower():
                self.params["maptype"] = self.terrainType.get().lower()
                self.app.thread(self.getMapData)

    def changeLocation(self, location):
        self.location.set(location) # update the entry
        if self.params["center"] != location:
            self.params["center"] = location
            self.app.thread(self.getMapData)

    def setZoom(self, zoom):
        if 0 <= zoom <= 22:
            self.params["zoom"] = zoom
            self.app.thread(self.getMapData)

    def zoom(self, mod):
        if mod == "+" and self.params["zoom"] < 22:
            self.params["zoom"] += 1
            self.app.thread(self.getMapData)
        elif mod == "-" and self.params["zoom"] > 0:
            self.params["zoom"] -= 1
            self.app.thread(self.getMapData)

    def updateMap(self):
        if not self.alive: return
        if not self.imageQueue.empty():
            self.rawData = self.imageQueue.get()
            self.mapData = base64.encodestring(self.rawData)
            try:
                imgObj = PhotoImage(data=self.mapData)
            except:
                gui.error("Error parsing image data")
            else:
                self.canvas.itemconfig(self.image_on_canvas, image=imgObj)
                self.canvas.img = imgObj

                h = imgObj.height()
                w = imgObj.width()

                if h != self.h or w != self.w:
                    self.__removeControls()
                    self.h = h
                    self.w = w
                    self.canvas.config(width=self.w, height=self.h)
                    self.__placeControls()
                if self.request is not None:
                    self.buttons[3].registerWebpage(self.request)
                    self.__addTooltip(self.buttons[3], self.request)
        self.updateMapId = self.parent.after(200, self.updateMap)

    def __buildQueryURL(self):
        self.request = self.MAP_URL + urlencode(self.params)
        if len(self.markers) > 0:
            m = "|".join(self.markers)
            m = quote_plus(m)
            self.request += "&markers=" + m
            
        gui.debug("GoogleMap search URL: " + self.request)

    def __buildGeoURL(self, location):
        """ for future use - gets the location
        """
        p = {}
        p["address"] = location
        p["key"] = self.API_KEY
        req = self.GEO_URL + urlencode(p)
        return req

    def getMapData(self):
        """ will query GoogleMaps & download the image data as a blob """
        if self.params['center'] == "":
            self.params["center"] = self.currentLocation
        self.__buildQueryURL()
        gotMap = False
        while not gotMap:
            if self.request is not None:
                try:
                    u = urlopen(self.request)
                    rawData = u.read()
                    u.close()
                    self.imageQueue.put(rawData)
                    gotMap = True
                except Exception as e:
                    gui.error("Unable to contact GoogleMaps")
                    time.sleep(1)
            else:
                gui.debug("No request")
                time.sleep(.25)

    def getMapFile(self, fileName):
        """ will query GoogleMaps & download the image into the named file """
        self.__buildQueryURL()
        self.buttons[3].registerWebpage(self.request)
        try:
            urlretrieve(self.request, fileName)
            return fileName
        except Exception as e:
            gui.error("Unable to contact GoogleMaps")
            return None

    def setCurrentLocation(self):
        gui.debug("Location request URL: " + self.LOCATION_URL)
        try:
            self.currentLocation = self.__locationLookup()
        except Exception as e:
            gui.error("Unable to contact location server, using default: " + self.defaultLocation)
            self.currentLocation = self.defaultLocation

    def __locationLookup(self):
        u =  urlopen(self.LOCATION_URL)
        data = u.read().decode("utf-8")
        u.close()
        gui.debug("Location data: " + data)
        data = json.loads(data)
#        location = data["loc"]
        location = str(data["latitude"]) + "," + str(data["longitude"])
        return location


#####################################
class CanvasDnd(Canvas):
    """
    A canvas to which we have added those methods necessary so it can
        act as both a TargetWidget and a TargetObject. 
        
    Use (or derive from) this drag-and-drop enabled canvas to create anything
        that needs to be able to receive a dragged object.    
    """    
    def __init__(self, Master, cnf={}, **kw):
        if cnf:
            kw.update(cnf)
        Canvas.__init__(self, Master,  kw)
        self.config(bd=0, highlightthickness=0)

    #----- TargetWidget functionality -----
    
    def dnd_accept(self, source, event):
        #Tkdnd is asking us (the TargetWidget) if we want to tell it about a
        #    TargetObject. Since CanvasDnd is also acting as TargetObject we
        #    return 'self', saying that we are willing to be the TargetObject.
        gui.debug("<<"+str(type(self))+".dnd_accept>> " + str(source))
        return self

    #----- TargetObject functionality -----

    # This is called when the mouse pointer goes from outside the
    # Target Widget to inside the Target Widget.
    def dnd_enter(self, source, event):
        gui.debug("<<"+str(type(self))+".dnd_enter>> " + str(source))
        XY = gui.MOUSE_POS_IN_WIDGET(self, event)
        # show the dragged object
        source.appear(self ,XY)
        
    # This is called when the mouse pointer goes from inside the
    # Target Widget to outside the Target Widget.
    def dnd_leave(self, source, event):
        gui.debug("<<"+str(type(self))+".dnd_leave>> " + str(source))
        # hide the dragged object
        source.vanish()
        
    #This is called when the mouse pointer moves withing the TargetWidget.
    def dnd_motion(self, source, event):
        gui.debug("<<"+str(type(self))+".dnd_motion>> " + str(source))
        XY = gui.MOUSE_POS_IN_WIDGET(self,event)
        # move the dragged object
        source.move(self, XY)
        
    #This is called if the DraggableWidget is being dropped on us.
    def dnd_commit(self, source, event):
        gui.debug("<<"+str(type(self))+".dnd_commit>> " + str(source))

# A canvas specifically for deleting dragged objects.
class TrashBin(CanvasDnd):
    def __init__(self, master, **kw):
        if "width" not in kw:
            kw['width'] = 150
        if "height" not in kw:
            kw['height'] = 25    

        CanvasDnd.__init__(self, master, kw)
        self.config(relief="sunken", bd=2)
        x = kw['width'] / 2
        y = kw['height'] / 2
        self.textId = self.create_text(x, y, text='TRASH', anchor="center")

    def dnd_commit(self, source, event):
        gui.debug("<<TRASH_BIN.dnd_commit>> vanishing source")
        source.vanish(True)

    def config(self, **kw):
        self.configure(**kw)

    def configure(self, **kw):
        kw = gui.CLEAN_CONFIG_DICTIONARY(**kw)
        if "fg" in kw:
            fg=kw.pop('fg')
            self.itemconfigure(self.textId, fill=fg)

        if PYTHON2:
            CanvasDnd.config(self, **kw)
        else:
            super(__class__, self).config(**kw)

# This is a prototype thing to be dragged and dropped.
class DraggableWidget:
    discardDragged = False

    def dnd_accept(self, source, event):
        return None
    
    def __init__(self, parent, title, name, XY, widg=None):
        self.parent = parent
        gui.debug("<<DRAGGABLE_WIDGET.__init__>>")

        #When created we are not on any canvas
        self.Canvas = None
        self.OriginalCanvas = None
        self.widg = widg

        #This sets where the mouse cursor will be with respect to our label
        self.OffsetCalculated = False
        self.OffsetX = XY[0]
        self.OffsetY = XY[1]

        # give ourself a name
        self.Name = name
        self.Title = title

        self.OriginalID = None
        self.dropTarget = None
        
    # this gets called when we are dropped
    def dnd_end(self, target, event):
        gui.debug("<<DRAGGABLE_WIDGET.dnd_end>> " + str(self.Name) + " target=" + str(target))

        # from somewhere, dropped nowhere - self destruct, or put back
        if self.Canvas is None:
            gui.debug("<<DRAGGABLE_WIDGET.dnd_end>> dropped with Canvas (None)")
            if DraggableWidget.discardDragged:
                gui.debug("<<DRAGGABLE_WIDGET.dnd_end>> DISCARDING under order")
            else:
                if self.OriginalCanvas is not None:
                    gui.debug("<<DRAGGABLE_WIDGET.dnd_end>> RESTORING")
                    self.restoreOldData()
                    self.Canvas.dnd_enter(self, event)
                else:
                    gui.debug("<<DRAGGABLE_WIDGET.dnd_end>> DISCARDING as nowhere to go")

        # have been dropped somewhere
        else:
            gui.debug("<<DRAGGABLE_WIDGET.dnd_end>> dropped with Canvas("+str(self.Canvas)+") Target=" + str(self.dropTarget))
            if not self.dropTarget:
                # make the dragged object re-draggable
                self.Label.bind('<ButtonPress>', self.press)
            else:
                if self.dropTarget.keepWidget(self.Title, self.Name):
                    self.Label.bind('<ButtonPress>', self.press)
                else:
                    self.vanish(True)

            # delete any old widget
            if self.OriginalCanvas:
                self.OriginalCanvas.delete(self.OriginalID)
                self.OriginalCanvas = None
                self.OriginalID = None
                self.OriginalLabel = None

    # put a label representing this DraggableWidget instance on Canvas.
    def appear(self, canvas, XY):
    
        if not isinstance(canvas, CanvasDnd):
            self.dropTarget = canvas
            canvas = canvas.dnd_canvas
#        else:
#            self.dropTarget = None

        if self.Canvas:
            gui.debug("<<DRAGGABLE_WIDGET.appear> - ignoring, as we already exist?: " + str(canvas) + str(XY))
            return
        else:
            gui.debug("<<DRAGGABLE_WIDGET.appear> - appearing: " + str(canvas) + str(XY))

            self.Canvas = canvas
            self.X, self.Y = XY    
            self.Label = Label(self.Canvas, text=self.Name, borderwidth=2, relief=RAISED)

            # Offsets are received as percentages from initial button press
            # so calculate Offset from a percentage
            if not self.OffsetCalculated:
                self.OffsetX = self.Label.winfo_reqwidth() * self.OffsetX
                self.OffsetY = self.Label.winfo_reqheight() * self.OffsetY
                self.OffsetCalculated = True

            self.ID = self.Canvas.create_window(self.X-self.OffsetX, self.Y-self.OffsetY, window=self.Label, anchor="nw")
            gui.debug("<<DRAGGABLE_WIDGET.appear> - created: " + str(self.Label) + str(self.Canvas))

    # if there is a label representing us on a canvas, make it go away.
    def vanish(self, all=False):
        # if we had a canvas, delete us
        if self.Canvas:
            gui.debug("<<DRAGGABLE_WIDGET.vanish> - vanishing")
            self.storeOldData()
            self.Canvas.delete(self.ID)
            self.Canvas = None
            del self.ID
            del self.Label
        else:
            gui.debug("<<DRAGGABLE_WIDGET.vanish>> ignoring")

        if all and self.OriginalCanvas:
            gui.debug("<<DRAGGABLE_WIDGET.vanish>> restore original")
            self.OriginalCanvas.delete(self.OriginalID)
            self.OriginalCanvas = None
            del self.OriginalID
            del self.OriginalLabel

    # if we have a label on a canvas, then move it to the specified location. 
    def move(self, widget, XY):
        gui.debug("<<DRAGGABLE_WIDGET.move>> " + str(self.Canvas) + str(XY))
        if self.Canvas:
            self.X, self.Y = XY
            self.Canvas.coords(self.ID, self.X-self.OffsetX, self.Y-self.OffsetY)
        else:
            gui.error("<<DRAGGABLE_WIDGET.move>> unable to move - NO CANVAS!") 

    def press(self, event):
        gui.debug("<<DRAGGABLE_WIDGET.press>>")
        self.storeOldData()

        self.ID = None
        self.Canvas = None
        self.Label = None

        #Ask Tkdnd to start the drag operation
        if INTERNAL_DND.dnd_start(self, event):
            self.OffsetX, self.OffsetY = gui.MOUSE_POS_IN_WIDGET(self.OriginalLabel, event, False)
            XY = gui.MOUSE_POS_IN_WIDGET(self.OriginalCanvas, event, False)
            self.appear(self.OriginalCanvas, XY)

    def storeOldData(self, phantom=False):
        gui.debug("<<DRAGGABLE_WIDGET.storeOldData>>")
        self.OriginalID = self.ID
        self.OriginalLabel = self.Label
        self.OriginalText = self.Label['text']
        self.OriginalCanvas = self.Canvas
        if phantom:
            gui.debug("<<DRAGGABLE_WIDGET.storeOldData>> keeping phantom")
            self.OriginalLabel["text"] = "<Phantom>"
            self.OriginalLabel["relief"] = RAISED
        else:
            gui.debug("<<DRAGGABLE_WIDGET.storeOldData>> hiding phantom")
            self.OriginalCanvas.delete(self.OriginalID)
        
    def restoreOldData(self):
        if self.OriginalID:
            gui.debug("<<DRAGGABLE_WIDGET.restoreOldData>>")
            self.ID = self.OriginalID
            self.Label = self.OriginalLabel
            self.Label['text'] = self.OriginalText
            self.Label['relief'] = RAISED
            self.Canvas = self.OriginalCanvas
            self.OriginalCanvas.itemconfigure(self.OriginalID, state='normal')
            self.Label.bind('<ButtonPress>', self.press)
        else:
            gui.debug("<<DRAGGABLE_WIDGET.restoreOldData>> unable to restore - NO OriginalID")


#####################################
# MAIN - for testing
#####################################
if __name__ == "__main__":
    print("This is a library class and cannot be executed.")
    sys.exit()
