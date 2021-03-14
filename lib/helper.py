import sys,os
import ROOT
import numpy as np

calc_var_func_call = {"theta":calculate_theta,
                      "phi_a":calculate_acoplanarity,
                      "alpha":calculate_mod_acoplanarity,
                      "cos_theta":calculate_cos_theta;
                      "m_inv":calculate_inv_m,
                      "m_rec":calculate_recoil_m}

calc_var_func_args = {"theta":"eta",
                      "phi_a":"phi",
                      "alpha":"eta,phi:2",
                      "cos_theta":calculate_cos_theta;
                      "m_inv":calculate_inv_m,
                      "m_rec":calculate_recoil_m}

particle_mass = {"electron": 0.000511
                 "muon": 0.1057}

delphes_var_list = ['pt', 'eta', 'phi', 'energy', 'charge']

'''
INPUT -------------------------------------------------------------------------
|* (str) string: the string to be converted to list
|
ROUTINE -----------------------------------------------------------------------
|* converts a string to a string element in a list
|  - if not comma-separated, then the whole string becomes one single element
OUTPUT ------------------------------------------------------------------------
|* (float) string: the list-lized string
+------------------------------------------------------------------------------
'''
def to_list_of_string(string):
	if type(string) == str:
		string = string.split(",") # items have to be comma-separated 
		return string
	elif type(string) == list:
		return string
	else:
		sys.exit(("to_list_of_string(string): cannot convert an inpit that is"
                  "neither a single string or a list of strings"))  

'''
INPUT -------------------------------------------------------------------------
|* (str) or list(str) variables: the list of variables of interest in lowercase
|                                must be COMMA-SEPARATED when passed in as str
|  
ROUTINE -----------------------------------------------------------------------
|* select out the variables that can be found in delphes, pu them into list(str)
|* put the rest into another list(str)
| 
OUTPUT ------------------------------------------------------------------------
|* list(str) delphes_variables: the list of variables already in delphes
|* list(str) calc_variables: the list of variables need to be calculated
+------------------------------------------------------------------------------ 
''' 
def sep_var_into_delphes_calculated(variables):
	variables = to_list_of_string(variables)
	delphes_variable_list = ["pt", "eta", "phi", "charge", "energy"] 
	delphes_variables = []
	calc_variables = []
	for variable in variables:
		if (variable in delphes_variable_list):
			delphes_variables.append(variable)
		else:
			calc_variables.append(variable)
	return delphes_variables, calc_variables

'''
INPUT -------------------------------------------------------------------------
|* (str) or list(str) variables: the lowercase variables to be converted to the 
|                                delphes format, must be COMMA-SEPARATED
|                                and contained in the delphes sample
|
ROUTINE -----------------------------------------------------------------------
|* make variables into a list of strings
|* capitalize every string
|* deal with special instances such as 'PT' instead of 'Pt' for delphes
|
OUTPUT ------------------------------------------------------------------------
|* list(str) Variables: the delphes-formatted variables
+------------------------------------------------------------------------------
'''
def variables_to_delphes_format(variables):
	variables = to_list_of_string(variables)
	Variables = [variable.capitalize() for variable in variables]
	for i, Variable in enumerate(Variables):
		if Variable == 'Pt' or Variable == u'Pt':
			Variables[i] = 'PT'
		if Variable == 'Energy':
			Variables[i] = 'E'
	return Variables

'''
INPUT -------------------------------------------------------------------------
|* list(str) delphes_var: the delphes variables
|* list(str) calc_var: the variables to be calculated from delphes variables
|  
ROUTINE -----------------------------------------------------------------------
|* sort the two lists of strings, then combine the sorted two lists, with  
|  the delphes variables before the calculated variables
| 
OUTPUT ------------------------------------------------------------------------
|* list(str) the sorted variables 
+------------------------------------------------------------------------------ 
''' 
def sort_delphes_and_calc_var(delphes_var, calc_var):
	delphes_var = sorted(delphes_var)
	calc_var = sorted(calc_var)
	return delphes_var + calc_var

