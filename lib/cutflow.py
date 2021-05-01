import ROOT
from helper import *

'''
INPUT -------------------------------------------------------------------------
|*(str) ntuple_file_path: the fuill path to the ntuple file of interest
| OR
| (str) delphes_filename: the name of the delphes sample, with suffix
|*(float) lumi_in_inverse_pb: the luminosity in units of inverse picobarn
|  
ROUTINE -----------------------------------------------------------------------
|* get the name of the delphes file used to produce the ntuple
|* look up for the cross section (in pb) + number of evts in the delphes_gen_info
|  dictionary
|* calculate the factor to normalize evts to the input luminosity
| 
OUTPUT ------------------------------------------------------------------------
|* (float) the normalization factor
+------------------------------------------------------------------------------ 
''' 
def get_normalization_factor(filename, lumi_in_inverse_pb):
	ntuple_delimiter = ':'
	if len(filename.split(ntuple_delimiter)) > 1:
		delphes_filename = get_delphes_filename(filename)
	else:
		delphes_filename = filename
	nevts = float(delphes_gen_info[delphes_filename]['nevt'])
	xsec = delphes_gen_info[delphes_filename]['xsec']
	return xsec * lumi_in_inverse_pb / nevts

def get_ntuple_trees(sig_filepaths, bkg_filepaths, channels):
	channels = string_to_list(channels)
	sig_files = {}
	bkg_files = {}
	sig_trees = {}
	bkg_trees = {}
	for chn in channels: 
		sig_trees[chn] = {}
		bkg_trees[chn] = {}
	for key, f in sig_filepaths.items():
		sig_files[key] = ROOT.TFile.Open(f)
		
	for key, f in bkg_filepaths.items():
		bkg_files[key] = ROOT.TFile.Open(f)
	return trees
		
# pointer to files + trees
# str to store cuts
# get number of evts after each cut
# plot the cutflow
# save histograms as rootfile
