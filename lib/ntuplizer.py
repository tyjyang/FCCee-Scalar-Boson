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
	particles = string_to_list(particles)
	Particles = [particle.capitalize() for particle in particles]
	Particle_pointers = [(Particle + "*") for Particle in Particles]
	for pointer in Particle_pointers: chain.SetBranchStatus(pointer, 1) 
	return chain

'''
INPUT -------------------------------------------------------------------------
|* (TObject) event: the delphes event to look at
|* (str) particle: the particle of interest 
|  
ROUTINE -----------------------------------------------------------------------
|* look through the particle candidates in the event and record the number of
|  that particle in the event
| 
OUTPUT ------------------------------------------------------------------------
|* (int) num_ptcl: the number of the input type of particle in the event
+------------------------------------------------------------------------------ 
''' 
def get_num_ptcl(event, particle):
	num_ptcl = 0
	for x in getattr(event, particle.capitalize()): num_ptcl += 1
	return num_ptcl

'''
INPUT -------------------------------------------------------------------------
|* (TObject) event: the delphes event object to look at
|* (str) particle: the particle(s) to be used for the veto
|* (str) var: the one variable of that particle(s) to be used for the veto
|* (str) threshold: The condition which, when satisfied, allow the event to pass
|                   takes the form {quantifier inequaility critical_val uint}
|                   e.g. threshold = "highest < 10 GeV"
|  
ROUTINE -----------------------------------------------------------------------
|* parse the threshold string into quantifier, inequality, critical_val
|* when no ptcl found
|  - return 1 for "for all, there doesn't exist" logic 
|  - return 0 for "there must exist" logic in the threshold clause
|* fetch the particle value with event.particle[quantifier].Var
|* check if the threshold condition is met
|  - if yes, return 0 to signal veto of the event
|  - if no, return 1 to signal passing 
|
OUTPUT ------------------------------------------------------------------------
|* (int): 0 for vetoed event; 1 for passed event 
+------------------------------------------------------------------------------ 
'''
def particle_var_veto(event, particles, var, var_in_delphes, threshold):
	var = list_to_string(vars_to_delphes_form(var))
	particles = string_to_list(particles)
	# check if threshold is corrected formatted
	if len(threshold.split()) != 4:
		sys.exit("invalid threshold format for event veto")
	else:
		quantifier, inequality, crit_val, unit = threshold.split()
		crit_val = int(crit_val)
	# for the case where no ptcl of the type in (list) particles is found
	num_particle = 0
	for ptcl in particles:
		for candidate in getattr(event, ptcl.capitalize()):
			num_particle += 1
			break
	if num_particle == 0: 
		# these conditions translate to: for all ptcls, there do not exist ...
		# such that ... So if no ptcl found, the event passes the veto
		if ((quantifier == "highest" and inequality == "<") or
		    (quantifier == "lowest" and inequality == ">")):
			return 1
		# these translate to: there exist some ptcl such that ...
		# So if no ptcl found, the event is vetoed
		else: 
			return 0
		
	for ptcl in particles:
		if quantifier == "highest":
			for i_cand, cand in enumerate(getattr(event, ptcl.capitalize())):
				if i_cand == 0:
					particle_var_max = getattr(cand,var)
				else:
					if getattr(cand,var) > particle_var_max: 
						particle_var_max = getattr(cand,var)
			if inequality == ">":
				if particle_var_max > crit_val: return 1
				else: return 0
			elif inequality == "<":
				if particle_var_max < crit_val: return 1
				else: return 0
			else: sys.exit("invalid inequality for event veto")
		elif quantifier == "lowest":
			for i_cand, cand in enumerate(getattr(event, ptcl.capitalize())):
				if i_cand == 0:
					particle_var_min = getattr(cand,var)
				else:
					if getattr(cand,var) < particle_var_min:
						particle_var_min = getattr(cand,var)
			if inequality == ">":
				if particle_var_min > crit_val: return 1
				else: return 0
			elif inequality == "<":
				if particle_var_min < crit_val: return 1
				else: return 0
			else: sys.exit("invalid inequality for event veto")
		else: sys.exit("invalid particle quantifier for event veto")

