import sys,os
import ROOT
import numpy as np

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
def calculate_mod_acoplanarity(eta_1, phi_1, eta_2, phi_2):
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
def calculate_inv_m(pt_1, eta_1, phi_1, m_1, pt_2, eta_2, phi_2, m_2):
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
def calculate_recoil_m(s, pt_1, eta_1, phi_1, m_1, pt_2, eta_2, phi_2, m_2):
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
|* (float) pt
|* (float) eta
|  
ROUTINE -----------------------------------------------------------------------
|* calculate the magnitude of the 3-momentum
| 
OUTPUT ------------------------------------------------------------------------
|* (float): the magnitude of the 3-momentum
+------------------------------------------------------------------------------ 
'''
def calculate_mag_momentum(pt, eta):
	return pt*np.cosh(eta) 

calc_var_func_call = {"theta":calculate_theta,
                      "phi_a":calculate_acoplanarity,
                      "alpha":calculate_mod_acoplanarity,
                      "cos_theta":calculate_cos_theta;
                      "m_inv":calculate_inv_m,
                      "m_rec":calculate_recoil_m,
                      "p_mag":calculate_mag_momentum}

calc_var_func_args = {"theta":"eta:1",
                      "phi_a":"phi:2",
                      "alpha":"eta,phi:2",
                      "cos_theta":"eta:1",
                      "m_inv":"pt,eta,phi,m:2",
                      "m_rec":"s:0-pt,eta,phi,m:2",
                      "p_mag":"pt,eta:1"}

particle_mass = {"electron": 0.000511
                 "muon": 0.1057}

delphes_variable_list = ['pt', 'eta', 'phi', 'energy', 'charge']

consts = {"s":91**2}

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
def vars_to_delphes_form(variables):
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
|* (str) var_calc: the variable to be calculated from delphes vars
|  
ROUTINE -----------------------------------------------------------------------
|* fetch the value for the var_calc key in the dict calc_var_func_args
|* separate the str of variables into var1,var2:num_ptcl entires, by -
|* convert each entry to a tuple of the format (["var1","var2"],num_ptcl)
|* return the list of tuples
| 
OUTPUT ------------------------------------------------------------------------
|* list(tuple) args: [(["var1","var2"],num_ptcl)]
+------------------------------------------------------------------------------ 
''' 
def get_args_calc_var(var_calc):
	args_in_str = calc_var_func_args[var_calc]
	args_in_list = args_in_str.split("-")
	args = []
	for entry in args_in_list:
		var, num_ptcl = entry.split(":")
		var = to_list_of_string(var)
		num_ptcl = int(num_ptcl)
		args.append((var,num_ptcl)) 
	return args


'''
INPUT -------------------------------------------------------------------------
|* (TObject) event: the delphes event to look at 
|* (str) ptcl: the single particle of interst
|* (int) or list(int) cand: the list of indices for particle candidates
|* (str) var_calc: the single variable to be calculated
|
ROUTINE -----------------------------------------------------------------------
|* call get_args_calc_var() to convert args need for var_calac to list of tuples
|* for each element of the tuple, look at the 2nd element, which is the num of
|  particles the variables in the 1st element takes.
|* Look at the first N particles in the candidate list, and fetch their vars
|  put all vars of one particle before going to next var 
|* if var == "m", look at the particle_mass dict to fetch particle mass
|  if var == "s", look at consts dict to fetch center of mass energy^2
|
OUTPUT ------------------------------------------------------------------------
|* list(float) args: the list of args in their numerical value 
+------------------------------------------------------------------------------ 
''' 
def get_args_val(event, ptcl, cand_ind, var_calc):
	args = get_args_calc_var(var_calc)
	args_val = []
	for arg_tuple in args:
		input_vars = arg_tuple[0]
		num_ptcl = arg_tuple[1]
		num_ptcl_checked = 0
		for i_cand, cand in enumerate(getattr(event, ptcl.capitalize())):
			if i_cand in cand_ind:
				num_ptcl_checked += 1
				for var in input_vars:
					if var in delphes_variable_list:
						var = vars_to_delphes_form(var)
						args_val.append(cand.var)
					if var == 's':
						args_val.append(consts[var])
					if var == 'm':
						args_val.append(particle_mass[ptcl])
			if num_ptcl_checked == num_ptcl: break
	return args_val

'''
INPUT -------------------------------------------------------------------------
|* (TObject) event: the delphes event to look at
|* (dict) ptcl_cands: keys are the particle of interst in the event.
|                     values are the indices of candidates grouped in lists
|                     	e.g. for calculating a var that takes in 2 particles,
|                     	the candidate pairs should be: [[i_1,j_1], [i_2,j_2]] 
|                     each element in the cand list is used to get the set of
|                     ptcl cand to calc var
|* (str) or list(str) var: the variable(s) of interest. 
|                          must be COMMA-SEPARATED when passed in as str
|                          same var(s) for all particles passed in
|
ROUTINE -----------------------------------------------------------------------
|* 
| 
OUTPUT ------------------------------------------------------------------------
|* 
+------------------------------------------------------------------------------ 
''' 
def calc_var(event, ptcl_cands, var):
	var = to_list_of_string(var)
	for ptcl, cand_inds in ptcl_cand.items():
		for cand_ind in cand_inds:
			var_val = []
			for v in var:
				args_val = get_args_val(event, ptcl, cand_ind, v)
				var_val.append(calc_var_func_call[v](*args_val))
			result[ptcl].append(var_val)