'''
INPUT -------------------------------------------------------------------------
|* (str) delphes_file_path: the full absolute path to the delphes file
|* (dict) particle_variable: particles are in the keys, with values of 
|                            their corresponding variables in an array
|                            of strings. e.g. {"electron":["pt", "eta", "phi"]}  
ROUTINE -----------------------------------------------------------------------
|* get rid of everything before the last "/" and the file suffix
|* append the ntuple column content after the delphes file name 
|* in format ":particle1_var1_var2-particle2_var1_var2"
|* 
OUTPUT ------------------------------------------------------------------------
|* (str) the full filename of the ntuple file
+------------------------------------------------------------------------------ 
''' 
def get_ntuple_filename(delphes_file_path, particle_variable):
	delphes_file = delphes_path.split("/")[-1] # get rid of path
	delphes_file = delphes_file.split(".")[0]  # get rid of file suffix
	ntuple_content = delphes_file + ':'
	variable_separator = '_'
	particles = particle_variable.keys()

	for particle in sorted(particles):
		variables = list(particle_variable[particle])
		ntuple_content += particle + "_" + variable_separator.join(variables)
		if particle != sorted(particles)[-1]: # use "-" btwn particles
			ntuple_content += "-"

	return ntuple_content + '.root'

'''
INPUT -------------------------------------------------------------------------
|* (float) eta: the pseudorapidity
|
ROUTINE -----------------------------------------------------------------------
|* calculate the exponential of the negative pseudorapidity
|* take the arctan of the result, and double that to get the forward angle 
|
OUTPUT ------------------------------------------------------------------------
|* (float) theta: the forward angle 
+------------------------------------------------------------------------------
'''
def calculate_theta(eta):
	return 2 * np.arctan(np.exp(-1 * eta))

'''
INPUT -------------------------------------------------------------------------
|* (float) phi1: the azimuthal angle of the first particle
|* (float) phi2: the azimuthla angle of teh second particle
|
ROUTINE -----------------------------------------------------------------------
|* calculate the acoplanarity angle betwen the 2 particles
|
OUTPUT ------------------------------------------------------------------------
|* (float) phi_a: the acoplanarity angle
+------------------------------------------------------------------------------
'''
def calculate_acoplanarity(phi_1, phi_2):
	return np.pi - np.absolute(phi_1 - phi_2)

''' 
INPUT -------------------------------------------------------------------------
|* (float) eta_1: the pseudorapidity of the first particle
|* (float) eta_2: the pseudorapidity of the second particle
|
ROUTINE -----------------------------------------------------------------------
|* calculate the forward angle 
|* calculate the acolinearity angle 
|
OUTPUT ------------------------------------------------------------------------
|* (float) theta_a: the acolinearity angle
+------------------------------------------------------------------------------
'''
def calculate_acolinearity(eta_1, eta_2):
	theta_1 = calculate_theta(eta_1)
	theta_2 = calculate_theta(eta_2)
	return np.pi - np.absolute(theta_1 - theta_2)


'''
INPUT -------------------------------------------------------------------------
|* (float) eta_1: the pseudorapidity of the first particle
|* (float) eta_2: the pseudorapodity of the second particle
|* (float) phi_1: the azimuthal angle of the first particle
|* (float) phi_2: the azimuthal angle of the second particle
ROUTINE -----------------------------------------------------------------------
|* calculate the forward angles
|* take the average of the sin(theta) of the 2 leptons
|* call calculate_acoplanarity(), and weigh it by the average of the sins
| 
OUTPUT ------------------------------------------------------------------------
|* (float) the modified acoplanarity
+------------------------------------------------------------------------------ 
''' 
def calculate_mod_acoplanarity(eta_1, eta_2, phi_1, phi_2):
	theta_1 = calculate_theta(eta_1)
	theta_2 = calculate_theta(eta_2)
	w = 0.5 * (np.sin(theta_1) + np.sin(theta_2))
	phi_a = calculate_acoplanarity(phi_1, phi_2)
	return w * phi_a

