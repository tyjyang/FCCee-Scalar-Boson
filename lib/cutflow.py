##############################
# Author: T. J. Yang        #
#---------------------------#
# tyjyang@mit.edu           #
#---------------------------#
# May 24, 2021              #
##############################

import ROOT
import helper as hlp
'''
INPUT -------------------------------------------------------------------------
|* (str) delphes_filepath: the fullpath to the delphes sample 
|* (float) lumi_in_inverse_pb: the luminosity in units of inverse picobarn
|  
ROUTINE -----------------------------------------------------------------------
|* get the number of evts from the delphes file by calling hlp.get_num_evts()
|* look up for the cross section (in pb) in the DELPHES_GEN_INFO dictionary
|* calculate the factor to normalize evts to the input luminosity
| 
OUTPUT ------------------------------------------------------------------------
|* (float) the normalization factor
+------------------------------------------------------------------------------ 
''' 
def get_normalization_factor(delphes_filepath, lumi_in_inverse_pb):
	nevts = hlp.get_num_evts(delphes_filepath, "Delphes")
	delphes_filename = delphes_filepath.split("/")[-1]
	xsec = hlp.DELPHES_GEN_INFO[delphes_filename]['xsec']
	return xsec * lumi_in_inverse_pb / nevts

'''
INPUT -------------------------------------------------------------------------
|* (dict) filepaths: the dict of full paths to the ntuple files from which the 
|                    function gets the TNtuple trees, keys are short-handed filenames
|* list(str) channels: the final state particle channels from whose name the
|                      function fetches the trees in the rootfiles 
|  
ROUTINE -----------------------------------------------------------------------
|* store the filename keys and the pointers to rootfiles into a 1D
|  dictionary files
|* Nest the trees, one per channel per file, into a 2D dictionary, with the 1st
|  dim being the channel and the 2nd being the filename keys
| 
OUTPUT ------------------------------------------------------------------------
|* dict(dict(ROOT.TNtuple)) trees: the 2D dict containing root ntuple trees
+------------------------------------------------------------------------------ 
''' 
def get_ntuple_tree(filepaths, channels):
	channels = hlp.string_to_list(channels)
	files = {}
	trees = {}
	for chn in channels: 
		trees[chn] = {}
		print chn
	for key, f in filepaths.items():
		files[key] = ROOT.TFile.Open(f)
		print files[key]
		for chn in channels:
			trees[chn][key] = files[key].Get(chn)
			print trees[chn][key]
	print trees
	return trees

'''
INPUT -------------------------------------------------------------------------
|* (dict) filepaths: a dictionary whose keys are the filename in short, and 
|                    whose values are the full paths to the delphes files
|* (float) lumi: the luminosity for normalization in units of inverse pb
|  
ROUTINE -----------------------------------------------------------------------
|* declare an empty dict for storing the weights
|* copy the keys from keys of filepaths, and get the value entries from
|  get_normalization_factor(), using the lumi passed in
| 
OUTPUT ------------------------------------------------------------------------
|* (dict) w: short filenames in keys, weights in values
+------------------------------------------------------------------------------ 
''' 
def get_tree_weight(filepaths, lumi):
	w = {}
	for key, f in filepaths.items():
		w[key] = get_normalization_factor(f, lumi)
	return w

#def set_tree_weights(trees, 
		
# implement channel recognition from filenames
# setting tree weights
# str to store cuts
# get number of evts after each cut
# plot the cutflow
# save histograms as rootfile
