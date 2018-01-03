# http://stackoverflow.com/questions/14267900/python-drag-and-drop-explorer-files-to-tkinter-entry-widget/
import os
try: import tkinter
except: import Tkinter as tkinter

def _load_tkdnd(master):
    tkdndlib = os.environ.get('TKDND_LIBRARY')
    if tkdndlib:
        master.tk.eval('global auto_path; lappend auto_path {%s}' % tkdndlib)
    master.tk.eval('package require tkdnd')
    master._tkdnd_loaded = True
    
class TkDND(object):
    def __init__(self, master):
        if not getattr(master, '_tkdnd_loaded', False):
            _load_tkdnd(master)
        self.master = master
        self.tk = master.tk

    # Available pre-defined values for the 'dndtype' parameter:
    #   text/plain
    #   text/plain;charset=UTF-8
    #   text/uri-list

    def bindtarget(self, window, callback, dndtype, event='<Drop>', priority=50):
        cmd = self._prepare_tkdnd_func(callback)
        return self.tk.call('dnd', 'bindtarget', window, dndtype, event, cmd, priority)

    def bindtarget_query(self, window, dndtype=None, event='<Drop>'):
        return self.tk.call('dnd', 'bindtarget', window, dndtype, event)

    def cleartarget(self, window):
        self.tk.call('dnd', 'cleartarget', window)

    def bindsource(self, window, callback, dndtype, priority=50):
        cmd = self._prepare_tkdnd_func(callback)
        self.tk.call('dnd', 'bindsource', window, dndtype, cmd, priority)

    def bindsource_query(self, window, dndtype=None):
        return self.tk.call('dnd', 'bindsource', window, dndtype)

    def clearsource(self, window):
        self.tk.call('dnd', 'clearsource', window)

    def drag(self, window, actions=None, descriptions=None,
            cursorwin=None, callback=None):
        cmd = None
        if cursorwin is not None:
            if callback is not None:
                cmd = self._prepare_tkdnd_func(callback)
        self.tk.call('dnd', 'drag', window, actions, descriptions,
                cursorwin, cmd)


    _subst_format = ('%A', '%a', '%b', '%D', '%d', '%m', '%T',
            '%W', '%X', '%Y', '%x', '%y')
    _subst_format_str = " ".join(_subst_format)

    def _prepare_tkdnd_func(self, callback):
        funcid = self.master.register(callback, self._dndsubstitute)
        cmd = ('%s %s' % (funcid, self._subst_format_str))
        return cmd

    def _dndsubstitute(self, *args):
        if len(args) != len(self._subst_format):
            return args

        def try_int(x):
            x = str(x)
            try:
                return int(x)
            except ValueError:
                return x

        A, a, b, D, d, m, T, W, X, Y, x, y = args

        event = tkinter.Event()
        event.action = A       # Current action of the drag and drop operation.
        event.action_list = a  # Action list supported by the drag source.
        event.mouse_button = b # Mouse button pressed during the drag and drop.
        event.data = D         # The data that has been dropped.
        event.descr = d        # The list of descriptions.
        event.modifier = m     # The list of modifier keyboard keys pressed.
        event.dndtype = T
        event.widget = self.master.nametowidget(W)
        event.x_root = X       # Mouse pointer x coord, relative to the root win.
        event.y_root = Y
        event.x = x            # Mouse pointer x coord, relative to the widget.
        event.y = y

        event.action_list = str(event.action_list).split()
        for name in ('mouse_button', 'x', 'y', 'x_root', 'y_root'):
            setattr(event, name, try_int(getattr(event, name)))

        return (event, )
