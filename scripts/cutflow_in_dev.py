import ROOT
import numpy as np
import time
import ntuplizer as ntp 
import helper as hlp 
import cutflow as ctf 
import autobinning as atb
from collections import OrderedDict
from array import array
##################
# I/O variables #
##################
#ntuple_path = '../ntuples-no-photon-veto/'
ntuple_path = '../ntuples_IDEA_500MeV/'
delphes_path = '/scratch5/arapyan/fcc_ee/scalar_delphes_idea/'
plot_path = '../plots/'
table_path = '../tables/'
hist_path = '../hists/'
combine_path = '../combine/'
#output_suffix = 'IDEA_500MeV_no_photon_veto'
output_suffix = 'IDEA_500MeV'
ctf_hist_file = ROOT.TFile(hist_path + "cutflow_hists_" + output_suffix + ".root",
                          "RECREATE") # root file to store all cutflow hists
bin_option = "manual"
#bin_option = "auto"
channels = ['electron', 'muon']
lumi = 150 * 10 ** 6

sig_ntuple_filenames = OrderedDict([
('0p5',('eeZS_p5_photon500:electron-muon:pt-eta-phi-cos_theta-alpha-'
       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')),
('2'  ,('eeZS_2_photon500:electron-muon:pt-eta-phi-cos_theta-alpha-'
       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')),
('5'  ,('eeZS_5_photon500:electron-muon:pt-eta-phi-cos_theta-alpha-'
       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')),
('10' ,('eeZS_10_photon500:electron-muon:pt-eta-phi-cos_theta-alpha-'
       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')),
('15' ,('eeZS_15_photon500:electron-muon:pt-eta-phi-cos_theta-alpha-'
       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')),
('25' ,('eeZS_25_photon500:electron-muon:pt-eta-phi-cos_theta-alpha-'
       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root'))
])      
bkg_ntuple_filenames = OrderedDict([
('2f-mutau'   ,('ee2fermion_mutau_photon500:electron-muon:pt-eta-phi-cos_theta-'
                'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')),
('2f-e'       ,('ee2fermion_electron_photon500:electron-muon:pt-eta-phi-cos_theta-'
                'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')),
('4f-2mutau2l',('ee4lepton_mutau_photon500:electron-muon:pt-eta-phi-cos_theta-'
                'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')),
('4f-2e2l',    ('ee4eequark_electron_photon500:electron-muon:pt-eta-phi-cos_theta-'
                'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')),
('4f-2mutau2q',('ee4lepquark_mutau_photon500:electron-muon:pt-eta-phi-cos_theta-'
                'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')),
('4f-2e2q',    ('ee4eequark_electron_photon500:electron-muon:pt-eta-phi-cos_theta-'
                'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root'))
])

##################
# cut variables #
##################
cut_bounds = OrderedDict()
cuts = OrderedDict()
for fs_chn in channels: 
	cut_bounds[fs_chn] = OrderedDict()
	cuts[fs_chn] = OrderedDict()

# NOTE: for readability, the strings in cuts are not citing the bounds here
#       if changing cut_bounds, remember to change cuts as well
cut_bounds['electron']['alpha']         = [0.11    , 2.0    ]
cut_bounds['electron']['angle']         = ['-infty', 0.9    ]
cut_bounds['electron']['momentum']      = [27      , 'infty']
cut_bounds['electron']['missing_angle'] = ['-infty', 0.98   ]
cut_bounds['electron']['m_inv']         = [20      , 100    ]
cut_bounds['muon']    ['alpha']         = [0.11    , 2.0    ]
cut_bounds['muon']    ['angle']         = ['-infty', 0.94   ]
cut_bounds['muon']    ['momentum']      = [30      , 'infty']
cut_bounds['muon']    ['missing_angle'] = ['-infty', 0.98   ]
cut_bounds['muon']    ['m_inv']         = [20      , 100    ]

cuts['electron']['alpha']  = "alpha > 0.11 && alpha < 2.0"
cuts['muon']['alpha']      = cuts['electron']['alpha']

cuts['electron']['angle'] = ("TMath::Abs(cos_theta_1) < 0.9 &&"
                             "TMath::Abs(cos_theta_2) < 0.9")
cuts['muon']['angle']     = ("TMath::Abs(cos_theta_1) < 0.94 &&"
                             "TMath::Abs(cos_theta_2) < 0.94")

cuts['electron']['momentum'] = ("TMath::Max(p_mag_1, p_mag_2) > 27 &&"
                                "TMath::Min(p_mag_1, p_mag_2) > 20")
cuts['muon']['momentum']     = ("TMath::Max(p_mag_1, p_mag_2) > 30 &&"
                                "TMath::Min(p_mag_1, p_mag_2) > 20")

cuts['electron']['missing_angle'] = (
"(p_mag_missing <= 2 ||" 
"(p_mag_missing > 2  && TMath::Abs(cos_theta_p_missing) < 0.98))")
cuts['muon']['missing_angle'] = cuts['electron']['missing_angle']

cuts['electron']['m_inv'] = "m_inv > 20 && m_inv < 100"
cuts['muon']['m_inv']     = cuts['electron']['m_inv']

##################
# plot varibles #
##################
ctf_plot_param = OrderedDict() # plotting params that differs for each cut
ctf_plot_param['alpha'] = {
'xmin':0, 
'xmax':3.1,
'nbins':31,
'ymin':1000,
'ymax':200000,
'xvar':'alpha',
'xunit':'rad',
'xtitle':'#alpha',
'scale':'logy'
} 
ctf_plot_param['angle'] = {
'xmin':0, 
'xmax':1,
'nbins':15,
'ymin':1000,
'ymax':100,
'xvar':'abs(cos_theta_1)',
'xunit':'',
'xtitle':'|cos(#theta_{1})|',
'scale':'logy'
}
ctf_plot_param['momentum'] = {
'xmin':0, 
'xmax':45,
'nbins':45,
'ymin':1000,
'ymax':100,
'xvar':'max(p_mag_1, p_mag_2)',
'xunit':'GeV',
'xtitle':'|p_{1}|',
'scale':'logy'
}
ctf_plot_param['missing_angle'] = {
'xmin':0, 
'xmax':1,
'nbins':15, 
'ymin':1000, 
'ymax':100,
'xvar':'abs(cos_theta_p_missing)',
'xunit':'',
'xtitle':'|cos(#theta_{miss})|',
'scale':'logy'
}
ctf_plot_param['m_inv'] = {
'xmin':0, 
'xmax':100,
'nbins':10, 
'ymin':0, 
'ymax':100,
'xvar':'m_inv',
'xunit':'GeV',
'xtitle':'m_{ll}',
'scale':'linear'
}
ctf_plot_param['mrec'] = {
'xmin':-5, 
'xmax':40,
'nbins':45, 
'ymin':1000, 
'ymax':100,
'xvar':'m_rec',
'xunit':'GeV',
'xtitle':'m_{rec}',
'scale':'logy'
}

for cutname, params in ctf_plot_param.items():
	params['binsize'] = (params['xmax'] - params['xmin']) / float(params['nbins'])
	decimal_place = str(params['binsize'])[::-1].find('.')
	if params['xunit'] != '': params['xtitle'] += ' [' + params['xunit'] + ']'
	if decimal_place > 3:
		params['ytitle'] = ('Events/' + "{:.4f}".format(params['binsize']) + 
	                        ' ' + params['xunit'])
	else:
		params['ytitle'] = ('Events/' + str(params['binsize']) + 
	                        ' ' + params['xunit'])

# params that are the same for each cut
## hists
sig_linecolors = {
'0p5': ROOT.kRed,
'5': ROOT.kBlue+2,
'25': ROOT.kGreen+2}
sig_linewidth = 2
sig_linestyle = 1

bkg_linecolor = ROOT.kBlack 
bkg_fillcolors = {
'2f': ROOT.kGreen,
'4f-4l': ROOT.kYellow,
'4f-2l2q': ROOT.kOrange}
bkg_linewidth = 1
bkg_linestyle = 1

## stacks and pads
axis_title_textsize = 0.05
sig_stack_options = "hist, same, nostack"
bkg_stack_options = "hist"
pad_ymax_ratio = {'linear': 1.2, 'logy': 5} # the ratio between the y upper bound
                                            # of a pad and the peak of its plots
pad_ymax_lb = {'linear':0.7, 'logy': 0.1} # the min fraction of the pad's ymax
                                          # that can be above all plot's peaks
pad_ymax_ub = {'linear':0.95, 'logy': 0.9} # the max fraction of the pad's ymax
                                           # that can be above all plot's peaks
## lines and arrows
cut_linewidth = 2
arrow_len_coeff = 0.1 # ratio between arrow len and horizontal range of pad
arrow_vert_pos = {'linear': 0.7, 'logy':0.05} # 0 if at bottom, 1 if at top
arrow_size = 0.005
arrow_style = "|>"
arrow_angle = 60
arrow_linewidth = 2

## canvas 
hist_pixel_x = 600
hist_pixel_y = 450
num_hist_x = 3
num_hist_y = 2
ROOT.gStyle.SetHistTopMargin(0)
#ROOT.gStyle.SetHistBottomMargin(0)
#ROOT.gStyle.SetPadTopMargin(0)
#ROOT.gStyle.SetPadBottomMargin(0)
canvas_titles = OrderedDict()
canvas_title_x = 0.1
canvas_title_y = 0.9
canvas_titles['electron'] = "e^{+}e^{-} events @ #sqrt{s} = 91.2 GeV"
canvas_titles['muon']     = "#mu^{+}#mu^{-} events @ #sqrt{s} = 91.2 GeV"
canvas_title_x = 0.1
canvas_title_y = 0.9
canvas_title_textsize = 0.05
pad_title_x = 0.4
pad_title_y = 0.95
pad_title_textsize = 0.05
## legends
legend_x_bl = 0.1 # x-coordinate of the bottom left point of the legend box
legend_y_bl = 0.6
legend_x_tr = 0.6
legend_y_tr = 0.85
sig_legend_entry = OrderedDict()
bkg_legend_entry = OrderedDict()
for fs_chn in channels: 
	sig_legend_entry[fs_chn] = OrderedDict()
	bkg_legend_entry[fs_chn] = OrderedDict()
sig_legend_entry['electron']['0p5']     = "m_{s} = 0.5 GeV"
sig_legend_entry['muon']    ['0p5']     = sig_legend_entry['electron']['0p5']
sig_legend_entry['electron']['5']       = "m_{s} = 5 GeV"
sig_legend_entry['muon']    ['5']       = sig_legend_entry['electron']['5']
sig_legend_entry['electron']['25']      = "m_{s} = 25 GeV"
sig_legend_entry['muon']    ['25']      = sig_legend_entry['electron']['25']
bkg_legend_entry['electron']['2f']      = "2 fermions"
bkg_legend_entry['muon']    ['2f']      = bkg_legend_entry['electron']['2f']
bkg_legend_entry['electron']['4f-4l']   = "4 fermions - 2e+2l"
bkg_legend_entry['muon']    ['4f-4l']   = "4 fermions - 2#mu+2l"
bkg_legend_entry['electron']['4f-2l2q'] = "4 fermions - 2e+2q"
bkg_legend_entry['muon']    ['4f-2l2q'] = "4 fermions - 2#mu+2q"
sig_legend_style = "l"
bkg_legend_style = "f"

######################
# derived variables #
######################
# get the full paths to the ntuple files 
sig_ntuple_filepaths = OrderedDict()
bkg_ntuple_filepaths = OrderedDict()
for i, f in sig_ntuple_filenames.items(): 
	sig_ntuple_filepaths[i] = ntuple_path + f 
for i, f in bkg_ntuple_filenames.items(): 
	bkg_ntuple_filepaths[i] = ntuple_path + f 
# get pointers to the ntuple trees and normalize nevts to the lumi above
sig_ntuple_files = OrderedDict()
bkg_ntuple_files = OrderedDict()
sig_trees = OrderedDict()
bkg_trees = OrderedDict()
sig_w  = OrderedDict()
bkg_w  = OrderedDict()

for key, f in sig_ntuple_filepaths.items():
	# files need to be open and in memory in order for the trees to be 
	# accessible by pointers
	sig_ntuple_files[key] = ROOT.TFile.Open(f)
	# get normalization factor by looking at nevts in the delphes file
	delphes_filepath = delphes_path + hlp.get_delphes_filename(f)
	sig_w[key] = ctf.get_normalization_factor(delphes_filepath, lumi)
for chn in channels:
	sig_trees[chn] = OrderedDict()
	for key, f in sig_ntuple_filepaths.items():
		# get the pointers to the trees and set weights
		sig_trees[chn][key] = sig_ntuple_files[key].Get(chn)
		sig_trees[chn][key].SetWeight(sig_w[key])

for key, f in bkg_ntuple_filepaths.items():
	bkg_ntuple_files[key] = ROOT.TFile.Open(f)
	# get normalization factor by looking at nevts in the delphes file
	delphes_filepath = delphes_path + hlp.get_delphes_filename(f)
	bkg_w[key] = ctf.get_normalization_factor(delphes_filepath, lumi)
for chn in channels:
	bkg_trees[chn] = OrderedDict()
	for key, f in bkg_ntuple_filepaths.items():
		# get the pointers to the trees and set weights
		bkg_trees[chn][key] = bkg_ntuple_files[key].Get(chn)
		bkg_trees[chn][key].SetWeight(bkg_w[key])
# TODO 
# make each production channel be able to take an arbitrary number of files
# by using TChain to concatenate TTrees

ntp.load_delphes_lib()
ctf_hist_file.cd()
''' preamble ends here '''
''' script procedures below '''

########################
# make cutflow tables #
########################
'''

md_table_string = ctf.make_cutflow_table(sig_trees, sig_w, bkg_trees, bkg_w,
                                         delphes_path, sig_ntuple_filepaths, cuts,
                                         sig_eff = True)
for chn, table in md_table_string.items():
	mdfile = open(table_path + chn + "_cutflow_table_" + output_suffix + ".md", "w")
	mdfile.write(table)
	mdfile.close()
'''

######################################
# merge trees from same bkg channel #
######################################
bkg_merge_scheme = OrderedDict([
("4f-2l2q",['4f-2mutau2q', '4f-2e2q']),
("4f-4l",['4f-2mutau2l', '4f-2e2l']),
("2f",["2f-mutau","2f-e"])
])
for fs_chn in channels:
	for merged_treename, treenames_to_merge in bkg_merge_scheme.items():
		weights_to_merge = []
		trees_to_merge = []
		for t in treenames_to_merge: # load the tree and weights into dicts
			weights_to_merge.append(bkg_w[t])
			trees_to_merge.append(bkg_trees[fs_chn][t])
		bkg_trees[fs_chn][merged_treename] = ctf.merge_trees_w_weights(
		                                     trees_to_merge, weights_to_merge)
		# get rid of trees before the merge
		for t in treenames_to_merge: del bkg_trees[fs_chn][t]
		if fs_chn == channels[-1]: # change the weight dict for only once
			bkg_w[merged_treename] = bkg_trees[fs_chn][merged_treename].GetWeight()
			for t in treenames_to_merge: del bkg_w[t]

#######################
# make cutflow plots #
#######################
sig_hists = OrderedDict()
bkg_hists = OrderedDict()
sig_mrec_hists = OrderedDict()  
bkg_mrec_hists = OrderedDict()
sig_stacks = OrderedDict()
bkg_stacks = OrderedDict()
lb_line = OrderedDict()
ub_line = OrderedDict()
lb_arrow = OrderedDict()
ub_arrow = OrderedDict()
canvases = OrderedDict()
for fs_chn in channels:
	canvases[fs_chn] = ROOT.TCanvas(
		fs_chn + "_cutflow", "cutflow plots for the " + fs_chn + " channel",
		hist_pixel_x * num_hist_x, hist_pixel_y * num_hist_y
	)
	canvases[fs_chn].Divide(num_hist_x, num_hist_y)
	sig_hists[fs_chn] = OrderedDict()
	bkg_hists[fs_chn] = OrderedDict()
	sig_stacks[fs_chn] = OrderedDict()
	bkg_stacks[fs_chn] = OrderedDict()
	lb_line[fs_chn] = OrderedDict()
	ub_line[fs_chn] = OrderedDict()
	lb_arrow[fs_chn] = OrderedDict()
	ub_arrow[fs_chn] = OrderedDict()
	cumulative_cutstr = ""
	i_pad = 1
	for cutname, cutstring in cuts[fs_chn].items():
		canvases[fs_chn].cd(i_pad)
		# draw pd_chn hists and add them to sig and bkg stacks with styles
		sig_hists[fs_chn][cutname] = OrderedDict() 
		sig_stack_ymax = 0
		for pd_chn, tree in sig_trees[fs_chn].items():
			hist_title = 'hist_' + fs_chn + '_' + pd_chn + '_' + cutname
			hist_dscrp = hist_title
			# declare hist, one per cut per prod chn per fs chn
			sig_hists[fs_chn][cutname][pd_chn] = ROOT.TH1D(
				hist_title, hist_dscrp, 
				ctf_plot_param[cutname]['nbins'],
				ctf_plot_param[cutname]['xmin'],
				ctf_plot_param[cutname]['xmax'])
			# fill the cutted trees to the hists
			tree.Draw(ctf_plot_param[cutname]['xvar'] + ">>" + hist_title, 
			cumulative_cutstr, "goff")
			# store sum of squared weights to calculate stat uncertainty
			sig_hists[fs_chn][cutname][pd_chn].Sumw2()
			sig_hists[fs_chn][cutname][pd_chn].Write()
		sig_stacks[fs_chn][cutname] = ROOT.THStack(
		                              'hs_sig_' + fs_chn + '_' + cutname, "")
		for pd_chn, hist in sig_hists[fs_chn][cutname].items(): 
			if pd_chn in sig_linecolors.keys():
				sig_stacks[fs_chn][cutname].Add(hist)
				# set plotting style for the hists
				hist.SetLineColor(sig_linecolors[pd_chn])
				hist.SetLineWidth(sig_linewidth)
				hist.SetLineStyle(sig_linestyle)
				sig_hist_ymax = hist.GetBinContent(hist.GetMaximumBin())
				if sig_hist_ymax > sig_stack_ymax: sig_stack_ymax = sig_hist_ymax

		bkg_hists[fs_chn][cutname] = OrderedDict()
		bkg_stack_ymax = 0
		for pd_chn, tree in bkg_trees[fs_chn].items():
			hist_title = 'hist_' + fs_chn + '_' + pd_chn + '_' + cutname
			hist_dscrp = hist_title
			# declare hist, one per cut per prod chn per fs chn
			bkg_hists[fs_chn][cutname][pd_chn] = ROOT.TH1D(
				hist_title, hist_dscrp, 
				ctf_plot_param[cutname]['nbins'],
				ctf_plot_param[cutname]['xmin'],
				ctf_plot_param[cutname]['xmax'])
			# fill the cutted trees to the hists
			tree.Draw(ctf_plot_param[cutname]['xvar'] + ">>" + hist_title, 
			cumulative_cutstr, "goff")
			# store sum of squared weights to calculate stat uncertainty
			bkg_hists[fs_chn][cutname][pd_chn].Sumw2()
			bkg_hists[fs_chn][cutname][pd_chn].Write()
		bkg_stacks[fs_chn][cutname] = ROOT.THStack(
		                             'hs_bkg_' + fs_chn + '_' + cutname, "")
		for pd_chn, hist in bkg_hists[fs_chn][cutname].items(): 
			if pd_chn in bkg_fillcolors.keys():
				bkg_stacks[fs_chn][cutname].Add(hist)
				# set plotting style for the hists
				hist.SetLineColor(bkg_linecolor)
				hist.SetFillColor(bkg_fillcolors[pd_chn])
				hist.SetLineWidth(bkg_linewidth)
				hist.SetLineStyle(bkg_linestyle)
		# calculate the ymax of stacked bkgs
		for i_bin in np.arange(1, ctf_plot_param[cutname]['nbins'] + 1):
			sum_bin_content = 0
			for pd_chn, hist in bkg_hists[fs_chn][cutname].items():
				sum_bin_content += hist.GetBinContent(i_bin)
			if sum_bin_content > bkg_stack_ymax: bkg_stack_ymax = sum_bin_content
		graph_ymax = max(sig_stack_ymax, bkg_stack_ymax)
		# automatic adjustment of ymax for the pad
		if (ctf_plot_param[cutname]['ymax'] *
		    pad_ymax_ub[ctf_plot_param[cutname]['scale']] < graph_ymax or
		    ctf_plot_param[cutname]['ymax'] * 
		    pad_ymax_lb[ctf_plot_param[cutname]['scale']] > graph_ymax):
			ctf_plot_param[cutname]['ymax'] = graph_ymax * pad_ymax_ratio[
			                                  ctf_plot_param[cutname]['scale']]
		if ctf_plot_param[cutname]['scale'] == 'logy': ROOT.gPad.SetLogy()
		bkg_stacks[fs_chn][cutname].SetMinimum(ctf_plot_param[cutname]['ymin'])
		bkg_stacks[fs_chn][cutname].SetMaximum(ctf_plot_param[cutname]['ymax'])
		bkg_stacks[fs_chn][cutname].Draw(bkg_stack_options)
		bkg_stacks[fs_chn][cutname].GetHistogram().SetXTitle(
		ctf_plot_param[cutname]['xtitle'])
		bkg_stacks[fs_chn][cutname].GetHistogram().SetYTitle(
		ctf_plot_param[cutname]['ytitle'])
		bkg_stacks[fs_chn][cutname].GetHistogram().SetTitleSize(
		axis_title_textsize, "xy")
		ROOT.gPad.Update()
		sig_stacks[fs_chn][cutname].SetMinimum(ctf_plot_param[cutname]['ymin'])
		sig_stacks[fs_chn][cutname].SetMaximum(ctf_plot_param[cutname]['ymax'])
		sig_stacks[fs_chn][cutname].Draw(sig_stack_options)
		ROOT.gPad.Update()
		# draw the cut lines and arrows
		if ctf_plot_param[cutname]['scale'] == 'logy':
			ctf_plot_param[cutname]['ymax'] = 10 ** ROOT.gPad.GetUymax()
			ctf_plot_param[cutname]['ymin'] = 10 ** ROOT.gPad.GetUymin()
		line_ymax = ctf_plot_param[cutname]['ymax']
		line_ymin = ctf_plot_param[cutname]['ymin']
		lb, ub = cut_bounds[fs_chn][cutname][0], cut_bounds[fs_chn][cutname][1]
		x_range = (ctf_plot_param[cutname]['xmax'] -
		           ctf_plot_param[cutname]['xmin'])
		y_range = (ctf_plot_param[cutname]['ymax'] - 
		           ctf_plot_param[cutname]['ymin'])
		arrow_len = x_range * arrow_len_coeff
		arrow_y = ctf_plot_param[cutname]['ymin'] + y_range * arrow_vert_pos[
		          ctf_plot_param[cutname]['scale']]
		#if ctf_plot_param[cutname]['scale'] == 'logy':
		#	arrow_y = 10 ** arrow_y
		if lb == '-infty': pass
		else:
			lb_line[fs_chn][cutname] = ROOT.TLine(lb, line_ymin, lb, line_ymax)
			lb_line[fs_chn][cutname].SetLineWidth(cut_linewidth)
			lb_line[fs_chn][cutname].Draw("same")
			lb_arrow[fs_chn][cutname] = ROOT.TArrow(
			lb, arrow_y, lb + arrow_len, arrow_y, arrow_size, arrow_style)
			lb_arrow[fs_chn][cutname].SetAngle(arrow_angle)
			lb_arrow[fs_chn][cutname].SetLineWidth(arrow_linewidth)
			lb_arrow[fs_chn][cutname].Draw()
		if ub == 'infty': pass
		else:
			ub_line[fs_chn][cutname] = ROOT.TLine(ub, line_ymin, ub, line_ymax)
			ub_line[fs_chn][cutname].SetLineWidth(cut_linewidth)
			ub_line[fs_chn][cutname].Draw("same")
			ub_arrow[fs_chn][cutname] = ROOT.TArrow(
			ub, arrow_y, ub - arrow_len, arrow_y, arrow_size, arrow_style)
			ub_arrow[fs_chn][cutname].SetAngle(arrow_angle)
			ub_arrow[fs_chn][cutname].SetLineWidth(arrow_linewidth)
			ub_arrow[fs_chn][cutname].Draw()
		if cumulative_cutstr != '': cumulative_cutstr += '&&'
		cumulative_cutstr += cutstring
		i_pad += 1
	canvases[fs_chn].cd(i_pad)
	legend = ROOT.TLegend(legend_x_bl, legend_y_bl, legend_x_tr, legend_y_tr)
	for pd_chn, legend_text in sig_legend_entry[fs_chn].items():
		legend.AddEntry(
			sig_hists[fs_chn][cutname][pd_chn], legend_text, sig_legend_style
		)
	for pd_chn, legend_text in bkg_legend_entry[fs_chn].items():
		legend.AddEntry(
			bkg_hists[fs_chn][cutname][pd_chn], legend_text, bkg_legend_style
		)
	legend.Draw()
	canvas_title = ROOT.TLatex(canvas_title_x, canvas_title_y, canvas_titles[fs_chn])
	canvas_title.SetTextSize(canvas_title_textsize)
	canvas_title.Draw()
	canvases[fs_chn].Print(plot_path + fs_chn + '_cutflow_plot_' + output_suffix
	                       + ".png")

###############
# mrec plots #
###############
sig_mrec_hists = OrderedDict()
bkg_mrec_hists = OrderedDict()
bkg_mrec_tot = OrderedDict()
canvas_mrec = OrderedDict()
for fs_chn in channels:
	sig_mrec_hists[fs_chn] = OrderedDict()
	bkg_mrec_hists[fs_chn] = OrderedDict()
	 
	for pd_chn, tree in sig_trees[fs_chn].items():
		hist_title = 'hist_' + fs_chn + '_' + pd_chn + '_mrec'
		hist_dscrp = hist_title
		# declare hist, one per cut per prod chn per fs chn
		sig_mrec_hists[fs_chn][pd_chn] = ROOT.TH1D(
			hist_title, hist_dscrp, 
			ctf_plot_param['mrec']['nbins'],
			ctf_plot_param['mrec']['xmin'],
			ctf_plot_param['mrec']['xmax'])
		# fill the cutted trees to the hists
		tree.Draw(ctf_plot_param['mrec']['xvar'] + ">>" + hist_title, 
		cumulative_cutstr, "goff")
		# store sum of squared weights to calculate stat uncertainty
		sig_mrec_hists[fs_chn][pd_chn].Sumw2()
		#sig_mrec_hists[fs_chn][pd_chn].Write()

	bkg_mrec_tot[fs_chn] = ROOT.TH1D(
		'hist_' + fs_chn + '_total_bkg_mrec',
		'hist_' + fs_chn + '_total_bkg_mrec',
		ctf_plot_param['mrec']['nbins'],
		ctf_plot_param['mrec']['xmin'],
		ctf_plot_param['mrec']['xmax']
	)
	
	for pd_chn, tree in bkg_trees[fs_chn].items():
		hist_title = 'hist_' + fs_chn + '_' + pd_chn + '_mrec'
		hist_dscrp = hist_title
		# declare hist, one per cut per prod chn per fs chn
		bkg_mrec_hists[fs_chn][pd_chn] = ROOT.TH1D(
			hist_title, hist_dscrp, 
			ctf_plot_param['mrec']['nbins'],
			ctf_plot_param['mrec']['xmin'],
			ctf_plot_param['mrec']['xmax'])
		# fill the cutted trees to the hists
		tree.Draw(ctf_plot_param['mrec']['xvar'] + ">>" + hist_title, 
		cumulative_cutstr, "goff")
		# store sum of squared weights to calculate stat uncertainty
		bkg_mrec_hists[fs_chn][pd_chn].Sumw2()
		#bkg_mrec_hists[fs_chn][pd_chn].Write()
		bkg_mrec_tot[fs_chn].Add(bkg_mrec_hists[fs_chn][pd_chn])


# rebin the sig + total bkg histograms
binning = OrderedDict()

for fs_chn in channels:
	binning[fs_chn] = OrderedDict()
	for pd_chn, hist in sig_mrec_hists[fs_chn].items():
		if bin_option == "auto":
			b = atb.AutoRebin(
				bkg_mrec_tot[fs_chn].Clone("b_bkg_copy"), 
				hist.Clone("h_sig_copy"), 
				0.2, 
				0.2
			)
			b.rebin() 
			binning[fs_chn][pd_chn] = array('d',b.getBinArray()) #enforcing type 
		elif bin_option == "manual":
			x_cur = ctf_plot_param['mrec']['xmin']
			binning[fs_chn][pd_chn] = array('d')
			while x_cur <= ctf_plot_param['mrec']['xmax']:
				binning[fs_chn][pd_chn].append(x_cur)
				x_cur += ctf_plot_param['mrec']['binsize']
			binning[fs_chn][pd_chn] = array('d',binning[fs_chn][pd_chn])

bkg_mrec_hists_rebin = OrderedDict()
sig_mrec_hists_rebin = OrderedDict()
bkg_mrec_stack_rebin = OrderedDict()
tot_mrec_hists = OrderedDict()
mrec_files = OrderedDict()
for fs_chn in channels:
	mrec_files[fs_chn] = OrderedDict()
	sig_mrec_hists_rebin[fs_chn] = OrderedDict()
	bkg_mrec_hists_rebin[fs_chn] = OrderedDict()
	bkg_mrec_stack_rebin[fs_chn] = OrderedDict()
	tot_mrec_hists[fs_chn] = OrderedDict()
	canvas_mrec[fs_chn] = ROOT.TCanvas(
		fs_chn + "_mrec", "m_rec plot for the " + fs_chn + " channel",
		hist_pixel_x * num_hist_x, hist_pixel_y * num_hist_y
	)
	canvas_mrec[fs_chn].Divide(num_hist_x, num_hist_y)
	pad_titles = OrderedDict()
	i_pad = 1
	for sig_pd_chn, sig_hist in sig_mrec_hists[fs_chn].items():
		mrec_files[fs_chn][sig_pd_chn] = ROOT.TFile(
			combine_path + 'mrec_' + fs_chn + '_' + sig_pd_chn + '_' +
			output_suffix + '_' + bin_option + '.root',
			'RECREATE'
		)
		mrec_files[fs_chn][sig_pd_chn].cd()
		tot_mrec_hists[fs_chn][sig_pd_chn] = ROOT.TH1D(
			'tot_mrec_' + fs_chn + '_' + sig_pd_chn,
			'tot_mrec_' + fs_chn + '_' + sig_pd_chn,
			len(binning[fs_chn][sig_pd_chn]) - 1,
			binning[fs_chn][sig_pd_chn]
		)
		canvas_mrec[fs_chn].cd(i_pad)
		sig_mrec_hists_rebin[fs_chn][sig_pd_chn] = atb.Rebin(
			sig_hist, binning[fs_chn][sig_pd_chn]
		)
		tot_mrec_hists[fs_chn][sig_pd_chn].Add(
			sig_mrec_hists_rebin[fs_chn][sig_pd_chn]
		)
		# set plotting style for the hists
		sig_mrec_hists_rebin[fs_chn][sig_pd_chn].SetLineColor(ROOT.kRed)
		sig_mrec_hists_rebin[fs_chn][sig_pd_chn].SetLineWidth(sig_linewidth)
		sig_mrec_hists_rebin[fs_chn][sig_pd_chn].SetLineStyle(sig_linestyle)
		sig_rebin_ymax = sig_mrec_hists_rebin[fs_chn][sig_pd_chn].GetBinContent(
			sig_mrec_hists_rebin[fs_chn][sig_pd_chn].GetMaximumBin()
		)
		sig_mrec_hists_rebin[fs_chn][sig_pd_chn].Sumw2()
		sig_mrec_hists_rebin[fs_chn][sig_pd_chn].Write()
		bkg_mrec_stack_rebin[fs_chn][sig_pd_chn] = ROOT.THStack(
			'hs_bkg_' + fs_chn + '_mrec_rebin', ""
		)
		bkg_mrec_hists_rebin[fs_chn][sig_pd_chn] = OrderedDict()
		for bkg_pd_chn, bkg_hist in bkg_mrec_hists[fs_chn].items():
			bkg_mrec_hists_rebin[fs_chn][sig_pd_chn][bkg_pd_chn] = atb.Rebin(
				bkg_hist, binning[fs_chn][sig_pd_chn]
			)
			tot_mrec_hists[fs_chn][sig_pd_chn].Add(
				bkg_mrec_hists_rebin[fs_chn][sig_pd_chn][bkg_pd_chn]
			)
			bkg_mrec_hists_rebin[fs_chn][sig_pd_chn][bkg_pd_chn].SetLineColor(
				bkg_linecolor)
			bkg_mrec_hists_rebin[fs_chn][sig_pd_chn][bkg_pd_chn].SetFillColor(
				bkg_fillcolors[bkg_pd_chn])
			bkg_mrec_hists_rebin[fs_chn][sig_pd_chn][bkg_pd_chn].SetLineWidth(
				bkg_linewidth)
			bkg_mrec_hists_rebin[fs_chn][sig_pd_chn][bkg_pd_chn].SetLineStyle(
				bkg_linestyle)
			bkg_mrec_stack_rebin[fs_chn][sig_pd_chn].Add(
				bkg_mrec_hists_rebin[fs_chn][sig_pd_chn][bkg_pd_chn]
			) 
			bkg_mrec_hists_rebin[fs_chn][sig_pd_chn][bkg_pd_chn].Sumw2()
			bkg_mrec_hists_rebin[fs_chn][sig_pd_chn][bkg_pd_chn].Write()

		tot_mrec_hists[fs_chn][sig_pd_chn].Write()
		# calculate the ymax of stacked bkgs
		bkg_mrec_stack_rebin_ymax = 0
		for i_bin in np.arange(1, len(binning[fs_chn][sig_pd_chn]) + 1):
			sum_bin_content = 0
			for bkg_pd_chn, hist in bkg_mrec_hists_rebin[fs_chn][sig_pd_chn].items():
				sum_bin_content += hist.GetBinContent(i_bin)
			if sum_bin_content > bkg_mrec_stack_rebin_ymax:
				bkg_mrec_stack_rebin_ymax = sum_bin_content
		graph_max = max(sig_rebin_ymax,bkg_mrec_stack_rebin_ymax)
		# automatic adjustment of ymax for the pad
		if (ctf_plot_param['mrec']['ymax'] *
		    pad_ymax_ub[ctf_plot_param['mrec']['scale']] < graph_ymax or
		    ctf_plot_param['mrec']['ymax'] * 
		    pad_ymax_lb[ctf_plot_param['mrec']['scale']] > graph_ymax):
			ctf_plot_param['mrec']['ymax'] = graph_ymax * pad_ymax_ratio[
			                                  ctf_plot_param['mrec']['scale']]
		if ctf_plot_param['mrec']['scale'] == 'logy': ROOT.gPad.SetLogy()
		bkg_mrec_stack_rebin[fs_chn][sig_pd_chn].SetMinimum(
			ctf_plot_param['mrec']['ymin'])
		bkg_mrec_stack_rebin[fs_chn][sig_pd_chn].SetMaximum(
			ctf_plot_param['mrec']['ymax'])
		bkg_mrec_stack_rebin[fs_chn][sig_pd_chn].Draw(bkg_stack_options)
		bkg_mrec_stack_rebin[fs_chn][sig_pd_chn].GetHistogram().SetXTitle(
			ctf_plot_param['mrec']['xtitle'])
		bkg_mrec_stack_rebin[fs_chn][sig_pd_chn].GetHistogram().SetYTitle(
			'Events/bin')
		bkg_mrec_stack_rebin[fs_chn][sig_pd_chn].GetHistogram().SetTitleSize(
			axis_title_textsize, "xy")
		ROOT.gPad.Update()
		sig_mrec_hists_rebin[fs_chn][sig_pd_chn].SetMinimum(
			ctf_plot_param['mrec']['ymin'])
		sig_mrec_hists_rebin[fs_chn][sig_pd_chn].SetMaximum(
			ctf_plot_param['mrec']['ymax'])
		sig_mrec_hists_rebin[fs_chn][sig_pd_chn].Draw("hist, same")
		ROOT.gPad.Update()
		if sig_pd_chn == '0p5': scalar_mass = "0.5"
		else: scalar_mass = sig_pd_chn
		pad_titles[sig_pd_chn] = ROOT.TLatex(
			pad_title_x, pad_title_y, "m_{s} = " + scalar_mass + " GeV"
		)
		pad_titles[sig_pd_chn].SetNDC()
		pad_titles[sig_pd_chn].SetTextSize(pad_title_textsize)
		pad_titles[sig_pd_chn].Draw()
		if i_pad == 1:
			canvas_mrec_title = ROOT.TLatex(0, 0.95, fs_chn) 
			canvas_mrec_title.SetNDC()
			canvas_mrec_title.SetTextSize(0.1)
			canvas_mrec_title.Draw()
		ROOT.gPad.Modified()
		ROOT.gPad.Update()
		i_pad += 1
	canvas_mrec[fs_chn].Print(plot_path + fs_chn + '_mrec_' + output_suffix
		                          + '_' + bin_option+ "_binning.png")

ctf_hist_file.Close()