'''
INPUT -------------------------------------------------------------------------
|* (TObject) event: the delphes event to look at
|* (str) or list(str) particles: the list of particle trees to look at
|                                must be COMMA-SEPARATED when passing in
|                                multiple ptcls in a single str
|* (str) var: the var of interest. Only one var, the final one used for select-
|             ion, can be passed in 
|* (bool) var_in_delphes: the boolean var to indicate whether the var passed in
|                         in already in the delphes file
|* list(list(int)) candidates: the list of candidate groups to look at
|                              each group must contain 2 ptcls
|                              when "all" is passed in, we generate all subsets
|                              of candidates with size 2 and go through them
|  
ROUTINE -----------------------------------------------------------------------
|* make sure the ptcls are in list(str) and var is in (str)
|* for each ptcl, create all cand subsets if "all" candidates are passed in
|* check if var is in delphes, calc the var if not
|* if the var of interest is opposite (check by looking at product), append
|  the cand idx to cand_selected[ptcl]
|* remove cand_selected[ptcl] from (dict) cand_selected if none selected
| 
OUTPUT ------------------------------------------------------------------------
|* 0: if cand_selected in empty
|* (dict) cand_selected: {ptcl:[[i1,j1],[i2,j2]]}
+------------------------------------------------------------------------------ 
''' 
def select_ptcl_var_opposite(delphes_file, event, particles, var, var_in_delphes,
                             candidates="all"):
	particles = string_to_list(particles)
	var = string_to_list(var)
	cand_selected = OrderedDict()
	for ptcl in particles:
		if candidates == "all":
			ptcl_cands = get_idx_candidate_sets(event, ptcl, subset_size = 2)
		elif candidates == 0:
			return 0
		else: 
			ptcl_cands = candidates[ptcl]
		if len(ptcl_cands) == 0: continue
		cand_selected[ptcl] = []
		if var_in_delphes:
			for cand in ptcl_cands:
				cand_var_val = get_ptcl_var_by_idx(event, ptcl, cand, var)
				if cand_var_val[0,0] * cand_var_val[0,1] < 0:
					cand_selected[ptcl].append(cand)
		else:
			for cand in ptcl_cands:
				var_calc = var + "_prod"
				cand_var_val = calc_ptcl_var_by_idx(delphes_file, event, ptcl,
				                                    cand, var_calc)[0]
				if cand_var_val < 0:
					cand_selected[ptcl].append(cand)
		if len(cand_selected[ptcl]) == 0: del cand_selected[ptcl]
	if len(cand_selected) == 0: return 0
	else: return cand_selected

