import ROOT
import numpy
import time
from ntuplizer import *
from helper import *



#-----------------
# Global Variables
#-----------------
delphes_path = '/uscms/home/tyang/nobackup/data/FCCee-Scalar-Boson-delphes-samples/'
#delphes_file_list = ['eeTollS_0p5_inc.root', 'eeTollS_5_inc.root', 'eeTollS_25_inc.root',
#                     'ee2fermion_mutau.root', 'four_lepton.root']
delphes_file_list = [#'eeZS_p5.root', 
                     'eeZS_2.root',
                     'eeZS_5.root', 
                     'eeZS_10.root',
                     'eeZS_15.root',
                     'eeZS_25.root',  
                     'ee2fermion_mutau.root',
                     'ee4lepton_muon.root',
                     'ee4lepquark.root'
                    ]
ntuple_path = '../ntuples_gen_photon'
particles =  ['electron', 'muon', 'photon']
var_to_wrt = ['pt', 'eta', 'phi', 'cos_theta', 'alpha',
              'p_mag', 'm_inv', 'm_rec','p_mag_missing', 'cos_theta_p_missing']  
ptcl_var_to_wrt = {'electron':var_to_wrt, 'muon':var_to_wrt}
pythia_out_ID = [1]
photon_ID = 22
gen_photon_E_thres = 1
flatten_vars = True
sort_each_var = False
load_delphes_lib()

for delphes_file in string_to_list(delphes_file_list):
	delphes_file_path = delphes_path + delphes_file
	print "ntuplizing delphes file: ", delphes_file_path
	print "-------------------------------------------------------------------"
	evt_chain = load_delphes_file(delphes_file_path, particles)
	num_evts_failed_photon_veto = 0
	num_evts_failed_oppo_charge_req = 0

	ntuple_file = create_ntuple_file(ntuple_path, delphes_file_path, ptcl_var_to_wrt)
	ntuple_trees = create_ntuple_trees(ptcl_var_to_wrt, flatten_vars)

	start = time.time()
	for ievt, evt in enumerate(evt_chain):
		passed_gen_photon_veto = 1
		for gen_ptcl in evt.Particle:
			if (gen_ptcl.Status in pythia_out_ID and 
			    gen_ptcl.PID == photon_ID):
				if gen_ptcl.E > gen_photon_E_thres:
					passed_gen_photon_veto = 0
					break
		if passed_gen_photon_veto:
			opposite_charge_pairs = select_ptcl_var_opposite(delphes_file,
			evt, ['electron', 'muon'], 'charge', var_in_delphes = True
			)
			if opposite_charge_pairs != 0:
				final_cand = select_ptcl_var_highest(delphes_file,
				evt, ['electron', 'muon'], 'sum_p_mag',
				var_in_delphes = False, candidates = opposite_charge_pairs
				)
				write_to_ntuple_tree(delphes_file, ntuple_trees, evt, 
				                     final_cand, var_to_wrt, flatten_vars)
			else:
				 num_evts_failed_oppo_charge_req += 1
		else:
			num_evts_failed_photon_veto += 1
		end =time.time()
		if (ievt % 10000 == 0):
			print (end-start), " seconds has elapsed. ", ievt, " events has been processed"
	print num_evts_failed_photon_veto, " evts failed the photon veto"
	print num_evts_failed_oppo_charge_req, " evts failed the opposite charge requirement"
	for ptclname,tree in ntuple_trees.items(): 
		tree.Write(ptclname, ROOT.TObject.kOverwrite)
	ntuple_file.Close()

