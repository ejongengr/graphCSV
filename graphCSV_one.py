# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 15:08:12 2016

@author: Jason

- use x-axis data
- seperate curve
- multiply or offset data by factor
- show graph statistics
-

"""

import argparse
import datetime as dt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.dates as mdates
from matplotlib import widgets
from matplotlib.widgets import Cursor
#from matplotlib.dates import DateFormatter
# https://pypi.python.org/pypi/mpldatacursor#downloads
# from mpldatacursor import datacursor
from matplot_cursor import FollowDotCursor
from matplot_control import ControlSys
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
#from PyQt4 import QtCore
from PyQt5.QtCore import QObject, pyqtSignal
#from PyQt4.QtCore import QObject, pyqtSignal
import sys
import matplotlib.pyplot as plt

class CGraph():
    def __init__(self, fig, ax, df):
        print("Cursor init")
        self.fig = fig
        self.ax = ax
        
        self.df = df
        self.col_len = len(df.columns)
        self.lst_graph = [None for i in range(self.col_len)]
        self.index = range(len(df))
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
        #self.fig.canvas.set_window_title(datfile)
		
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
        self.txt_dt = ax.text(0.1, 0.9, '', transform=ax.transAxes)

        self.cursor_on(1, False)
        self.cursor_on(2, False)

        #self.plt.gcf().autofmt_xdate()
        # Print Datetime on status bar
        self.tscol = None # timestamp column name
        self.tsindx = self.index[0] # timestamp column index
        #ax.format_coord = self.make_format()

    def onpress(self, event):
        print('onprese')
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
        print('mouse move')
        if self.tscol != None:
            self.tsindx = np.searchsorted(self.index, [event.xdata])[0]
            date = self.toDate(self.index[self.tsindx])
            self.txt_dt.set_text('%s' % (date))
            
        if not event.inaxes:
            plt.draw()
            return
        if self.fig.canvas.manager.toolbar._active is not None:
        # toolbar is not trying to grab clicks (either through pan or zoom)
            plt.draw()
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
        
        plt.draw()

    def handle_close(self, event):
        print('Closed Figure!')
        sys.exit()
        
    def toDate(self, ts):
        # input : timestamp
        # output : datetime
         return dt.datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
    
    def load_graph(self, i):
        col_name = self.df.columns[i]
        try:
            p, = self.ax.plot(self.index, self.df[col_name], label=col_name, marker='.')
        except:
            print (col_name, ":Value Error changed to NaN(Not A Number) !!!")
            for k, mem in enumerate(self.df[col_name]):
                try:
                    float(mem)
                    self.df.set_value(k, col_name, np.float64(mem))
                except ValueError:
                    #pass
                    self.df.set_value(k, col_name, np.float64(np.nan))
            p, = self.ax.plot(self.index, self.df[col_name], label=col_name, marker='.')
        self.lst_graph[i] = p
        # Update legend
        self.legend.append(p)
        # Put a legend to the right of the current axis
        self.ax.legend(handles=self.legend, loc='center left', bbox_to_anchor=(1, 0.5))

    def reset_xdata(self):    
        for p in enumerate(self.lst_graph):
            if p[1] != None:
                p[1].set_xdata(self.index)
        self.update_draw()
        
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

    def select_index(self, index):
        if index == None:
            self.index = range(len(self.df))
            self.x1 = self.index
            self.x2 = self.index
        else:
            self.index = self.df[str(index)]
            self.x1 = self.index
            self.x2 = self.index
        self.ax.set_xlim(min(self.index),max(self.index))
        self.reset_xdata()
     
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

    def set_timestamp(self, ts_colname):
        # set timestamp column name
        self.tscol = ts_colname
        if ts_colname == None:
            self.txt_dt.set_text('')
            def pretty_num(x):
                return "{:,}".format(x)
            self.ax.fmt_xdata = pretty_num
        else:
            self.ax.fmt_xdata = self.toDate
                
class MyWidget(QWidget):
    
    def __init__(self, app, df, title, parent=None):
        #super(MyWidget, self).__init__(parent)
        
        super().__init__()
        self.legend = []
        self.df = df
                
        # Figure
        fig, ax = plt.subplots(1, 1)
        ax.grid()
        self.canvas = FigureCanvas(fig)
#        self.canvas.setFocusPolicy( Qt.ClickFocus )
#        self.canvas.setFocus()
        self.toolbar = NavigationToolbar(self.canvas, self)
        # Cursor
        self.cg = CGraph(fig, ax, df)
        # Another Cursor
        
        self.cursor = Cursor(ax, lw = 2)
        self.canvas.draw()
        
        # Control
        ctrl_sys = ControlSys(fig, ax)

        # window size
        '''
        screen_rect = app.desktop().screenGeometry()
        width, height = screen_rect.width(), screen_rect.height()
        x1 = 50
        y1 = 50
        self.setGeometry(x1,y1,width-x1-100,height-y1-50)
        '''
        
        self.setWindowTitle(title)

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.toolbar)
        leftLayout.addWidget(self.canvas)
        
        # Vbox
        self.topLayout = QVBoxLayout()

        # grid
        self.grid=QGridLayout()

        #combo box
        self.combo_L = QComboBox(self)
        self.combo_R = QComboBox(self)
        self.combo_I = QComboBox(self)
        for hd in df.columns.values:
            header = hd #str(unicode(hd)) #unicode(hd, 'cp949') # Korean character
            self.combo_L.addItem(header)
            self.combo_R.addItem(header)
            self.combo_I.addItem(header)
        
        # Check Box
        self.grid.addWidget(self.combo_L,0,0)
        self.cb_L = QCheckBox("L cursor", self)
        self.grid.addWidget(self.cb_L, 0, 1)

        self.grid.addWidget(self.combo_R,1,0)
        self.cb_R = QCheckBox("R cursor", self)
        self.grid.addWidget(self.cb_R, 1, 1)
      
        self.grid.addWidget(self.combo_I,2,0)
        self.cb_I = QCheckBox("Select X-axis", self)
        self.grid.addWidget(self.cb_I, 2, 1)

        # Push Button
        self.all_Visible=QPushButton('Show All', self)
        self.all_Visible.clicked.connect(self.AllVisible)
        self.all_Hide=QPushButton('Hide All', self)
        self.all_Hide.clicked.connect(self.AllHide)
        self.grid.addWidget(self.all_Visible,4,0)
        self.grid.addWidget(self.all_Hide,5,0)

        # Check Box
        self.cb_TS = QCheckBox("X-axis is TimeStamp", self)
        self.grid.addWidget(self.cb_TS, 4, 1)
        self.cb_scale = QCheckBox("Auto Fit Height", self)
        self.cb_scale.setCheckState(2)
        self.grid.addWidget(self.cb_scale, 5, 1)
        self.b_autoscale = True

        self.topLayout.addLayout(self.grid)
       
        # Scrollable Check Box
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget(self.scrollArea)
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(5,30,400,680))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.topLayout.addWidget(self.scrollArea)

        self.gridScroll = QGridLayout(self.scrollAreaWidgetContents)
        self.cb = []
        i = 0   # layout index
        for header in [column for column in df]:
            c = QCheckBox(header, self)                            
            c.stateChanged.connect(self.ToggleVisibility)
            col_number = 2 # how many columns 
            j = (i-2) // col_number + 2
            k = (i-2) % col_number
            self.gridScroll.addWidget(c, j, k)
            i += 1
            self.cb.append(c)            
        
        # Status bar
        self.StatusBar = QStatusBar(self)
        self.topLayout.addWidget(self.StatusBar)
        self.StatusBar.showMessage("Happy Day  ")

        #self.setLayout(self.topLayout)
        #self.Line,QtCore.SLOT('setText(QString)'))
        
        self.combo_L.activated.connect(lambda: self.select_cursor_data(1))
        self.combo_R.activated.connect(lambda: self.select_cursor_data(2))
        self.combo_I.activated.connect(self.select_index)
        self.cb_L.stateChanged.connect(self.cursor_on)
        self.cb_R.stateChanged.connect(self.cursor_on)
        self.cb_I.stateChanged.connect(self.index_on)
        self.cb_TS.stateChanged.connect(self.timestamp_on)
        self.cb_scale.stateChanged.connect(self.ToggelAutoScale)
    
        layout = QHBoxLayout()
        layout.addLayout(leftLayout)
        layout.addLayout(self.topLayout)
        layout.setStretchFactor(leftLayout, 3)
        layout.setStretchFactor(self.topLayout, 0)

        self.setLayout(layout)

    def index_on(self):
        if self.cb_I.isChecked():
            idx = self.combo_I.currentText()
            self.cg.select_index(idx)
        else:
            self.cg.select_index(None)
            
    def select_index(self):
        self.cb_I.setCheckState(2)
        idx = self.combo_I.currentText()
        self.cg.select_index(idx)

    def timestamp_on(self):
        if self.cb_TS.isChecked():
            idx = self.combo_I.currentText()
            self.cg.set_timestamp(idx)
        else:
            self.cg.set_timestamp(None)
                        
    def closeEvent(self, event):
        print ("Closing GUI")
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
        
def graph_csv(df, title, ion):       
    app = QApplication(sys.argv)
    w = MyWidget(app, df, title)
    w.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    if sys.version[0] == '2':
        reload(sys)
        sys.setdefaultencoding('utf-8')

    parser = argparse.ArgumentParser(description="Plot a CSV file")
    parser.add_argument("datafile", help="The CSV File")
    parser.add_argument("-ion", action='store_true',
                        help="Interactive mode on")
    parser.add_argument("args", nargs=argparse.REMAINDER,
                        help="... remaining arguments passed to pandas.read_csv(..)")
    args = parser.parse_args()			
    
    # parsing comand line parameter and pass to function
    param = dict()
    for p in args.args:
        key,val = p.split('=')
        if val.isdigit():
            val = int(val)            
        param[key] = val

    #sep=',', header=0, skiprows=[1], encoding="iso8859-1"
    df = pd.read_csv(args.datafile, encoding="iso8859-1", **param)
    if sys.version[0] == '2':
        graph_csv(df, unicode(args.datafile, 'cp949'), args.ion)
    else:
        graph_csv(df, args.datafile, args.ion)