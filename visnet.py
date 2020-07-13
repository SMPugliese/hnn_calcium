import sys, os
import pyqtgraph as pg        
from pyqtgraph.Qt import QtCore, QtGui
#from pyqtgraph.graphicsItems.AxisItem import *
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np

from morphology import shapeplot, getshapecoords
from mpl_toolkits.mplot3d import Axes3D
import pylab as plt
from neuron import h
from L5_pyramidal import L5Pyr
from L2_pyramidal import L2Pyr
from L2_basket import L2Basket
from L5_basket import L5Basket
from run import net

drawallcells = True # False 
cell = net.cells[-1]

# colors for the different cell types
dclr = {'L2_pyramidal' : 'g', L2Pyr: (0.,1.,0.,0.6),
        'L5_pyramidal' : 'r', L5Pyr: (1.,0.,0.,0.6),
        'L2_basket' : 'k', L2Basket: (1.,1.,1.,0.6),
        'L5_basket' : 'b', L5Basket: (0.,0.,1.,0.6)}

def getcellpos (net,ty):
  lx,ly = [],[]
  for cell in net.cells:
    if type(cell) == ty:
      lx.append(cell.pos[0])
      ly.append(cell.pos[1])
  return lx,ly

def cellsecbytype (ty):
  lss = []
  for cell in net.cells:
    if type(cell) == ty:
      ls = cell.get_sections()
      for s in ls: lss.append(s)
  return lss

def getdrawsec (ncells=1,ct=L2Pyr):
  global cell
  if drawallcells: return list(h.allsec())
  ls = []
  nfound = 0
  for c in net.cells:
    if type(c) == ct: 
      cell = c
      lss = c.get_sections()
      for s in lss: ls.append(s)
      nfound += 1
      if nfound >= ncells: break
  return ls

dsec = {}
for ty in [L2Pyr, L5Pyr, L2Basket, L5Basket]: dsec[ty] = cellsecbytype(ty)
dlw = {L2Pyr:1, L5Pyr:1,L2Basket:4,L5Basket:4}
whichdraw = [L2Pyr, L2Basket, L5Pyr, L5Basket]

lsecnames = cell.get_section_names()

def get3dinfo (sidx,eidx):
  llx,lly,llz,lldiam = [],[],[],[]
  for i in range(sidx,eidx,1):
    lx,ly,lz,ldiam = net.cells[i].get3dinfo()
    llx.append(lx); lly.append(ly); llz.append(lz); lldiam.append(ldiam)
  return llx,lly,llz,lldiam

llx,lly,llz,lldiam = get3dinfo(0,len(net.cells))

def countseg (ls): return sum([s.nseg for s in ls])

defclr = 'k'; selclr = 'r'
useGL = True
fig = None

def drawcellspylab3d ():
  global shapeax,fig
  plt.ion(); fig = plt.figure()
  shapeax = plt.subplot(111, projection='3d')
  #shapeax.set_xlabel('X',fontsize=24); shapeax.set_ylabel('Y',fontsize=24); shapeax.set_zlabel('Z',fontsize=24)
  shapeax.set_xticks([]); shapeax.set_yticks([]); shapeax.set_zticks([])
  shapeax.view_init(elev=105,azim=-71)
  shapeax.grid(False)
  lshapelines = []
  for ty in whichdraw:
    ls = dsec[ty]
    lshapelines.append(shapeplot(h,shapeax,sections=ls,cvals=[dclr[ty] for i in range(countseg(ls))],lw=dlw[ty]))
  return lshapelines

if not useGL: drawcellspylab3d()

def onclick(event):
  try:
    print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          (event.button, event.x, event.y, event.xdata, event.ydata))
  except:
    pass

def setcolor (ls,clr):
  for l in ls: l.set_color(clr)

# click on section event handler - not used for network 
def onpick (event):
  print('onpick')
  thisline = event.artist
  c = thisline.get_color()
  idx = -1
  setcolor(shapelines,defclr)    
  for idx,l in enumerate(shapelines):
    if l == thisline:
      break
  try:
    print('idx is ', idx, 'selected',lsecnames[idx])
    xdata = thisline.get_xdata()
    ydata = thisline.get_ydata()
    ind = event.ind
    points = tuple(zip(xdata[ind], ydata[ind]))
    print('onpick points:', points)
    if c == defclr:
      thisline.set_color(selclr)
    else:
      thisline.set_color(defclr)
    print(ind)
    #print(dir(thisline))
  except:
    pass

