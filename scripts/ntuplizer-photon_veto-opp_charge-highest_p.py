import ROOT
import numpy
import time
from ntuplizer import *



#-----------------
# Global Variables
#-----------------
delphes_file_path = ('~/nobackup/data/FCCee-Scalar-Boson-delphes-samples/'
                     'eeTo2fermion.root')
ntuple_path = '../ntuples'
particles =  ['electron', 'muon', 'photon']
var_to_wrt = ['pt', 'eta', 'phi', 'charge', 'theta', 'phi_a', 'alpha',
              'p_mag', 'm_inv', 'm_rec']  
ptcl_var_to_wrt = {'electron':var_to_wrt, 'muon':var_to_wrt}

load_delphes_lib()
evt_chain = load_delphes_file(delphes_file_path, particles)
num_evts_failed_photon_veto = 0
num_evts_failed_oppo_charge_req = 0

ntuple_file = create_ntuple_file(ntuple_path, delphes_file_path, ptcl_var_to_wrt)
ntuple_trees = create_ntuple_trees(ptcl_var_to_wrt)

start = time.time()
for ievt, evt in enumerate(evt_chain):
	if particle_var_veto(evt, 'photon', 'energy', 'highest < 10 GeV'):
		
		opposite_charge_pairs = select_ptcl_var_opposite(
		evt, ['electron', 'muon'], 'charge', var_in_delphes = True
		)
		if opposite_charge_pairs != 0:
			final_cand = select_ptcl_var_highest(
			evt, ['electron', 'muon'], 'sum_p_mag',
			var_in_delphes = False, candidates = opposite_charge_pairs
			)
			write_pair_to_ntuple_tree(ntuple_trees, evt, final_cand, var_to_wrt)
		else:
			 num_evts_failed_oppo_charge_req += 1
	else:
		num_evts_failed_photon_veto += 1
	end =time.time()
	if (ievt % 10000 == 0):
		print (end-start), " seconds has elapsed. ", ievt, " events has been processed"

ntuple_file.close()
