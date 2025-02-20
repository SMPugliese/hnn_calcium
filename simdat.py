import os
from PyQt5.QtWidgets import QMenu, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np
from math import ceil
from conf import dconf
import conf
import spikefn
from paramrw import usingOngoingInputs, usingEvokedInputs, usingPoissonInputs, usingTonicInputs, find_param, quickgetprm, countEvokedInputs
from scipy import signal
from gutils import getscreengeom

if dconf['fontsize'] > 0: plt.rcParams['font.size'] = dconf['fontsize']
else: plt.rcParams['font.size'] = dconf['fontsize'] = 10

debug = dconf['debug']

ddat = {} # current simulation data
dfile = {} # data file information for current simulation

lsimdat = [] # list of simulation data
lsimidx = 0 # index into lsimdat

def updatelsimdat(paramf,dpl):
  # update lsimdat with paramf and dipole dpl
  # but if the specific sim already run put dipole at that location in list
  global lsimdat,lsimidx
  # while len(lsimdat)>0 and lsimidx!=len(lsimdat)-1: lsimdat.pop() # redos popped
  found = False
  for i,l in enumerate(lsimdat):
    if l[0] == paramf:
      lsimdat[i][1] = dpl
      found = True
      break
  if not found: lsimdat.append([paramf,dpl]) # if not found, append to end of the list
  lsimidx = len(lsimdat) - 1 # current simulation index

def rmse (a1, a2):
  # return root mean squared error between a1, a2; assumes same lengths, sampling rates
  len1,len2 = len(a1),len(a2)
  sz = min(len1,len2)
  if debug: print('len1:',len1,'len2:',len2,'ty1:',type(a1),'ty2:',type(a2))
  return np.sqrt(((a1[0:sz] - a2[0:sz]) ** 2).mean())

def readdpltrials (basedir,ntrial):
  # read dipole data files for individual trials
  if debug: print('in readdpltrials',basedir,ntrial)
  ldpl = []
  for i in range(ntrial):
    fn = os.path.join(basedir,'dpl_'+str(i)+'.txt')
    if not os.path.exists(fn): break
    ldpl.append(np.loadtxt(fn))
    if debug: print('loaded ', fn)
  return ldpl

def getinputfiles (paramf):
  # get a dictionary of input files based on simulation parameter file paramf
  global dfile,basedir
  dfile = {}
  basedir = os.path.join(dconf['datdir'],paramf.split(os.path.sep)[-1].split('.param')[0])
  # print('basedir:',basedir)
  dfile['dpl'] = os.path.join(basedir,'dpl.txt')
  dfile['spec'] = os.path.join(basedir,'rawspec.npz')
  dfile['spk'] = os.path.join(basedir,'spk.txt')
  dfile['outparam'] = os.path.join(basedir,'param.txt')
  return dfile

def updatedat (paramf):
  # update data dictionary (ddat) from the param file
  if debug: print('paramf:',paramf)
  try:
    getinputfiles(paramf)
    for k in ['dpl','spk']:
      if not os.path.isfile(dfile[k]): return False
    ddat['dpl'] = np.loadtxt(dfile['dpl']);
    if os.path.isfile(dfile['spec']): ddat['spec'] = np.load(dfile['spec'])
    else: ddat['spec'] = None
    # if os.stat('spk.txt').st_size != 0: ddat['spk'] = np.loadtxt(dfile['spk'])
    # else: ddat['spk'] = []
    ddat['spk'] = np.loadtxt(dfile['spk'])
    ddat['dpltrials'] = readdpltrials(basedir,quickgetprm(paramf,'N_trials',int))
    return True
  except:
    print('updatedat ERR: exception in getting input files. paramf:',paramf)
    return False

def getscalefctr (paramf):
  # get dipole scaling factor parameter value from paramf file
  try:
    xx = quickgetprm(paramf,'dipole_scalefctr',float)
    if type(xx) == float: return xx
  except:
    pass
  if 'dipole_scalefctr' in dconf:
    return dconf['dipole_scalefctr']
  return 30e3

