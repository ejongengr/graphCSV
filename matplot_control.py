# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 11:24:10 2016

Display analog data from Sensor Board
Usage: c:> python scope_matplot.py

        self.maxLen = 100
        self.a0_buffer = []

		  
@author: Jason Lee
"""

from collections import OrderedDict
import math
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
from matplotlib import widgets
import numpy as np
import sys
import threading
       
INTERVAL = 100 # How open update windows, in miliseconds

class PickControl:
    def __init__(self, fig):
        self.fig = fig
        self._pickers = []
        self._pickcids = []

    def connect_picks(self):
        for i, picker in enumerate(self._pickers):
            if self._pickcids[i] is None:
                cid = self.fig.canvas.mpl_connect('pick_event', picker)
                self._pickcids[i] = cid

    def disconnect_picks(self):
        for i, cid in enumerate(self._pickcids):
            if cid is not None:
                self.fig.canvas.mpl_disconnect(cid)
                self._pickcids[i] = None

    def add_pick_action(self, picker):
        if not callable(picker):
            raise ValueError("Invalid picker. Picker function is not callable")
        if  picker in self._pickers:
            raise ValueError("Picker is already in the list of pickers")
        self._pickers.append(picker)
        cid = self.fig.canvas.mpl_connect('pick_event', picker)
        self._pickcids.append(cid)

class KeymapControl:
    def __init__(self, fig):
        self.fig = fig
        # Deactivate the default keymap
        fig.canvas.mpl_disconnect(fig.canvas.manager.key_press_handler_id)
        self._keymap = OrderedDict()
        # Activate my keymap
        self.connect_keymap()
        self._lastkey = None

    def connect_keymap(self):
        self._keycid = self.fig.canvas.mpl_connect('key_press_event',
                                                   self.keypress)

    def disconnect_keymap(self):
        if self._keycid is not None:
            self.fig.canvas.mpl_disconnect(self._keycid)
            self._keycid = None

    def add_key_action(self, key, description, action_func):
        if not callable(action_func):
            raise ValueError("Invalid key action. Key '%s' Description '%s'"
                             " - action function is not a callable" %
                             (key, description))
        if key in self._keymap:
            raise ValueError("Key '%s' is already in the keymap" % key)
        self._keymap[key] = (description, action_func)

    def keypress(self, event):
        action_tuple = self._keymap.get(event.key, None)
        if action_tuple:
            self._lastkey = event.key
            action_tuple[1]()

    def display_help_menu(self):
        print("Help Menu")
        print("Key         Action")
        print("=========== ============================================")
        for key, (description, _) in self._keymap.items():
            print("%11s %s" % (key, description))
        
class ButtonControl:
    def __init__(self, fig, width, height):
        self.fig = fig
        # Give us some room along the top
        fig.subplots_adjust(top=1-height*2)
        self._buttonwidth = width
        self._buttonheight = height
        self._buttonmap = {}

    def connect_buttonmap(self):
        for text, (cid, func, button) in self._buttonmap.items():
            if cid is None:
                cid = button.on_clicked(func)
                self._buttonmap[text] = (cid, func, button)

    def disconnect_buttonmap(self):
        for text, (cid, func, button) in self._buttonmap.items():
            if cid is not None:
                button.disconnect(cid)
                self._buttonmap[text] = (None, func, button)

    def add_button_action(self, text, action_func):
        if not callable(action_func):
            raise ValueError("Invalid button action. Button '%s''s"
                             " action function is not a callable" % text)
        if text in self._buttonmap:
            raise ValueError("Button '%s' is already a button" % text)
        ax = self.fig.add_axes([len(self._buttonmap) * self._buttonwidth,
                                0.99 - self._buttonheight,
                                self._buttonwidth, self._buttonheight])
        button = widgets.Button(ax, text)
        # Swallow the event parameter. We don't need it for these buttons
        func = lambda event: action_func()
        cid = button.on_clicked(func)
        self._buttonmap[text] = (cid, func, button)

def build_progress_bar(fig, lastframe, height):
    # Give us some room along the bottom
    fig.subplots_adjust(bottom = 4*height)
    barax = fig.add_axes([0.08, 0.005, 0.78, height])
    bar = widgets.Slider(barax, 'Test', 0, lastframe, valinit=0,
                         valfmt='%d of '+str(lastframe))
    return bar
        
def build_check_buttons(fig, width):
    # Give us some room along the right
    fig.subplots_adjust(right = 1-width)
    boxax = fig.add_axes([0.99 - width, 0.8, width, 0.1])
    checks = widgets.CheckButtons(boxax, ('Auto Scale', 'Test'),
                                  [True]*2)
    return checks
    
class ControlSys(PickControl, KeymapControl, ButtonControl):
    def __init__(self, fig, ax):
        self.ax = ax
        PickControl.__init__(self, fig)
        KeymapControl.__init__(self, fig)
        ButtonControl.__init__(self, fig, 0.1, 0.05)
        #self._progress_bar = build_progress_bar(fig, 1, 0.02)
        #self._toggle_buttons = build_check_buttons(fig, 0.1)

        self._connect('help', lambda x: self.display_help_menu())
        # Progress bar
        #self._progress_bar.on_changed(
        #        lambda frame: self.progress_func())

        # Check button
        #self._toggle_buttons.on_clicked(self.toggle_autoscale)
        self.b_autoscale = True
        
        # Key map
        self.add_key_action('i', 'Display this help menu',
                            lambda : self._emit('help', None))
        # Button
        self.add_button_action('Fit H', lambda : self.fit_height())
        self.add_button_action('Help', lambda : self._emit('help', None))
        # Pick
        self.add_pick_action(self.select_line)
        # Event
        #fig.canvas.mpl_connect('draw_event', self.ondraw)
        #self.count = 0

    def ondraw(self, event):        
        self.count += 1
        print self.count, ":auto scale", self.b_autoscale
        if self.b_autoscale == True:
            self.autoscale_y(self.ax)
    
    def _emit(self, event, eventdata):
        self.fig.canvas.callbacks.process(event, eventdata)

    def _connect(self, event, callback):
        self.fig.canvas.mpl_connect(event, callback)

    def fit_height(self):
        self.autoscale_y(self.ax)
        self.fig.canvas.draw()
        
    def progress_func(self):
        pass

    def select_line(self, event):
        pass
    
    def toggle_autoscale(self, item):
        if item == 'Auto Scale':
            self.b_autoscale ^= True
        else:
            raise ValueError("Invalid name %s for auto scale toggling" % item)
        
    def autoscale_y(self, ax, margin=0.5):
        """This function rescales the y-axis based on the data that is visible given the current xlim of the axis.
        ax -- a matplotlib axes object
        margin -- the fraction of the total height of the y-data to pad the upper and lower ylims"""

        def get_bottom_top(line):
            yd = line.get_ydata()
            bot = np.min(yd)
            top = np.max(yd)
            return bot,top

        lines = ax.get_lines()
        bot,top = np.inf, -np.inf

        for line in lines:
            if line.get_visible():
                new_bot, new_top = get_bottom_top(line)
                if new_bot < bot: 
                    bot = new_bot
                if new_top > top: 
                    top = new_top
        h = top - bot
        top = top + margin*h
        bot = bot - margin*h

        ax.set_ylim(bot,top)    

        
# call main
if __name__ == '__main__':
    import numpy as np
    
    fig = plt.figure()
    xlim = (0, 100)
    ylim=(0, 1)
    ax = plt.axes(xlim=xlim, ylim=ylim)
    plt.grid()
    line, = ax.plot(range(100), np.random.rand(100))
    ctrl_sys = ControlSys(fig)
    plt.show()
    
    
