# import ROOT in batch mode
import sys,os
oldargv = sys.argv[:]
import ROOT
import numpy as np
from helper import *

'''
INPUT -------------------------------------------------------------------------
|* NONE
|
ROUTINE -----------------------------------------------------------------------
|* load the local delphes lobrary into ROOT
|
OUTPUT ------------------------------------------------------------------------
|* NONE
+------------------------------------------------------------------------------
'''
def load_delphes_lib():
	ROOT.gSystem.Load("libDelphes.so")
	ROOT.gInterpreter.Declare('#include "classes/DelphesClasses.h"');

'''
INPUT -------------------------------------------------------------------------   
|* (str) path_delphes_file: the path to the delphes file to be loaded
|* list(str) particles: the list of particle trees to be loaded
|
ROUTINE -----------------------------------------------------------------------
|* load events in the delphes file into a TChain
|* set the address of aech tree to a pointer of the tree name
|
OUTPUT ------------------------------------------------------------------------
|* (ROOT.TChain) chain: the TChain containing events inside the delphes file
|                       with trees by particle type readily accessible by 
|                       for evt in chain: particle_tree = evt.Particle
+------------------------------------------------------------------------------
'''
def load_delphes_file(delphes_file_path, particles):
	chain = ROOT.TChain("Delphes")
	chain.Add(delphes_file_path)
	Particles = [particle.capitalize() for particle in particles]
	Particle_pointers = [(Particle + "*") for Particle in Particles]
	for pointer in Particle_pointers: chain.SetBranchStatus(pointer, 1) 
	return chain

'''
INPUT -------------------------------------------------------------------------
|* (TObject) event: the delphes event object to look at
|* (str) particle: the particle to be used for the veto
|* (str) var: the variable of that particle to be used for the veto
|* (str) threshold: The condition, when satisfied, vetos the event
|                   takes the form {quantifier inequaility critical_val uint}
|                   e.g. threshold = "highest > 10 GeV"
|  
ROUTINE -----------------------------------------------------------------------
|* parse the threshold string into quantifier, inequality, critical_val
|* fetch the particle value with event.particle[quantifier].Var
|* check if the threshold condition is met
|  - if yes, return 0 to signal veto of the event
|  - if no, return 1 to signal passing 
|
OUTPUT ------------------------------------------------------------------------
|* (int): 0 for vetoed event; 1 for passed event 
+------------------------------------------------------------------------------ 
'''
def particle_var_veto(event, particle, var, threshold):
	if len(threshold.split()) != 4:
		sys.exit("invalid threshold format for event veto")
	else:
		quantifier, inequality, crit_val, unit = threshold.split()
	
	var = vars_to_delphes_form(var)
	num_particle = 0
	for candidate in getattr(event, particle.captialize()):
		num_particle += 1
	if num_particle == 0: return 1

	if quantifier == "highest":
		for i_cand, cand in enumerate(getattr(event, particle.captialize())):
			if i_cand = 0:
				particle_var_max = getattr(cand,var)
			else:
				if getattr(cand,var) > particle_var_max: 
					particle_var_max = getattr(cand,var)
		if inequality == ">":
			if particle_var_max > crit_val: return 0
			else: return 1
		elif inequality == "<":
			if particle_var_max < crit_val: return 0
			else: return 1
		else: sys.exit("invalid inequality for event veto")
	elif quantifier == "lowest":
		for i_cand, cand in enumerate(getattr(event, particle.captialize())):
			if i_cand = 0:
				particle_var_min = getattr(cand,var)
			else:
				if getattr(cand,var) < particle_var_min:
					particle_var_min = getattr(cand,var)
		if inequality == ">":
			if particle_var_min > crit_val: return 0
			else: return 1
		elif inequality == "<":
			if particle_var_min < crit_val: return 0
			else: return 1
		else: sys.exit("invalid inequality for event veto")
	else: sys.exit("invalid particle quantifier for event veto")

'''
INPUT -------------------------------------------------------------------------
|* (TObject) event: the delphes event to look at
|* (str) or list(str) particles: the particle type(s) for the selection
|                      - NOTE that there can be more than one ptcl type, 
|                        as opposed to ptcl var veto
|                      - must be COMMA-SEPARATED when passed in as str
|* (str) var: the variable based on which one makes the selection
|             - NOTE that there can only be one variables passed in
|               if the selection is based on a variable derived from multiple
|               other variables, then the calculation should be done by calling
|               calc_var().
|* (bool) var_in_delphes: the boolean var to indicate whether the var passed in
                          is already in delphes or needs to be calculated
|* (dict) candidates: the dict of ptcl candidate indices. Keys are ptcl types,
|                     values are lists of cand set indices
|                     e.g. {'electron': [[1,2],[1,3]]}
|  
ROUTINE -----------------------------------------------------------------------
|* check candidates passed in.
|  - if "all", we make a list of all possible cand sets in the ptcl tree
|  - if 0: previous steps in the selection have already ruled out all cands,
|          return 0 to signal non-passing.
|  - else, look at the candidate dict ptcl by ptcl
|* for each cand set in a ptcl tree, check if their val of interst are opposite
|  - if yes, append their indices to cand_selected[ptcl], which was declared to
|    be an empty list
|* for each cand_selected[ptcl], if len == 0, then drop from dict cand_select
|* if cand_select is empty, i.e., no candidate set passed selection in any 
|  ptcl tree, then return 0. Else, return the dict cand_select 
| 
OUTPUT ------------------------------------------------------------------------
|* 0 or (dict) cand_selected: the list of cand set indices grouped in ptcls
+------------------------------------------------------------------------------ 
'''

