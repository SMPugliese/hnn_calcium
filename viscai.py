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

# # colors for the different compartments
# dclr = {1 : 'g',    # apical tuft
#         2 : 'r',    # apical 2
#         3 : 'k',    # apical 1
#         4 : 'b',    # soma
#         5 : 'y'}    # basal

ntrial = 1; tstop = -1; outparamf = caipath = paramf = '';

maxCount = 10 # how many cells to draw

for i in range(len(sys.argv)):
  if sys.argv[i].endswith('.param'):
    paramf = sys.argv[i]
    tstop = paramrw.quickgetprm(paramf,'tstop',float)
    ntrial = paramrw.quickgetprm(paramf,'N_trials',int)
    outparamf = os.path.join(dconf['datdir'],paramf.split('.param')[0].split(os.path.sep)[-1],'param.txt')
  elif sys.argv[i] == 'maxperty':
    maxCount = int(sys.argv[i])

if ntrial <= 1:
  caipath = os.path.join(dconf['datdir'],paramf.split('.param')[0].split(os.path.sep)[-1],'cai.pkl')
else:
  caipath = os.path.join(dconf['datdir'],paramf.split('.param')[0].split(os.path.sep)[-1],'cai_1.pkl')

class CaiCanvas (FigureCanvas):
  def __init__ (self, paramf, index, parent=None, width=12, height=10, dpi=120, title='Calcium Concentration Viewer'):
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

  def drawcai (self, dcai, fig, G, sz=8, ltextra=''):
      # # with open(caipath, 'rb') as caiFile:
      #     caiData = pickle.load(caiFile)
      #     caiFile.close()
      cai_time = dcai['cai_time']
      ap2_cai = []
      for gid in dcai.keys():
          if gid == 'cai_time': continue
          cell_cai = dcai[gid][1]
          ap2_cai.append(cell_cai)

      ap2_cai = np.asarray(ap2_cai)
      weighted_cai = np.multiply(ap2_cai,np.tile(np.linspace(100,1,num=np.shape(ap2_cai)[1]),(100,1)))
      ap2_cai = ap2_cai[np.flip(np.argsort(weighted_cai.sum(axis=1))),:]

      imAx = fig.add_subplot(2,2,1)
      lax = [imAx]
      heatmap = imAx.imshow(ap2_cai,cmap='plasma',aspect='auto',extent=[0,tstop,100,0],vmin=0,vmax=0.3)
      cbar = plt.colorbar(heatmap, ax=imAx)
      cbar.set_label('Ca concenration (mM)')
      imAx.set_xlabel('Time (ms)')
      imAx.set_ylabel('Cells')

      # ax.plot(cai_time,dcai[267][1],'k')
      # print(dcai[172])
      # plt.plot(dcai['cai_time'],dcai[172])
      # im = ax.imshow(dcai[2])


    # count = 0
    # for gid,it in dcai.items():
    #     ty = it[0]
    #     if type(gid) != int: continue
    #     if ty == "L5_pyramidal":
    #         count += 1
    #         if count > maxCount: continue
    #         # if count < 80: continue
    #         for i in range(1,6):
    #             ax = fig.add_subplot(5,1,i)
    #             lax = [ax]
    #             cai_time = dcai['cai_time']
    #             cai = it[i]
    #             ax.plot(cai_time, cai, dclr[i], linewidth = self.gui.linewidth)
    #             # ax.ylim(0,0.2)
    #             # ax.ylabel("Ca Concentration")
    #             # ax.xlabel("Time (ms)")
    #             if not self.invertedax:
    #               ax.set_ylim(ax.get_ylim()[::-1])
    #               self.invertedax = True
    #             ax.set_yticks([])
    #
    #             ax.set_facecolor('w')
    #             # ax.grid(True)
    #             if tstop != -1: ax.set_xlim((0,tstop))
    #             if i ==0: ax.set_title(ltextra)
    #             ax.set_xlabel('Time (ms)');
    #             ax.set_ylim((0,0.5))
    #             ax.set_ylabel('Ca concentration')
    #
    # green_patch = mpatches.Patch(color='green', label='Apical tuft')
    # red_patch = mpatches.Patch(color='red', label='Apical 2')
    # black_patch = mpatches.Patch(color='black', label='Apical 1')
    # blue_patch = mpatches.Patch(color='blue', label='Soma')
    # yellow_patch = mpatches.Patch(color='yellow', label='Basal')
    # ax.legend(handles=[green_patch,red_patch,black_patch,blue_patch,yellow_patch])

    # self.figure.subplots_adjust(bottom=0.04, left=0.025, right=0.99, top=0.99, wspace=0.1, hspace=0.25)
      return lax

  def plot (self):
    if self.index == 0:
      if ntrial == 1:
        dcai = pickle.load(open(caipath,'rb'))
      else:
        dcai = pickle.load(open(caipath,'rb'))
      self.lax = self.drawcai(dcai,self.figure, self.G, 5, ltextra='All Trials')
    else:
      caipathtrial = os.path.join(dconf['datdir'],paramf.split('.param')[0].split(os.path.sep)[-1],'cai_'+str(self.index)+'.pkl')
      dcaitrial = pickle.load(open(caipathtrial,'rb'))
      self.lax=self.drawcai(dcaitrial,self.figure, self.G, 5, ltextra='Trial '+str(self.index));
    self.draw()

class CaiGUI (QMainWindow):
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
    exitAction.setStatusTip('Exit HNN Calcium Viewer.')
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
    self.m = CaiCanvas(paramf, self.index, parent = self, width=12, height=10, dpi=getmplDPI())
    # this is the Navigation widget
    # it takes the Canvas widget and a parent
    self.toolbar = NavigationToolbar(self.m, self)
    self.grid.addWidget(self.toolbar, 0, 0, 1, 4);
    self.grid.addWidget(self.m, 1, 0, 1, 4);

  def initUI (self):
    self.initMenu()
    self.statusBar()
    self.setGeometry(300, 300, 1300, 1100)
    self.setWindowTitle('Calcium Concentration Viewer - ' + paramf)
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
  ex = CaiGUI()
  sys.exit(app.exec_())
