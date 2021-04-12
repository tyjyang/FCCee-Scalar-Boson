import ROOT
from helper import *

def get_normalization_factor(ntuple_file_path, lumi_in_inverse_pb):
	delphes_filename = get_delphes_filename(ntuple_file_path)
	nevts = float(delphes_gen_info[delphes_filename]['nevt'])
	xsec = delphes_gen_info[delphes_filename]['xsec']
	return xsec * lumi_in_inverse_pb / nevts