def setcallbacks ():
  if useGL: return []
  lcid = []
  if False: lcid.append(fig.canvas.mpl_connect('button_press_event', onclick))
  if not drawallcells: lcid.append(fig.canvas.mpl_connect('pick_event', onpick))
  return lcid

lcid = setcallbacks()

#
def drawinputs2d (cell,clr,ax):
  for lsrc in [cell.ncfrom_L2Pyr, cell.ncfrom_L2Basket, cell.ncfrom_L5Pyr, cell.ncfrom_L5Basket]:
    for src in lsrc:
      precell = src.precell()
      ax.plot([precell.pos[0],cell.pos[0]],[precell.pos[1],cell.pos[1]],clr)

#
def drawconn2d ():
  plt.figure()
  ax = plt.gca()
  """
  loc = np.array(net.pos_dict['L2_basket'])
  plot(loc[:,0],loc[:,1],'ko',markersize=14)
  loc = np.array(net.pos_dict['L2_pyramidal'])
  plot(loc[:,0],loc[:,1],'ro',markersize=14)
  loc = np.array(net.pos_dict['L2_basket'])
  plot(loc[:,0],loc[:,1],'bo',markersize=10)
  """
  lx = [cell.pos[0] for cell in net.cells]
  ly = [cell.pos[1] for cell in net.cells]
  ax.plot(lx,ly,'ko',markersize=14)
  """
  self.ncfrom_L2Pyr = []
  self.ncfrom_L2Basket = []
  self.ncfrom_L5Pyr = []
  self.ncfrom_L5Basket = []
  """
  for cell in net.cells:
    drawinputs2d(cell,'r',ax)
    break

#
def drawinputs3d (cell,clr,widg,width=2.0):
  for lsrc in [cell.ncfrom_L2Pyr, cell.ncfrom_L2Basket, cell.ncfrom_L5Pyr, cell.ncfrom_L5Basket]:
    for src in lsrc:
      precell = src.precell()
      pts = np.vstack([[precell.pos[0]*100,cell.pos[0]*100],[precell.pos[2],cell.pos[2]],[precell.pos[1]*100,cell.pos[1]*100]]).transpose()
      plt = gl.GLLinePlotItem(pos=pts, color=clr, width=width, antialias=True, mode='lines')
      widg.addItem(plt)

#
def drawconn3d (widg,width=2.0,clr=(1.0,0.0,0.0,0.5)):
  i = 0
  for cell in net.cells:
    drawinputs3d(cell,clr,widg,width)
    i += 1
    #if i > 20: break

def drawcells3dgl (ty,widget,width=2.2):
  for cell in net.cells:
    if type(cell) != ty: continue
    lx,ly,lz = getshapecoords(h,cell.get_sections())  
    pts = np.vstack([lx,ly,lz]).transpose()
    plt = gl.GLLinePlotItem(pos=pts, color=dclr[type(cell)], width=width, antialias=True, mode='lines')
    #plt.showGrid(x=True,y=True)
    widget.addItem(plt)
  #axis = pg.AxisItem(orientation='bottom')
  #print(dir(axis))
  #print(dir(widget))
  #print(widget.getViewport())
  #axis.linkToView(axis.getViewBox())#widget.getViewport())
  #widget.addItem(pg.AxisItem(orientation='bottom'))

def drawallcells3dgl (wcells):
  drawcells3dgl(L5Pyr,wcells,width=15.0)
  drawcells3dgl(L2Pyr,wcells,width=15.0)
  drawcells3dgl(L5Basket,wcells,width=40.0)
  drawcells3dgl(L2Basket,wcells,width=40.0)
  wcells.opts['distance'] = 4320.9087386478195
  wcells.opts['elevation']=105
  wcells.opts['azimuth']=-71
  wcells.opts['fov'] = 90
  wcells.setWindowTitle('Network Visualization')

if __name__ == '__main__':
  app = QtGui.QApplication([])
  widg = gl.GLViewWidget()
  for s in sys.argv:
    if s == 'cells':
      drawallcells3dgl(widg)
    if s == 'Econn':
      drawconn3d(widg,clr=(1.0,0.0,0.0,0.25))
    if s == 'Iconn':
      drawconn3d(widg,clr=(0.0,0.0,1.0,0.25))
  #app.axis = axis = pg.AxisItem(orientation='bottom')
  #app.pqg_plot_item.showAxis('bottom',True)
  widg.show()
  if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    QtGui.QApplication.instance().exec_()

