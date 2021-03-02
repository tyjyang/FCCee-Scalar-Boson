# import ROOT in batch mode
import sys,os
oldargv = sys.argv[:]
import ROOT
import numpy as np

'''
====================
Parameters         
====================
NONE
====================
Routine
====================
# load the local delphes lobrary into ROOT
====================
Output
====================
NONE
'''

def load_delphes():
	ROOT.gSystem.Load("libDelphes.so")
	ROOT.gInterpreter.Declare('#include "classes/DelphesClasses.h"');
	

'''
====================
Parameters
====================
* (str) or list(str) variables: the variables to be converted to the 
                                delphes format, must be COMMA-SEPARATED
====================
Routine
====================
* make variables into a list of strings
* capitalize every string
* deal with special instances such as 'PT' instead of 'Pt' for delphes
====================
Output
====================
* [(str)] Variables: the delphes-formatted variables
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
====================
Parameters
====================
* (float) eta: the pseudorapidity
====================
Routine
====================
* calculate the forward angle theta 
====================
Output
====================
* (float) theta: the forward angle 
'''
def calculate_theta(eta):
	return 2 * np.arctan(np.exp(-1 * eta))

'''
====================
Parameters
====================
* (float) phi1: the azimuthal angle of the first particle
* (float) phi2: the azimuthla angle of teh second particle
====================
Routine
====================
* calculate the acoplanarity angle betwen the 2 particles
====================
Output
====================
* (float) phi_a: the acoplanarity angle
'''
def calculate_acoplanarity(phi1, phi2):
	return np.pi - np.absolute(phi1 - phi2)

'''
====================
Parameters
====================
* (float) theta1: the forward angle of the first particle
* (float) theta2: the forward angle of the second particle
====================
Routine
====================
* calculate the acolinearity angle betwen the 2 particles
====================
Output
====================
* (float) theta_a: the acolinearity angle
'''
def calculate_acolinearity(theta1, theta2):
	return np.pi - np.absolute(theta1 - theta2)

'''
====================
Parameters
====================
* (float) pt: the transverse momentum of the particle
* (float) eta: the pseudorapidity of the particle
* (float) phi: the azimuthal angle of the particle
* (float) m: the mass of the particle
====================
Routine
====================
* store the 4-momentum of a particle into a ROOT.TLorentzVector object
====================
Output
====================
* (ROOT.TLorentzVector) p4: the 4-momentum in PtEtaPhiM
'''

def to_pt_eta_phi_m(pt, eta, phi, m):
	p4 = ROOT.TLorentzVector(0,0,0,0)
	p4.SetPtEtaPhiM(pt, eta, phi, m)
	return p4

'''
====================
Parameters
====================
* (ROOT.TLorentzVector) p4_1: the 4-momentum of the first particle in 
                              (pt, eta, phi, m)
* (ROOT.TLorentzVector) p4_2: the 4-momentum of the second particle in 
                              (pt, eta, phi, m)
====================
Routine
====================
* add up the 2 4-momenta and get mass by .M() 
====================
Output
====================
* (float) inv_m: the invariant mass
'''
def calculate_inv_m(p4_1, p4_2):
	return (p4_1 + p4_2).M()

'''
====================
Parameters
====================
* (float) 
* (float) theta1: the forward angle of the first particle
* (float) theta2: the forward angle of the second particle
====================
Routine
====================
* calculate the acolinearity angle betwen the 2 particles
====================
Output
====================
* (float) theta_a: the acolinearity angle
'''
def calculate_recoil_m(s, p4_1, p4_2):
	return np.pi - np.absolute(theta1 - theta2)

'''
====================
Parameters
====================
* (TObject) event: the delphes event object to look at
* (str) particle: the particle type to be selected in the final state
* (str) or list(str) variables: the variable based on which one makes the 
                                selection.
                                Must be COMMA-SEPARATED when passed as str
* (str) or list(str) criteria: the criteria to select particles based on 
                               their variable
                               Must be COMMA-SEPARATED when passed as str
====================
Routine
====================
* within each event, look at the variables of a type of particles
* according to the criteria on each varialbe, select the pair of 
  particle from that type
====================
Output
====================
* list(int) [i, j]: The indices of the selected pair of particles 
                    if all conditions are satisfied
* int 0: if the number of candidates is less than two, or if no pair
         from the candidate pool satisfy all the criteria
'''

def select_fs_particle_pair(event, particle, variables, criteria):
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
		for i_candidate, candidate in 
		enumerate(getattr(event, particle.capitalize())):
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
====================
Parameters
====================
* (str) delphes_path: the path to the delphes file to be ntuplized
* (dict) particle_variable: the dictionary specifying which 
		 variables are to be extracted from each particle.
		 e.g. particle_variable = {"electron":["pt", "eta", "phi"]}
====================
Routine
====================
# checks if file with that informaiton already exists
#- if yes, return message
#- if no, produce the requested ntuple file
	# put each particle into one root TNtuple object
	# write the root file with TNtuple objects only 
====================
Output
====================
# message indicating file already exist
OR
# a TFile with only TNtuple objects
'''

def delphes_to_ntuple(delphes_path, particle_variable):
	chain = ROOT.TChain("Delphes")
	chain.Add(delphes_path)
	particles = particle_variable.keys()
	Particles = [particle.capitalize() for particle in particles]
	Particle_pointers = [(Particle + "*") for Particle in Particles]
	for pointer in Particle_pointers: chain.SetBranchStatus(pointer, 1) 
	
	delphes_file = delphes_path.split("/")[-1]
	delphes_file = delphes_file.split(",")[0]
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