'''
INPUT -------------------------------------------------------------------------
|* (float) pt: the transverse momentum of the particle
|* (float) eta: the pseudorapidity of the particle
|* (float) phi: the azimuthal angle of the particle
|* (float) m: the mass of the particle
|
ROUTINE -----------------------------------------------------------------------
|* store the 4-momentum of a particle into a ROOT.TLorentzVector object 
|  with format (pt, eta, phi, m)
|
OUTPUT ------------------------------------------------------------------------
|* (ROOT.TLorentzVector) p4: the 4-momentum in PtEtaPhiM
+------------------------------------------------------------------------------
'''
def to_TLorentzVector(pt, eta, phi, m):
	p4 = ROOT.TLorentzVector(0,0,0,0)
	p4.SetPtEtaPhiM(pt, eta, phi, m)
	return p4

'''
INPUT -------------------------------------------------------------------------
|* (float) pt_1, eta_1, phi_1, m_1: the kinematic variables for the 1st particle 
|* (float) pt_2, eta_2, phi_2, m_2: the kinematic variables for the 2nd particle 
|
ROUTINE -----------------------------------------------------------------------
|* convert the inputs to (ROOT.TLorentzVector) for the two particles
|* add up the 2 4-momenta and get mass by .M() 
|
OUTPUT ------------------------------------------------------------------------
|* (float) inv_m: the invariant mass
+------------------------------------------------------------------------------
'''
def calculate_inv_m(pt_1, pt_2, eta_1, eta_2, phi_1, phi_2, m_1, m_2):
	p4_1 = to_TLorentzVector(pt_1, eta_1, phi_1, m_1)
	p4_2 = to_TLorentzVector(pt_2, eta_2, phi_2, m_2)
	return (p4_1 + p4_2).M()

'''
INPUT -------------------------------------------------------------------------
|* (float) s: the square of the COM energy
|* (float) pt_1, eta_1, phi_1, m_1: the kinematic variables for the 1st particle 
|* (float) pt_2, eta_2, phi_2, m_2: the kinematic variables for the 2nd particle 
|
ROUTINE -----------------------------------------------------------------------
|* add the two p4 up
|* calculate the m_rec squared using s, and m and E of the di-particle system
|* if m_rec >= 0, take sqrt 
|* if m_rec < 0, take negative of sqrt(-m_rec^2)
|
OUTPUT ------------------------------------------------------------------------
|* (float) the mass of the recoiling particle
+------------------------------------------------------------------------------
'''
def calculate_recoil_m(s, pt_1, pt_2, eta_1, eta_2, phi_1, phi_2, m_1, m_2):
	p4_1 = to_TLorentzVector(pt_1, eta_1, phi_1, m_1)
	p4_2 = to_TLorentzVector(pt_2, eta_2, phi_2, m_2)
	p4_sum = p4_1 + p4_2
	E_ll = p4_sum.E()
	m_ll = p4_sum.M()
	m_rec_sq = s + m_ll ^ 2 - 2 * np.sqrt(s) * E_ll
	if m_rec_sq < 0: return -np.sqrt(-m_rec_sq)
	else: return np.sqrt(m_rec_sq)

'''
INPUT -------------------------------------------------------------------------
|* (str) particle
|* (dict) delphes_var_dict
|* (dict) calc_var_dict
|* (np.array) var_data
|  
ROUTINE -----------------------------------------------------------------------
|* create an empty array with dim [2,num_var] to store data
|* using delphes_var_dict and calc_var_dict to call calculating functions
| 
OUTPUT ------------------------------------------------------------------------
|* 
+------------------------------------------------------------------------------ 
'''

'''
INPUT -------------------------------------------------------------------------
|* (TObject) event: the delphes event to look at
|* (str) particle: the particle of interst in the event.
|* (str) or list(str): the variables of 
ROUTINE -----------------------------------------------------------------------
|* 
| 
OUTPUT ------------------------------------------------------------------------
|* 
+------------------------------------------------------------------------------ 
''' 
def calc_var(event, particle, var, *candidate):
	

