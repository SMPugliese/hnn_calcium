import sys, os
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QToolTip, QPushButton, QFormLayout
from PyQt5.QtWidgets import QMenu, QSizePolicy, QMessageBox, QWidget, QFileDialog, QComboBox, QTabWidget
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox, QDialog, QGridLayout, QLineEdit, QLabel
from PyQt5.QtWidgets import QCheckBox, QInputDialog
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import QCoreApplication, QThread, pyqtSignal, QObject, pyqtSlot
from PyQt5 import QtCore
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import pylab as plt
import matplotlib.gridspec as gridspec
from neuron import h
from run import net
import paramrw
import pickle
from conf import dconf
from gutils import getmplDPI

if dconf['fontsize'] > 0: plt.rcParams['font.size'] = dconf['fontsize']
else: dconf['fontsize'] = 10

# colors for the different cell types
dclr = {1 : 'g',    # apical tuft
        2 : 'r',    # apical 2
        3 : 'k',    # apical 1
        4 : 'b',    # soma
        5 : 'y'}    # basal


ntrial = 1; tstop = -1; outparamf = voltpath = paramf = '';

maxCount = 4

for i in range(len(sys.argv)):
  if sys.argv[i].endswith('.param'):
    paramf = sys.argv[i]
    tstop = paramrw.quickgetprm(paramf,'tstop',float)
    ntrial = paramrw.quickgetprm(paramf,'N_trials',int)
    outparamf = os.path.join(dconf['datdir'],paramf.split('.param')[0].split(os.path.sep)[-1],'param.txt')
  elif sys.argv[i] == 'maxperty':
    maxCount = int(sys.argv[i])

if ntrial <= 1:
  voltpath = os.path.join(dconf['datdir'],paramf.split('.param')[0].split(os.path.sep)[-1],'volt.pkl')
else:
  voltpath = os.path.join(dconf['datdir'],paramf.split('.param')[0].split(os.path.sep)[-1],'volt_1.pkl')

class L5VoltCanvas (FigureCanvas):
  def __init__ (self, paramf, index, parent=None, width=12, height=10, dpi=120, title='L5 Compartmentwise Voltage Viewer'):
    FigureCanvas.__init__(self, Figure(figsize=(width, height), dpi=dpi))
    self.title = title
    self.setParent(parent)
    self.gui = parent
    self.index = index
    self.invertedax = False
    FigureCanvas.setSizePolicy(self,QSizePolicy.Expanding,QSizePolicy.Expanding)
    FigureCanvas.updateGeometry(self)
    self.paramf = paramf
    self.G = gridspec.GridSpec(10,1)
    self.plot()

# Comment in for heatmap
  def drawvolt (self, dvolt, fig, G, sz=8, ltextra=''):
    # volt_time = dvolt['vtime']
    compartments = ['Soma','Tuft']
    compartment_idxs = [4,1]

    for i in range(2):
        volt = []
        for gid in dvolt.keys():
            if gid == 'vtime': continue
            if dvolt[gid][0] == 'L5_pyramidal':
                cell_volt = dvolt[gid][compartment_idxs[i]]
                volt.append(cell_volt)

        volt = np.asarray(volt)

        if i==0:
            weighted_volt = np.multiply(volt,np.tile(np.linspace(100,1,num=np.shape(volt)[1]),(100,1)))
        volt = volt[np.flip(np.argsort(weighted_volt.sum(axis=1))),:]

        imAx = fig.add_subplot(2,3,i+1)
        lax = [imAx]
        heatmap = imAx.imshow(volt,cmap='plasma',aspect='auto',extent=[-0,170,100,0],vmin=-80,vmax=20)
        imAx.set_xlabel('Time (ms)')#,fontsize=16);
        imAx.set_ylabel('Cells')#,fontsize=16);
        imAx.set_title(compartments[i])#,fontsize=24)

    cbar = plt.colorbar(heatmap, ax=imAx)
    cbar.set_label('Voltage (mV)') #,fontsize=16)

    return lax

