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
	num_double_channel_evts = 0
	num_no_id_evts = 0
	for ievt, evt in enumerate(evt_chain):
		#print 'Event number ', ievt, ": "
		#print "=============================="
		#print "Hard leptons excluding incoming: "
		num_electron, num_positron, num_muon, num_antimuon, num_tau, num_antitau = (
		0,0,0,0,0,0)
		for cand in evt.Particle:
			if cand.Status == pythia_out_ID:
				if cand.PID == electron_PID:
					num_electron += 1
				elif cand.PID == -1*electron_PID:
					num_positron += 1
				elif cand.PID == muon_PID:
					num_muon += 1
				elif cand.PID == -1*muon_PID:
					num_antimuon += 1
				elif cand.PID == tau_PID:
					num_tau += 1
				elif cand.PID == -1*tau_PID:
					num_antitau += 1
		if (((num_electron == 1 and num_positron == 1) and 
		     (num_muon     == 1 and num_antimuon == 1)) or
		    ((num_electron == 1 and num_positron == 1) and 
		     (num_tau      == 1 and num_antitau  == 1)) or
		    ((num_tau      == 1 and num_antitau  == 1) and 
		     (num_muon     == 1 and num_antimuon == 1))):
			print '==============================='
			for cand in evt.Particle:
				if (abs(cand.PID) == electron_PID or 
				    abs(cand.PID) == muon_PID     or
				    abs(cand.PID) == tau_PID) and cand.Status == pythia_out_ID:
					print cand.M1, ">>", cand.PID
			num_double_channel_evts += 1
		elif ((num_electron == 1 and num_positron == 1) or
		      ((num_electron > 0 and num_positron >  0) and
		       (num_muon    == 0 or  num_antimuon == 0) and
		       (num_tau     == 0 or  num_antitau  == 0))):
			num_ee_evts += 1
			continue
		elif ((num_muon     == 1 and num_antimuon == 1) or
		      ((num_muon      > 0 and num_antimuon >  0) and
		       (num_electron == 0 or  num_positron == 0) and
		       (num_tau      == 0 or  num_antitau  == 0))):
			num_mumu_evts += 1
		elif ((num_electron == 0 or num_positron == 0) and
		      (num_muon     == 0 or num_antimuon == 0) and
		      (num_tau      == 0 or num_antitau  == 0)):
			num_no_id_evts += 1
	print 'number of ee events: ', num_ee_evts
	print 'number of mumu events: ', num_mumu_evts
	print 'number of double channel events: ', num_double_channel_evts
	print 'number of no id events: ', num_no_id_evts
