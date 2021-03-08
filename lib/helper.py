import sys,os
import ROOT
import numpy as np

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
def calculate_acoplanarity(phi1, phi2):
	return np.pi - np.absolute(phi1 - phi2)

''' 
INPUT -------------------------------------------------------------------------
|* (float) theta1: the forward angle of the first particle
|* (float) theta2: the forward angle of the second particle
|
ROUTINE -----------------------------------------------------------------------
|* calculate the acolinearity angle betwen the 2 particles
|
OUTPUT ------------------------------------------------------------------------
|* (float) theta_a: the acolinearity angle
+------------------------------------------------------------------------------
'''
def calculate_acolinearity(theta1, theta2):
	return np.pi - np.absolute(theta1 - theta2)

'''
INPUT -------------------------------------------------------------------------
|* (float) pt: the transverse momentum of the particle
|* (float) eta: the pseudorapidity of the particle
|* (float) phi: the azimuthal angle of the particle
|* (float) m: the mass of the particle
|
ROUTINE -----------------------------------------------------------------------
|* store the 4-momentum of a particle into a ROOT.TLorentzVector object
|
OUTPUT ------------------------------------------------------------------------
|* (ROOT.TLorentzVector) p4: the 4-momentum in PtEtaPhiM
+------------------------------------------------------------------------------
'''
def to_pt_eta_phi_m(pt, eta, phi, m):
	p4 = ROOT.TLorentzVector(0,0,0,0)
	p4.SetPtEtaPhiM(pt, eta, phi, m)
	return p4

'''
INPUT -------------------------------------------------------------------------
|* (ROOT.TLorentzVector) p4_1: the 4-momentum of the first particle in 
|                              (pt, eta, phi, m)
|* (ROOT.TLorentzVector) p4_2: the 4-momentum of the second particle in 
|                              (pt, eta, phi, m)
|
ROUTINE -----------------------------------------------------------------------
|* add up the 2 4-momenta and get mass by .M() 
|
OUTPUT ------------------------------------------------------------------------
|* (float) inv_m: the invariant mass
+------------------------------------------------------------------------------
'''
def calculate_inv_m(p4_1, p4_2):
	return (p4_1 + p4_2).M()

'''
INPUT -------------------------------------------------------------------------
|* (float) 
|* (float) theta1: the forward angle of the first particle
|* (float) theta2: the forward angle of the second particle
|
ROUTINE -----------------------------------------------------------------------
|* calculate the acolinearity angle betwen the 2 particles
|
OUTPUT ------------------------------------------------------------------------
|* (float) theta_a: the acolinearity angle
+------------------------------------------------------------------------------
'''
def calculate_recoil_m(s, p4_1, p4_2):
	return np.pi - np.absolute(theta1 - theta2)

'''
INPUT -------------------------------------------------------------------------
|* (str) string: the string to be converted to list
|
ROUTINE -----------------------------------------------------------------------
|* converts a string to a string element in a list
|
OUTPUT ------------------------------------------------------------------------
|* (float) string: the list-lized string
+------------------------------------------------------------------------------
'''

def to_list_of_string(string):
	if type(string) == str:
		string = string.split(",") # separate by ",", not commonly found in str
		return string
	elif type(string) == list:
		return string
	else:
		sys.exit(("to_list_of_string(string): cannot convert an inpit that is"
                  "neither a single string or a list of strings"))  
