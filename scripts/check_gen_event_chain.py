from ntuplizer import *
from helper import *
from cutflow import *
import time
import ROOT
import random
#-----------------
# Global Variables
#-----------------
delphes_path = '/scratch5/arapyan/fcc_ee/scalar_delphes_idea/'
delphes_file_list = {
'0p5':'eeZS_p5_photon500.root', 
'2':'eeZS_2_photon500.root', 
'5':'eeZS_5_photon500.root', 
'10':'eeZS_10_photon500.root',
'15':'eeZS_15_photon500.root',
'25':'eeZS_25_photon500.root'
#'ee2fermion_mutau.root',
#'ee4lepton_muon.root'
}
electron_PID = 11
muon_PID = 13
tau_PID = 15
photon_PID = 22
pythia_out_ID = 23

lumi = 115.4
#w = [get_normalization_factor(f, lumi) for f in delphes_file_list]

#delphes_file_list = ['eeTollS_0p5_inc.root']
ntuple_path = '../ntuples_in_prep'
particles =  ['particle']
var_to_wrt = ['pt', 'eta', 'alpha_sep', 'cos_theta', 'alpha',
              'p_mag', 'm_inv', 'm_rec','p_mag_missing', 'cos_theta_p_missing']  
ptcl_var_to_wrt = {'electron':var_to_wrt, 'muon':var_to_wrt}

load_delphes_lib()

ROOT.gROOT.SetBatch()
for i, (key,delphes_file) in enumerate(delphes_file_list.items()):
	delphes_file_path = delphes_path + delphes_file
	print "checking gen photon origins in: ", delphes_file_path
	print "-------------------------------------------------------------------"
	evt_chain = load_delphes_file(delphes_file_path, particles)
	print "i_ptcl    M1    M2  >>  PID    status    Energy"
	for ievt, evt in enumerate(evt_chain):
		if ievt % 50000 == 0:
			evt_selected = random.randint(ievt, ievt+49999)
		if ievt == evt_selected:
			print "========== checking event #", ievt, "=========="
			for cand in evt.Particle: 
				outstr = ''
#				outstr += str(counter) + '    ' 
				if cand.M1 != -1:
					outstr += str(evt.Particle.At(cand.M1).PID) + '    '
				else:
					outstr += str(-1) + '    '
				if cand.M2 != -1:
					outstr += str(evt.Particle.At(cand.M2).PID) + '  '
				else:
					outstr += str(-1) + '  '
				outstr += '>>  ' + str(cand.PID) + '    '
				outstr += str(cand.Status) + '    '
				outstr += str(cand.E)
				print outstr

