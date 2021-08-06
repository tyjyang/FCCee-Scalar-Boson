import ROOT
import numpy
import time
from ntuplizer import *
from helper import *



#-----------------
# Global Variables
#-----------------
delphes_path = '/scratch5/arapyan/fcc_ee/scalar_delphes_idea/'
#delphes_file_list = ['eeTollS_0p5_inc.root', 'eeTollS_5_inc.root', 'eeTollS_25_inc.root',
#                     'ee2fermion_mutau.root', 'four_lepton.root']
delphes_file_list = ['eeZS_p5_photon500.root', 
                     'eeZS_2_photon500.root',
                     'eeZS_5_photon500.root', 
                     'eeZS_10_photon500.root',
                     'eeZS_15_photon500.root',
                     'eeZS_25_photon500.root',  
                     'ee2fermion_mutau_photon500.root',
                     'ee2fermion_electron_photon500.root',
                     'ee4lepton_electron_photon500.root',
                     'ee4lepton_mutau_photon500.root',
                     'ee4eequark_electron_photon500.root',
                     'ee4lepquark_mutau_photon500.root'
                    ]
ntuple_path = '../ntuples_IDEA_500MeV_w_RECO_photons/'
particles =  ['electron', 'muon', 'photon']
var_to_wrt = ['pt', 'eta', 'phi', 'cos_theta', 'alpha',
              'p_mag', 'm_inv', 'm_rec','p_mag_missing', 'cos_theta_p_missing']  
photon_var_to_wrt = ['pt', 'eta', 'phi', 'energy']
ptcl_var_to_wrt = {'electron':var_to_wrt, 'muon':var_to_wrt}

load_delphes_lib()
flatten_vars = True
sort_each_var = False
for delphes_file in string_to_list(delphes_file_list):
	delphes_file_path = delphes_path + delphes_file
	print "ntuplizing delphes file: ", delphes_file_path
	print "-------------------------------------------------------------------"
	evt_chain = load_delphes_file(delphes_file_path, particles)
	num_evts_failed_photon_veto = 0
	num_evts_failed_oppo_charge_req = 0

	ntuple_file = create_ntuple_file(ntuple_path, delphes_file_path, ptcl_var_to_wrt)
	ntuple_trees = create_ntuple_trees(
		ptcl_var_to_wrt, photon_var_to_wrt, flatten_vars, sort_each_var)
	start = time.time()
	for ievt, evt in enumerate(evt_chain):
	#	if particle_var_veto(evt, 'photon', 'energy',True, 'highest < 1 GeV'):
			
		opposite_charge_pairs = select_ptcl_var_opposite(delphes_file,
		evt, ['electron', 'muon'], 'charge', var_in_delphes = True
		)
		if opposite_charge_pairs != 0:
			final_cand = select_ptcl_var_highest(
				delphes_file, evt, ['electron', 'muon'], 'sum_p_mag',
				var_in_delphes = False, candidates = opposite_charge_pairs
			)
			if get_num_ptcl(evt, 'photon'):
				photon_cand = select_ptcl_var_highest(
					delphes_file, evt, 'photon', 'pt', var_in_delphes = True
				)
			else:
				photon_cand = 0
			write_to_ntuple_tree(
				delphes_file, ntuple_trees, evt, final_cand, photon_cand, 
				var_to_wrt, photon_var_to_wrt, flatten_vars, sort_each_var)
		else:
			 num_evts_failed_oppo_charge_req += 1
#		else:
#			num_evts_failed_photon_veto += 1
		end =time.time()
		if (ievt % 10000 == 0):
			print (end-start), " seconds has elapsed. ", ievt, " events has been processed"
	print num_evts_failed_photon_veto, " evts failed the photon veto"
	print num_evts_failed_oppo_charge_req, " evts failed the opposite charge requirement"
	for ptclname,tree in ntuple_trees.items(): 
		tree.Write(ptclname, ROOT.TObject.kOverwrite)
	ntuple_file.Close()

