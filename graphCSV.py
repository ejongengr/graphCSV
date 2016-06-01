# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 15:08:12 2016

@author: Jason
"""

from argparse import ArgumentParser
import matplotlib.pyplot as plt
from matplotlib import widgets
from matplotlib.widgets import Cursor
# https://pypi.python.org/pypi/mpldatacursor#downloads
# from mpldatacursor import datacursor
from matplot_cursor import FollowDotCursor
from matplot_control import ControlSys
import numpy as np
import pandas as pd
from PyQt4 import QtGui, QtCore
import sys

class CGraph():
    def __init__(self, fig, plt, ax, ctrl_sys, df, datfile):
        self.fig = fig
        self.plt = plt
        self.ax = ax
        self.ctrl = ctrl_sys
        
        self.df = df
        self.col_len = len(df.columns)
        self.lst_graph = [None for i in range(self.col_len)]
        self.minmax = {}
        
        #close event
        fig.canvas.mpl_connect('close_event', self.handle_close)

        # Cursor
        plt.connect('button_press_event', self.onpress)
        plt.connect('button_release_event', self.release)
        plt.connect('motion_notify_event', self.move_mouse)
        self.Lbtn_Pressed = False
        self.Rbtn_Pressed = False

        #legend
        self.legend = []
        # Shrink current axis by 20%
        box = ax.get_position()
        self.ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        
		#Title
        self.fig.canvas.set_window_title(datfile)
		
        # Cursor 1
        self.cur1_en = False
        self.lx1 = ax.axhline(color='r')  # the horiz line
        self.ly1 = ax.axvline(color='r')  # the vert line
        self.x1 = range(self.df.shape[0])
        self.y1 = self.df[df.columns[0]]
        self.xl = 0
        self.yl = 0
        # Cursor 2
        self.cur2_en = False
        self.lx2 = ax.axhline(color='b')  # the horiz line
        self.ly2 = ax.axvline(color='b')  # the vert line
        self.x2 = range(self.df.shape[0])
        self.y2 = self.df[df.columns[0]]
        self.xr = 0
        self.yr = 0

        # text location in axes coords
        self.txt1 = ax.text(0.7, 0.9, '', transform=ax.transAxes)
        self.txt2 = ax.text(0.7, 0.85, '', transform=ax.transAxes)
        self.txt3 = ax.text(0.7, 0.8, '', transform=ax.transAxes)

        self.cursor_on(1, False)
        self.cursor_on(2, False)
        

    def onpress(self, event):
        if event.button == 1:   # mouse left button press
            self.Lbtn_Pressed = True
        elif event.button == 3:    # mouse right button press
            self.Rbtn_Pressed = True
          
    def release(self, event):
        if event.button == 1:   # mouse left button release
            self.Lbtn_Pressed = False
        elif event.button == 3:    # mouse right button release
            self.Rbtn_Pressed = False

    def move_mouse(self, event):
        if not event.inaxes:
            return
        if self.fig.canvas.manager.toolbar._active is not None:
        # toolbar is not trying to grab clicks (either through pan or zoom)
            return
        
        x, y = event.xdata, event.ydata

        if self.cur1_en and self.Lbtn_Pressed:
            indx = np.searchsorted(self.x1, [x])[0]
            try:
                self.xl = self.x1[indx]
                self.yl = self.y1[indx]
            except: 
                return
            self.lx1.set_ydata(self.yl)
            self.ly1.set_xdata(self.xl)
            self.txt1.set_text('x(L)=%1.2f, y(L)=%1.2f\n' % (self.xl, self.yl))
        elif self.cur2_en and self.Rbtn_Pressed:
            indx = np.searchsorted(self.x2, [x])[0]
            try:
                self.xr = self.x2[indx]
                self.yr = self.y2[indx]
            except:
                return
            self.lx2.set_ydata(self.yr)
            self.ly2.set_xdata(self.xr)
            self.txt2.set_text('x(R)=%1.2f, y(R)=%1.2f\n' % (self.xr, self.yr))
        if self.cur1_en and self.cur2_en:
            dx = self.xr - self.xl
            dy = self.yr - self.yl
            self.txt3.set_text('dx=%1.2f, dy=%1.2f\n' % (dx, dy))

        self.plt.draw()

    def handle_close(self, event):
        print('Closed Figure!')
        sys.exit()
        
    def load_graph(self, i):
        col_name = self.df.columns[i]
        p, = self.ax.plot(self.df[col_name], label=col_name, marker='.')
        self.lst_graph[i] = p
        # Update legend
        self.legend.append(p)
        # Put a legend to the right of the current axis
        self.ax.legend(handles=self.legend, loc='center left', bbox_to_anchor=(1, 0.5))
                
    def update_draw(self):
        self.ax.legend(handles=self.legend, loc='center left', bbox_to_anchor=(1, 0.5))
        self.fig.canvas.draw()             

    def set_visible(self, i, tf):
        p = self.lst_graph[i]
        if tf:  #True
            if p == None:   # graph not loaded yet
                self.load_graph(i)
            elif not p.get_visible(): # not visible
                p.set_visible(True)
                self.legend.append(p)
        else:  #False              
            if p != None:   # graph loaded already
                if p.get_visible():
                    p.set_visible(False)
                    self.legend.remove(p)
   
    def cursor_on(self, btn, checked):
        if btn == 1:
            if checked:
                self.cur1_en = True
                self.lx1.set_visible(True)
                self.ly1.set_visible(True)
                self.txt1.set_visible(True)
            else:
                self.cur1_en = False
                self.lx1.set_visible(False)
                self.ly1.set_visible(False)            
                self.txt1.set_visible(False)
        elif btn == 2:    
            if checked:
                self.cur2_en = True
                self.lx2.set_visible(True)
                self.ly2.set_visible(True)
                self.txt2.set_visible(True)
            else:
                self.cur2_en = False
                self.lx2.set_visible(False)
                self.ly2.set_visible(False)
                self.txt2.set_visible(False)
        if self.cur1_en and self.cur2_en:
            self.txt3.set_visible(True)
        else:
            self.txt3.set_visible(False)        
        
        self.update_draw()

    def select_cursor_data(self, btn, header):
        if btn == 1: #Left
            self.y1 = self.df[str(header)]
        else:
            self.y2 = self.df[str(header)]

    def autoscale_y(self, margin=0.5):
        """This function rescales the y-axis based on the data that is visible given the current xlim of the axis.
        ax -- a matplotlib axes object
        margin -- the fraction of the total height of the y-data to pad the upper and lower ylims"""

        def get_bottom_top(label):
            if label in self.minmax: # min max already calculated and stored in dictionary
                bot, top = self.minmax[label]
            else:
                bot = self.df[label].min()
                top = self.df[label].max()
                self.minmax[label] = (bot, top)
            return bot,top

        lines = self.ax.get_lines()
        bot, top = np.inf, -np.inf

        for line in lines:
            label = line.get_label()
            if label in self.df.columns.values:   # remove unused u'_line0'
                if line.get_visible():
                    new_bot, new_top = get_bottom_top(label)
                    new_bot = float(new_bot) # 0.02<inf : false
                    new_top = float(new_top)
                    if new_bot < bot:                        
                        bot = new_bot
                    if new_top > top: 
                        top = new_top
        h = top - bot
        top = top + margin*h
        bot = bot - margin*h

        self.ax.set_ylim(bot,top)    
        
        
class MyWidget(QtGui.QWidget):
    
    def __init__(self, fig, plt, ax, df, datfile, parent=None):
        self.legend = []
        self.ax = ax
        self.df = df
        
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle(datfile)
        self.setGeometry(20,50,150,150)

        self.grid=QtGui.QGridLayout()

        # Line
        #self.grid.addWidget(self.Line,0,0)

        #combo box
        self.combo_L = QtGui.QComboBox(self)
        self.combo_R = QtGui.QComboBox(self)
        for header in df.columns.values:
            self.combo_L.addItem(header)
            self.combo_R.addItem(header)
        self.connect(self.combo_L,QtCore.SIGNAL('currentIndexChanged(QString)'),
                    lambda: self.select_cursor_data(1))
        self.connect(self.combo_R,QtCore.SIGNAL('currentIndexChanged(QString)'),
                    lambda: self.select_cursor_data(2))
        
        self.grid.addWidget(self.combo_L,0,0)
        self.cb_L = QtGui.QCheckBox("L cursor", self)
        self.connect(self.cb_L, QtCore.SIGNAL('stateChanged(int)'),
                        self.cursor_on)
        self.grid.addWidget(self.cb_L, 0, 1)

        self.grid.addWidget(self.combo_R,1,0)
        self.cb_R = QtGui.QCheckBox("R cursor", self)
        self.connect(self.cb_R, QtCore.SIGNAL('stateChanged(int)'),
                        self.cursor_on)
        self.grid.addWidget(self.cb_R, 1, 1)
       
        # Push Button
        self.all_Visible=QtGui.QPushButton('Show All', self)
        self.connect(self.all_Visible, QtCore.SIGNAL('clicked()'),self.AllVisible)
        self.all_Hide=QtGui.QPushButton('Hide All', self)
        self.connect(self.all_Hide, QtCore.SIGNAL('clicked()'),self.AllHide)
        self.grid.addWidget(self.all_Visible,2,0)
        self.grid.addWidget(self.all_Hide,3,0)

        # Check Box
        self.cb_scale = QtGui.QCheckBox("Auto Fit Height", self)
        self.cb_scale.setCheckState(2)
        self.connect(self.cb_scale, QtCore.SIGNAL('stateChanged(int)'),
                        self.ToggelAutoScale)
        self.grid.addWidget(self.cb_scale, 3, 1)
        self.b_autoscale = True
        
        self.cb = []
        i = 6   # layout index
        for header in [column for column in df]:
            c = QtGui.QCheckBox(header, self)                            
            self.connect(c, QtCore.SIGNAL('stateChanged(int)'),
                     self.ToggleVisibility)
            col_number = 2 # how many columns 
            j = (i-2) // col_number + 2
            k = (i-2) % col_number
            self.grid.addWidget(c, j, k)
            i += 1
            self.cb.append(c)            
        
        # Status bar
        self.StatusBar = QtGui.QStatusBar(self)
        self.grid.addWidget(self.StatusBar, i, 0)
        self.StatusBar.showMessage("Happy Day  ")

        self.setLayout(self.grid)
        #self.Line,QtCore.SLOT('setText(QString)'))
        
        # Graph
        ctrl_sys = ControlSys(fig, ax)
        self.cg = CGraph(fig, plt, ax, ctrl_sys, df, datfile)
   
    def closeEvent(self, event):
        print "Closing GUI"
        sys.exit()

    def AllVisible(self):
        i = 0
        for each in self.cb:
            each.setCheckState(2)
            self.cg.set_visible(i, True)
            i += 1
        self.UpdateDraw()
        
    def AllHide(self):
        i = 0
        for each in self.cb:
            each.setCheckState(0)
            self.cg.set_visible(i, False)
            i += 1
        self.UpdateDraw()
        
    def ToggleVisibility(self):
        i = 0
        for each in self.cb:
            if each.isChecked():	#checked
                self.cg.set_visible(i, True)
            else:
                self.cg.set_visible(i, False)            
            i += 1
        self.UpdateDraw()
        
    def UpdateDraw(self):
        if self.b_autoscale:
            self.cg.autoscale_y()
        self.cg.update_draw()             
    
    def GetAddr(self):
        return self.addr

    def ToggelAutoScale(self):
        self.b_autoscale ^= True
        if self.b_autoscale:
            self.cg.autoscale_y()
            self.cg.update_draw()             

 
    def cursor_on(self):
        if self.cb_L.isChecked():
            self.cg.cursor_on(1, True)
        else:
            self.cg.cursor_on(1, False)
        if self.cb_R.isChecked():
            self.cg.cursor_on(2, True)
        else:
            self.cg.cursor_on(2, False)
    
    def select_cursor_data(self, btn):
        if btn == 1: #Left
            header = self.combo_L.currentText()
            self.cb_L.setCheckState(2)
        else:
            header = self.combo_R.currentText()
            self.cb_R.setCheckState(2)
        self.cg.select_cursor_data(btn, header)
        # check box check
        clist = list(self.df.columns.values) # make headers to list
        i = clist.index(header) #find index of the header
        self.cb[i].setCheckState(2) #check checkbox
        self.cg.set_visible(i, True) #make visiabel
        
def graph_csv(datfile, no_header, ion, d):
    # read csv to array
    if no_header:
        df = pd.read_csv(datfile, sep=',', header=None)
    else:
        df = pd.read_csv(datfile, sep=',', header=0)
    
    if d:
        df.drop(df.index[0:1], inplace=True)
    
    fig, ax = plt.subplots(1, 1)
    
    plt.grid()
    if ion:
        plt.ion()
    else:
        plt.ioff()

    app = QtGui.QApplication(sys.argv)
    screen_rect = app.desktop().screenGeometry()
    width, height = screen_rect.width(), screen_rect.height()

    w = MyWidget(fig, plt, ax, df, datfile)
    w.show()
    #window size
    top = w.frameGeometry().top()
    right = w.frameGeometry().right()
    # screen size
    #width = 800
    #height = 600
    mngr = plt.get_current_fig_manager()
    # to put it into the upper left corner for example:
    x1 = right + 20
    y1 = top + 31
    mngr.window.setGeometry(x1,y1,width-x1-70,height-y1-40)

    plt.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':

    parser = ArgumentParser(description="Plot a CSV file")
    parser.add_argument("datafile", help="The CSV File")
    parser.add_argument("-no_header", action='store_true',
                        help="The CSV file has no header column")
    parser.add_argument("-ion", action='store_true',
                        help="Interactive mode on")
    parser.add_argument("-d", action='store_true',
                        help="remove 2nd row")
    # Require at least one column name
    args = parser.parse_args()
    
    graph_csv(args.datafile, args.no_header, args.ion, args.d)
