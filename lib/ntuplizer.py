# import ROOT in batch mode
import sys,os
oldargv = sys.argv[:]
import ROOT
import numpy as np
from helper import *

'''
INPUT -------------------------------------------------------------------------   |* (str) path_delphes_file: the path to the delphes file to be loaded
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

def load_delphes_file(path_delphes_file, particles):
	chain = ROOT.TChain("Delphes")
	chain.Add(path_delphes_file)
	Particles = [particle.capitalize() for particle in particles]
	Particle_pointers = [(Particle + "*") for Particle in Particles]
	for pointer in Particle_pointers: chain.SetBranchStatus(pointer, 1) 
	return chain

'''
INPUT -------------------------------------------------------------------------
|* (str) or list(str) variables: the variables to be converted to the 
|                                delphes format, must be COMMA-SEPARATED
|
ROUTINE ------------------------------------------------------------------------
|* make variables into a list of strings
|* capitalize every string
|* deal with special instances such as 'PT' instead of 'Pt' for delphes
|
OUTPUT ------------------------------------------------------------------------
|* [(str)] Variables: the delphes-formatted variables
+------------------------------------------------------------------------------
'''
def variables_to_delphes_format(variables):
	if type(variables) == str:
		variables = variables.split()
	Variables = [variable.capitalize() for variable in variables]
	for i, Variable in enumerate(Variables):
		if Variable == 'Pt' or Variable == u'Pt':
			Variables[i] = 'PT'
	return Variables

'''
INPUT -------------------------------------------------------------------------
|* (TObject) event: the delphes event object to look at
|* (str) particle: the particle type to be selected in the final state
|* (str) or list(str) variables: the variable based on which one makes the 
|                                selection.
|                                Must be COMMA-SEPARATED when passed as str
|* (str) or list(str) criteria: the criteria to select particles based on 
|                               their variable
|                               Must be COMMA-SEPARATED when passed as str
|
|ROUTINE -----------------------------------------------------------------------
|* within each event, look at the variables of a type of particles
|* according to the criteria on each varialbe, select the pair of 
|  particle from that type
|
|OUTPUT ------------------------------------------------------------------------
|* list(int) [i, j]: The indices of the selected pair of particles 
|                    if all conditions are satisfied
|* int 0: if the number of candidates is less than two, or if no pair
|         from the candidate pool satisfy all the criteria
+------------------------------------------------------------------------------
'''

def preselect_fs_lepton_pair(event, particle, variables, criteria):
	# loop over candidates to extract variable of interest
	if type(variables) == str:
		variables = variables.split(",")
	if type (criteria) == str:
		criteria = criteria.split(",")

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
		if criterium == 'leading':
			variable_col = candidates[:, i_criterium]
			i_max = []
			for i in np.arange(0, num_particle):
				i_max.append(np.argmax(variable_col))
				variable_col[np.argmax(variable_col)] = np.amin(variable_col)
		
		# select the parir of particles with highest possible value for the
		# "leading" variable, while satisfy the "opposite" criterium for
		# the other variable
		    
		for i in i_max:
			if (i in i_plus):
				for j in i_max[i:]:
					if (j in i_minus): return [i, j]
			elif (i in i_minus):
				for j in i_max[i:]:
					if (j in i_plus): return [i, j]
		return 0


'''
INPUT -------------------------------------------------------------------------
|* (str) delphes_path: the path to the delphes file to be ntuplized
|* (dict) particle_variable: the dictionary specifying which 
|         variables are to be extracted from each particle.
|         e.g. particle_variable = {"electron":["pt", "eta", "phi"]}
|
ROUTINE -----------------------------------------------------------------------
|* checks if file with that informaiton already exists
|* if yes, return message
|* if no, produce the requested ntuple file
|   # put each particle into one root TNtuple object
|   # write the root file with TNtuple objects only 
|
OUTPUT ------------------------------------------------------------------------
|* message indicating file already exist
|OR
|* a TFile with only TNtuple objects
+------------------------------------------------------------------------------
'''

def delphes_to_ntuple(path_delphes_file, particle_variable):
	load_delphes_file(path_delphes_file)
	particles = particle_variable.keys()
	delphes_file = delphes_path.split("/")[-1] # get rid of path
	delphes_file = delphes_file.split(".")[0]  # get rid of file suffix
	ntuple_path = '../ntuples/'
	ntuple_content = delphes_file + ':'
	variable_separator = '_'

	# put content info of the ntuple file into the filename
	# this is for documenting purposes as well as to avoid
	# make duplicate files
	# use a separate loop here to get the full filename first
	for particle in sorted(particles):
		variables = list(particle_variable[particle])
		ntuple_content += particle + "_" + variable_separator.join(variables)
		if particle != sorted(particles)[-1]:
			ntuple_content += "-"

	ntuple_file = ntuple_path + ntuple_content + '.root'
	if os.path.exists(ntuple_file):
		return "ntuple file:" + ntuple_file + " already exists."
	else: 
		outfile = ROOT.TFile(ntuple_file, 'CREATE')

	
	for particle in sorted(particles):
		
		# create a ROOT Ntuple tree to store all variables of desire for 
		# each particle
		variables = particle_variable[particle]
		delphes_variables = variables_to_delphes_format(variables) 
		particle_variables = [particle + '_' + variable 
							for variable in variables]
		ntuple_separator = ":"
		variables_combined = ntuple_separator.join(particle_variables)
		ntuple_tree = ROOT.TNtuple(particle, "Flat ntuple tree for " + particle,
							  variables_combined)

		# loop over events to fill the ntuple tree
		for event in chain:
			for candidate in getattr(event, particle.capitalize()):
				ntuple_tree.Fill(*[getattr(candidate, variable) 
								for variable in delphes_variables])

		
		# write the tree to file
		
		ntuple_tree.Write()
	outfile.Close()

