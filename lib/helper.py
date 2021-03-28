import sys,os
import ROOT
import numpy as np

delphes_gen_info = {
'eeTollS_0p5_inc.root':{'s':91, 'nevt':300000, 'xsec':3.348},
'eeTollS_5_inc.root':{'s':91, 'nevt':300000, 'xsec':1.586},
'eeTollS_25_inc.root':{'s':91, 'nevt':300000, 'xsec':2.186},
'eeTo2fermion.root':{'s':91, 'nevt':1000000, 'xsec':8530},
'four_lepton.root':{'s':91, 'nevt':1000000, 'xsec':3.88}
}

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
|* (float) theta
|  
ROUTINE -----------------------------------------------------------------------
|* calcualte the cosine of the forward angle
| 
OUTPUT ------------------------------------------------------------------------
|* (float) cos_theta
+------------------------------------------------------------------------------ 
''' 
def calculate_cos_theta(theta):
	return np.cos(theta)

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
	m_rec_sq = s + m_ll ** 2 - 2 * np.sqrt(s) * E_ll
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
def calculate_momentum(pt, eta):
	return pt * np.cosh(eta) 

'''
INPUT -------------------------------------------------------------------------
|*(float) pt1, eta1, pt2, eta2
|  
ROUTINE -----------------------------------------------------------------------
|* get the sum of the momentum of 2 particles
| 
OUTPUT ------------------------------------------------------------------------
|* (float) sum_p
+------------------------------------------------------------------------------ 
'''
def calculate_sum_momentum(pt1, eta1, pt2, eta2):
	p_mag_1 = calculate_momentum(pt1, eta1)
	p_mag_2 = calculate_momentum(pt2, eta2)
	return p_mag_1 + p_mag_2

'''
INPUT -------------------------------------------------------------------------
|* (float) charge1, charge2: the electric charge of the 2 ptcls
|  
ROUTINE -----------------------------------------------------------------------
|* calculate the product of the charges
| 
OUTPUT ------------------------------------------------------------------------
|* (float) charge_prod: the product of the charges
+------------------------------------------------------------------------------ 
''' 
def calculate_charge_prod(charge1, charge2):
	return charge1 * charge2

calc_var_func_call = {"theta":calculate_theta,
                      "phi_a":calculate_acoplanarity,
                      "alpha":calculate_mod_acoplanarity,
                      "cos_theta":calculate_cos_theta,
                      "m_inv":calculate_inv_m,
                      "m_rec":calculate_recoil_m,
                      "p_mag":calculate_momentum,
                      "sum_p_mag":calculate_sum_momentum,
                      "charge_prod":calculate_charge_prod}

calc_var_func_args = {"theta":"eta:1",
                      "phi_a":"phi:2",
                      "alpha":"eta,phi:2",
                      "cos_theta":"eta:1",
                      "m_inv":"pt,eta,phi,m:2",
                      "m_rec":"s:1-pt,eta,phi,m:2",
                      "p_mag":"pt,eta:1",
                      "sum_p_mag":"pt,eta:2",
                      "charge_prod":"charge:2"}

particle_mass = {"electron": 0.000511,
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
def string_to_list(string):
	if type(string) == str:
		string = string.split(",") # items have to be comma-separated 
		return string
	elif type(string) == list:
		return string
	else:
		sys.exit(("string_to_list(): cannot convert an inpit that is"
                  "neither a single string or a list of strings"))  

'''
INPUT -------------------------------------------------------------------------
|* list(str): a list of strings
|  
ROUTINE -----------------------------------------------------------------------
|* convert the list of string to a single string by join()
| 
OUTPUT ------------------------------------------------------------------------
|* (str): the resulted string
+------------------------------------------------------------------------------ 
''' 
def list_to_string(list_str):
	if type(list_str) == str:
		return list_str
	elif type(list_str) == list:
		string = ""
		return string.join(list_str)
	else:
		sys.exit(("list_to_string(): cannot convert an inpit that is"
                  "neither a single string or a list of strings"))  

'''
INPUT -------------------------------------------------------------------------
|* (int) integer 
|  
ROUTINE -----------------------------------------------------------------------
|* converts a single integer to an element in a list
| 
OUTPUT ------------------------------------------------------------------------
|* (list)
+------------------------------------------------------------------------------ 
''' 
def int_to_list(integer):
	if (type(integer) == list or type(integer) == np.ndarray
	    or type(integer) == tuple):
		return integer
	elif type(integer) == int:
		return [integer]
	else:
		sys.exit(("int_to_list(): cannot convert an input that is "
                  "neither a single integer or a list")) 

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
	variables = string_to_list(variables)
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
	variables = string_to_list(variables)
	
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
	delphes_file = delphes_file_path.split("/")[-1] # get rid of path
	delphes_file = delphes_file.split(".")[0]  # get rid of file suffix
	ntuple_content = delphes_file + ':'
	variable_separator = '_'
	particles = particle_variable.keys()

	for i, particle in enumerate(sorted(particles)):
		ntuple_content += particle + "-"
		if i == len(particles) - 1: # use "-" btwn particles
			variables = string_to_list(particle_variable[particle])
			ntuple_content += "_" + variable_separator.join(variables)

	return ntuple_content + '.root'

'''
INPUT -------------------------------------------------------------------------
|* (str) var_calc: the variable to be calculated from delphes vars
|  
ROUTINE -----------------------------------------------------------------------
|* fetch the value of the passed-in var_calc key in the dict calc_var_func_args
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
		var = string_to_list(var)
		num_ptcl = int(num_ptcl)
		args.append((var,num_ptcl)) 
	return args

