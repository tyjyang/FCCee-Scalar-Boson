from ntuplizer import *
from helper import *
from cutflow import *
import time
#-----------------
# Global Variables
#-----------------
delphes_path = '/uscms/home/tyang/nobackup/data/FCCee-Scalar-Boson-delphes-samples/'
delphes_file_list = ['eeZS_p5.root', 
                     'eeZS_2.root', 
                     'eeZS_5.root', 
                     'eeZS_15.root',
                     'eeZS_25.root',
                     'ee2fermion_mutau.root',
                     'ee4lepton_muon.root']
electron_PID = 11
muon_PID = 13
tau_PID = 15
pythia_out_ID = 23

#delphes_file_list = ['eeTollS_0p5_inc.root']
ntuple_path = '../ntuples_in_prep'
particles =  ['particle']
var_to_wrt = ['pt', 'eta', 'alpha_sep', 'cos_theta', 'alpha',
              'p_mag', 'm_inv', 'm_rec','p_mag_missing', 'cos_theta_p_missing']  
ptcl_var_to_wrt = {'electron':var_to_wrt, 'muon':var_to_wrt}

load_delphes_lib()

for delphes_file in delphes_file_list:
	delphes_file_path = delphes_path + delphes_file
	print "separating e and mu channel evts in ", delphes_file_path
	print "-------------------------------------------------------------------"
	evt_chain = load_delphes_file(delphes_file_path, particles)
	num_ee_evts = 0
	num_mumu_evts = 0
	for ievt, evt in enumerate(evt_chain):
		#print 'Event number ', ievt, ": "
		#print "=============================="
		#print "Hard leptons excluding incoming: "
		for cand in evt.Particle:
			if cand.Status == pythia_out_ID:
				if abs(cand.PID) == electron_PID:
					
					num_ee_evts += 1
					break
				if abs(cand.PID) == muon_PID:
					num_mumu_evts += 1
					break
	print 'number of ee events: ', num_ee_evts
	print 'number of mumu events: ', num_mumu_evts