'''
INPUT -------------------------------------------------------------------------
|* (TObject) event: the delphes event to look at
|* (str) or list(str) particles: the list of particle trees to look at
|                                must be COMMA-SEPARATED when passing in
|                                multiple ptcls in a single str
|* (str) var: the var of interest. Only one var, the final one used for select-
|             ion, can be passed in 
|* (bool) var_in_delphes: the boolean var to indicate whether the var passed in
|                         in already in the delphes file
|* list(list(int)) candidates: the list of candidate groups to look at
|                              if var_in_delphe == True, group size must be 1
|                              when "all" is passed in, we generate all subsets
|                              of candidates with size N and go through them
|  
ROUTINE -----------------------------------------------------------------------
|* make sure the ptcls are in list(str) and var is in (str)
|* for each ptcl, create all cand subsets if "all" candidates are passed in
|* check if var is in delphes, calc the var if not
|* set var_max to be the var_val of the 1st cand group in the 1st ptcl tree,
|  update var_max if var_val from subsequent cnad group is larger
|* store the ptcl and cand idx info in (dict) cand_max.
|  update the dict if var_max is updated
| 
OUTPUT ------------------------------------------------------------------------
|* 0: if candidate passed in == 0
|* (dict) cand_max: {ptcl:[i,j]}
+------------------------------------------------------------------------------ 
''' 
def select_ptcl_var_highest(delphes_file, event, particles, var, var_in_delphes,
                                candidates="all"):
	particles = string_to_list(particles)
	# overwrite particles passed in with particles contained in the pre-selected
	# candidate set
	if candidates != "all":
		particles = candidates.keys()
	var = string_to_list(var)
	cand_max = OrderedDict()
	var_max = 0
	for i_ptcl, ptcl in enumerate(particles):
		if candidates == "all":
			ptcl_cands = get_idx_candidate_sets(event, ptcl, subset_size = 2)
		elif candidates == 0:
			return 0
		else:
			ptcl_cands = candidates[ptcl]
		if len(ptcl_cands) == 0: continue
		if var_in_delphes:
			for i_cand, cand in enumerate(ptcl_cands):
				if len(cand) != 1:
					sys.exit(("cand group size must be 1 when passing delphes"
					         "var into select_particle_var_highest(): [i, j..]")) 
				var_val = get_ptcl_var_by_idx(event, ptcl, cand, var)
				if i_ptcl == 0 and i_cand == 0:
					var_max = var_val[0,0]
					cand_max[ptcl] = cand
				else:
					if var_val > var_max: 
						var_max = var_val[0,0]
						cand_max.clear()
						cand_max[ptcl] = cand
		else:
			for i_cand, cand in enumerate(ptcl_cands):
				ptcl_cands = {ptcl:cand}
				var_calc = calc_ptcl_var_by_idx(delphes_file, event,
				                                ptcl_cands, var)
				if i_ptcl == 0 and i_cand == 0:
					var_max = var_calc[0]
					cand_max[ptcl] = cand
				else:
					if var_calc[0] > var_max: 
						var_max = var_calc[0]
						cand_max.clear()
						cand_max[ptcl] = cand
	return cand_max

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
def create_ntuple_file(ntuple_path, delphes_file_path, ptcl_var):
	ntuple_filename = get_ntuple_filename(delphes_file_path, ptcl_var)
	ntuple_file_path = ntuple_path + '/' + ntuple_filename
	if os.path.exists(ntuple_file_path):
		sys.exit("ntuple file:" + ntuple_filename + 
		         " already exists under " + ntuple_path)
	else: 
		return ROOT.TFile(ntuple_file_path, 'CREATE')

'''
INPUT -------------------------------------------------------------------------
|* (str) or list(str) variables: the list of variables of interest in lowercase
|                                must be COMMA-SEPARATED when passed in as str
|  
ROUTINE -----------------------------------------------------------------------
|* seperate the variables into delphes and calculated vars
|* for delphes vars, separate into ptcl and evt vars, based on list of vars from
|  ptcl_var_delphes_list and evt_var_delphes_list
|* for calculated vars, check the input vars needed to calculate them
|  if input vars are delphes evt vars, then put calculated var to evt_var_calc
|  otherwise, put it into ptcl_var_calc
| 
OUTPUT ------------------------------------------------------------------------
|* list(str) the four lists of variables
+------------------------------------------------------------------------------ 
''' 
def sep_vars_into_delph_calc_ptcl_evt(variables):
	variables = string_to_list(variables)
	ptcl_var_delphes, evt_var_delphes, ptcl_var_calc, evt_var_calc = [[],[],[],[]]
	for var in variables:
		if var in ptcl_var_delphes_list:
			ptcl_var_delphes.append(var)
		elif var in evt_var_delphes_list:
			evt_var_delphes.append(var)
		
	for var in ptcl_var_delphes: variables.remove(var)
	for var in evt_var_delphes: variables.remove(var)
	
	for var in variables:
		input_var_list = []
		args = get_args_calc_var(var)
		for arg_tuple in args:
			for input_var in arg_tuple[0]:
				input_var_list.append(input_var)
		for input_var in input_var_list:
			if input_var in evt_var_delphes_list:
				evt_var_calc.append(var)
	
	for var in evt_var_calc: variables.remove(var)
	ptcl_var_calc = variables
	return ptcl_var_delphes, evt_var_delphes, ptcl_var_calc, evt_var_calc