def select_ptcl_var_opposite(event, particles, var, var_in_delphes,
                             candidates="all"):
	particles = str_to_list(particles)
	var = list_to_str(var)
	cand_selected = {}
	for ptcl in particles:
		if candidates == "all":
			ptcl_cands = get_idx_candidate_sets(event, ptcl, subset_size = 2)
		elif candidates == 0:
			return 0
		else: 
			ptcl_cands = candidates[ptcl]
		cand_selected[ptcl] = []
		for cand in ptcl_cands:
			if var_in_delphes:
				cand_var_val = get_ptcl_var_by_idx(event, ptcl, cand, var)
				if cand_var_val[0] * cand_var_val[1] < 0:
					cand_selected[ptcl].append(cand)
			else:
				var_calc = var + "_prod"
				cand_var_val = calc_ptcl_var_by_idx(event, ptcl, cand, var_calc)
				if cand_var_val < 0:
					cand_selected[ptcl].append(cand)
		if len(cand_selected[ptcl] == 0): del cand_selected[ptcl]
	if len(cand_selected == 0): return 0
	else: return cand_selected

def select_particle_var_highest(event, particles, var, *candidates="all"):

'''
INPUT -------------------------------------------------------------------------
|* (TObject) event: the delphes event object to look at
|* (dict) particle_variable_criteria:
|* (str) or list(str) particle: the particle type to be selected 
|                               in the final state
|                               must be COMMA-SEPARATED when passed in as str
|* (dict) variable_criteria: the dictionary with variabels as keys and their
|                            corresponding pre-selection criteria as values 
|  - the criteria to select particles based on their variable
|  - criteria can be one of the following:
|    - "opposite": require the values of the variable to have opposite signs
|    - "highest": select the lepton pair with the highest possible sum in the 
|                 value of the variable while satisfying other criteria
|
|ROUTINE ----------------------------------------------------------------------
|* within each event, look at the variables of a type of particles
|* according to the criteria on each varialbe, select the pair of 
|  particle from that type
|* 
|
|OUTPUT -----------------------------------------------------------------------
|* [pair indices, pair_sum]: The indices of the selected pair of particles 
|                            as an integer list of length 2
|                            And the sum of variable required to be "highest" 
|* int 0: if the number of candidates is less than two, or if no pair
|         from the candidate pool satisfy all the criteria
+------------------------------------------------------------------------------
'''
def preselect_fs_lepton_pair(event, particle_variable_criteria):
	# loop over candidates to extract variable of interest
	particles = string_to_list(particles)
	variables = string_to_list(variables)
	criteria = string_to_list(criteria)

	# check that there is a criterium for each variable
	if len(variable) == len(criteria):
		# store particle candidate's variables into a 2d array for 
		# later selection based on criteria
		candidates = []
		delphes_variables = vars_to_delphes_form(variables)
		for i_candidate, candidate in enumerate(
		getattr(event, particle.capitalize())):
			candidates[i_candidate] = ([getattr(candidate, variable)
			                           for variable in delphes_variables])
	else:
		print("Number of variables and criteria do not match "
			  "in selection of final state leptons, "
			  "check parameters for fs_particle_selection()")
		return 

	candidates = np.array(candidates)
	
	# check if there are no less than 2 particle candidates to select from
	if len(candidates[:, 0]) < 2:
		print("Number of particle candidates is less than two.")
		return 0
	
	# apply the criteria to make the selection
	for i_criterium, criterium in enumerate(criteria):
		if criterium == 'opposite':
			i_plus = []
			i_minus = []
			for i_candidate, candidate in enumerate(candidates):
				if candidate[i_criterium] < 0:
					i_plus.append(i_candidate)
				else:
					i_minus.append(i_candidate)
		if criterium == 'highest':
			variable_col = candidates[:, i_criterium]
			i_max = []
			for i in np.arange(0, num_particle):
				i_max.append(np.argmax(variable_col))
				variable_col[np.argmax(variable_col)] = np.amin(variable_col)
		
	# select the parir of particles with highest possible value for the
	# "leading" variable, while satisfy the "opposite" criterium for
	# the other variable
	pair_indices = []    
	pair_sum = 0
	for i in i_max:
		if (i in i_plus):
			for j in i_max[i:]:
				if (j in i_minus):
					new_sum = (candidates[i][i_criterium] + 
					           candidates[j][i_criterium])
					if new_sum > pair_sum:
						pair_sum = new_sum
						pair_indices = [i, j]
		elif (i in i_minus):
			for j in i_max[i:]:
				if (j in i_plus):
					new_sum = (candidates[i][i_criterium] + 
					           candidates[j][i_criterium])
					if new_sum > pair_sum:
						pair_sum = new_sum
						pair_indices = [i, j]
	if len(pair_indices) > 0:
		return [pair_indices, pair_sum]
	else:
		return 0

