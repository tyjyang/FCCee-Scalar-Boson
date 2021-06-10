##############################
# Author: T. J. Yang        #
#---------------------------#
# tyjyang@mit.edu           #
#---------------------------#
# May 24, 2021              #
##############################

import sys,os
import ROOT
import numpy as np
from collections import OrderedDict

DELPHES_GEN_INFO = { #xsec in units of pb
#'eeTollS_0p5_inc.root':{'s':91**2, 'nevt':300000, 'xsec':3.348},
#'eeTollS_5_inc.root':{'s':91**2, 'nevt':300000, 'xsec':1.586},
#'eeTollS_25_inc.root':{'s':91**2, 'nevt':300000, 'xsec':2.186},
#'eeTo2fermion.root':{'s':91**2, 'nevt':1000000, 'xsec':8530},
#'four_lepton.root':{'s':91**2, 'nevt':1000000, 'xsec':3.88},
'eeZS_p5.root':{'s':91**2, 'xsec':37.42},
'eeZS_2.root':{'s':91**2, 'xsec':27.53},
'eeZS_5.root':{'s':91**2, 'xsec':17.01},
'eeZS_10.root':{'s':91**2, 'xsec':7.851},
'eeZS_15.root':{'s':91**2, 'xsec':5.751},
'eeZS_25.root':{'s':91**2, 'xsec':2.2896},
'ee2fermion_mutau.root':{'s':91**2, 'xsec':3011.7},
'ee2fermion_electron.root':{'s':91**2, 'xsec':4096.5},
'ee4lepton_mutau.root':{"s":91**2, 'xsec':3.0735},
'ee4lepton_electron.root':{'s':91**2, 'xsec':2.4868},
'ee4lepquark_mutau.root':{'s':91**2, 'xsec':1.0131},
'ee4eequark_electron.root':{'s':91**2, 'xsec':2.1187}
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
	return float(2 * np.arctan(np.exp(-1 * eta)))

'''
INPUT -------------------------------------------------------------------------
|* (float) phi1: the azimuthal angle of the first particle
|* (float) phi2: the azimuthla angle of teh second particle
|
ROUTINE -----------------------------------------------------------------------
|* calculate the opening angle in the azimuthal plane by
|  - taking the absolute difference in the two azimuthal angles
|  - define the opening angle to be always less than pi
|* calculate the acoplanarity angle by (pi - phi_{open})
|
OUTPUT ------------------------------------------------------------------------
|* (float) phi_a: the acoplanarity angle
+------------------------------------------------------------------------------
'''
def calculate_acoplanarity(phi_1, phi_2):
	return float(np.absolute(np.pi - np.absolute(phi_1 - phi_2)))

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
	return float(np.pi - np.absolute(theta_1 - theta_2))


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
	return float(w * phi_a)

'''
INPUT -------------------------------------------------------------------------
|* (float) eta
|  
ROUTINE -----------------------------------------------------------------------
|* calcualte the cosine of the forward angle
| 
OUTPUT ------------------------------------------------------------------------
|* (float) cos_theta
+------------------------------------------------------------------------------ 
''' 
def calculate_cos_theta(eta):
	theta = calculate_theta(eta)
	return float(np.cos(theta))

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
	return float((p4_1 + p4_2).M())

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
	m_rec_sq = s + m_ll ** 2 - 2 * np.sqrt(s) * E_ll
	if m_rec_sq < 0: return float(-np.sqrt(-m_rec_sq))
	else: return float(np.sqrt(m_rec_sq))

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
	return float(pt * np.cosh(eta)) 

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
def calculate_sum_momentum(pt_1, pt_2, eta_1, eta_2):
	p_mag_1 = calculate_momentum(pt_1, eta_1)
	p_mag_2 = calculate_momentum(pt_2, eta_2)
	return float(p_mag_1 + p_mag_2)

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
def calculate_charge_prod(charge_1, charge_2):
	return float(charge_1 * charge_2)

'''
INPUT -------------------------------------------------------------------------
|* (float): pseudorapidity and azimuthal angle of 2 particle tracks
|  
ROUTINE -----------------------------------------------------------------------
|* WLOG, make the 1st track pointing in (1,0,0)
|* The 2nd track then points in the direction
|  (cos_phi*sin_theta, sin_phi*sin_theta, cos_theta), where phi and theta are
|  the absolute difference between the azimuthal and forward angles
|* Use the law of cosine to get the angle between the 2 tracks
| 
OUTPUT ------------------------------------------------------------------------
|* (float) alpha_sep: the separation angle between the two tracks
+------------------------------------------------------------------------------ 
''' 
def calculate_alpha_sep(eta_1, eta_2, phi_1, phi_2):
	theta_1 = calculate_theta(eta_1)
	theta_2 = calculate_theta(eta_2)
	d_theta = np.absolute(theta_1 - theta_2)
	d_phi = np.absolute(phi_1 - phi_2)
	return float(np.arccos(np.cos(d_phi) * np.sin(d_theta)))

'''
INPUT -------------------------------------------------------------------------
|* (float) eta_p_missing: the pseudorapidity of the missing momentum, fetched
|                         from the MissingET.Eta branch in delphes.
|  
ROUTINE -----------------------------------------------------------------------
|* calculate the theta angle, then take cosine of that.
| 
OUTPUT ------------------------------------------------------------------------
|* (float) cosine of the forrward angle of the misssing momentum
+------------------------------------------------------------------------------ 
''' 
def calculate_cos_theta_p_missing(eta_p_missing):
	return float(np.cos(calculate_theta(eta_p_missing)))

CALC_VAR_FUNC_CALL = {"theta":calculate_theta,
                      "theta_a":calculate_acolinearity,
                      "phi_a":calculate_acoplanarity,
                      "alpha":calculate_mod_acoplanarity,
                      "cos_theta":calculate_cos_theta,
                      "m_inv":calculate_inv_m,
                      "m_rec":calculate_recoil_m,
                      "p_mag":calculate_momentum,
                      "sum_p_mag":calculate_sum_momentum,
                      "charge_prod":calculate_charge_prod,
                      "alpha_sep":calculate_alpha_sep,
                      "cos_theta_p_missing":calculate_cos_theta_p_missing}

CALC_VAR_FUNC_ARGS = {"theta":"eta:1",
                      "theta_a":"eta:2",
                      "phi_a":"phi:2",
                      "alpha":"eta,phi:2",
                      "cos_theta":"eta:1",
                      "m_inv":"pt,eta,phi,m:2",
                      "m_rec":"s:1-pt,eta,phi,m:2",
                      "p_mag":"pt,eta:1",
                      "sum_p_mag":"pt,eta:2", 
                      "charge_prod":"charge:2",
                      "alpha_sep":"eta,phi:2",
                      "cos_theta_p_missing":"eta_p_missing:1"}

PARTICLE_MASS = {"electron": 0.000511,
                 "muon": 0.1057}

PTCL_VAR_DELPHES_LIST = ['pt', 'eta', 'phi', 'energy', 'charge'] 
EVT_VAR_DELPHES_LIST = ['p_mag_missing','eta_p_missing']
# the location of the event variable in forms of "treename:tree_var"
EVT_VAR_DELPHES_LOCATION = {'eta_p_missing':'MissingET,eta',
                            'p_mag_missing':'MissingET,met'} 

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
		sys.exit(("string_to_list(): cannot convert an input that is "
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
		sys.exit(("list_to_string(): cannot convert an input that is"
                  " neither a single string or a list of strings"))  

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
		if Variable == 'Met':
			Variables[i] = 'MET'
	return Variables

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
	variable_separator = '-'
	particles = particle_variable.keys()
	
	for i, particle in enumerate(sorted(particles)):
		if i == len(particles) - 1: # use "-" btwn particles
			variables = string_to_list(particle_variable[particle])
			ntuple_content += particle + ':' + variable_separator.join(variables)
		else: ntuple_content += particle + "-"
			
	return ntuple_content + '.root'

'''
INPUT -------------------------------------------------------------------------
|* (str) ntuple_file_path: the ntuple filename, with or without the path
|  
ROUTINE -----------------------------------------------------------------------
|* strip off the path and var content after the ":" in the ntuple filename to
|  get the physics process
|* append the file suffix (".root") to get the original delphes file name 
|
OUTPUT ------------------------------------------------------------------------
|* (str) delphes_filename
+------------------------------------------------------------------------------ 
''' 
def get_delphes_filename(ntuple_file_path):
	ntuple = ntuple_file_path.split("/")[-1]
	ntuple = ntuple.split(":")[0]
	return ntuple + '.root'

'''
INPUT -------------------------------------------------------------------------
|* (str) delphes_filepath: the full path to the delphes file of interest 
|* (str) treename: the name of the tree to get nevt from
|  
ROUTINE -----------------------------------------------------------------------
|* get the pointer to the TFile object of the delphes file
|* use the Get() function provided by pyroot to get the tree
|* use GetEntries() on the TTree to get nevts 
| 
OUTPUT ------------------------------------------------------------------------
|* (int) number of evts
+------------------------------------------------------------------------------ 
'''
def get_num_evts(delphes_filepath, treename):
	f = ROOT.TFile.Open(delphes_filepath)
	tree = f.Get(treename)
	nevts = tree.GetEntries()
	f.Close()
	return nevts

'''
INPUT -------------------------------------------------------------------------
|* (TObject) event: the delphes event to look at
|* (str) particle: the particle name in lowercase 
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
|* (TObject) event: the delphes event to look at
|* (str) particle: the single particle of interest
|* (int) or list(int) cand: the particle cand indices
|* (str) or list(str) var: the variables of interst
|  
ROUTINE -----------------------------------------------------------------------
|* fetch the var values for particles with the given indices in a delphes event
|* we fetch one var_val per var per ptcl candidate
|
OUTPUT ------------------------------------------------------------------------
|* np.ndarray(floats): The 2D numpy array of variable values with each particle
|                      taking a col and each variable taking a row.
+------------------------------------------------------------------------------ 
''' 
def get_ptcl_var_by_idx(event, particle, cand, var):
	particle = list_to_string(particle)
	var = vars_to_delphes_form(var)
	i_cand = int_to_list(cand)
	var_val = np.empty([len(var), len(i_cand)])
	ptcl_idx = 0
	for i, cand in enumerate(getattr(event, particle.capitalize())):
		if i in i_cand:
			var_val[:, ptcl_idx] = [getattr(cand, v) for v in var]
			ptcl_idx += 1
	return var_val

'''
INPUT -------------------------------------------------------------------------
|* (TObject) event: the delphes event to look at
|* (str) or list(str) var: the event variables of interst
|  
ROUTINE -----------------------------------------------------------------------
|* look for the delphes tree and tree-variable name in order to access the
|  event variable
|* One value is obtained per event variable, an empty 2D numpy array with
|  len(var) rows and 1 col is filled with the values
|
OUTPUT ------------------------------------------------------------------------
|* np.ndarray(floats): The 2D numpy array (1 col) of evt variable values.
+------------------------------------------------------------------------------ 
''' 
def get_delphes_evt_var(event, var):
	var = string_to_list(var)
	var_val = np.empty([len(var),1])
	for i, v in enumerate(var):
		tree, tree_var = EVT_VAR_DELPHES_LOCATION[v].split(',')
		tree_var = list_to_string(vars_to_delphes_form(tree_var))
		var_val[i][0] = [getattr(data, tree_var) for data in getattr(event, tree)][0]
	return var_val

'''
INPUT -------------------------------------------------------------------------
|* (str) var_calc: the variable to be calculated from delphes vars
|  
ROUTINE -----------------------------------------------------------------------
|* fetch the value of the passed-in var_calc key in the dict CALC_VAR_FUNC_ARGS
|* separate the str of variables into var1,var2:num_ptcl entires, by -
|* convert each entry to a tuple of the format (["var1","var2"],num_ptcl)
|* return the list of tuples
| 
OUTPUT ------------------------------------------------------------------------
|* list(tuple) args: [(["var1","var2"],num_ptcl)]
+------------------------------------------------------------------------------ 
''' 
def get_args_calc_var(var_calc):
	var_calc = list_to_string(var_calc)
	args_in_str = CALC_VAR_FUNC_ARGS[var_calc]
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
|* (str) or list(str) var_calc: the single varialbe of interest
|  
ROUTINE -----------------------------------------------------------------------
|* look over all parameters it takes to calculate the variable, and get the 
|  number of ptcls these parameters come from. 
| 
OUTPUT ------------------------------------------------------------------------
|* (int) the number of ptcls it takes to calculat the variable
+------------------------------------------------------------------------------ 
'''
def get_num_ptcl_to_calc_var(var_calc):
	args = get_args_calc_var(var_calc)
	return max([arg_tuple[1] for arg_tuple in args])

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
|* Look at the N particles in the candidate list, and fetch their vars.
|  put all values of one variable before going to next one.
|  for input vars that takes n < N particles, look at the first n entries
|* if var == "m", look at the PARTICLE_MASS dict to fetch particle mass
|  if var == "s", look at DELPHES_GEN_INFO for center of mass energy^2
|
OUTPUT ------------------------------------------------------------------------
|* list(float) args: the list of args in their numerical value 
+------------------------------------------------------------------------------ 
''' 
def get_args_val(delphes_file, event, ptcl_cand, var_calc):
	args = get_args_calc_var(var_calc)
	args_val = []
	for arg_tuple in args:
		input_vars = arg_tuple[0]
		num_ptcl = arg_tuple[1]
		for var in input_vars:
			num_ptcl_checked = 0
			if var in PTCL_VAR_DELPHES_LIST:
				for ptcl in ptcl_cand.keys():
					if num_ptcl_checked == num_ptcl: break
					for i_cand, cand in enumerate(getattr(event, ptcl.capitalize())):
						if i_cand in ptcl_cand[ptcl]:
							val = get_ptcl_var_by_idx(event, ptcl, i_cand, var)
							args_val.append(*val)
							num_ptcl_checked += 1
							if num_ptcl_checked == num_ptcl: break
			elif var in EVT_VAR_DELPHES_LIST:
				val = get_delphes_evt_var(event, var)
				args_val.append(*val)
			elif var == 's':
				args_val.append(DELPHES_GEN_INFO[delphes_file][var])
			elif var == 'm':
				for ptcl in ptcl_cand.keys():
					if num_ptcl_checked == num_ptcl: break
					for cand in ptcl_cand[ptcl]:
						args_val.append(PARTICLE_MASS[ptcl])
						num_ptcl_checked += 1
						if num_ptcl_checked == num_ptcl: break
	return args_val

'''
INPUT -------------------------------------------------------------------------
|* (OrderedDict) ptcl_cand: of the format 'particle_type':[indices]. The element
|                           of the indices list has to be int.
|* list(str) or (str) var_calc: the variable based on which to get the size n
|  
ROUTINE -----------------------------------------------------------------------
|* Get the number of particles it takes to calculate the var passed in, call it N
|* Get a subset of the list by excluding the first r elements, or the remainder
|  from division on the length of the previous list by N. 
|  For the first list, r = 0 as there is no remainder from the previous list.
|* For all lists,  we do the division on the subset with the first r elements
|  excluded. The quotient is q and the remainder is r.
|* For a number of q size-n blocks within a list, we write the key-value pair.
|  Key is just the key of that list.
|* For blocks that cross two lists, we write the keys of the two lists and their
|  corresponding values.
|* Remainder of the last list is discarded.
|  
OUTPUT ------------------------------------------------------------------------
|* list(OrderedDict()): each element of the format 'ptcl_type':[indices], with
|                       len of the indices lists sum up to N
+------------------------------------------------------------------------------ 
''' 
def dvd_ptcl_cand_into_size_n(ptcl_cand, var_calc):
	ptcl_cand_list = []
	num_block_in_ptcl_cand = len(ptcl_cand.keys())
	i_block = 0
	n = get_num_ptcl_to_calc_var(var_calc)
	r = 0
	for ptcl, idx in ptcl_cand.items():
		idx = int_to_list(idx)
		if r != 0 and r + len(idx) >= n:
			x_block_piece = OrderedDict()
			x_block_piece[prev_ptcl] = idx_block[-(n - r):]
			x_block_piece[ptcl] = idx[:r]
			ptcl_cand_list.append(x_block_piece)
		idx_block = idx[r:]
		r = len(idx_block) % n
		q = len(idx_block) / n
		for i in range(q):
			b = OrderedDict([(ptcl,idx_block[i*n:(i + 1)*n])])
			ptcl_cand_list.append(b)
		if idx_block == num_block_in_ptcl_cand: break
		i_block += 1
		prev_ptcl = ptcl
	return ptcl_cand_list

'''
INPUT -------------------------------------------------------------------------
|* (str) delphes_file: the name of the delphes file containing relevant data
|* (TObject) event: the delphes event to look at
|* (OrderedDict) ptcl_cand: of the format 'particle_type':[indices]. 
|                           elements of the indices list have to be int
|* (str) or list(str) var: the variable(s) to be calculated
|                          must be COMMA-SEPARATED when passed in as str
|
ROUTINE -----------------------------------------------------------------------
|* for the candidate idx of the particle tree, loop through every var to be
|  calculated.
|* for each variable to be calculated, divide the ptcl_cand passed in into 
|  pieces of size N, where N is the number of particles it takes to calculate
|  this variable.
|* for each variable to be calculated, pass in the particle type, candidate in-
|  dices, and the variable name to get_args_val() to get the values of the args
|  needed to return the variable to be calculated. 
|* call the calculation function from the dictionary CALC_VAR_FUNC_CALL, which
|  links name of calculated variable to the corresponding function.
|* put values of one var into a list, and values of all vars into a list of lists
|
OUTPUT ------------------------------------------------------------------------
|* (np.ndarray) var_val: 2D grouped column-wise (one list == vals for one var)
+------------------------------------------------------------------------------ 
''' 
def calc_ptcl_var_by_idx(delphes_file, event, ptcl_cand, var):
	var = string_to_list(var)
	var_val = [i for i,v in enumerate(var)] # init a list with length len(var)
	for i, v in enumerate(var):
		var_val[i] = []
		ptcl_cand_list = dvd_ptcl_cand_into_size_n(ptcl_cand, v)
		for ptcl_cand_size_n in ptcl_cand_list:
			args_val = get_args_val(delphes_file, event, ptcl_cand_size_n, v)
			var_val[i].append(CALC_VAR_FUNC_CALL[v](*args_val))
	return np.array(var_val)

'''
INPUT -------------------------------------------------------------------------
|* (str) delphes_file: the name of the delphes file for fetching gen-level info
|                      to calculate vars
|* (TObject) evt: the delphes evt to look at
|* (str) or list(str) var: the variable(s) of interest
|  
ROUTINE -----------------------------------------------------------------------
|* loop through variables, for each variable:
|  - call get_args_val(), which calls get_delphes_evt_var(), which looks at
|    the delphes_evt_var_location dict for particle tree and tree var to fetch
|    the value of the variables to calculate the evt variable
|  - Use the CALC_VAR_FUNC_CALL dict to look up for function to calculate the 
|    evt variable
|  - write the calculation result to a row of a 2D numpy array, with col size
|    == 1 since evt vars only have one value
|* note that all input var to calculate evt var are themselves evt var. All
|  input var to calculate ptcl var are all ptcl vars. 
| 
OUTPUT ------------------------------------------------------------------------
|* (np.ndarray) the 2D numpy array containing vals for the calculated vars
+------------------------------------------------------------------------------ 
''' 
def calc_evt_var(delphes_file, evt, var):
	var = string_to_list(var)
	var_val = np.empty([len(var),1])
	for i, v in enumerate(var):
		args_val = get_args_val(delphes_file, evt, {"placeholder":0}, v)
		var_val[i][0] = CALC_VAR_FUNC_CALL[v](*args_val)
	return var_val

'''
INPUT -------------------------------------------------------------------------
|* (np.ndarray) arrays: 2D numpy arrays each with 1D arrays containing values 
|                       for one variable each.
|  
ROUTINE -----------------------------------------------------------------------
|* take all the 1D arrays, each corresponding to values of one var for all ptcl,
|  out of the 2D arrays.
|* put all these 1D arrays together into one 2D array
| 
OUTPUT ------------------------------------------------------------------------
|* (np.ndarray) arr: the 2D numpy array with each array containing values of one
|  var for the ptcls
+------------------------------------------------------------------------------ 
''' 
def concatenate_var_val_arrays(*arrays):
	arr = []
	for array in arrays:
		for i in array:
			arr.append(i)
	return np.array(arr)

'''
INPUT -------------------------------------------------------------------------
|* (bool) sort_each_var: the option to sort the multi_valued vars in the arrays
|                        passed in. If TRUE, sort in descending order; otherwise,
|                        keep them in then original order when they'are passed in
|* (np.ndarray) arrays: 2D numpy arrays, each made of 1D arrays containing values 
|                       for one variable.
|  
ROUTINE -----------------------------------------------------------------------
|* take all the 1D arrays, each corresponding to values of one var for all ptcl,,
|  from the 2D array passed in
|* sort each 1D array of floats in descending order 
|  OR
|  flatten the arrays by the order of elements passed in; i.e. by particle
|  idx in the delphes tree
|* put all elements of these 1D arrays together into one 1D array
| 
OUTPUT ------------------------------------------------------------------------
|* (np.ndarray) flat_arr: the 1D numpy array of flattened values for vars
+------------------------------------------------------------------------------ 
''' 
def flatten_var_val_arrays(sort_each_var, *arrays):
	flat_arr = []
	for array in arrays:
		for arr_1d in array:
			# check all array elements are floats and sort each array
			if sort_each_var:
				if all(isinstance(n, float) for n in arr_1d):
					arr_1d = sorted(arr_1d, key = float, reverse = True)
				else:
					sys.exit('no known way to sort an array with non-float elements')
			for i in arr_1d:
				flat_arr.append(i)
	return np.array(flat_arr)

'''
INPUT -------------------------------------------------------------------------
|* list(list(float)) jagged_array: an array of arrays with varied lengths
|* fill: the variable to fill the holes in the rectangularized array
|  
ROUTINE -----------------------------------------------------------------------
|* get the number of row of the rect_array from the number of vars (arrays) in
|  the jagged array; get the number of col of the rect_array from length of the
|  longest array in jagged_array.
|* loop over elements in jagged_array, which corresponds to columns in the rect
|  array. For each col, fill in the data from jagged_array in an evenly-spaced
|  fashion, and fill the gaps + ends with the variable fill (defaulted to be 
|  float("NaN"))
|* Note: the jagged array is transposed before being rectangularized
| 
OUTPUT ------------------------------------------------------------------------
|* (np.ndarray) rect_arraay: a 2D numpy array containing rectangularized data
+------------------------------------------------------------------------------ 
''' 
def rectangularize_jagged_array_T(jagged_array, fill=float("NaN")):
	num_row = max([len(col) for col in jagged_array])
	num_col = len(jagged_array)
	rect_array = np.empty([num_row, num_col])
	for i_col, col in enumerate(jagged_array):
		spacing = num_row / len(col)
		for data_idx in range(len(col)):
			rect_array[0 + data_idx * spacing][i_col] = col[data_idx]
			for fill_idx in range(spacing - 1):
				rect_array[1 + data_idx * spacing + fill_idx][i_col] = fill
		if len(col) * spacing != num_row:
			rect_array[(len(col) * spacing):,i_col] = fill
	return rect_array 
 
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
|* list(int) superset: the indices for the particle superset
|
ROUTINE -----------------------------------------------------------------------
|* from a delphes event, select a set of particle candidates from one particle
|  tree by the indices passed in from "superset". The size of this superset is N
|* from these N particles, find all subsets of size M
|* return a list of indices for these subsets
| 
OUTPUT ------------------------------------------------------------------------
|* list(tuple): the list of indices tuples
+------------------------------------------------------------------------------ 
''' 
def get_idx_candidate_sets(event, particle, subset_size, superset = "all"):
	particle = list_to_string(particle)
	if superset == "all":
		idx = []
		for i, x in enumerate(getattr(event, particle.capitalize())):
			idx.append(i)
	else:
		idx = superset
	return list(get_idx_recur(idx, subset_size))