# Comment in for voltage trace plot
  # def drawvolt (self, dvolt, fig, G, sz=8, ltextra=''):
  #     count = 0
  #     sumSignal = np.zeros(dvolt[1][1].shape)
  #     for gid,it in dvolt.items():
  #         # count = 0
  #         ty = it[0]
  #         if type(gid) != int: continue
  #         if ty == "L5_pyramidal":
  #             count += 1
  #             if count != maxCount: continue
  #             # if count not in [2,4]: continue
  #             ax1 = fig.add_subplot(4,3,1)
  #             if tstop != -1: ax1.set_xlim((0,tstop))
  #             ax1.set_xlabel('Time (ms)');
  #             # ax1.set_ylim(-8000,-2000)
  #             # ax1.set_ylim(-100,60)
  #             ax1.set_ylim(-80,60)
  #             ax1.set_ylabel('mV')
  #             for i in range(1,6):
  #                 ax = fig.add_subplot(6,1,i+1)
  #                 lax = [ax]
  #                 vtime = dvolt['vtime']
  #                 volt = it[i]
  #                 if i == 1:
  #                     sumSignal += volt
  #                 ax.plot(vtime, volt, dclr[i], linewidth = self.gui.linewidth)
  #                 if i in [1,2,4]:
  #                     ax1.plot(vtime, volt, dclr[i], linewidth = self.gui.linewidth)
  #                 if not self.invertedax:
  #                   ax.set_ylim(ax.get_ylim()[::-1])
  #                   self.invertedax = True
  #                 # ax.set_yticks([])
  #
  #                 ax.set_facecolor('w')
  #                 if tstop != -1: ax.set_xlim((0,tstop))
  #                 if i ==0: ax.set_title(ltextra)
  #                 ax.set_xlabel('Time (ms)');
  #                 # ax.set_ylim((-100,60))
  #                 ax.set_ylim(-80,60)
  #                 ax.set_ylabel('Voltage (mV)')
  #
  #     # sumSignal /= count
  #     # ax1.plot(vtime,sumSignal)
  #
  #     green_patch = mpatches.Patch(color='green', label='Apical tuft')
  #     red_patch = mpatches.Patch(color='red', label='Apical 2')
  #     black_patch = mpatches.Patch(color='black', label='Apical 1')
  #     blue_patch = mpatches.Patch(color='blue', label='Soma')
  #     yellow_patch = mpatches.Patch(color='yellow', label='Basal')
  #     ax.legend(handles=[green_patch,red_patch,black_patch,blue_patch,yellow_patch])
  #
  #     # self.figure.subplots_adjust(bottom=0.04, left=0.025, right=0.99, top=0.99, wspace=0.1, hspace=0.25)
  #     self.figure.subplots_adjust(bottom=0.04, left=0.1, right=0.99, top=0.99, wspace=0.05, hspace=0.365)
  #
  #
  #     return lax

  def plot (self):
    if self.index == 0:
      if ntrial == 1:
        dvolt = pickle.load(open(voltpath,'rb'))
      else:
        dvolt = pickle.load(open(voltpath,'rb'))
      self.lax = self.drawvolt(dvolt,self.figure, self.G, 5, ltextra='All Trials')
    else:
      voltpathtrial = os.path.join(dconf['datdir'],paramf.split('.param')[0].split(os.path.sep)[-1],'vsoma_'+str(self.index)+'.pkl')
      dvolttrial = pickle.load(open(voltpathtrial,'rb'))
      self.lax=self.drawvolt(dvolttrial,self.figure, self.G, 5, ltextra='Trial '+str(self.index));
    self.draw()