'''
INPUT -------------------------------------------------------------------------
|* list(str) var_lists: the variables separated into lists of delphes_ptcl,
|                       delphes_evt, calc_ptcl, and calc_evt
|  
ROUTINE -----------------------------------------------------------------------
|* sort each list passed in
| 
OUTPUT ------------------------------------------------------------------------
|* list(str) the sorted variables 
+------------------------------------------------------------------------------ 
''' 
def sort_separated_vars(*var_lists):
	sorted_var_lists = []
	for var_list in var_lists:
		sorted_var_lists.append(sorted(var_list))
	return sorted_var_lists

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
def create_ntuple_trees(particle_variable):
	ntuple_tree = {}
	particles = particle_variable.keys()
	for particle in sorted(particles):
		
		# create a ROOT Ntuple tree to store all variables of desire for 
		# each particle
		variables = particle_variable[particle]
		a,b,c,d = sep_vars_into_delph_calc_ptcl_evt(variables)
		sorted_var_lists = sort_separated_vars(a,b,c,d)
		sorted_var = []
		for var_list in sorted_var_lists:
			for var in var_list:
				sorted_var.append(var)
		particle_variables = [variable for variable in sorted_var]
		column_separator = ":"
		variables_combined = column_separator.join(particle_variables)
		ntuple_tree[particle] = ROOT.TNtuple(particle, "Flat ntuple tree for " 
		                                     + particle, variables_combined)
	return ntuple_tree

'''
INPUT -------------------------------------------------------------------------
|* (str) delphes_file: the name of the delphes file. Passed in for 
|                      calc_ptcl_var_by_idx() to fetch gen-level info relevant
|                      to calculation of vars (e.g. sqrt(s))
|* (dict) tree_chain: keys are ptcl name in str, values are TTree for the ptcl
|* (TObject) event: the delphes event to look at
|* (dict) ptcl_cand: keys are ptcl name in str, values are list(int) cand idx
|* list(str) var: the vars to be written to the ntuple tree. same for all ptcl
|
ROUTINE -----------------------------------------------------------------------
|* separate variables into ptcl_var_delphes, evt_var_delphes, ptcl_var_calc,
|  and evt_var_calc. Each sorted to match the var order in the ntuple tree.
|* fetch/calculate those variables by calling:
|  - get_ptcl_var_by_idx()
|  - get_delphes_evt_var()
|  - calc_ptcl_var_by_idx()
|  - calc_evt_var()
|* Concatenate the four arrays, rectangularize and then transpose the result
|  array so each particle info takes one row, and the columns are vars
|* write the rectangular array to the ntuple tree row by row
|
OUTPUT ------------------------------------------------------------------------
|* NONE
+------------------------------------------------------------------------------
'''
def write_to_ntuple_tree(delphes_file, tree_chain, event, ptcl_cand, variables):
	particles = ptcl_cand.keys()
	if len(particles) > 1: sys.exit("only one ptcl species can be wrtn per evt")
	else: ptcl = list_to_string(particles)
	cand = list(ptcl_cand[ptcl])
	variables = string_to_list(variables)
	a,b,c,d = sep_vars_into_delph_calc_ptcl_evt(variables)
	ptcl_var_delphes, evt_var_delphes, ptcl_var_calc, evt_var_calc = (
	sort_separated_vars(a,b,c,d))
	
	arr_delphes_ptcl = get_ptcl_var_by_idx(event, ptcl, cand, ptcl_var_delphes)
	arr_delphes_evt = get_delphes_evt_var(event, evt_var_delphes)
	arr_calc_ptcl = calc_ptcl_var_by_idx(delphes_file, event, ptcl_cand,
	                                     ptcl_var_calc)
	arr_calc_evt = calc_evt_var(event, calc_evt_var)
	arr_all_var = concatenate_var_val_arrays(arr_delphes_ptcl, arr_delphes_evt,
	                                         arr_calc_ptcl, arr_calc_evt)
	var_data = rectangularize_jagged_array_T(arr_all_var)
	for i in range(len(var_data)):
		tree_chain[ptcl].Fill(*var_data[i,:])