'''
INPUT -------------------------------------------------------------------------
|* (str) ntuple_path: the path to the folder containing all ntuple files
|* (str) ntuple_filename: the name of the ntuple file
|  
ROUTINE -----------------------------------------------------------------------
|* check if a file with ntuple_filename already exists under ntuple_path
|* if yes, stop execution and return an error msg
|* if no, create the file 
| 
OUTPUT ------------------------------------------------------------------------
|* sys.exit() msg
|OR
|* (ROOT.TFile) the created ntuple file 
+------------------------------------------------------------------------------
''' 
def open_ntuple_file(ntuple_path, ntuple_filename):
	if os.path.exists(ntuple_filename):
		sys.exit("ntuple file:" + ntuple_filename + 
		         " already exists under " + ntuple_path)
	else: 
		return ROOT.TFile(ntuple_filename, 'CREATE')

'''
INPUT -------------------------------------------------------------------------
|* (dict) particle_variable: the dictionary specifying which 
|         variables are to be extracted from each particle.
|         e.g. particle_variable = {"electron":["pt", "eta", "phi"]}
|  
ROUTINE -----------------------------------------------------------------------
|* create an enpty dict of TNtuple trees
|* create a TNtuple tree for each particle with their corresponding variables
|  to be written, put it into the dict with the particle name as key
|* for each tree, the columns are ordered in sorted delphes var in lowercase +
|  sorted calc var in lowercase
| 
OUTPUT ------------------------------------------------------------------------
|* {(str) "particle":(TNtuple) ntuple_Tree} the dict containing all trees
+------------------------------------------------------------------------------ 
''' 
def create_tntuple_trees(particle_variable):
	ntuple_tree = {}
	particles = particle_variable.keys()
	for particle in sorted(particles):
		
		# create a ROOT Ntuple tree to store all variables of desire for 
		# each particle
		variables = particle_variable[particle]
		delphes, calc = sep_var_into_delphes_calculated(variables)
		sorted_var = sort_delphes_and_calc_var(delphes, calc)
		particle_variables = [particle + '_' + variable 
		                      for variable in sorted_var]
		column_separator = ":"
		variables_combined = column_separator.join(particle_variables)
		ntuple_tree[particle] = ROOT.TNtuple(particle, "Flat ntuple tree for " 
		                                     + particle, variables_combined)
	return ntuple_tree

'''
INPUT -------------------------------------------------------------------------
|* (str) or list(str) variables
|  
ROUTINE -----------------------------------------------------------------------
|* split the variables into delphes and calc
|* sort the two lists, and convert them to dict with ind as values
OUTPUT ------------------------------------------------------------------------
|* (dict) delphes_var_dict, calc_var_dict
+------------------------------------------------------------------------------ 
''' 
def get_var_ind_dicts(variables):
	delphes_var, calc_var = sep_var_into_delphes_calculated(variables)
	delphes_var_dict = {x: i for i, x in enumerate(sorted(delphes_var))}
	calc_var_dict = {x: i for i, x in enumerate(sorted(calc_var))}
	return delphes_var_dict, calc_var_dict

'''
INPUT -------------------------------------------------------------------------
|* (TObject) event: the delphes event to look at
|* list(int) pair_indices: the indices for the pair of leptons in the event
|* (str) particle: the particle for the ntuple tree to be filled
|* (dict) delphes_var_dict: the dict of delphes vars with var name as keys 
|                           and indices as values
|* (dict) calc)_var_dict: same as delphes_var_dict but with calc vars 
|* (TNtuple) tree: the ntuple tree to be filled
|
ROUTINE -----------------------------------------------------------------------
|* separate variables into those alredy in delphes and those need to be 
|  calculated by calling sep_var_into_delphes_calculated()
|* calculate those variables
|* fill the event as a row into the TNtuple tree for the particle
|
OUTPUT ------------------------------------------------------------------------
|* NONE
+------------------------------------------------------------------------------
'''
def write_event_to_ntuple_tree(event, pair_indices, particle, 
                               delphes_var_dict, calc_var_dict, tree):
	delphes_var = delphes_var_dict.keys()
	delphes_format_var = vars_to_delphes_form(delphes_var) 
	calc_var = calc_var_dict.keys()
	variables = delphes_var + calc_var
	num_var = len(variables)
	num_delphes_var = len(delphes_var)
	var_data = np.empty([2,num_var])
	
	# select the lepton pair and fill their delphes data to the data array 
	i = 0
	for i_candidate, candidate in (
	enumerate(getattr(event, particle.capitalize()))):
		if i_candidate in pair_indices:
			var_data[i][:num_delphes_var] = (
			[getattr(candidate, variable) for variable in delphes_format_var])
			i += 1
	var_data = calculate_all_var(particle, delphes_var_dict, calc_var_dict, 
                                 var_data[:,:num_delphes_var])
	tree.Fill(*var_data[0,:])
	tree.Fill(*var_data[1,:])

