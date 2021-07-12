##############################
# Author: T. J. Yang        #
#---------------------------#
# tyjyang@mit.edu           #
#---------------------------#
# May 24, 2021              #
##############################

import ROOT
import ntuplizer as ntp
import helper as hlp
import sys
from collections import OrderedDict
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
|* (str) delphes_filepath: full path to the delphes file
|  
ROUTINE -----------------------------------------------------------------------
|* loop over the delphes events, for each event, look at the genParticles
|* categorize the events into the electron or muon channel
| 
OUTPUT ------------------------------------------------------------------------
|* dict(int): the keys are chn names, the values are nevts in that chn
+------------------------------------------------------------------------------ 
''' 
def get_e_mu_nevts_from_gen(delphes_filepath):
	electron_PID = 11
	muon_PID = 13
	pythia_out_ID = 23
	evt_chain = ntp.load_delphes_file(delphes_filepath, ['particle'])
	num_ee_evts = 0
	num_mumu_evts = 0
	for evt in evt_chain:
		num_electron, num_positron, num_muon, num_antimuon = (
		0,0,0,0)
		for cand in evt.Particle:
			if cand.Status == pythia_out_ID:
				if cand.PID == electron_PID:
					num_electron += 1
				elif cand.PID == -1 * electron_PID:
					num_positron += 1
				elif cand.PID == muon_PID:
					num_muon += 1
				elif cand.PID == -1 * muon_PID:
					num_antimuon += 1
		if ((num_electron == 1 and num_positron == 1) or
		    ((num_electron > 0 and num_positron >  0) and
		     (num_muon    == 0 or  num_antimuon == 0))):
			num_ee_evts += 1
			continue
		elif ((num_muon     == 1 and num_antimuon == 1) or
		      ((num_muon      > 0 and num_antimuon >  0) and
		       (num_electron == 0 or  num_positron == 0))):
			num_mumu_evts += 1
	return {'electron': num_ee_evts, 'muon': num_mumu_evts}

'''
INPUT -------------------------------------------------------------------------
|* OrderedDict(OrderedDict(TTree)) sig_trees: pointers to signal trees, grouped
|                                             in final state and production chns
|* OrderedDict(float) sig_w: weight of signal trees
|* OrderedDict(OrderedDict(TTree)) bkg_trees
|* OrderedDict(float) bkg_w
|* OrderedDict(OrderedDict(str)) cuts: the strings to be used by TCut
|* (str) align: option to align to "right", "center" or "left" for the numeric cells
|* (int) decimal_places: the number of digits after the decimal pt for table floats
|  
ROUTINE -----------------------------------------------------------------------
|* want to write everything into a string for a markdown table
|* get gen-level nevts in each channel for the inclusive signal samples
|* write one table for each final state channel
|* for each table, first write a header row, a separator row, and a row for 
|  nevts from preselection before any cuts were applied
|  * first column of these 3 lines are always "chn_name cuts", "|---|" and "Pre-
|    selection" respectively.
|  * loop over the production channels to fill the rest columns of these 3 rows 
|* for the next rows for each cut:
|  * in the 1st column, write the cut name
|  * for the rest of the columns, loop over production chns and fill nevts from
|    the ROOT::EntryList obtained by putting in the cut str in TTree::Draw()
|* last row of the table is signal efficiency calculated by dividing final yield
|  by nevts from generation.
|* put all rows into a table, separated by the newline char '\n'
| 
OUTPUT ------------------------------------------------------------------------
|* dict(str): keys are final state channel name, values are markdown str for table 
+------------------------------------------------------------------------------ 
''' 
def make_cutflow_table(sig_trees, sig_w, bkg_trees, bkg_w,
                       delphes_path, sig_ntuple_filepaths, cuts, 
                       align = "right", decimal_places = '2', sig_eff = True):
	# do a few checks to make sure the input parameters make sense
	chns = sig_trees.keys()
	if bkg_trees.keys() == chns and cuts.keys() == chns:
		if (sig_trees[chns[0]].keys() == sig_w.keys() and
		    bkg_trees[chns[0]].keys() == bkg_w.keys()):
			pass
		else: sys.exit("keys in trees and theirs weights are not consistent") 
	else: sys.exit("channels in sig and bkg trees and cuts are not consistent")
	# table formatting options
	if align == "right":
		align_str = "--:"
	elif align == "center":
		align_str = "---"
	elif align == "left":
		align_str = ":--"
	decimal_places_str = "{:." + decimal_places + "f}"
	# get the nevts from gen-level for signal delphes files, for eff calc later
	if sig_eff:
		sig_gen_nevts = OrderedDict()
		for chn in chns: sig_gen_nevts[chn] = OrderedDict()
		for key, f in sig_ntuple_filepaths.items():
			delphes_filepath = delphes_path + hlp.get_delphes_filename(f)
			gen_nevts = get_e_mu_nevts_from_gen(delphes_filepath)
			for chn, nevts in gen_nevts.items():
				sig_gen_nevts[chn][key] = float(nevts)
				print key, '::', chn, ' has ', nevts, ' events'

	# make table and store into markdown strings
	table_string = {}
	for chn in chns:
		table_string[chn] = ""
		ctf_table_header = "|" + chn + " cuts|"
		ctf_table_separator = "|---|"
		ctf_table_preselection = "|Pre-selection|"
		ctf_table_rows = []
		for key, tree in sig_trees[chn].items():
			ctf_table_header += key + "|"
			ctf_table_separator += align_str + "|"
			ctf_table_preselection += decimal_places_str.format(
			                          tree.GetEntries() * sig_w[key]) + '|'
		for key, tree in bkg_trees[chn].items():
			ctf_table_header += key + "|"
			ctf_table_separator += align_str + "|"
			ctf_table_preselection += decimal_places_str.format(
			                          tree.GetEntries() * bkg_w[key]) + '|'
		current_cut = ""
		for cutname, cut in cuts[chn].items():
			ctf_table_row = "|" + cutname + "|"
			sig_last_row_yields = {}
			if current_cut != "": current_cut += "&&"
			current_cut += cut
			for key, tree in sig_trees[chn].items():
				if tree.GetEntries() != 0:
					tree.Draw(">>evts_pass_cut", current_cut, "entrylist")
					evts_pass_cut = ROOT.gDirectory.Get("evts_pass_cut")
					nevts_pass_cut = evts_pass_cut.GetN() 
				else: #if tree is empty, avoid using evts_pass_cut from prev tree
					nevts_pass_cut = 0
				norm_nevts_pass_cut = nevts_pass_cut * sig_w[key]
				sig_last_row_yields[key] = nevts_pass_cut
				ctf_table_row += decimal_places_str.format(norm_nevts_pass_cut) + "|"
			for key, tree in bkg_trees[chn].items():
				if tree.GetEntries() != 0:
					tree.Draw(">>evts_pass_cut", current_cut, "entrylist")
					evts_pass_cut = ROOT.gDirectory.Get("evts_pass_cut")
					nevts_pass_cut = evts_pass_cut.GetN() 
				else: #if tree is empty, avoid using evts_pass_cut from prev tree
					nevts_pass_cut = 0
				norm_nevts_pass_cut = nevts_pass_cut * bkg_w[key]
				ctf_table_row += decimal_places_str.format(norm_nevts_pass_cut) + "|"
			ctf_table_rows.append(ctf_table_row)
		ctf_table_eff = "|Efficiency|"
		if sig_eff:
			for key, nevts in sig_gen_nevts[chn].items():
				ctf_table_eff += decimal_places_str.format(
				                 sig_last_row_yields[key] / nevts * 100) + "%|"
		table_string[chn] += ctf_table_header + '\n'
		table_string[chn] += ctf_table_separator + '\n'
		table_string[chn] += ctf_table_preselection + '\n'
		for row in ctf_table_rows: table_string[chn] += row + '\n'
		if sig_eff:
			table_string[chn] += ctf_table_eff
	return table_string
#def set_tree_weights(trees, 
		
# implement channel recognition from filenames
# setting tree weights
# str to store cuts
# get number of evts after each cut
# plot the cutflow
# save histograms as rootfile
