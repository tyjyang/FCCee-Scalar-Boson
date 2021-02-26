from ROOT import TFile
import pandas as pd

def test(a):
	return a+1
'''
--------------------
Parameters
--------------------
# (str) or list[(str)] ntuple_files: name of the ntuplized rootfile
# (str) or list[(str)] particles: name of the particles, 
# (str) or list[(str)] variables: name of the variables of that particle
--------------------
Routine
--------------------
# opens a 
#
#
'''
def get_particle_data_by_variable(ntuple_files, particle, varible):
	data = {}
	for ntuple_file in ntuple_files:
		file_objcet = TFile.Open(ntuple_file)
		
		# import data from one variable of a particle
		data[ntuple_file + ":" + particle + "_" + variable] = (
		[getattr(entries, particle + "_" + variable) 
		for entries in getattr(file_object, particle)])

		file_object.Close()
	return data

def group_by_event(data):
	for key in list(data):