def drawraster ():
  # draw raster to standalone matplotlib figure - for debugging (not used in main HNN GUI)
  if 'spk' in ddat:
    # print('spk shape:',ddat['spk'].shape)
    plt.ion()
    plt.figure()
    for pair in ddat['spk']:
      plt.plot([pair[0]],[pair[1]],'ko',markersize=10)
    plt.xlabel('Time (ms)',fontsize=dconf['fontsize']); plt.ylabel('ID',fontsize=dconf['fontsize'])

def calcerr (ddat):
  # calculates RMSE error from ddat dictionary
  try:
    NSig = errtot = 0.0; lerr = []
    ddat['errtot']=None; ddat['lerr']=None
    for fn,dat in ddat['dextdata'].items():
      shp = dat.shape
      # first downsample simulation timeseries to 600 Hz (assumes same time length as data)
      dpldown = signal.resample(ddat['dpl'][:,1], len(dat[:,1]))
      for c in range(1,shp[1],1):
        err0 = rmse(dat[:,c], dpldown)
        lerr.append(err0)
        errtot += err0
        print('RMSE: ',err0)
        NSig += 1
    errtot /= NSig
    print('Avg. RMSE:' + str(round(errtot,2)))
    ddat['errtot'] = errtot
    ddat['lerr'] = lerr
    return lerr, errtot
  except:
    #print('exception in calcerr')
    return [],-1.0