'''
INPUT -------------------------------------------------------------------------
|* (TObject) event: the delphes event to look at 
|* (str) ptcl: the single particle of interst
|* (int) or list(int) cand: the list of indices for particle candidates
|                           the length of the list should be equal to the
|                           max of num_ptcl in the args_tuple
|* (str) var_calc: the single variable to be calculated
|
ROUTINE -----------------------------------------------------------------------
|* call get_args_calc_var() to convert args need for var_calac to list of tuples
|* for each element of the tuple, look at the 2nd element, which is the num of
|  particles (N) the variables in the 1st element takes.
|* Look at the first N particles in the candidate list, and fetch their vars
|  put all vars of one particle before going to next one 
|* if var == "m", look at the particle_mass dict to fetch particle mass
|  if var == "s", look at consts dict to fetch center of mass energy^2
|
OUTPUT ------------------------------------------------------------------------
|* list(float) args: the list of args in their numerical value 
+------------------------------------------------------------------------------ 
''' 
def get_args_val(delphes_file, event, ptcl, cand_ind, var_calc):
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
						var = list_to_string(vars_to_delphes_form(var))
						args_val.append(getattr(cand, var))
					if var == 's':
						args_val.append(delphes_gen_info[delphes_file][var])
					if var == 'm':
						args_val.append(particle_mass[ptcl])
			if num_ptcl_checked == num_ptcl: break
	return args_val

'''
INPUT -------------------------------------------------------------------------
|* (TObject) event: the delphes event to look at
|* (str) ptcl: the particle of interest
|* list(int) or (int) cand: the indices for the candidate set
|* (str) or list(str) var: the variable(s) of interest. 
|                          must be COMMA-SEPARATED when passed in as str
|
ROUTINE -----------------------------------------------------------------------
|* for the candidate idx of the particle tree, loop through every var to be
|  calculated.
|* for each variable to be calculated, pass in the particle type, candidate in-
|  dices, and the variable name to get_args_val() to get the values of the args
|  needed to return the variable to be calculated. 
|* call the calculation function from the dictionary calc_var_func_call, which
|  links name of calculated variable to the corresponding function.
|* Note that if the var to be calculated only takes in N particles, and the 
|  number of ptcl exceeds N in the cand idx list passed in, then this function
|  will only look at the FIRST N ptcl for calculation of the var.  
|
OUTPUT ------------------------------------------------------------------------
|* lsit(float) var_val
+------------------------------------------------------------------------------ 
''' 
def calc_ptcl_var_by_idx(delphes_file, event, ptcl, cand, var):
	ptcl = list_to_string(ptcl)
	cand = int_to_list(cand)
	var = string_to_list(var)
	var_val = []
	for v in var:
		args_val = get_args_val(delphes_file, event, ptcl, cand, v)
		var_val.append(calc_var_func_call[v](*args_val))
	return var_val

'''
INPUT -------------------------------------------------------------------------
|* (TObject) event: the delphes event to look at
|* (str) particle: the single particle of interest
|* (int) or list(int) cand: the particle cand indices
|* (str) var: the single variable of interst
|  
ROUTINE -----------------------------------------------------------------------
|* fetch the var values for particles with the given indices in a delphes event
|* we fetch one var_val per var per ptcl, as opposed to calc_ptcl_var_by_ind(),
|  where we only return one var_val per var per cand group  
|
OUTPUT ------------------------------------------------------------------------
|* list(float): the var values
+------------------------------------------------------------------------------ 
''' 
def get_ptcl_var_by_idx(event, particle, cand, var):
	particle = list_to_string(particle)
	var = vars_to_delphes_form(var)
	cand = int_to_list(cand)
	var_val = np.empty([len(cand), len(var)])
	row_num = 0
	for i, ptcl in enumerate(getattr(event, particle.capitalize())):
		if i in cand:
			var_val[row_num,:] = [getattr(ptcl, v) for v in var]
			row_num += 1
	return var_val

'''
INPUT -------------------------------------------------------------------------
|* list(int) idx: the array of indices [0,1,2,3...N-1]
|* (int) subset_size: the size of the set to be chosen from the N elements
|  
ROUTINE -----------------------------------------------------------------------
|* From an array of size N, select all subsets of size M recursively
| 
OUTPUT ------------------------------------------------------------------------
|* (tuple) set indices
|  returned by yield, remember to use list(get_idx_candidate_sets()) when call  
+------------------------------------------------------------------------------ 
''' 
def get_idx_recur(idx, subset_size):
	for i in xrange(len(idx)):
		if subset_size == 1:
			yield (idx[i],)
		else:
			for next in get_idx_recur(idx[i+1:len(idx)], subset_size-1):
				yield (idx[i],) + next

'''
INPUT -------------------------------------------------------------------------
|* (TObject) event: the delphes event to look at
|* (str) particle: the particle tree of interest
|* (int) subset_size: the size of the candidate set 
|
ROUTINE -----------------------------------------------------------------------
|* from a delphes event, extract the number of particle X, denote as N
|* from these N particles, find all subsets of M particles
|* return a list of indices for particle subsets
| 
OUTPUT ------------------------------------------------------------------------
|* list(tuple): the list of indices tuples
+------------------------------------------------------------------------------ 
''' 
def get_idx_candidate_sets(event, particle, subset_size):
	particle = list_to_string(particle)
	idx = []
	for i, x in enumerate(getattr(event, particle.capitalize())):
		idx.append(i)
	return list(get_idx_recur(idx, subset_size))

