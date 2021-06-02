##############################
# Author: T. J. Yang        #
#---------------------------#
# tyjyang@mit.edu           #
#---------------------------#
# May 24, 2021              #
##############################

import ROOT
from helper import *

'''
INPUT -------------------------------------------------------------------------
|* (str) delphes_filepath: the fullpath to the delphes sample 
|* (float) lumi_in_inverse_pb: the luminosity in units of inverse picobarn
|  
ROUTINE -----------------------------------------------------------------------
|* get the name of the delphes file used to produce the ntuple
|* look up for the cross section (in pb) + number of evts in the DELPHES_GEN_INFO
|  dictionary
|* calculate the factor to normalize evts to the input luminosity
| 
OUTPUT ------------------------------------------------------------------------
|* (float) the normalization factor
+------------------------------------------------------------------------------ 
''' 
def get_normalization_factor(delphes_filepath, lumi_in_inverse_pb):
	ntuple_delimiter = ':'
	if len(filename.split(ntuple_delimiter)) > 1:
		delphes_filename = get_delphes_filename(filename)
	else:
		delphes_filename = filename
	nevts = get_num_evts(
	xsec = DELPHES_GEN_INFO[delphes_filename]['xsec']
	return xsec * lumi_in_inverse_pb / nevts

'''
INPUT -------------------------------------------------------------------------
|* (dict) filepaths: the list of full paths to rootfiles from which the 
|                    function gets the ntuple trees
|* list(str) channels: the final state particle channels from whose name the
|                      function fetches the trees in the rootfiles 
|  
ROUTINE -----------------------------------------------------------------------
|* store the short-handed filenames and the pointers to rootfiles into a 1D
|  dictionary files
|* Nest the trees, one per channel per file, into a 2D dictionary, with the 1st
|  dim being the channel and the 2nd being the files
| 
OUTPUT ------------------------------------------------------------------------
|* dict(dict(ROOT.TNtuple)) trees: the 2D dict containing root ntuple trees
+------------------------------------------------------------------------------ 
''' 
def get_ntuple_trees(filepaths, channels):
	channels = string_to_list(channels)
	files = {}
	trees = {}
	for chn in channels: 
		trees[chn] = {}
	for key, f in filepaths.items():
		files[key] = ROOT.TFile.Open(f)
		for chn in channels:
			trees[chn][key] = getattr(files[key], chn)
	return trees

def get_ntuple_weights(filepaths, lumi):
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
