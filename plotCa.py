# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pickle
import numpy
import matplotlib.pyplot as plt


with open('/Users/sarahpugliese/hnn/data/ERPYes3Trials_ca_test/cai.pkl','rb') as cai:
    caidata = pickle.load(cai)
    cai.close()
#
# with open('/Users/sarahpugliese/hnn/data/SRJ_2007_Fig6_ThreshP/volt.pkl','rb') as v:
#     vdata = pickle.load(v)
#     v.close()
#
# with open('/Users/sarahpugliese/hnn/data/SRJ_2007_Fig6_ThreshP/ica.pkl','rb') as ica:
#     icadata = pickle.load(ica)
#     ica.close()

print(cai)
#
# plt.plot(vdata['vtime'],vdata[3][1])
# plt.xlim([0,vdata['vtime'][-1]])
# plt.ylim([-80,40])
# plt.title('Apical tuft voltage')
# plt.xlabel('Time (ms)')
# plt.ylabel('Voltage (mV)')
#
# plt.savefig('ca_figures/tuftV_mar29_1.png',format='png')
#
# # plt.show()
#
# plt.plot(vdata['vtime'],vdata[3][2])
# plt.xlim([0,vdata['vtime'][-1]])
# plt.ylim([-80,40])
# plt.title('Apical 2 voltage')
# plt.xlabel('Time (ms)')
# plt.ylabel('Voltage (mV)')
#
# plt.savefig('ca_figures/apical2V_mar29_1.png',format='png')
#
# # plt.show()
#
# plt.plot(vdata['vtime'],vdata[3][3])
# plt.xlim([0,vdata['vtime'][-1]])
# plt.ylim([-80,40])
# plt.title('Apical 1 voltage')
# plt.xlabel('Time (ms)')
# plt.ylabel('Voltage (mV)')
#
# plt.savefig('ca_figures/apical1V_mar29_1.png',format='png')
#
# # plt.show()
#
# plt.plot(vdata['vtime'],vdata[3][4])
# plt.xlim([0,vdata['vtime'][-1]])
# plt.ylim([-80,40])
# plt.title('Somatic voltage')
# plt.xlabel('Time (ms)')
# plt.ylabel('Voltage (mV)')
#
# plt.savefig('ca_figures/somaV_mar29_1.png',format='png')
#
# # plt.show()
#
# plt.plot(vdata['vtime'],vdata[3][5])
# plt.xlim([0,vdata['vtime'][-1]])
# plt.ylim([-80,40])
# plt.title('Basal dendrite voltage')
# plt.xlabel('Time (ms)')
# plt.ylabel('Voltage (mV)')
#
# plt.savefig('ca_figures/basalV_mar29_1.png',format='png')
#
# # plt.show()
#
# plt.plot(caidata['cai_time'],caidata[3][1])
# plt.xlim([0,vdata['vtime'][-1]])
# plt.ylim([0,0.25])
# plt.title('Apical tuft dendritic Ca concentration')
# plt.xlabel('Time (ms)')
# plt.ylabel('Calcium concentration (mM)')
#
# plt.savefig('ca_figures/tuft_mar29_1.png',format='png')
#
# # plt.show()
#
# plt.plot(caidata['cai_time'],caidata[3][2])
# plt.xlim([0,vdata['vtime'][-1]])
# plt.ylim([0,0.25])
# plt.title('Apical 2 dendritic Ca concentration')
# plt.xlabel('Time (ms)')
# plt.ylabel('Calcium concentration (mM)')
#
# plt.savefig('ca_figures/apical2_mar29_1.png',format='png')
#
# # plt.show()
#
# plt.plot(caidata['cai_time'],caidata[3][3])
# plt.xlim([0,vdata['vtime'][-1]])
# plt.ylim([0,0.25])
# plt.title('Apical 1 dendritic Ca concentration')
# plt.xlabel('Time (ms)')
# plt.ylabel('Calcium concentration (mM)')
#
# plt.savefig('ca_figures/apical1_mar29_1.png',format='png')
#
# # plt.show()
#
# plt.plot(caidata['cai_time'],caidata[3][4])
# plt.xlim([0,vdata['vtime'][-1]])
# plt.ylim([0,0.25])
# plt.title('Somatic Ca concentration')
# plt.xlabel('Time (ms)')
# plt.ylabel('Calcium concentration (mM)')
#
# plt.savefig('ca_figures/soma_mar29_1.png',format='png')
#
# # plt.show()
#
# plt.plot(caidata['cai_time'],caidata[3][5])
# plt.xlim([0,vdata['vtime'][-1]])
# plt.ylim([0,0.25])
# plt.title('Basal dendritic Ca concentration')
# plt.xlabel('Time (ms)')
# plt.ylabel('Calcium concentration (mM)')
#
# plt.savefig('ca_figures/basal_mar29_1.png',format='png')
#
# # plt.show()
#
# plt.plot(icadata['ica_time'],icadata[3][1])
# plt.xlim([0,vdata['vtime'][-1]])
# plt.ylim([-0.1,0.05])
# plt.title('Apical tuft dendritic Ca current')
# plt.xlabel('Time (ms)')
# plt.ylabel('Calcium current (mA/cm^2)')
#
# plt.savefig('ca_figures/tuftI_mar29_1.png',format='png')
#
# # plt.show()
#
# plt.plot(icadata['ica_time'],icadata[3][2])
# plt.xlim([0,vdata['vtime'][-1]])
# plt.ylim([-0.1,0.05])
# plt.title('Apical 2 dendritic Ca current')
# plt.xlabel('Time (ms)')
# plt.ylabel('Calcium current (mA/cm^2)')
#
# plt.savefig('ca_figures/apical2I_mar29_1.png',format='png')
#
# # plt.show()
#
# plt.plot(icadata['ica_time'],icadata[3][3])
# plt.xlim([0,vdata['vtime'][-1]])
# plt.ylim([-0.1,0.05])
# plt.title('Apical 1 dendritic Ca current')
# plt.xlabel('Time (ms)')
# plt.ylabel('ca_figures/Calcium current (mA/cm^2)')
#
# plt.savefig('ca_figures/apical1I_mar29_1.png',format='png')
#
# # plt.show()
#
# plt.plot(icadata['ica_time'],icadata[3][4])
# plt.xlim([0,vdata['vtime'][-1]])
# plt.ylim([-0.1,0.05])
# plt.title('Somatic Ca current')
# plt.xlabel('Time (ms)')
# plt.ylabel('Calcium current (mA/cm^2)')
#
# plt.savefig('ca_figures/somaI_mar29_1.png',format='png')
#
# # plt.show()
#
# plt.plot(icadata['ica_time'],icadata[3][5])
# plt.xlim([0,vdata['vtime'][-1]])
# plt.ylim([-0.1,0.05])
# plt.title('Basal dendritic Ca current')
# plt.xlabel('Time (ms)')
# plt.ylabel('Calcium current (mA/cm^2)')
#
# plt.savefig('ca_figures/basalI_mar29_1.png',format='png')
#
# # plt.show()
