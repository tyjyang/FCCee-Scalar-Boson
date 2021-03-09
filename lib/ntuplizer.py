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
|* (str) particle: the particle type to be selected in the final state
|* (str) or list(str) variables: the variable based on which one makes the 
|                                selection.
|                                Must be COMMA-SEPARATED when passed as str
|* (str) or list(str) criteria: 
|  - the criteria to select particles based on their variable
|  - must be COMMA-SEPARATED when passed as str
|  - can be one of the following:
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

def preselect_fs_lepton_pair(event, particle, variables, criteria):
	# loop over candidates to extract variable of interest
	particles = to_list_of_string(particles)
	variables = to_list_of_string(variables)
	criteria = to_list_of_string(criteria)

	# check that there is a criterium for each variable
	if len(variable) == len(criteria):
		# store particle candidate's variables into a 2d array for 
		# later selection based on criteria
		candidates = []
		delphes_variables = variables_to_delphes_format(variables)
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
					           candidates[j][i_criterium})
					if new_sum > pair_sum:
						pair_sum = new_sum
						pair_indices = [i, j]
		elif (i in i_minus):
			for j in i_max[i:]:
				if (j in i_plus):
					new_sum = (candidates[i][i_criterium] + 
					           candidates[j][i_criterium})
					if new_sum > pair_sum:
						pair_sum = new_sum
						pair_indices = [i, j]
	if len(pair_indices) > 0:
		return [pair_indices, pair_sum]
	else:
		return 0

'''
INPUT -------------------------------------------------------------------------
|* (TObject) event: the delphes event object to look at
|* (float) threshold: the photon veto threshold energy
|  
ROUTINE -----------------------------------------------------------------------
|* find the energy of the most energetic photon in an event
|* discard the event if there are fs photons and 
|  the most energetic one exceeds the threshold energy
|* keep the event otherwise 
|
OUTPUT ------------------------------------------------------------------------
|* (int): 0 for discarded event; 1 for passed event 
+------------------------------------------------------------------------------ 
''' 
def photon_veto(event, threshold):
	max_photon_energy = 0
	num_of_photon = 0
	for photon in event.Photon:
		num_of_photon += 1
		if photon.E > max_photon_energy: max_photon_energy = photon.E
	if num_of_photon > 0 and max_photon_energy > threshold:
		return 0
	else:
		return 1

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
		particle_variables = [particle + '_' + variable 
		                      for variable in variables]
		column_separator = ":"
		variables_combined = column_separator.join(particle_variables)
		ntuple_tree[particle] = ROOT.TNtuple(particle, "Flat ntuple tree for " 
		                                     + particle, variables_combined)
	return ntuple_tree

'''
INPUT -------------------------------------------------------------------------
|* (TObject) event: the delphes event to look at
|* (str) particle: the particle for the ntuple tree to be filled
|* list(str) or (str) variables: the list of variables to be filled for 
|                                that particle
|                                must be COMMA-SEPARATED when passed in as (str) 
|* list(int) pair_indices
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

def write_event_to_ntuple_tree(event, particle, variables, pair_indices):
	variables = to_list_of_string(variables)
	delphes, calculated = sep_var_into_delphes_calculated(variables)
	delphes_variables = variables_to_delphes_format(delphes) 

	# select the lepton pair and fill their data to the ntuple tree
	for candidate, i_candidate in (
	enumerate(getattr(event, particle.capitalize()))):
		if i_candidate in pair_indices:
			
			ntuple_tree.Fill(*[getattr(candidate, variable) 
			                   for variable in delphes_variables])

