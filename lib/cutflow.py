import ROOT
from helper import *

'''
INPUT -------------------------------------------------------------------------
|*(str) ntuple_file_path: the fuill path to the ntuple file of interest
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
def get_normalization_factor(ntuple_file_path, lumi_in_inverse_pb):
	delphes_filename = get_delphes_filename(ntuple_file_path)
	nevts = float(delphes_gen_info[delphes_filename]['nevt'])
	xsec = delphes_gen_info[delphes_filename]['xsec']
	return xsec * lumi_in_inverse_pb / nevts

def get_ntuple_tree(sig_file_paths, bkg_file_paths, treename):
	sig_files = []
	bkg_files = []
	for f in sig_file_paths:
		sig_files.append(ROOT.TFile.Open(f))
	for f in bkg_file_paths:
		bkg_files.append(ROOT.TFile.Open(f))
		
		
# pointer to files + trees
# str to store cuts
# get number of evts after each cut
# plot the cutflow
# save histograms as rootfile