class SIMCanvas (FigureCanvas):
  # matplotlib/pyqt-compatible canvas for drawing simulation & external data
  # based on https://pythonspot.com/en/pyqt5-matplotlib/

  def __init__ (self, paramf, parent=None, width=5, height=4, dpi=40, title='Simulation Viewer'):
    FigureCanvas.__init__(self, Figure(figsize=(width, height), dpi=dpi))
    self.title = title
    self.lextdatobj = [] # external data object
    self.clridx = 5 # index for next color for drawing external data
    self.lpatch = [mpatches.Patch(color='black', label='Sim.')] # legend for dipole signals
    self.setParent(parent)
    self.gui = parent
    FigureCanvas.setSizePolicy(self,QSizePolicy.Expanding,QSizePolicy.Expanding)
    FigureCanvas.updateGeometry(self)
    self.paramf = paramf
    self.invertedhistax = False
    self.initaxes()
    self.G = gridspec.GridSpec(10,1)
    self.plot()

  def initaxes (self):
    # initialize the axes; lax is list of axes
    self.axdist = self.axprox = self.axdipole = self.axspec = self.axpois = None
    self.lax = []

  def plotinputhist (self, xl, dinty):
    """ plot input histograms
        xl = x axis limits
        dinty = dict of input types used, determines how many/which axes created/displayed
    """
    xlim_new = (ddat['dpl'][0,0],ddat['dpl'][-1,0])
    # print('xlim_new:',xlim_new)
    # set number of bins (150 bins per 1000ms)
    bins = ceil(150. * (xlim_new[1] - xlim_new[0]) / 1000.) # bins needs to be an int
    if debug: print('bins:',bins)
    extinputs = None

    try:
      if debug: print('dfilespk:',dfile['spk'],'dfileoutparam',dfile['outparam'])
      extinputs = spikefn.ExtInputs(dfile['spk'], dfile['outparam'])
      extinputs.add_delay_times()
      dinput = extinputs.inputs
      if len(dinput['dist']) <= 0 and len(dinput['prox']) <= 0 and \
         len(dinput['evdist']) <= 0 and len(dinput['evprox']) <= 0 and \
         len(dinput['pois']) <= 0:
        if debug: print('all hists 0!')
        return False
    except:
      print('plotinputhist ERR: problem with extinputs')
    self.hist=hist={x:None for x in ['feed_dist','feed_prox','feed_evdist','feed_evprox','feed_pois']}

    hasPois = len(dinput['pois']) > 0 and dinty['Poisson'] # this ensures synaptic weight > 0

    gRow = 0
    axdist = axprox = axpois = None # axis objects

    # check poisson inputs, create subplot
    if hasPois:
      self.axpois = axpois = self.figure.add_subplot(self.G[gRow,0])
      self.lax.append(axpois)
      gRow += 1

    # check distal inputs, create subplot
    if (len(dinput['dist']) > 0 and dinty['OngoingDist']) or \
       (len(dinput['evdist']) > 0 and dinty['EvokedDist']):
      self.axdist = axdist = self.figure.add_subplot(self.G[gRow,0]);
      gRow+=1
      self.lax.append(axdist)

    # check proximal inputs, create subplot
    if (len(dinput['prox']) > 0 and dinty['OngoingProx']) or \
       (len(dinput['evprox']) > 0 and dinty['EvokedProx']):
      self.axprox = axprox = self.figure.add_subplot(self.G[gRow,0]);
      gRow+=1
      self.lax.append(axprox)

    # check input types provided in simulation
    if extinputs is not None: # only valid param.txt file after sim was run
      if debug:
        print(len(dinput['dist']),len(dinput['prox']),len(dinput['evdist']),len(dinput['evprox']),len(dinput['pois']))

      if hasPois: # any Poisson inputs?
        hist['feed_pois'] = extinputs.plot_hist(axpois,'pois',ddat['dpl'][:,0],bins,xlim_new,color='k',hty='step',lw=self.gui.linewidth+1)

      if len(dinput['dist']) > 0 and dinty['OngoingDist']: # dinty condition ensures synaptic weight > 0
        hist['feed_dist'] = extinputs.plot_hist(axdist,'dist',ddat['dpl'][:,0],bins,xlim_new,color='g',lw=self.gui.linewidth+1)

      if len(dinput['prox']) > 0 and dinty['OngoingProx']: # dinty condition ensures synaptic weight > 0
        hist['feed_prox'] = extinputs.plot_hist(axprox,'prox',ddat['dpl'][:,0],bins,xlim_new,color='r',lw=self.gui.linewidth+1)

      if len(dinput['evdist']) > 0 and dinty['EvokedDist']: # dinty condition ensures synaptic weight > 0
        hist['feed_evdist'] = extinputs.plot_hist(axdist,'evdist',ddat['dpl'][:,0],bins,xlim_new,color='g',hty='step',lw=self.gui.linewidth+1)

      if len(dinput['evprox']) > 0 and dinty['EvokedProx']: # dinty condition ensures synaptic weight > 0
        hist['feed_evprox'] = extinputs.plot_hist(axprox,'evprox',ddat['dpl'][:,0],bins,xlim_new,color='r',hty='step',lw=self.gui.linewidth+1)

      if hist['feed_dist'] is None and hist['feed_prox'] is None and \
         hist['feed_evdist'] is None and hist['feed_evprox'] is None and \
         hist['feed_pois'] is None:
        self.invertedhistax = False
        if debug: print('all hists None!')
        return False
      else:
        if not self.invertedhistax and axdist:# only need to invert axis 1X
          axdist.invert_yaxis()
          self.invertedhistax = True
        for ax in [axpois,axdist,axprox]:
          if ax:
            ax.set_xlim(xlim_new)
            ax.legend()
        return True,gRow

  def clearaxes (self):
    # clear the figures axes
    try:
      for ax in self.lax:
        if ax:
          ax.cla()
      self.lax = []
    except:
      pass

  def getNTrials (self):
    # get the number of trials
    N_trials = 1
    try:
      xx = quickgetprm(self.paramf,'N_trials',int)
      if type(xx) == int: N_trials = xx
    except:
      pass
    return N_trials

  def getNPyr (self):
    # get the number of pyramidal neurons used in the simulation
    try:
      x = quickgetprm(self.paramf,'N_pyr_x',int)
      y = quickgetprm(self.paramf,'N_pyr_y',int)
      if type(x)==int and type(y)==int:
        return int(x * y * 2)
    except:
      return 0

  def getEVInputTimes (self):
    # get the evoked input times
    nprox, ndist = countEvokedInputs(self.paramf)
    ltprox, ltdist = [], []
    try:
      for i in range(nprox): ltprox.append(quickgetprm(self.paramf,'t_evprox_' + str(i+1), float))
      for i in range(ndist): ltdist.append(quickgetprm(self.paramf,'t_evdist_' + str(i+1), float))
    except:
      print('except in getEVInputTimes')
    return ltprox, ltdist

  def drawEVInputTimes (self, ax, yl, h=0.1, w=15):
    # draw the evoked input times using arrows
    ltprox, ltdist = self.getEVInputTimes()
    yrange = abs(yl[1] - yl[0])
    #print('drawEVInputTimes:',yl,yrange,h,w,h*yrange,-h*yrange,yl[0]+h*yrange,yl[1]-h*yrange)
    for tt in ltprox: ax.arrow(tt,yl[0],0,h*yrange,fc='r',ec='r', head_width=w,head_length=w)#head_length=w,head_width=1.)#w/4)#length_includes_head=True,
    for tt in ltdist: ax.arrow(tt,yl[1],0,-h*yrange,fc='g',ec='g',head_width=w,head_length=w)#head_length=w,head_width=1.)#w/4)

  def getInputs (self):
    """ get a dictionary of input types used in simulation
        with distal/proximal specificity for evoked,ongoing inputs
    """
    dinty = {'Evoked':False,'Ongoing':False,'Poisson':False,'Tonic':False,'EvokedDist':False,\
             'EvokedProx':False,'OngoingDist':False,'OngoingProx':False}
    try:
      dinty['Evoked'] = usingEvokedInputs(dfile['outparam'])
      dinty['EvokedDist'] = usingEvokedInputs(dfile['outparam'], lsuffty = ['_evdist_'])
      dinty['EvokedProx'] = usingEvokedInputs(dfile['outparam'], lsuffty = ['_evprox_'])
      dinty['Ongoing'] = usingOngoingInputs(dfile['outparam'])
      dinty['OngoingDist'] = usingOngoingInputs(dfile['outparam'], lty = ['_dist'])
      dinty['OngoingProx'] = usingOngoingInputs(dfile['outparam'], lty = ['_prox'])
      dinty['Poisson'] = usingPoissonInputs(dfile['outparam'])
      dinty['Tonic'] = usingTonicInputs(dfile['outparam'])
    except:
      pass
    return dinty

  def setupaxdipole (self):
    # setup the figure axis for drawing the dipole signal
    dinty = self.getInputs()

    # whether to draw the specgram - should draw if user saved it or have ongoing, poisson, or tonic inputs
    DrawSpec = False
    try:
      DrawSpec = find_param(dfile['outparam'],'save_spec_data') or OngoingInputs or PoissonInputs or TonicInputs
    except:
      pass

    gRow = 0

    if dinty['Ongoing'] or dinty['Evoked']: gRow = 2

    if DrawSpec: # dipole axis takes fewer rows if also drawing specgram
      self.axdipole = ax = self.figure.add_subplot(self.G[gRow:5,0]); # dipole
    else:
      self.axdipole = ax = self.figure.add_subplot(self.G[gRow:-1,0]); # dipole

  def getnextcolor (self):
    # get next color for external data (colors selected in order)
    self.clridx += 5
    if self.clridx > 100: self.clridx = 5
    return self.clridx

  def plotextdat (self, recalcErr=True):
    # plot 'external' data (e.g. from experiment/other simulation)
    try:
      #self.plotsimdat()
      if recalcErr: calcerr(ddat) # recalculate/save the error?
      lerr, errtot = ddat['lerr'], ddat['errtot']

      hassimdata = self.hassimdata() # has the simulation been run yet?

      if not hasattr(self,'axdipole'): self.setupaxdipole() # do we need an axis for drawing?
      elif self.axdipole is None: self.setupaxdipole()

      ax = self.axdipole
      yl = ax.get_ylim()

      cmap=plt.get_cmap('nipy_spectral')
      csm = plt.cm.ScalarMappable(cmap=cmap);
      csm.set_clim((0,100))

      self.clearlextdatobj() # clear annotation objects

      ddx = 0
      for fn,dat in ddat['dextdata'].items():
        shp = dat.shape
        clr = csm.to_rgba(self.getnextcolor())
        c = min(shp[1],1)
        self.lextdatobj.append(ax.plot(dat[:,0],dat[:,c],color=clr,linewidth=self.gui.linewidth+1))
        yl = ((min(yl[0],min(dat[:,c]))),(max(yl[1],max(dat[:,c]))))
        fx = int(shp[0] * float(c) / shp[1])
        if lerr:
          tx,ty=dat[fx,0],dat[fx,c]
          txt='RMSE:' + str(round(lerr[ddx],2))
          self.lextdatobj.append(ax.annotate(txt,xy=(dat[0,0],dat[0,c]),xytext=(tx,ty),color=clr,fontweight='bold'))
        self.lpatch.append(mpatches.Patch(color=clr, label=fn.split(os.path.sep)[-1].split('.txt')[0]))
        ddx+=1

      ax.set_ylim(yl)

      if self.lextdatobj and self.lpatch:
        self.lextdatobj.append(ax.legend(handles=self.lpatch))

      if errtot:
        tx,ty=0,0
        txt='Avg. RMSE:' + str(round(errtot,2))
        self.annot_avg = ax.annotate(txt,xy=(0,0),xytext=(0.005,0.005),textcoords='axes fraction',fontweight='bold')

      if not hassimdata: # need axis labels
        left = 0.08
        w,h=getscreengeom()
        if w < 2800: left = 0.1
        ax.set_xlabel('Time (ms)',fontsize=dconf['fontsize'])
        ax.set_ylabel('Dipole (nAm)',fontsize=dconf['fontsize'])
        myxl = ax.get_xlim()
        if myxl[0] < 0.0: ax.set_xlim((0.0,myxl[1]+myxl[0]))
        self.figure.subplots_adjust(left=left,right=0.99,bottom=0.0,top=0.99,hspace=0.1,wspace=0.1) # reduce padding

    except:
      print('simdat ERR: could not plotextdat')
      return False
    return True

  def hassimdata (self):
    # check if any simulation data available in ddat dictionary
    return 'dpl' in ddat

  def clearlextdatobj (self):
    # clear list of external data objects
    try:
      for o in self.lextdatobj:
        try:
          o.set_visible(False)
        except:
          o[0].set_visible(False)
      del self.lextdatobj
      self.lextdatobj = [] # reset list of external data objects
      self.lpatch = [] # reset legend
      self.clridx = 5 # reset index for next color for drawing external data
      if self.hassimdata(): self.lpatch.append(mpatches.Patch(color='black', label='Simulation'))
      if hasattr(self,'annot_avg'):
        self.annot_avg.set_visible(False)
        del self.annot_avg
    except:
      if debug: print('ERR: exception in clearlextdatobj')

  def plotsimdat (self):
    # plot the simulation data

    if not updatedat(self.paramf): return # if no data from sim, or data load problem return

    self.clearaxes()
    plt.close(self.figure);
    if len(ddat.keys()) == 0: return

    dinty = self.getInputs() # get dict of input types used (influences which/how plots drawn)

    # whether to draw the specgram - should draw if user saved it or have ongoing, poisson, or tonic inputs
    DrawSpec = find_param(dfile['outparam'],'save_spec_data') or dinty['Ongoing'] or dinty['Poisson'] or dinty['Tonic']
    try:
      ds = None
      xl = (0,find_param(dfile['outparam'],'tstop'))
      dt = find_param(dfile['outparam'],'dt')

      # get spectrogram if it exists, then adjust axis limits but only if drawing spectrogram
      if DrawSpec and 'spec' in ddat:
        if ddat['spec'] is not None:
          ds = ddat['spec'] # spectrogram
          xl = (ds['time'][0],ds['time'][-1]) # use specgram time limits

      gRow = 0

      sampr = 1e3/dt # dipole sampling rate
      sidx, eidx = int(sampr*xl[0]/1e3), int(sampr*xl[1]/1e3) # use these indices to find dipole min,max

      if dinty['Ongoing'] or dinty['Evoked'] or dinty['Poisson']:
        xo = self.plotinputhist(xl, dinty)
        if xo: gRow = xo[1]

      if DrawSpec: # dipole axis takes fewer rows if also drawing specgram
        self.axdipole = ax = self.figure.add_subplot(self.G[gRow:5,0]); # dipole
        self.lax.append(ax)
      else:
        self.axdipole = ax = self.figure.add_subplot(self.G[gRow:-1,0]); # dipole
        self.lax.append(ax)

      N_trials = self.getNTrials()
      if debug: print('simdat: N_trials:',N_trials)

      yl = [np.amin(ddat['dpl'][sidx:eidx,1]),np.amax(ddat['dpl'][sidx:eidx,1])]

      for lsim in lsimdat: # plot average dipoles from prior simulations
        olddpl = lsim[1]
        if debug: print('olddpl has shape ',olddpl.shape,len(olddpl[:,0]),len(olddpl[:,1]))
        ax.plot(olddpl[:,0],olddpl[:,1],'--',color='black',linewidth=self.gui.linewidth)
        yl[0] = min(yl[0],olddpl[sidx:eidx,1].min())
        yl[1] = max(yl[1],olddpl[sidx:eidx,1].max())

      if N_trials>1 and dconf['drawindivdpl'] and len(ddat['dpltrials']) > 0: # plot dipoles from individual trials
        for dpltrial in ddat['dpltrials']:
          ax.plot(dpltrial[:,0],dpltrial[:,1],color='gray',linewidth=self.gui.linewidth)
          yl[0] = min(yl[0],dpltrial[sidx:eidx,1].min())
          yl[1] = max(yl[1],dpltrial[sidx:eidx,1].max())

      if dinty['Evoked']: self.drawEVInputTimes(ax,yl,0.1,(xl[1]-xl[0])*.02)#15.0)
      #if dinty['Evoked']: self.drawEVInputTimes(ax,yl,0.1,15.0)

      if conf.dconf['drawavgdpl'] or N_trials <= 1:
        # this is the average dipole (across trials)
        # it's also the ONLY dipole when running a single trial
        ax.plot(ddat['dpl'][:,0],ddat['dpl'][:,1],'k',linewidth=self.gui.linewidth+1)

      scalefctr = getscalefctr(self.paramf)
      NEstPyr = int(self.getNPyr() * scalefctr)

      if NEstPyr > 0:
        ax.set_ylabel(r'Dipole (nAm $\times$ '+str(scalefctr)+')\nFrom Estimated '+str(NEstPyr)+' Cells',fontsize=dconf['fontsize'])
      else:
        ax.set_ylabel(r'Dipole (nAm $\times$ '+str(scalefctr)+')\n',fontsize=dconf['fontsize'])
      ax.set_xlim(xl); ax.set_ylim(yl)

      bottom = 0.0
      left = 0.08
      w,h=getscreengeom()
      if w < 2800: left = 0.1

      if DrawSpec: #
        if debug: print('ylim is : ', np.amin(ddat['dpl'][sidx:eidx,1]),np.amax(ddat['dpl'][sidx:eidx,1]))
        gRow = 6
        self.axspec = ax = self.figure.add_subplot(self.G[gRow:10,0]); # specgram
        self.lax.append(ax)
        cax = ax.imshow(ds['TFR'],extent=(ds['time'][0],ds['time'][-1],ds['freq'][-1],ds['freq'][0]),aspect='auto',origin='upper',cmap=plt.get_cmap('jet'))
        ax.set_ylabel('Frequency (Hz)',fontsize=dconf['fontsize'])
        ax.set_xlabel('Time (ms)',fontsize=dconf['fontsize'])
        ax.set_xlim(xl)
        ax.set_ylim(ds['freq'][-1],ds['freq'][0])
        cbaxes = self.figure.add_axes([0.6, 0.49, 0.3, 0.005])
        cb = plt.colorbar(cax, cax = cbaxes, orientation='horizontal') # horizontal to save space
        for ax in self.lax:
          if ax: ax.set_xlim(xl)
        bottom = 0.08
      else:
        ax.set_xlabel('Time (ms)',fontsize=dconf['fontsize'])
    except:
      print('ERR: in plotsimdat')
    for i in range(len(self.lax)-1):
        self.lax[i].get_xaxis().set_visible(False)

    # self.figure.subplots_adjust(left=left,right=0.99,bottom=bottom,top=0.99,hspace=0.1,wspace=0.1) # reduce padding
    self.figure.subplots_adjust(left=0.2,right=0.96,bottom=0.05,top=0.99,hspace=0.1,wspace=0.1) # reduce padding

  def plot (self):
    self.plotsimdat()
    self.draw()