class L5VoltGUI (QMainWindow):
  def __init__ (self):
    global dfile, ddat, paramf
    super().__init__()
    self.fontsize = dconf['fontsize']
    self.linewidth = plt.rcParams['lines.linewidth'] = 1
    self.markersize = plt.rcParams['lines.markersize'] = 5
    self.initUI()

  def changeFontSize (self):
    i, okPressed = QInputDialog.getInt(self, "Set Font Size","Font Size:", plt.rcParams['font.size'], 1, 100, 1)
    if okPressed:
      self.fontsize = plt.rcParams['font.size'] = dconf['fontsize'] = i
      self.initCanvas()
      self.m.plot()

  def changeLineWidth (self):
    i, okPressed = QInputDialog.getInt(self, "Set Line Width","Line Width:", plt.rcParams['lines.linewidth'], 1, 20, 1)
    if okPressed:
      self.linewidth = plt.rcParams['lines.linewidth'] = i
      self.initCanvas()
      self.m.plot()

  def changeMarkerSize (self):
    i, okPressed = QInputDialog.getInt(self, "Set Marker Size","Font Size:", self.markersize, 1, 100, 1)
    if okPressed:
      self.markersize = plt.rcParams['lines.markersize'] = i
      self.initCanvas()
      self.m.plot()

  def initMenu (self):
    exitAction = QAction(QIcon.fromTheme('exit'), 'Exit', self)
    exitAction.setShortcut('Ctrl+Q')
    exitAction.setStatusTip('Exit HNN Volt Viewer.')
    exitAction.triggered.connect(qApp.quit)

    menubar = self.menuBar()
    fileMenu = menubar.addMenu('&File')
    menubar.setNativeMenuBar(False)
    fileMenu.addAction(exitAction)

    viewMenu = menubar.addMenu('&View')
    changeFontSizeAction = QAction('Change Font Size',self)
    changeFontSizeAction.setStatusTip('Change Font Size.')
    changeFontSizeAction.triggered.connect(self.changeFontSize)
    viewMenu.addAction(changeFontSizeAction)
    changeLineWidthAction = QAction('Change Line Width',self)
    changeLineWidthAction.setStatusTip('Change Line Width.')
    changeLineWidthAction.triggered.connect(self.changeLineWidth)
    viewMenu.addAction(changeLineWidthAction)
    changeMarkerSizeAction = QAction('Change Marker Size',self)
    changeMarkerSizeAction.setStatusTip('Change Marker Size.')
    changeMarkerSizeAction.triggered.connect(self.changeMarkerSize)
    viewMenu.addAction(changeMarkerSizeAction)


  def initCanvas (self):
    self.invertedax = False
    try: # to avoid memory leaks remove any pre-existing widgets before adding new ones
      self.grid.removeWidget(self.m)
      self.grid.removeWidget(self.toolbar)
      self.m.setParent(None)
      self.toolbar.setParent(None)
      self.m = self.toolbar = None
    except:
      pass
    self.m = L5VoltCanvas(paramf, self.index, parent = self, width=12, height=10, dpi=getmplDPI())
    # this is the Navigation widget
    # it takes the Canvas widget and a parent
    self.toolbar = NavigationToolbar(self.m, self)
    self.grid.addWidget(self.toolbar, 0, 0, 1, 4);
    self.grid.addWidget(self.m, 1, 0, 1, 4);

  def initUI (self):
    self.initMenu()
    self.statusBar()
    self.setGeometry(300, 300, 1300, 1100)
    self.setWindowTitle('Volt Viewer - ' + paramf)
    self.grid = grid = QGridLayout()
    self.index = 0
    self.initCanvas()
    self.cb = QComboBox(self)
    self.grid.addWidget(self.cb,2,0,1,4)

    for i in range(ntrial): self.cb.addItem('Trial ' + str(i+1))
    self.cb.activated[int].connect(self.onActivated)

    # need a separate widget to put grid on
    widget = QWidget(self)
    widget.setLayout(grid)
    self.setCentralWidget(widget);

    try: self.setWindowIcon(QIcon(os.path.join('res','icon.png')))
    except: pass

    self.show()

  def onActivated(self, idx):
    if idx != self.index:
      self.index = idx
      self.statusBar().showMessage('Loading data from trial ' + str(self.index+1) + '.')
      self.m.index = self.index
      self.initCanvas()
      self.m.plot()
      self.statusBar().showMessage('')

if __name__ == '__main__':

  app = QApplication(sys.argv)
  ex = L5VoltGUI()
  sys.exit(app.exec_())
