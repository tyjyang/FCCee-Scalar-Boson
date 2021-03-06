import ROOT
import numpy as np
import time
import ntuplizer as ntp 
import helper as hlp 
import cutflow as ctf 
from collections import OrderedDict

# variables
ntuple_path = '../ntuples-no-photon-veto/'
delphes_path = '/scratch5/arapyan/fcc_ee/scalar_delphes_idea/'
channels = ['electron', 'muon']
lumi = 115.4
output_suffix = 'IDEA_500MeV_no_photon_veto'
#sig_ntuple_filenames = {
#'0p5':('eeZS_p5:electron-muon:pt-eta-phi-cos_theta-alpha-'
#       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root'),
#'2'  :('eeZS_2:electron-muon:pt-eta-phi-cos_theta-alpha-'
#       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root'),
#'5'  :('eeZS_5:electron-muon:pt-eta-phi-cos_theta-alpha-'
#       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root'),
#'10' :('eeZS_10:electron-muon:pt-eta-phi-cos_theta-alpha-'
#       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root'),
#'15' :('eeZS_15:electron-muon:pt-eta-phi-cos_theta-alpha-'
#       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root'),
#'25' :('eeZS_25:electron-muon:pt-eta-phi-cos_theta-alpha-'
#       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')
#}      
#bkg_ntuple_filenames = {
#'2f'       :('ee2fermion_mutau:electron-muon:pt-eta-phi-cos_theta-'
#             'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root'),
#'4f' :('ee4lepton_mutau:electron-muon:pt-eta-phi-cos_theta-'
#             'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root'),
#'4fqq' :('ee4lepquark_mutau:electron-muon:pt-eta-phi-cos_theta-'
#             'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')
#}
sig_ntuple_filenames = {
'0p5':('eeZS_p5_photon500:electron-muon:pt-eta-phi-cos_theta-alpha-'
       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root'),
'2'  :('eeZS_2_photon500:electron-muon:pt-eta-phi-cos_theta-alpha-'
       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root'),
'5'  :('eeZS_5_photon500:electron-muon:pt-eta-phi-cos_theta-alpha-'
       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root'),
'10' :('eeZS_10_photon500:electron-muon:pt-eta-phi-cos_theta-alpha-'
       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root'),
'15' :('eeZS_15_photon500:electron-muon:pt-eta-phi-cos_theta-alpha-'
       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root'),
'25' :('eeZS_25_photon500:electron-muon:pt-eta-phi-cos_theta-alpha-'
       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')
}      
bkg_ntuple_filenames = {
'2f'       :('ee2fermion_mutau_photon500:electron-muon:pt-eta-phi-cos_theta-'
             'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root'),
'4f' :('ee4lepton_mutau_photon500:electron-muon:pt-eta-phi-cos_theta-'
             'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root'),
'4fqq' :('ee4lepquark_mutau_photon500:electron-muon:pt-eta-phi-cos_theta-'
             'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')
}
# get the full paths to the ntuple files 
sig_ntuple_filepaths = {}
bkg_ntuple_filepaths = {}
for i, f in sig_ntuple_filenames.items(): 
	sig_ntuple_filepaths[i] = ntuple_path + f 
for i, f in bkg_ntuple_filenames.items(): 
	bkg_ntuple_filepaths[i] = ntuple_path + f 

# get pointers to the ntuple trees and set weights by getting the number of
# events from the delphes file
ntuple_files = {}
electrons = OrderedDict()
muons = OrderedDict()
w = {}
for key, f in sig_ntuple_filepaths.items():
	ntuple_files[key] = ROOT.TFile.Open(f)
	electrons[key] = ntuple_files[key].Get('electron')
	muons[key] = ntuple_files[key].Get('muon')
	delphes_file = hlp.get_delphes_filename(f)
	delphes_filepath = delphes_path + delphes_file
	w[key] = ctf.get_normalization_factor(delphes_filepath, lumi)
	electrons[key].SetWeight(w[key])
	muons[key].SetWeight(w[key])
for key, f in bkg_ntuple_filepaths.items():
	ntuple_files[key] = ROOT.TFile.Open(f)
	electrons[key] = ntuple_files[key].Get('electron')
	muons[key] = ntuple_files[key].Get('muon')
	delphes_file = hlp.get_delphes_filename(f)
	delphes_filepath = delphes_path + delphes_file
	w[key] = ctf.get_normalization_factor(delphes_filepath, lumi)
	electrons[key].SetWeight(w[key])
	muons[key].SetWeight(w[key])
for key in muons:
	print muons[key]
# create rootfile to save the histograms
cutflow_file = ROOT.TFile("cutflow.root","RECREATE")
cutflow_file.cd()
# specifying the cuts in the cutflow
electron_cuts = {}
muon_cuts = {}
cut_names = ['anlge','momentum','alpha','m_inv','cos_theat_p_missing']

e_angle_cut_low = -0.9
e_angle_cut_high = 0.9
electron_cuts['angle'] = (
"TMath::abs(cos_theta_1) < 0.9 &&"
"TMath::abs(cos_theta_2) < 0.9")
#electron_cuts['angle'] = (
#"(leading_eta < 1.47 && leading_eta > -1.47) &&"
#"(trailing_eta < 1.47 && trailing_eta > -1.47)")
mu_angle_cut_low = -0.94
mu_angle_cut_high = 0.94
muon_cuts['angle'] = (
"(cos_theta_1 < 0.94 && cos_theta_1 > -0.94) &&"
"(cos_theta_2 < 0.94 && cos_theta_2 > -0.94)")

e_momentum_cut_low = 27
mu_momentum_cut_low = 30 
electron_cuts['momentum'] = ("TMath::Max(p_mag_1, p_mag_2) > 27 &&"
                             "TMath::Min(p_mag_1, p_mag_2) > 20")
muon_cuts['momentum'] = ("TMath::Max(p_mag_1, p_mag_2) > 30 &&"
                         "TMath::Min(p_mag_1, p_mag_2) > 20")

e_alpha_cut_low = 0.11
e_alpha_cut_high = 2
mu_alpha_cut_low = e_alpha_cut_low
mu_alpha_cut_high = e_alpha_cut_high
electron_cuts['alpha'] = "alpha > 0.11 && alpha < 2.0"
muon_cuts['alpha'] = electron_cuts['alpha']

e_m_inv_cut_low = 20
e_m_inv_cut_high = 100
mu_m_inv_cut_low = e_m_inv_cut_low
mu_m_inv_cut_high = e_m_inv_cut_high
electron_cuts['m_inv'] = "m_inv > 20 && m_inv < 100"
muon_cuts['m_inv'] = electron_cuts['m_inv']

e_cos_theta_p_missing_cut_low = -0.98
e_cos_theta_p_missing_cut_high = 0.98
mu_cos_theta_p_missing_cut_low = e_cos_theta_p_missing_cut_low
mu_cos_theta_p_missing_cut_high = e_cos_theta_p_missing_cut_high
electron_cuts['cos_theta_p_missing'] = (
"(p_mag_missing<=2 || (p_mag_missing>2&&"
"(cos_theta_p_missing<0.98&&cos_theta_p_missing>-0.98)))")
muon_cuts['cos_theta_p_missing'] = electron_cuts['cos_theta_p_missing']

hist_pixel_x = 600
hist_pixel_y = 450
num_hist_x = 3
num_hist_y = 2
'''
c_electron = ROOT.TCanvas("electron_cutflow","cutflow plots for Z -> ee at 91.2 GeV",
                           hist_pixel_x * num_hist_x, hist_pixel_y * num_hist_y)
c_electron.Divide(num_hist_x, num_hist_y)
print  electrons['0p5'].GetEntries()
print ('normalized num of Z-> ee evts from singal with m_s = 0.5 GeV: ',
       electrons['0p5'].GetEntries()*w['0p5'])
print ('normalized num of Z-> ee evts from singal with m_s = 5 GeV: ',
       electrons['5'].GetEntries()*w['5'])
print ('normalized num of Z-> ee evts from singal with m_s = 25 GeV: ',
       electrons['25'].GetEntries()*w['25'])
print ('normalized num of Z-> ee evts from 2-fermion background: ',
       electrons['2f'].GetEntries()*w['2f'])
print ('normalized num of Z-> ee evts from 4-fermion background: ',
       electrons['4f'].GetEntries()*w['4f'])

### first cut for the ee channel ###
c_electron.cd(1)
# get the entrylist after the cut
electrons['0p5'].Draw(">>e_0p5_cutlist1",electron_cuts['alpha'],"entrylist")
electrons['5'].Draw(">>e_5_cutlist1",electron_cuts['alpha'],"entrylist")
electrons['25'].Draw(">>e_25_cutlist1",electron_cuts['alpha'],"entrylist")
electrons['2f'].Draw(">>e_2f_cutlist1",electron_cuts['alpha'],"entrylist")
electrons['4f'].Draw(">>e_4f_cutlist1",electron_cuts['alpha'],"entrylist")
e_0p5_cutlist1 = ROOT.gDirectory.Get("e_0p5_cutlist1")
e_5_cutlist1 = ROOT.gDirectory.Get("e_5_cutlist1")
e_25_cutlist1 = ROOT.gDirectory.Get("e_25_cutlist1")
e_2f_cutlist1 = ROOT.gDirectory.Get("e_2f_cutlist1")
e_4f_cutlist1 = ROOT.gDirectory.Get("e_4f_cutlist1")
print ('num of singal evts with m_s = 0.5 GeV passing alpha cut: ', 
       e_0p5_cutlist1.GetN()*w['0p5'])
print ('num of singal evts with m_s = 5 GeV passing alpha cut: ', 
       e_5_cutlist1.GetN()*w['5'])
print ('num of singal evts with m_s = 25 GeV passing alpha cut: ', 
       e_25_cutlist1.GetN()*w['25'])
print ('num of 2-fermion bkg evts passing alpha cut: ', 
       e_2f_cutlist1.GetN()*w['2f'])
print ('num of 4-fermion bkg evts passing alpha cut: ', 
       e_4f_cutlist1.GetN()*w['4f'])
# plot the events vs. var being cut, up to all cuts applied before
hs_sig_e_1 = ROOT.THStack("hs_sig_e_1","")
hs_bkg_e_1 = ROOT.THStack("hs_bkg_e_1","")
e_1_xlow = 0
e_1_xhigh = 3.1
e_1_nbins = 31
e_1_descrp = "Z #rightarrow e^{+}e^{-} vs. #alpha @ 91.2 GeV"
hist_e_0p5_1 = ROOT.TH1F("e_0p5_alpha",
e_1_descrp, e_1_nbins, e_1_xlow, e_1_xhigh)
hist_e_5_1 = ROOT.TH1F("e_5_alpha",
e_1_descrp, e_1_nbins, e_1_xlow, e_1_xhigh)
hist_e_25_1 = ROOT.TH1F("e_25_alpha",
e_1_descrp, e_1_nbins, e_1_xlow, e_1_xhigh)
hist_e_2f_1 = ROOT.TH1F("e_2f_alpha",
e_1_descrp, e_1_nbins, e_1_xlow, e_1_xhigh)
hist_e_4f_1 = ROOT.TH1F("e_4f_alpha",
e_1_descrp, e_1_nbins, e_1_xlow, e_1_xhigh)
electrons['0p5'].Draw("alpha>>e_0p5_alpha", "", "goff")
electrons['5'].Draw("alpha>>e_5_alpha", "", "goff")
electrons['25'].Draw("alpha>>e_25_alpha","","goff")
electrons['2f'].Draw("alpha>>e_2f_alpha", "", "goff")
electrons['4f'].Draw("alpha>>e_4f_alpha", "", "goff")
#hist_e_0p5_1.SetDirectory(0)
#hist_e_5_1.SetDirectory(0)
#hist_e_25_1.SetDirectory(0)
#hist_e_2f_1.SetDirectory(0)
#hist_e_4f_1.SetDirectory(0)
hist_e_0p5_1.SetLineColor(ROOT.kRed)
hist_e_0p5_1.SetLineWidth(2)
hist_e_0p5_1.SetLineStyle(1)
hist_e_5_1.SetLineColor(ROOT.kBlue+2)
hist_e_5_1.SetLineWidth(2)
hist_e_5_1.SetLineStyle(1)
hist_e_25_1.SetLineColor(ROOT.kGreen+2)
hist_e_25_1.SetLineWidth(2)
hist_e_25_1.SetLineStyle(1)
hist_e_2f_1.SetLineColor(ROOT.kBlack)
hist_e_2f_1.SetFillColor(ROOT.kGreen)
hist_e_2f_1.SetLineWidth(1)
hist_e_2f_1.SetLineStyle(1)
hist_e_4f_1.SetLineColor(ROOT.kBlack)
hist_e_4f_1.SetFillColor(ROOT.kYellow)
hist_e_4f_1.SetLineWidth(1)
hist_e_4f_1.SetLineStyle(1)

hs_bkg_e_1.SetMinimum(0.1)
hs_sig_e_1.SetMinimum(0.1)


hs_sig_e_1.Add(hist_e_0p5_1)
hs_sig_e_1.Add(hist_e_5_1)
hs_sig_e_1.Add(hist_e_25_1)
hs_bkg_e_1.Add(hist_e_2f_1)
hs_bkg_e_1.Add(hist_e_4f_1)

ymin = []
ymax = []
xmin = []
xmax = []
ROOT.gPad.SetLogy()
hs_bkg_e_1.Draw("hist")
hs_bkg_e_1.GetHistogram().SetXTitle('#alpha [rad]')
hs_bkg_e_1.GetHistogram().SetYTitle('Events/0.1 rad')
hs_bkg_e_1.GetHistogram().SetTitleSize(0.05, "xy")
ROOT.gPad.Update()
ymin.append(ROOT.gPad.GetUymin())
ymax.append(ROOT.gPad.GetUymax())
xmin.append(ROOT.gPad.GetUxmin())
xmax.append(ROOT.gPad.GetUxmax())
hs_sig_e_1.Draw("hist, nostack, same")
ROOT.gPad.Update()
ymin.append(ROOT.gPad.GetUymin())
ymax.append(ROOT.gPad.GetUymax())
xmin.append(ROOT.gPad.GetUxmin())
xmax.append(ROOT.gPad.GetUxmax())
line_e_1_low = ROOT.TLine(e_alpha_cut_low, 10**min(ymin),
                          e_alpha_cut_low, 10**max(ymax))
line_e_1_low.SetLineWidth(2)
line_e_1_low.Draw("same")
line_e_1_high = ROOT.TLine(e_alpha_cut_high, 10**min(ymin),
                           e_alpha_cut_high, 10**max(ymax))
line_e_1_high.SetLineWidth(2)
line_e_1_high.Draw("same")
arrow_len = (max(xmax) - min(xmin)) * 0.1 
arrow_e_1_low = ROOT.TArrow(e_alpha_cut_low, 10**max(ymax)*0.01,
                e_alpha_cut_low + arrow_len, 10**max(ymax)*0.01, 0.005, "|>") 
arrow_e_1_low.SetAngle(60)
arrow_e_1_low.SetLineWidth(2)
arrow_e_1_low.Draw()
arrow_e_1_high = ROOT.TArrow(e_alpha_cut_high, 10**max(ymax)*0.01,
                 e_alpha_cut_high - arrow_len, 10**max(ymax)*0.01, 0.005, "|>") 
arrow_e_1_high.SetAngle(60)
arrow_e_1_high.SetLineWidth(2)
arrow_e_1_high.Draw()
#ROOT.gPad.Update()
hist_e_0p5_1.Write()
hist_e_5_1.Write()
hist_e_25_1.Write()
hist_e_2f_1.Write()
hist_e_4f_1.Write()

### second cut for the ee channel ###
c_electron.cd(2)
e_cut_2 = electron_cuts['alpha']+'&&'+electron_cuts['angle']
# get the entrylist after the cut
electrons['0p5'].Draw(">>e_0p5_cutlist2",e_cut_2,"entrylist")
electrons['5'].Draw(">>e_5_cutlist2",e_cut_2,"entrylist")
electrons['25'].Draw(">>e_25_cutlist2",e_cut_2,"entrylist")
electrons['2f'].Draw(">>e_2f_cutlist2",e_cut_2,"entrylist")
electrons['4f'].Draw(">>e_4f_cutlist2",e_cut_2,"entrylist")
e_0p5_cutlist2 = ROOT.gDirectory.Get("e_0p5_cutlist2")
e_5_cutlist2 = ROOT.gDirectory.Get("e_5_cutlist2")
e_25_cutlist2 = ROOT.gDirectory.Get("e_25_cutlist2")
e_2f_cutlist2 = ROOT.gDirectory.Get("e_2f_cutlist2")
e_4f_cutlist2 = ROOT.gDirectory.Get("e_4f_cutlist2")
print ('num of singal evts with m_s = 0.5 GeV passing angle cut: ', 
       e_0p5_cutlist2.GetN()*w['0p5'])
print ('num of singal evts with m_s = 5 GeV passing angle cut: ', 
       e_5_cutlist2.GetN()*w['5'])
print ('num of singal evts with m_s = 25 GeV passing angle cut: ', 
       e_25_cutlist2.GetN()*w['25'])
print ('num of 2-fermion bkg evts passing angle cut: ', 
       e_2f_cutlist2.GetN()*w['2f'])
print ('num of 4-fermion bkg evts passing angle cut: ', 
       e_4f_cutlist2.GetN()*w['4f'])
# plot the events vs. var being cut, up to all cuts applied before
hs_sig_e_2 = ROOT.THStack("hs_sig_e_2","")
hs_bkg_e_2 = ROOT.THStack("hs_bkg_e_2","")
e_2_xlow = 0
e_2_xhigh = 1
e_2_nbins = 15
e_2_descrp = "Z #rightarrow e^{+}e^{-} vs. |cos(#theta_{1})| @ 91.2 GeV"
hist_e_0p5_2 = ROOT.TH1F("e_0p5_angle",
e_2_descrp, e_2_nbins, e_2_xlow, e_2_xhigh)
hist_e_5_2 = ROOT.TH1F("e_5_angle",
e_2_descrp, e_2_nbins, e_2_xlow, e_2_xhigh)
hist_e_25_2 = ROOT.TH1F("e_25_angle",
e_2_descrp, e_2_nbins, e_2_xlow, e_2_xhigh)
hist_e_2f_2 = ROOT.TH1F("e_2f_angle",
e_2_descrp, e_2_nbins, e_2_xlow, e_2_xhigh)
hist_e_4f_2 = ROOT.TH1F("e_4f_angle",
e_2_descrp, e_2_nbins, e_2_xlow, e_2_xhigh)
electrons['0p5'].Draw("abs(leading_cos_theta)>>e_0p5_angle", electron_cuts['alpha'], "goff")
electrons['5'].Draw("abs(leading_cos_theta)>>e_5_angle", electron_cuts['alpha'], "goff")
electrons['25'].Draw("abs(leading_cos_theta)>>e_25_angle", electron_cuts['alpha'],"goff")
electrons['2f'].Draw("abs(leading_cos_theta)>>e_2f_angle", electron_cuts['alpha'], "goff")
electrons['4f'].Draw("abs(leading_cos_theta)>>e_4f_angle", electron_cuts['alpha'], "goff")
#hist_e_0p5_2.SetDirectory(0)
#hist_e_5_2.SetDirectory(0)
#hist_e_25_2.SetDirectory(0)
#hist_e_2f_2.SetDirectory(0)
#hist_e_4f_2.SetDirectory(0)
hist_e_0p5_2.SetLineColor(ROOT.kRed)
hist_e_0p5_2.SetLineWidth(2)
hist_e_0p5_2.SetLineStyle(1)
hist_e_5_2.SetLineColor(ROOT.kBlue+2)
hist_e_5_2.SetLineWidth(2)
hist_e_5_2.SetLineStyle(1)
hist_e_25_2.SetLineColor(ROOT.kGreen+2)
hist_e_25_2.SetLineWidth(2)
hist_e_25_2.SetLineStyle(1)
hist_e_2f_2.SetLineColor(ROOT.kBlack)
hist_e_2f_2.SetFillColor(ROOT.kGreen)
hist_e_2f_2.SetLineWidth(1)
hist_e_2f_2.SetLineStyle(1)
hist_e_4f_2.SetLineColor(ROOT.kBlack)
hist_e_4f_2.SetFillColor(ROOT.kYellow)
hist_e_4f_2.SetLineWidth(1)
hist_e_4f_2.SetLineStyle(1)

hs_bkg_e_2.SetMinimum(0.1)
hs_sig_e_2.SetMinimum(0.1)


hs_sig_e_2.Add(hist_e_0p5_2)
hs_sig_e_2.Add(hist_e_5_2)
hs_sig_e_2.Add(hist_e_25_2)
hs_bkg_e_2.Add(hist_e_2f_2)
hs_bkg_e_2.Add(hist_e_4f_2)

ymin = []
ymax = []
xmin = []
xmax = []
ROOT.gPad.SetLogy()
hs_bkg_e_2.Draw("hist")
hs_bkg_e_2.GetHistogram().SetXTitle('|cos(#theta_{1})|')
hs_bkg_e_2.GetHistogram().SetYTitle('Events/0.0667')
hs_bkg_e_2.GetHistogram().SetTitleSize(0.05, "xy")
ROOT.gPad.Update()
ymin.append(ROOT.gPad.GetUymin())
ymax.append(ROOT.gPad.GetUymax())
xmin.append(ROOT.gPad.GetUxmin())
xmax.append(ROOT.gPad.GetUxmax())
hs_sig_e_2.Draw("hist, nostack, same")
ROOT.gPad.Update()
ymin.append(ROOT.gPad.GetUymin())
ymax.append(ROOT.gPad.GetUymax())
xmin.append(ROOT.gPad.GetUxmin())
xmax.append(ROOT.gPad.GetUxmax())
line_e_2_high = ROOT.TLine(e_angle_cut_high, 10**min(ymin),
                           e_angle_cut_high, 10**max(ymax))
line_e_2_high.SetLineWidth(2)
line_e_2_high.Draw("same")
arrow_len = (max(xmax) - min(xmin)) * 0.1 
arrow_e_2_high = ROOT.TArrow(e_angle_cut_high, 10**max(ymax)*0.01,
                 e_angle_cut_high - arrow_len, 10**max(ymax)*0.01, 0.005, "|>") 
arrow_e_2_high.SetAngle(60)
arrow_e_2_high.SetLineWidth(2)
arrow_e_2_high.Draw()
#ROOT.gPad.Update()
hist_e_0p5_2.Write()
hist_e_5_2.Write()
hist_e_25_2.Write()
hist_e_2f_2.Write()
hist_e_4f_2.Write()

### third cut for the ee channel ###
c_electron.cd(3)
e_cut_3 = e_cut_2+'&&'+electron_cuts['momentum']
# get the entrylist after the cut
electrons['0p5'].Draw(">>e_0p5_cutlist3",e_cut_3,"entrylist")
electrons['5'].Draw(">>e_5_cutlist3",e_cut_3,"entrylist")
electrons['25'].Draw(">>e_25_cutlist3",e_cut_3,"entrylist")
electrons['2f'].Draw(">>e_2f_cutlist3",e_cut_3,"entrylist")
electrons['4f'].Draw(">>e_4f_cutlist3",e_cut_3,"entrylist")
e_0p5_cutlist3 = ROOT.gDirectory.Get("e_0p5_cutlist3")
e_5_cutlist3 = ROOT.gDirectory.Get("e_5_cutlist3")
e_25_cutlist3 = ROOT.gDirectory.Get("e_25_cutlist3")
e_2f_cutlist3 = ROOT.gDirectory.Get("e_2f_cutlist3")
e_4f_cutlist3 = ROOT.gDirectory.Get("e_4f_cutlist3")
print ('num of singal evts with m_s = 0.5 GeV passing momentum cut: ', 
       e_0p5_cutlist3.GetN()*w['0p5'])
print ('num of singal evts with m_s = 5 GeV passing momentum cut: ', 
       e_5_cutlist3.GetN()*w['5'])
print ('num of singal evts with m_s = 25 GeV passing momentum cut: ', 
       e_25_cutlist3.GetN()*w['25'])
print ('num of 2-fermion bkg evts passing momentum cut: ', 
       e_2f_cutlist3.GetN()*w['2f'])
print ('num of 4-fermion bkg evts passing momentum cut: ', 
       e_4f_cutlist3.GetN()*w['4f'])
# plot the events vs. var being cut, up to all cuts applied before
hs_sig_e_3 = ROOT.THStack("hs_sig_e_3","")
hs_bkg_e_3 = ROOT.THStack("hs_bkg_e_3","")
e_3_xlow = 0
e_3_xhigh = 45
e_3_nbins = 45
e_3_descrp = "Z #rightarrow e^{+}e^{-} vs. |p_{1}| @ 91.2 GeV"
hist_e_0p5_3 = ROOT.TH1F("e_0p5_momentum",
e_3_descrp, e_3_nbins, e_3_xlow, e_3_xhigh)
hist_e_5_3 = ROOT.TH1F("e_5_momentum",
e_3_descrp, e_3_nbins, e_3_xlow, e_3_xhigh)
hist_e_25_3 = ROOT.TH1F("e_25_momentum",
e_3_descrp, e_3_nbins, e_3_xlow, e_3_xhigh)
hist_e_2f_3 = ROOT.TH1F("e_2f_momentum",
e_3_descrp, e_3_nbins, e_3_xlow, e_3_xhigh)
hist_e_4f_3 = ROOT.TH1F("e_4f_momentum",
e_3_descrp, e_3_nbins, e_3_xlow, e_3_xhigh)
electrons['0p5'].Draw("leading_p_mag>>e_0p5_momentum", e_cut_2, "goff")
electrons['5'].Draw("leading_p_mag>>e_5_momentum", e_cut_2, "goff")
electrons['25'].Draw("leading_p_mag>>e_25_momentum", e_cut_2, "goff")
electrons['2f'].Draw("leading_p_mag>>e_2f_momentum", e_cut_2, "goff")
electrons['4f'].Draw("leading_p_mag>>e_4f_momentum", e_cut_2, "goff")
#hist_e_0p5_3.SetDirectory(0)
#hist_e_5_3.SetDirectory(0)
#hist_e_25_3.SetDirectory(0)
#hist_e_2f_3.SetDirectory(0)
#hist_e_4f_3.SetDirectory(0)
hist_e_0p5_3.SetLineColor(ROOT.kRed)
hist_e_0p5_3.SetLineWidth(2)
hist_e_0p5_3.SetLineStyle(1)
hist_e_5_3.SetLineColor(ROOT.kBlue+2)
hist_e_5_3.SetLineWidth(2)
hist_e_5_3.SetLineStyle(1)
hist_e_25_3.SetLineColor(ROOT.kGreen+2)
hist_e_25_3.SetLineWidth(2)
hist_e_25_3.SetLineStyle(1)
hist_e_2f_3.SetLineColor(ROOT.kBlack)
hist_e_2f_3.SetFillColor(ROOT.kGreen)
hist_e_2f_3.SetLineWidth(1)
hist_e_2f_3.SetLineStyle(1)
hist_e_4f_3.SetLineColor(ROOT.kBlack)
hist_e_4f_3.SetFillColor(ROOT.kYellow)
hist_e_4f_3.SetLineWidth(1)
hist_e_4f_3.SetLineStyle(1)

hs_bkg_e_3.SetMinimum(0.1)
hs_sig_e_3.SetMinimum(0.1)


hs_sig_e_3.Add(hist_e_0p5_3)
hs_sig_e_3.Add(hist_e_5_3)
hs_sig_e_3.Add(hist_e_25_3)
hs_bkg_e_3.Add(hist_e_2f_3)
hs_bkg_e_3.Add(hist_e_4f_3)

ymin = []
ymax = []
xmin = []
xmax = []
ROOT.gPad.SetLogy()
hs_bkg_e_3.Draw("hist")
hs_bkg_e_3.GetHistogram().SetXTitle('|p_{1}| [GeV]')
hs_bkg_e_3.GetHistogram().SetYTitle('Events/1 GeV')
hs_bkg_e_3.GetHistogram().SetTitleSize(0.05, "xy")
ROOT.gPad.Update()
ymin.append(ROOT.gPad.GetUymin())
ymax.append(ROOT.gPad.GetUymax())
xmin.append(ROOT.gPad.GetUxmin())
xmax.append(ROOT.gPad.GetUxmax())
hs_sig_e_3.Draw("hist, nostack, same")
ROOT.gPad.Update()
ymin.append(ROOT.gPad.GetUymin())
ymax.append(ROOT.gPad.GetUymax())
xmin.append(ROOT.gPad.GetUxmin())
xmax.append(ROOT.gPad.GetUxmax())
line_e_3_low = ROOT.TLine(e_momentum_cut_low, 10**min(ymin),
                          e_momentum_cut_low, 10**max(ymax))
line_e_3_low.SetLineWidth(2)
line_e_3_low.Draw("same")
arrow_len = (max(xmax) - min(xmin)) * 0.1 
arrow_e_3_low = ROOT.TArrow(e_momentum_cut_low, 10**max(ymax)*0.01,
                e_momentum_cut_low + arrow_len, 10**max(ymax)*0.01, 0.005, "|>") 
arrow_e_3_low.SetAngle(60)
arrow_e_3_low.SetLineWidth(2)
arrow_e_3_low.Draw()
#ROOT.gPad.Update()
hist_e_0p5_3.Write()
hist_e_5_3.Write()
hist_e_25_3.Write()
hist_e_2f_3.Write()
hist_e_4f_3.Write()

### fourth cut for the ee channel ###
c_electron.cd(4)
e_cut_4 = e_cut_3+'&&'+electron_cuts['cos_theta_p_missing']
# get the entrylist after the cut
electrons['0p5'].Draw(">>e_0p5_cutlist4",e_cut_4,"entrylist")
electrons['5'].Draw(">>e_5_cutlist4",e_cut_4,"entrylist")
electrons['25'].Draw(">>e_25_cutlist4",e_cut_4,"entrylist")
electrons['2f'].Draw(">>e_2f_cutlist4",e_cut_4,"entrylist")
electrons['4f'].Draw(">>e_4f_cutlist4",e_cut_4,"entrylist")
e_0p5_cutlist4 = ROOT.gDirectory.Get("e_0p5_cutlist4")
e_5_cutlist4 = ROOT.gDirectory.Get("e_5_cutlist4")
e_25_cutlist4 = ROOT.gDirectory.Get("e_25_cutlist4")
e_2f_cutlist4 = ROOT.gDirectory.Get("e_2f_cutlist4")
e_4f_cutlist4 = ROOT.gDirectory.Get("e_4f_cutlist4")
print ('num of singal evts with m_s = 0.5 GeV passing cos_theta_p_missing cut: ', 
       e_0p5_cutlist4.GetN()*w['0p5'])
print ('num of singal evts with m_s = 5 GeV passing cos_theta_p_missing cut: ', 
       e_5_cutlist4.GetN()*w['5'])
print ('num of singal evts with m_s = 25 GeV passing cos_theta_p_missing cut: ', 
       e_25_cutlist4.GetN()*w['25'])
print ('num of 2-fermion bkg evts passing cos_theta_p_missing cut: ', 
       e_2f_cutlist4.GetN()*w['2f'])
print ('num of 4-fermion bkg evts passing cos_theta_p_missing cut: ', 
       e_4f_cutlist4.GetN()*w['4f'])
# plot the events vs. var being cut, up to all cuts applied before
hs_sig_e_4 = ROOT.THStack("hs_sig_e_4","")
hs_bkg_e_4 = ROOT.THStack("hs_bkg_e_4","")
e_4_xlow = 0
e_4_xhigh = 1
e_4_nbins = 15
e_4_descrp = "Z #rightarrow e^{+}e^{-} vs. |cos(#theta_{miss})| @ 91.2 GeV"
hist_e_0p5_4 = ROOT.TH1F("e_0p5_cos_theta_p_missing",
e_4_descrp, e_4_nbins, e_4_xlow, e_4_xhigh)
hist_e_5_4 = ROOT.TH1F("e_5_cos_theta_p_missing",
e_4_descrp, e_4_nbins, e_4_xlow, e_4_xhigh)
hist_e_25_4 = ROOT.TH1F("e_25_cos_theta_p_missing",
e_4_descrp, e_4_nbins, e_4_xlow, e_4_xhigh)
hist_e_2f_4 = ROOT.TH1F("e_2f_cos_theta_p_missing",
e_4_descrp, e_4_nbins, e_4_xlow, e_4_xhigh)
hist_e_4f_4 = ROOT.TH1F("e_4f_cos_theta_p_missing",
e_4_descrp, e_4_nbins, e_4_xlow, e_4_xhigh)
electrons['0p5'].Draw("abs(cos_theta_p_missing)>>e_0p5_cos_theta_p_missing", e_cut_3, "goff")
electrons['5'].Draw("abs(cos_theta_p_missing)>>e_5_cos_theta_p_missing", e_cut_3, "goff")
electrons['25'].Draw("abs(cos_theta_p_missing)>>e_25_cos_theta_p_missing", e_cut_3,"goff")
electrons['2f'].Draw("abs(cos_theta_p_missing)>>e_2f_cos_theta_p_missing", e_cut_3, "goff")
electrons['4f'].Draw("abs(cos_theta_p_missing)>>e_4f_cos_theta_p_missing", e_cut_3, "goff")
#hist_e_0p5_4.SetDirectory(0)
#hist_e_5_4.SetDirectory(0)
#hist_e_25_4.SetDirectory(0)
#hist_e_2f_4.SetDirectory(0)
#hist_e_4f_4.SetDirectory(0)
hist_e_0p5_4.SetLineColor(ROOT.kRed)
hist_e_0p5_4.SetLineWidth(2)
hist_e_0p5_4.SetLineStyle(1)
hist_e_5_4.SetLineColor(ROOT.kBlue+2)
hist_e_5_4.SetLineWidth(2)
hist_e_5_4.SetLineStyle(1)
hist_e_25_4.SetLineColor(ROOT.kGreen+2)
hist_e_25_4.SetLineWidth(2)
hist_e_25_4.SetLineStyle(1)
hist_e_2f_4.SetLineColor(ROOT.kBlack)
hist_e_2f_4.SetFillColor(ROOT.kGreen)
hist_e_2f_4.SetLineWidth(1)
hist_e_2f_4.SetLineStyle(1)
hist_e_4f_4.SetLineColor(ROOT.kBlack)
hist_e_4f_4.SetFillColor(ROOT.kYellow)
hist_e_4f_4.SetLineWidth(1)
hist_e_4f_4.SetLineStyle(1)

hs_bkg_e_4.SetMinimum(0.1)
hs_sig_e_4.SetMinimum(0.1)


hs_sig_e_4.Add(hist_e_0p5_4)
hs_sig_e_4.Add(hist_e_5_4)
hs_sig_e_4.Add(hist_e_25_4)
hs_bkg_e_4.Add(hist_e_2f_4)
hs_bkg_e_4.Add(hist_e_4f_4)

ymin = []
ymax = []
xmin = []
xmax = []
ROOT.gPad.SetLogy()
hs_bkg_e_4.Draw("hist")
hs_bkg_e_4.GetHistogram().SetXTitle('|cos(#theta_{miss})|')
hs_bkg_e_4.GetHistogram().SetYTitle('Events/0.667')
hs_bkg_e_4.GetHistogram().SetTitleSize(0.05, "xy")
ROOT.gPad.Update()
ymin.append(ROOT.gPad.GetUymin())
ymax.append(ROOT.gPad.GetUymax())
xmin.append(ROOT.gPad.GetUxmin())
xmax.append(ROOT.gPad.GetUxmax())
hs_sig_e_4.Draw("hist, nostack, same")
ROOT.gPad.Update()
ymin.append(ROOT.gPad.GetUymin())
ymax.append(ROOT.gPad.GetUymax())
xmin.append(ROOT.gPad.GetUxmin())
xmax.append(ROOT.gPad.GetUxmax())
line_e_4_high = ROOT.TLine(e_cos_theta_p_missing_cut_high, 10**min(ymin),
                           e_cos_theta_p_missing_cut_high, 10**max(ymax))
line_e_4_high.SetLineWidth(2)
line_e_4_high.Draw("same")
arrow_len = (max(xmax) - min(xmin)) * 0.1 
arrow_e_4_high = ROOT.TArrow(e_cos_theta_p_missing_cut_high, 10**max(ymax)*0.01,
                 e_cos_theta_p_missing_cut_high - arrow_len, 10**max(ymax)*0.01, 0.005, "|>") 

arrow_e_4_high.SetAngle(60)
arrow_e_4_high.SetLineWidth(2)
arrow_e_4_high.Draw()
#ROOT.gPad.Update()
hist_e_0p5_4.Write()
hist_e_5_4.Write()
hist_e_25_4.Write()
hist_e_2f_4.Write()
hist_e_4f_4.Write()

### fifth cut for the ee channel ###
c_electron.cd(5)
e_cut_5 = e_cut_4+'&&'+electron_cuts['m_inv']
# get the entrylist after the cut
electrons['0p5'].Draw(">>e_0p5_cutlist5",e_cut_5,"entrylist")
electrons['5'].Draw(">>e_5_cutlist5",e_cut_5,"entrylist")
electrons['25'].Draw(">>e_25_cutlist5",e_cut_5,"entrylist")
electrons['2f'].Draw(">>e_2f_cutlist5",e_cut_5,"entrylist")
electrons['4f'].Draw(">>e_4f_cutlist5",e_cut_5,"entrylist")
e_0p5_cutlist5 = ROOT.gDirectory.Get("e_0p5_cutlist5")
e_5_cutlist5 = ROOT.gDirectory.Get("e_5_cutlist5")
e_25_cutlist5 = ROOT.gDirectory.Get("e_25_cutlist5")
e_2f_cutlist5 = ROOT.gDirectory.Get("e_2f_cutlist5")
e_4f_cutlist5 = ROOT.gDirectory.Get("e_4f_cutlist5")
print ('num of singal evts with m_s = 0.5 GeV passing m_inv cut: ', 
       e_0p5_cutlist5.GetN()*w['0p5'])
print ('num of singal evts with m_s = 5 GeV passing m_inv cut: ', 
       e_5_cutlist5.GetN()*w['5'])
print ('num of singal evts with m_s = 25 GeV passing m_inv cut: ', 
       e_25_cutlist5.GetN()*w['25'])
print ('num of 2-fermion bkg evts passing m_inv cut: ', 
       e_2f_cutlist5.GetN()*w['2f'])
print ('num of 4-fermion bkg evts passing m_inv cut: ', 
       e_4f_cutlist5.GetN()*w['4f'])
# plot the events vs. var being cut, up to all cuts applied before
hs_sig_e_5 = ROOT.THStack("hs_sig_e_5","")
hs_bkg_e_5 = ROOT.THStack("hs_bkg_e_5","")
e_5_xlow = 0
e_5_xhigh = 100
e_5_nbins = 10
e_5_descrp = "Z #rightarrow e^{+}e^{-} vs. m_{ee} @ 91.2 GeV"
hist_e_0p5_5 = ROOT.TH1F("e_0p5_m_inv",
e_5_descrp, e_5_nbins, e_5_xlow, e_5_xhigh)
hist_e_5_5 = ROOT.TH1F("e_5_m_inv",
e_5_descrp, e_5_nbins, e_5_xlow, e_5_xhigh)
hist_e_25_5 = ROOT.TH1F("e_25_m_inv",
e_5_descrp, e_5_nbins, e_5_xlow, e_5_xhigh)
hist_e_2f_5 = ROOT.TH1F("e_2f_m_inv",
e_5_descrp, e_5_nbins, e_5_xlow, e_5_xhigh)
hist_e_4f_5 = ROOT.TH1F("e_4f_m_inv",
e_5_descrp, e_5_nbins, e_5_xlow, e_5_xhigh)
electrons['0p5'].Draw("m_inv>>e_0p5_m_inv", e_cut_4, "goff")
electrons['5'].Draw("m_inv>>e_5_m_inv", e_cut_4, "goff")
electrons['25'].Draw("m_inv>>e_25_m_inv", e_cut_4, "goff")
electrons['2f'].Draw("m_inv>>e_2f_m_inv", e_cut_4, "goff")
electrons['4f'].Draw("m_inv>>e_4f_m_inv", e_cut_4, "goff")
#hist_e_0p5_5.SetDirectory(0)
#hist_e_5_5.SetDirectory(0)
#hist_e_25_5.SetDirectory(0)
#hist_e_2f_5.SetDirectory(0)
#hist_e_4f_5.SetDirectory(0)
hist_e_0p5_5.SetLineColor(ROOT.kRed)
hist_e_0p5_5.SetLineWidth(2)
hist_e_0p5_5.SetLineStyle(1)
hist_e_5_5.SetLineColor(ROOT.kBlue+2)
hist_e_5_5.SetLineWidth(2)
hist_e_5_5.SetLineStyle(1)
hist_e_25_5.SetLineColor(ROOT.kGreen+2)
hist_e_25_5.SetLineWidth(2)
hist_e_25_5.SetLineStyle(1)
hist_e_2f_5.SetLineColor(ROOT.kBlack)
hist_e_2f_5.SetFillColor(ROOT.kGreen)
hist_e_2f_5.SetLineWidth(1)
hist_e_2f_5.SetLineStyle(1)
hist_e_4f_5.SetLineColor(ROOT.kBlack)
hist_e_4f_5.SetFillColor(ROOT.kYellow)
hist_e_4f_5.SetLineWidth(1)
hist_e_4f_5.SetLineStyle(1)

hs_bkg_e_5.SetMinimum(0)
hs_sig_e_5.SetMinimum(0)


hs_sig_e_5.Add(hist_e_0p5_5)
hs_sig_e_5.Add(hist_e_5_5)
hs_sig_e_5.Add(hist_e_25_5)
hs_bkg_e_5.Add(hist_e_2f_5)
hs_bkg_e_5.Add(hist_e_4f_5)

ymin = []
ymax = []
xmin = []
xmax = []
#ROOT.gPad.SetLogy()
hs_bkg_e_5.Draw("hist")
hs_bkg_e_5.GetHistogram().SetXTitle('m_{ee} [GeV]')
hs_bkg_e_5.GetHistogram().SetYTitle('Events/10 GeV')
hs_bkg_e_5.GetHistogram().SetTitleSize(0.05, "xy")
ROOT.gPad.Update()
ymin.append(ROOT.gPad.GetUymin())
ymax.append(ROOT.gPad.GetUymax())
xmin.append(ROOT.gPad.GetUxmin())
xmax.append(ROOT.gPad.GetUxmax())
hs_sig_e_5.Draw("hist, nostack, same")
ROOT.gPad.Update()
ymin.append(ROOT.gPad.GetUymin())
ymax.append(ROOT.gPad.GetUymax())
xmin.append(ROOT.gPad.GetUxmin())
xmax.append(ROOT.gPad.GetUxmax())
line_e_5_low = ROOT.TLine(e_m_inv_cut_low, min(ymin),
                          e_m_inv_cut_low, max(ymax))
line_e_5_low.SetLineWidth(2)
line_e_5_low.Draw("same")
line_e_5_high = ROOT.TLine(e_m_inv_cut_high, min(ymin),
                          e_m_inv_cut_high, max(ymax))
line_e_5_high.SetLineWidth(2)
line_e_5_high.Draw("same")

arrow_len = (max(xmax) - min(xmin)) * 0.1 
arrow_e_5_low = ROOT.TArrow(e_m_inv_cut_low, max(ymax)*0.8,
                e_m_inv_cut_low + arrow_len, max(ymax)*0.8, 0.005, "|>") 
arrow_e_5_low.SetAngle(60)
arrow_e_5_low.SetLineWidth(2)
arrow_e_5_low.Draw()
arrow_e_5_high = ROOT.TArrow(e_m_inv_cut_high, max(ymax)*0.8,
                e_m_inv_cut_high - arrow_len, max(ymax)*0.8, 0.005, "|>") 
arrow_e_5_high.SetAngle(60)
arrow_e_5_high.SetLineWidth(2)
arrow_e_5_high.Draw()
#ROOT.gPad.Update()
hist_e_0p5_5.Write()
hist_e_5_5.Write()
hist_e_25_5.Write()
hist_e_2f_5.Write()
hist_e_4f_5.Write()

legend = ROOT.TLegend(0.1,0.6,0.6,0.85)
legend.AddEntry(hist_e_0p5_1, "m_{s} = 0.5 GeV", "l")
legend.AddEntry(hist_e_5_1, "m_{s} = 5 GeV", "l")
legend.AddEntry(hist_e_25_1, "m_{s} = 25 GeV", "l")
legend.AddEntry(hist_e_2f_1, "2 fermion", "f")
legend.AddEntry(hist_e_4f_1, "4 fermion", "f")
e_title = ROOT.TLatex(0.1,0.9,"Z #rightarrow e^{+}e^{-} @ #sqrt{s} = 91.2 GeV")
e_title.SetTextSize(0.05)
c_electron.cd(6)
legend.Draw()
e_title.Draw()

c_electron.Print("../plots/ZToee.png")
'''
###################################
######### muon channel ############
###################################
c_muon = ROOT.TCanvas("muon_cutflow","cutflow plots for Z -> mumu at 91.2 GeV",
                           hist_pixel_x * num_hist_x, hist_pixel_y * num_hist_y)
c_muon.Divide(num_hist_x, num_hist_y)
print ('normalized num of Z-> mumu evts from singal with m_s = 0.5 GeV: ',
       muons['0p5'].GetEntries()*w['0p5'])
#print ('normalized num of Z-> mumu evts from singal with m_s = 5 GeV: ',
#       muons['2'].GetEntries()*w['2'])
print ('normalized num of Z-> mumu evts from singal with m_s = 5 GeV: ',
       muons['5'].GetEntries()*w['5'])
#print ('normalized num of Z-> mumu evts from singal with m_s = 5 GeV: ',
#       muons['10'].GetEntries()*w['10'])
#print ('normalized num of Z-> mumu evts from singal with m_s = 5 GeV: ',
#       muons['15'].GetEntries()*w['15'])
print ('normalized num of Z-> mumu evts from singal with m_s = 25 GeV: ',
       muons['25'].GetEntries()*w['25'])
print ('normalized num of Z-> mumu evts from 2-fermion background: ',
       muons['2f'].GetEntries()*w['2f'])
print ('normalized num of Z-> mumu evts from 4-fermion lep background: ',
       muons['4f'].GetEntries()*w['4f'])
print ('normalized num of Z-> mumu evts from 4-fermion qq background: ',
       muons['4fqq'].GetEntries()*w['4fqq'])
''' first cut for the mumu channel '''
c_muon.cd(1)
# get the entrylist after the cut
muons['0p5'].Draw(">>mu_0p5_cutlist1",muon_cuts['alpha'],"entrylist")
muons['5'].Draw(">>mu_5_cutlist1",muon_cuts['alpha'],"entrylist")
muons['25'].Draw(">>mu_25_cutlist1",muon_cuts['alpha'],"entrylist")
muons['2f'].Draw(">>mu_2f_cutlist1",muon_cuts['alpha'],"entrylist")
muons['4f'].Draw(">>mu_4f_cutlist1",muon_cuts['alpha'],"entrylist")
muons['4fqq'].Draw(">>mu_4fqq_cutlist1",muon_cuts['alpha'],"entrylist")
mu_0p5_cutlist1 = ROOT.gDirectory.Get("mu_0p5_cutlist1")
mu_5_cutlist1 = ROOT.gDirectory.Get("mu_5_cutlist1")
mu_25_cutlist1 = ROOT.gDirectory.Get("mu_25_cutlist1")
mu_2f_cutlist1 = ROOT.gDirectory.Get("mu_2f_cutlist1")
mu_4f_cutlist1 = ROOT.gDirectory.Get("mu_4f_cutlist1")
mu_4fqq_cutlist1 = ROOT.gDirectory.Get("mu_4fqq_cutlist1")
print ('num of singal evts with m_s = 0.5 GeV passing alpha cut: ', 
       mu_0p5_cutlist1.GetN()*w['0p5'])
print ('num of singal evts with m_s = 5 GeV passing alpha cut: ', 
       mu_5_cutlist1.GetN()*w['5'])
print ('num of singal evts with m_s = 25 GeV passing alpha cut: ', 
       mu_25_cutlist1.GetN()*w['25'])
print ('num of 2-fermion bkg evts passing alpha cut: ', 
       mu_2f_cutlist1.GetN()*w['2f'])
print ('num of 4-fermion bkg evts passing alpha cut: ', 
       mu_4f_cutlist1.GetN()*w['4f'])
print ('num of 4-fermion bkg evts passing alpha cut: ', 
       mu_4fqq_cutlist1.GetN()*w['4fqq'])
# plot the events vs. var being cut, up to all cuts applied before
hs_sig_mu_1 = ROOT.THStack("hs_sig_mu_1","")
hs_bkg_mu_1 = ROOT.THStack("hs_bkg_mu_1","")
mu_1_xlow = 0
mu_1_xhigh = 3.1
mu_1_nbins = 31
mu_1_descrp = "Z #rightarrow e^{+}e^{-} vs. #alpha @ 91.2 GeV"
hist_mu_0p5_1 = ROOT.TH1F("mu_0p5_alpha",
mu_1_descrp, mu_1_nbins, mu_1_xlow, mu_1_xhigh)
hist_mu_5_1 = ROOT.TH1F("mu_5_alpha",
mu_1_descrp, mu_1_nbins, mu_1_xlow, mu_1_xhigh)
hist_mu_25_1 = ROOT.TH1F("mu_25_alpha",
mu_1_descrp, mu_1_nbins, mu_1_xlow, mu_1_xhigh)
hist_mu_2f_1 = ROOT.TH1F("mu_2f_alpha",
mu_1_descrp, mu_1_nbins, mu_1_xlow, mu_1_xhigh)
hist_mu_4f_1 = ROOT.TH1F("mu_4f_alpha",
mu_1_descrp, mu_1_nbins, mu_1_xlow, mu_1_xhigh)
hist_mu_4fqq_1 = ROOT.TH1F("mu_4fqq_alpha",
mu_1_descrp, mu_1_nbins, mu_1_xlow, mu_1_xhigh)
muons['0p5'].Draw("alpha>>mu_0p5_alpha", "", "goff")
muons['5'].Draw("alpha>>mu_5_alpha", "", "goff")
muons['25'].Draw("alpha>>mu_25_alpha","","goff")
muons['2f'].Draw("alpha>>mu_2f_alpha", "", "goff")
muons['4f'].Draw("alpha>>mu_4f_alpha", "", "goff")
muons['4fqq'].Draw("alpha>>mu_4fqq_alpha", "", "goff")
#hist_mu_0p5_1.SetDirectory(0)
#hist_mu_5_1.SetDirectory(0)
#hist_mu_25_1.SetDirectory(0)
#hist_mu_2f_1.SetDirectory(0)
#hist_mu_4f_1.SetDirectory(0)
hist_mu_0p5_1.SetLineColor(ROOT.kRed)
hist_mu_0p5_1.SetLineWidth(2)
hist_mu_0p5_1.SetLineStyle(1)
hist_mu_5_1.SetLineColor(ROOT.kBlue+2)
hist_mu_5_1.SetLineWidth(2)
hist_mu_5_1.SetLineStyle(1)
hist_mu_25_1.SetLineColor(ROOT.kGreen+2)
hist_mu_25_1.SetLineWidth(2)
hist_mu_25_1.SetLineStyle(1)
hist_mu_2f_1.SetLineColor(ROOT.kBlack)
hist_mu_2f_1.SetFillColor(ROOT.kGreen)
hist_mu_2f_1.SetLineWidth(1)
hist_mu_2f_1.SetLineStyle(1)
hist_mu_4f_1.SetLineColor(ROOT.kBlack)
hist_mu_4f_1.SetFillColor(ROOT.kYellow)
hist_mu_4f_1.SetLineWidth(1)
hist_mu_4f_1.SetLineStyle(1)
hist_mu_4f_1.SetLineColor(ROOT.kBlack)
hist_mu_4f_1.SetFillColor(ROOT.kYellow)
hist_mu_4f_1.SetLineWidth(1)
hist_mu_4f_1.SetLineStyle(1)
hist_mu_4fqq_1.SetLineColor(ROOT.kBlack)
hist_mu_4fqq_1.SetFillColor(ROOT.kOrange)
hist_mu_4fqq_1.SetLineWidth(1)
hist_mu_4fqq_1.SetLineStyle(1)
hs_bkg_mu_1.SetMinimum(0.1)
hs_sig_mu_1.SetMinimum(0.1)


hs_sig_mu_1.Add(hist_mu_0p5_1)
hs_sig_mu_1.Add(hist_mu_5_1)
hs_sig_mu_1.Add(hist_mu_25_1)
hs_bkg_mu_1.Add(hist_mu_2f_1)
hs_bkg_mu_1.Add(hist_mu_4f_1)
hs_bkg_mu_1.Add(hist_mu_4fqq_1)

ymin = []
ymax = []
xmin = []
xmax = []
ROOT.gPad.SetLogy()
hs_bkg_mu_1.Draw("hist")
hs_bkg_mu_1.GetHistogram().SetXTitle('#alpha [rad]')
hs_bkg_mu_1.GetHistogram().SetYTitle('Events/0.1 rad')
hs_bkg_mu_1.GetHistogram().SetTitleSize(0.05, "xy")
ROOT.gPad.Update()
ymin.append(ROOT.gPad.GetUymin())
ymax.append(ROOT.gPad.GetUymax())
xmin.append(ROOT.gPad.GetUxmin())
xmax.append(ROOT.gPad.GetUxmax())
hs_sig_mu_1.Draw("hist, nostack, same")
ROOT.gPad.Update()
ymin.append(ROOT.gPad.GetUymin())
ymax.append(ROOT.gPad.GetUymax())
xmin.append(ROOT.gPad.GetUxmin())
xmax.append(ROOT.gPad.GetUxmax())
linmu_mu_1_low = ROOT.TLine(mu_alpha_cut_low, 10**min(ymin),
                            mu_alpha_cut_low, 10**max(ymax))
linmu_mu_1_low.SetLineWidth(2)
linmu_mu_1_low.Draw("same")
linmu_mu_1_high = ROOT.TLine(mu_alpha_cut_high, 10**min(ymin),
                             mu_alpha_cut_high, 10**max(ymax))
linmu_mu_1_high.SetLineWidth(2)
linmu_mu_1_high.Draw("same")
arrow_len = (max(xmax) - min(xmin)) * 0.1 
arrow_mu_1_low = ROOT.TArrow(mu_alpha_cut_low, 10**max(ymax)*0.01,
                mu_alpha_cut_low + arrow_len, 10**max(ymax)*0.01, 0.005, "|>") 
arrow_mu_1_low.SetAngle(60)
arrow_mu_1_low.SetLineWidth(2)
arrow_mu_1_low.Draw()
arrow_mu_1_high = ROOT.TArrow(mu_alpha_cut_high, 10**max(ymax)*0.01,
                 mu_alpha_cut_high - arrow_len, 10**max(ymax)*0.01, 0.005, "|>") 
arrow_mu_1_high.SetAngle(60)
arrow_mu_1_high.SetLineWidth(2)
arrow_mu_1_high.Draw()
#ROOT.gPad.Update()
hist_mu_0p5_1.Write()
hist_mu_5_1.Write()
hist_mu_25_1.Write()
hist_mu_2f_1.Write()
hist_mu_4f_1.Write()
hist_mu_4fqq_1.Write()

''' second cut for the mumu channel '''
c_muon.cd(2)
mu_cut_2 = muon_cuts['alpha']+'&&'+muon_cuts['angle']
# get the entrylist after the cut
muons['0p5'].Draw(">>mu_0p5_cutlist2",mu_cut_2,"entrylist")
muons['5'].Draw(">>mu_5_cutlist2",mu_cut_2,"entrylist")
muons['25'].Draw(">>mu_25_cutlist2",mu_cut_2,"entrylist")
muons['2f'].Draw(">>mu_2f_cutlist2",mu_cut_2,"entrylist")
muons['4f'].Draw(">>mu_4f_cutlist2",mu_cut_2,"entrylist")
muons['4fqq'].Draw(">>mu_4fqq_cutlist2",mu_cut_2,"entrylist")
mu_0p5_cutlist2 = ROOT.gDirectory.Get("mu_0p5_cutlist2")
mu_5_cutlist2 = ROOT.gDirectory.Get("mu_5_cutlist2")
mu_25_cutlist2 = ROOT.gDirectory.Get("mu_25_cutlist2")
mu_2f_cutlist2 = ROOT.gDirectory.Get("mu_2f_cutlist2")
mu_4f_cutlist2 = ROOT.gDirectory.Get("mu_4f_cutlist2")
mu_4fqq_cutlist2 = ROOT.gDirectory.Get("mu_4fqq_cutlist2")
print ('num of singal evts with m_s = 0.5 GeV passing angle cut: ', 
       mu_0p5_cutlist2.GetN()*w['0p5'])
print ('num of singal evts with m_s = 5 GeV passing angle cut: ', 
       mu_5_cutlist2.GetN()*w['5'])
print ('num of singal evts with m_s = 25 GeV passing angle cut: ', 
       mu_25_cutlist2.GetN()*w['25'])
print ('num of 2-fermion bkg evts passing angle cut: ', 
       mu_2f_cutlist2.GetN()*w['2f'])
print ('num of 4-fermion bkg evts passing angle cut: ', 
       mu_4f_cutlist2.GetN()*w['4f'])
print ('num of 4-fermion bkg evts passing angle cut: ', 
       mu_4fqq_cutlist2.GetN()*w['4fqq'])
# plot the events vs. var being cut, up to all cuts applied before
hs_sig_mu_2 = ROOT.THStack("hs_sig_mu_2","")
hs_bkg_mu_2 = ROOT.THStack("hs_bkg_mu_2","")
mu_2_xlow = 0
mu_2_xhigh = 1
mu_2_nbins = 15
mu_2_descrp = "Z #rightarrow e^{+}e^{-} vs. |cos(#theta_{1})| @ 91.2 GeV"
hist_mu_0p5_2 = ROOT.TH1F("mu_0p5_angle",
mu_2_descrp, mu_2_nbins, mu_2_xlow, mu_2_xhigh)
hist_mu_5_2 = ROOT.TH1F("mu_5_angle",
mu_2_descrp, mu_2_nbins, mu_2_xlow, mu_2_xhigh)
hist_mu_25_2 = ROOT.TH1F("mu_25_angle",
mu_2_descrp, mu_2_nbins, mu_2_xlow, mu_2_xhigh)
hist_mu_2f_2 = ROOT.TH1F("mu_2f_angle",
mu_2_descrp, mu_2_nbins, mu_2_xlow, mu_2_xhigh)
hist_mu_4f_2 = ROOT.TH1F("mu_4f_angle",
mu_2_descrp, mu_2_nbins, mu_2_xlow, mu_2_xhigh)
hist_mu_4fqq_2 = ROOT.TH1F("mu_4fqq_angle",
mu_2_descrp, mu_2_nbins, mu_2_xlow, mu_2_xhigh)
muons['0p5'].Draw("abs(cos_theta_1)>>mu_0p5_angle", muon_cuts['alpha'], "goff")
muons['5'].Draw("abs(cos_theta_1)>>mu_5_angle", muon_cuts['alpha'], "goff")
muons['25'].Draw("abs(cos_theta_1)>>mu_25_angle", muon_cuts['alpha'],"goff")
muons['2f'].Draw("abs(cos_theta_1)>>mu_2f_angle", muon_cuts['alpha'], "goff")
muons['4f'].Draw("abs(cos_theta_1)>>mu_4f_angle", muon_cuts['alpha'], "goff")
muons['4fqq'].Draw("abs(cos_theta_1)>>mu_4fqq_angle", muon_cuts['alpha'], "goff")
#hist_mu_0p5_2.SetDirectory(0)
#hist_mu_5_2.SetDirectory(0)
#hist_mu_25_2.SetDirectory(0)
#hist_mu_2f_2.SetDirectory(0)
#hist_mu_4f_2.SetDirectory(0)
hist_mu_0p5_2.SetLineColor(ROOT.kRed)
hist_mu_0p5_2.SetLineWidth(2)
hist_mu_0p5_2.SetLineStyle(1)
hist_mu_5_2.SetLineColor(ROOT.kBlue+2)
hist_mu_5_2.SetLineWidth(2)
hist_mu_5_2.SetLineStyle(1)
hist_mu_25_2.SetLineColor(ROOT.kGreen+2)
hist_mu_25_2.SetLineWidth(2)
hist_mu_25_2.SetLineStyle(1)
hist_mu_2f_2.SetLineColor(ROOT.kBlack)
hist_mu_2f_2.SetFillColor(ROOT.kGreen)
hist_mu_2f_2.SetLineWidth(1)
hist_mu_2f_2.SetLineStyle(1)
hist_mu_4f_2.SetLineColor(ROOT.kBlack)
hist_mu_4f_2.SetFillColor(ROOT.kYellow)
hist_mu_4f_2.SetLineWidth(1)
hist_mu_4f_2.SetLineStyle(1)
hist_mu_4fqq_2.SetLineColor(ROOT.kBlack)
hist_mu_4fqq_2.SetFillColor(ROOT.kOrange)
hist_mu_4fqq_2.SetLineWidth(1)
hist_mu_4fqq_2.SetLineStyle(1)

hs_bkg_mu_2.SetMinimum(0.1)
hs_sig_mu_2.SetMinimum(0.1)
hs_bkg_mu_2.SetMaximum(50)
hs_sig_mu_2.SetMaximum(50)

hs_sig_mu_2.Add(hist_mu_0p5_2)
hs_sig_mu_2.Add(hist_mu_5_2)
hs_sig_mu_2.Add(hist_mu_25_2)
hs_bkg_mu_2.Add(hist_mu_2f_2)
hs_bkg_mu_2.Add(hist_mu_4f_2)
hs_bkg_mu_2.Add(hist_mu_4fqq_2)
ymin = []
ymax = []
xmin = []
xmax = []
ROOT.gPad.SetLogy()
hs_bkg_mu_2.Draw("hist")
hs_bkg_mu_2.GetHistogram().SetXTitle('|cos(#theta_{1})|')
hs_bkg_mu_2.GetHistogram().SetYTitle('Events/0.0667')
hs_bkg_mu_2.GetHistogram().SetTitleSize(0.05, "xy")
ROOT.gPad.Update()
ymin.append(ROOT.gPad.GetUymin())
ymax.append(ROOT.gPad.GetUymax())
xmin.append(ROOT.gPad.GetUxmin())
xmax.append(ROOT.gPad.GetUxmax())
hs_sig_mu_2.Draw("hist, same, nostack")
ROOT.gPad.RedrawAxis()
ROOT.gPad.Update()
ymin.append(ROOT.gPad.GetUymin())
ymax.append(ROOT.gPad.GetUymax())
xmin.append(ROOT.gPad.GetUxmin())
xmax.append(ROOT.gPad.GetUxmax())
linmu_mu_2_high = ROOT.TLine(mu_angle_cut_high, 10**min(ymin),
                           mu_angle_cut_high, 10**max(ymax))
linmu_mu_2_high.SetLineWidth(2)
linmu_mu_2_high.Draw("same")
arrow_len = (max(xmax) - min(xmin)) * 0.1 
arrow_mu_2_high = ROOT.TArrow(mu_angle_cut_high, 10**max(ymax)*0.01,
                 mu_angle_cut_high - arrow_len, 10**max(ymax)*0.01, 0.005, "|>") 
arrow_mu_2_high.SetAngle(60)
arrow_mu_2_high.SetLineWidth(2)
arrow_mu_2_high.Draw()
#ROOT.gPad.Update()
hist_mu_0p5_2.Write()
hist_mu_5_2.Write()
hist_mu_25_2.Write()
hist_mu_2f_2.Write()
hist_mu_4f_2.Write()
hist_mu_4fqq_2.Write()

''' third cut for the mumu channel '''
c_muon.cd(3)
mu_cut_3 = mu_cut_2+'&&'+muon_cuts['momentum']
# get the entrylist after the cut
muons['0p5'].Draw(">>mu_0p5_cutlist3",mu_cut_3,"entrylist")
muons['5'].Draw(">>mu_5_cutlist3",mu_cut_3,"entrylist")
muons['25'].Draw(">>mu_25_cutlist3",mu_cut_3,"entrylist")
muons['2f'].Draw(">>mu_2f_cutlist3",mu_cut_3,"entrylist")
muons['4f'].Draw(">>mu_4f_cutlist3",mu_cut_3,"entrylist")
muons['4fqq'].Draw(">>mu_4fqq_cutlist3",mu_cut_3,"entrylist")
mu_0p5_cutlist3 = ROOT.gDirectory.Get("mu_0p5_cutlist3")
mu_5_cutlist3 = ROOT.gDirectory.Get("mu_5_cutlist3")
mu_25_cutlist3 = ROOT.gDirectory.Get("mu_25_cutlist3")
mu_2f_cutlist3 = ROOT.gDirectory.Get("mu_2f_cutlist3")
mu_4f_cutlist3 = ROOT.gDirectory.Get("mu_4f_cutlist3")
mu_4fqq_cutlist3 = ROOT.gDirectory.Get("mu_4fqq_cutlist3")
print ('num of singal evts with m_s = 0.5 GeV passing momentum cut: ', 
       mu_0p5_cutlist3.GetN()*w['0p5'])
print ('num of singal evts with m_s = 5 GeV passing momentum cut: ', 
       mu_5_cutlist3.GetN()*w['5'])
print ('num of singal evts with m_s = 25 GeV passing momentum cut: ', 
       mu_25_cutlist3.GetN()*w['25'])
print ('num of 2-fermion bkg evts passing momentum cut: ', 
       mu_2f_cutlist3.GetN()*w['2f'])
print ('num of 4-fermion bkg evts passing momentum cut: ', 
       mu_4f_cutlist3.GetN()*w['4f'])
print ('num of 4-fermion bkg evts passing momentum cut: ', 
       mu_4fqq_cutlist3.GetN()*w['4fqq'])
# plot the events vs. var being cut, up to all cuts applied before
hs_sig_mu_3 = ROOT.THStack("hs_sig_mu_3","")
hs_bkg_mu_3 = ROOT.THStack("hs_bkg_mu_3","")
mu_3_xlow = 0
mu_3_xhigh = 45
mu_3_nbins = 45
mu_3_descrp = "Z #rightarrow e^{+}e^{-} vs. |p_{1}| @ 91.2 GeV"
hist_mu_0p5_3 = ROOT.TH1F("mu_0p5_momentum",
mu_3_descrp, mu_3_nbins, mu_3_xlow, mu_3_xhigh)
hist_mu_5_3 = ROOT.TH1F("mu_5_momentum",
mu_3_descrp, mu_3_nbins, mu_3_xlow, mu_3_xhigh)
hist_mu_25_3 = ROOT.TH1F("mu_25_momentum",
mu_3_descrp, mu_3_nbins, mu_3_xlow, mu_3_xhigh)
hist_mu_2f_3 = ROOT.TH1F("mu_2f_momentum",
mu_3_descrp, mu_3_nbins, mu_3_xlow, mu_3_xhigh)
hist_mu_4f_3 = ROOT.TH1F("mu_4f_momentum",
mu_3_descrp, mu_3_nbins, mu_3_xlow, mu_3_xhigh)
hist_mu_4fqq_3 = ROOT.TH1F("mu_4fqq_momentum",
mu_3_descrp, mu_3_nbins, mu_3_xlow, mu_3_xhigh)
muons['0p5'].Draw("p_mag_1>>mu_0p5_momentum", mu_cut_2, "goff")
muons['5'].Draw("p_mag_1>>mu_5_momentum", mu_cut_2, "goff")
muons['25'].Draw("p_mag_1>>mu_25_momentum", mu_cut_2, "goff")
muons['2f'].Draw("p_mag_1>>mu_2f_momentum", mu_cut_2, "goff")
muons['4f'].Draw("p_mag_1>>mu_4f_momentum", mu_cut_2, "goff")
muons['4fqq'].Draw("p_mag_1>>mu_4fqq_momentum", mu_cut_2, "goff")
#hist_mu_0p5_3.SetDirectory(0)
#hist_mu_5_3.SetDirectory(0)
#hist_mu_25_3.SetDirectory(0)
#hist_mu_2f_3.SetDirectory(0)
#hist_mu_4f_3.SetDirectory(0)
hist_mu_0p5_3.SetLineColor(ROOT.kRed)
hist_mu_0p5_3.SetLineWidth(2)
hist_mu_0p5_3.SetLineStyle(1)
hist_mu_5_3.SetLineColor(ROOT.kBlue+2)
hist_mu_5_3.SetLineWidth(2)
hist_mu_5_3.SetLineStyle(1)
hist_mu_25_3.SetLineColor(ROOT.kGreen+2)
hist_mu_25_3.SetLineWidth(2)
hist_mu_25_3.SetLineStyle(1)
hist_mu_2f_3.SetLineColor(ROOT.kBlack)
hist_mu_2f_3.SetFillColor(ROOT.kGreen)
hist_mu_2f_3.SetLineWidth(1)
hist_mu_2f_3.SetLineStyle(1)
hist_mu_4f_3.SetLineColor(ROOT.kBlack)
hist_mu_4f_3.SetFillColor(ROOT.kYellow)
hist_mu_4f_3.SetLineWidth(1)
hist_mu_4f_3.SetLineStyle(1)
hist_mu_4fqq_3.SetLineColor(ROOT.kBlack)
hist_mu_4fqq_3.SetFillColor(ROOT.kOrange)
hist_mu_4fqq_3.SetLineWidth(1)
hist_mu_4fqq_3.SetLineStyle(1)

hs_bkg_mu_3.SetMinimum(0.1)
hs_sig_mu_3.SetMinimum(0.1)
hs_bkg_mu_3.SetMaximum(60)
hs_sig_mu_3.SetMaximum(60)

hs_sig_mu_3.Add(hist_mu_0p5_3)
hs_sig_mu_3.Add(hist_mu_5_3)
hs_sig_mu_3.Add(hist_mu_25_3)
hs_bkg_mu_3.Add(hist_mu_2f_3)
hs_bkg_mu_3.Add(hist_mu_4f_3)
hs_bkg_mu_3.Add(hist_mu_4fqq_3)

ymin = []
ymax = []
xmin = []
xmax = []
ROOT.gPad.SetLogy()
hs_bkg_mu_3.Draw("hist")
hs_bkg_mu_3.GetHistogram().SetXTitle('|p_{1}| [GeV]')
hs_bkg_mu_3.GetHistogram().SetYTitle('Events/1 GeV')
hs_bkg_mu_3.GetHistogram().SetTitleSize(0.05, "xy")
ROOT.gPad.Update()
ymin.append(ROOT.gPad.GetUymin())
ymax.append(ROOT.gPad.GetUymax())
xmin.append(ROOT.gPad.GetUxmin())
xmax.append(ROOT.gPad.GetUxmax())
hs_sig_mu_3.Draw("hist, nostack, same")
ROOT.gPad.Update()
ymin.append(ROOT.gPad.GetUymin())
ymax.append(ROOT.gPad.GetUymax())
xmin.append(ROOT.gPad.GetUxmin())
xmax.append(ROOT.gPad.GetUxmax())
linmu_mu_3_low = ROOT.TLine(mu_momentum_cut_low, 10**min(ymin),
                          mu_momentum_cut_low, 10**max(ymax))
linmu_mu_3_low.SetLineWidth(2)
linmu_mu_3_low.Draw("same")
arrow_len = (max(xmax) - min(xmin)) * 0.1 
arrow_mu_3_low = ROOT.TArrow(mu_momentum_cut_low, 10**max(ymax)*0.01,
                mu_momentum_cut_low + arrow_len, 10**max(ymax)*0.01, 0.005, "|>") 
arrow_mu_3_low.SetAngle(60)
arrow_mu_3_low.SetLineWidth(2)
arrow_mu_3_low.Draw()
#ROOT.gPad.Update()
hist_mu_0p5_3.Write()
hist_mu_5_3.Write()
hist_mu_25_3.Write()
hist_mu_2f_3.Write()
hist_mu_4f_3.Write()
hist_mu_4fqq_3.Write()

''' fourth cut for the mumu channel '''
c_muon.cd(4)
mu_cut_4 = mu_cut_3+'&&'+muon_cuts['cos_theta_p_missing']
# get the entrylist after the cut
muons['0p5'].Draw(">>mu_0p5_cutlist4",mu_cut_4,"entrylist")
muons['5'].Draw(">>mu_5_cutlist4",mu_cut_4,"entrylist")
muons['25'].Draw(">>mu_25_cutlist4",mu_cut_4,"entrylist")
muons['2f'].Draw(">>mu_2f_cutlist4",mu_cut_4,"entrylist")
muons['4f'].Draw(">>mu_4f_cutlist4",mu_cut_4,"entrylist")
muons['4fqq'].Draw(">>mu_4fqq_cutlist4",mu_cut_4,"entrylist")
mu_0p5_cutlist4 = ROOT.gDirectory.Get("mu_0p5_cutlist4")
mu_5_cutlist4 = ROOT.gDirectory.Get("mu_5_cutlist4")
mu_25_cutlist4 = ROOT.gDirectory.Get("mu_25_cutlist4")
mu_2f_cutlist4 = ROOT.gDirectory.Get("mu_2f_cutlist4")
mu_4f_cutlist4 = ROOT.gDirectory.Get("mu_4f_cutlist4")
mu_4fqq_cutlist4 = ROOT.gDirectory.Get("mu_4fqq_cutlist4")
print ('num of singal evts with m_s = 0.5 GeV passing cos_theta_p_missing cut: ', 
       mu_0p5_cutlist4.GetN()*w['0p5'])
print ('num of singal evts with m_s = 5 GeV passing cos_theta_p_missing cut: ', 
       mu_5_cutlist4.GetN()*w['5'])
print ('num of singal evts with m_s = 25 GeV passing cos_theta_p_missing cut: ', 
       mu_25_cutlist4.GetN()*w['25'])
print ('num of 2-fermion bkg evts passing cos_theta_p_missing cut: ', 
       mu_2f_cutlist4.GetN()*w['2f'])
print ('num of 4-fermion bkg evts passing cos_theta_p_missing cut: ', 
       mu_4f_cutlist4.GetN()*w['4f'])
print ('num of 4-fermion bkg evts passing cos_theta_p_missing cut: ', 
       mu_4fqq_cutlist4.GetN()*w['4fqq'])
# plot the events vs. var being cut, up to all cuts applied before
hs_sig_mu_4 = ROOT.THStack("hs_sig_mu_4","")
hs_bkg_mu_4 = ROOT.THStack("hs_bkg_mu_4","")
mu_4_xlow = 0
mu_4_xhigh = 1
mu_4_nbins = 15
mu_4_descrp = "Z #rightarrow e^{+}e^{-} vs. |cos(#theta_{miss})| @ 91.2 GeV"
hist_mu_0p5_4 = ROOT.TH1F("mu_0p5_cos_theta_p_missing",
mu_4_descrp, mu_4_nbins, mu_4_xlow, mu_4_xhigh)
hist_mu_5_4 = ROOT.TH1F("mu_5_cos_theta_p_missing",
mu_4_descrp, mu_4_nbins, mu_4_xlow, mu_4_xhigh)
hist_mu_25_4 = ROOT.TH1F("mu_25_cos_theta_p_missing",
mu_4_descrp, mu_4_nbins, mu_4_xlow, mu_4_xhigh)
hist_mu_2f_4 = ROOT.TH1F("mu_2f_cos_theta_p_missing",
mu_4_descrp, mu_4_nbins, mu_4_xlow, mu_4_xhigh)
hist_mu_4f_4 = ROOT.TH1F("mu_4f_cos_theta_p_missing",
mu_4_descrp, mu_4_nbins, mu_4_xlow, mu_4_xhigh)
hist_mu_4fqq_4 = ROOT.TH1F("mu_4fqq_cos_theta_p_missing",
mu_4_descrp, mu_4_nbins, mu_4_xlow, mu_4_xhigh)
muons['0p5'].Draw("abs(cos_theta_p_missing)>>mu_0p5_cos_theta_p_missing", mu_cut_3, "goff")
muons['5'].Draw("abs(cos_theta_p_missing)>>mu_5_cos_theta_p_missing", mu_cut_3, "goff")
muons['25'].Draw("abs(cos_theta_p_missing)>>mu_25_cos_theta_p_missing", mu_cut_3,"goff")
muons['2f'].Draw("abs(cos_theta_p_missing)>>mu_2f_cos_theta_p_missing", mu_cut_3, "goff")
muons['4f'].Draw("abs(cos_theta_p_missing)>>mu_4f_cos_theta_p_missing", mu_cut_3, "goff")
muons['4fqq'].Draw("abs(cos_theta_p_missing)>>mu_4fqq_cos_theta_p_missing", mu_cut_3, "goff")
#hist_mu_0p5_4.SetDirectory(0)
#hist_mu_5_4.SetDirectory(0)
#hist_mu_25_4.SetDirectory(0)
#hist_mu_2f_4.SetDirectory(0)
#hist_mu_4f_4.SetDirectory(0)
hist_mu_0p5_4.SetLineColor(ROOT.kRed)
hist_mu_0p5_4.SetLineWidth(2)
hist_mu_0p5_4.SetLineStyle(1)
hist_mu_5_4.SetLineColor(ROOT.kBlue+2)
hist_mu_5_4.SetLineWidth(2)
hist_mu_5_4.SetLineStyle(1)
hist_mu_25_4.SetLineColor(ROOT.kGreen+2)
hist_mu_25_4.SetLineWidth(2)
hist_mu_25_4.SetLineStyle(1)
hist_mu_2f_4.SetLineColor(ROOT.kBlack)
hist_mu_2f_4.SetFillColor(ROOT.kGreen)
hist_mu_2f_4.SetLineWidth(1)
hist_mu_2f_4.SetLineStyle(1)
hist_mu_4f_4.SetLineColor(ROOT.kBlack)
hist_mu_4f_4.SetFillColor(ROOT.kYellow)
hist_mu_4f_4.SetLineWidth(1)
hist_mu_4f_4.SetLineStyle(1)
hist_mu_4fqq_4.SetLineColor(ROOT.kBlack)
hist_mu_4fqq_4.SetFillColor(ROOT.kOrange)
hist_mu_4fqq_4.SetLineWidth(1)
hist_mu_4fqq_4.SetLineStyle(1)

hs_bkg_mu_4.SetMinimum(0.1)
hs_sig_mu_4.SetMinimum(0.1)
hs_bkg_mu_4.SetMaximum(40)
hs_sig_mu_4.SetMaximum(40)

hs_sig_mu_4.Add(hist_mu_0p5_4)
hs_sig_mu_4.Add(hist_mu_5_4)
hs_sig_mu_4.Add(hist_mu_25_4)
hs_bkg_mu_4.Add(hist_mu_2f_4)
hs_bkg_mu_4.Add(hist_mu_4f_4)
hs_bkg_mu_4.Add(hist_mu_4fqq_4)

ymin = []
ymax = []
xmin = []
xmax = []
ROOT.gPad.SetLogy()
hs_bkg_mu_4.Draw("hist")
hs_bkg_mu_4.GetHistogram().SetXTitle('|cos(#theta_{miss})|')
hs_bkg_mu_4.GetHistogram().SetYTitle('Events/0.667')
hs_bkg_mu_4.GetHistogram().SetTitleSize(0.05, "xy")
ROOT.gPad.Update()
ymin.append(ROOT.gPad.GetUymin())
ymax.append(ROOT.gPad.GetUymax())
xmin.append(ROOT.gPad.GetUxmin())
xmax.append(ROOT.gPad.GetUxmax())
hs_sig_mu_4.Draw("hist, nostack, same")
ROOT.gPad.RedrawAxis()
ROOT.gPad.Update()
ymin.append(ROOT.gPad.GetUymin())
ymax.append(ROOT.gPad.GetUymax())
xmin.append(ROOT.gPad.GetUxmin())
xmax.append(ROOT.gPad.GetUxmax())
linmu_mu_4_high = ROOT.TLine(mu_cos_theta_p_missing_cut_high, 10**min(ymin),
                           mu_cos_theta_p_missing_cut_high, 10**max(ymax))
linmu_mu_4_high.SetLineWidth(2)
linmu_mu_4_high.Draw("same")
arrow_len = (max(xmax) - min(xmin)) * 0.1 
arrow_mu_4_high = ROOT.TArrow(mu_cos_theta_p_missing_cut_high, 10**max(ymax)*0.01,
                 mu_cos_theta_p_missing_cut_high - arrow_len, 10**max(ymax)*0.01, 0.005, "|>") 

arrow_mu_4_high.SetAngle(60)
arrow_mu_4_high.SetLineWidth(2)
arrow_mu_4_high.Draw()
#ROOT.gPad.Update()
hist_mu_0p5_4.Write()
hist_mu_5_4.Write()
hist_mu_25_4.Write()
hist_mu_2f_4.Write()
hist_mu_4f_4.Write()
hist_mu_4fqq_4.Write()

''' fifth cut for the mumu channel '''
c_muon.cd(5)
mu_cut_5 = mu_cut_4+'&&'+muon_cuts['m_inv']
# get the entrylist after the cut
muons['0p5'].Draw(">>mu_0p5_cutlist5",mu_cut_5,"entrylist")
muons['2'].Draw(">>mu_2_cutlist5",mu_cut_5,"entrylist")
muons['5'].Draw(">>mu_5_cutlist5",mu_cut_5,"entrylist")
muons['10'].Draw(">>mu_10_cutlist5",mu_cut_5,"entrylist")
muons['15'].Draw(">>mu_15_cutlist5",mu_cut_5,"entrylist")
muons['25'].Draw(">>mu_25_cutlist5",mu_cut_5,"entrylist")
muons['2f'].Draw(">>mu_2f_cutlist5",mu_cut_5,"entrylist")
muons['4f'].Draw(">>mu_4f_cutlist5",mu_cut_5,"entrylist")
muons['4fqq'].Draw(">>mu_4fqq_cutlist5",mu_cut_5,"entrylist")
mu_0p5_cutlist5 = ROOT.gDirectory.Get("mu_0p5_cutlist5")
mu_2_cutlist5 = ROOT.gDirectory.Get("mu_2_cutlist5")
mu_5_cutlist5 = ROOT.gDirectory.Get("mu_5_cutlist5")
mu_10_cutlist5 = ROOT.gDirectory.Get("mu_10_cutlist5")
mu_15_cutlist5 = ROOT.gDirectory.Get("mu_15_cutlist5")
mu_25_cutlist5 = ROOT.gDirectory.Get("mu_25_cutlist5")
mu_2f_cutlist5 = ROOT.gDirectory.Get("mu_2f_cutlist5")
mu_4f_cutlist5 = ROOT.gDirectory.Get("mu_4f_cutlist5")
mu_4fqq_cutlist5 = ROOT.gDirectory.Get("mu_4fqq_cutlist5")
print ('num of singal evts with m_s = 0.5 GeV passing m_inv cut: ', 
       mu_0p5_cutlist5.GetN()*w['0p5'])
print ('num of singal evts with m_s = 2 GeV passing m_inv cut: ', 
       mu_2_cutlist5.GetN()*w['2'])
print ('num of singal evts with m_s = 5 GeV passing m_inv cut: ', 
       mu_5_cutlist5.GetN()*w['5'])
print ('num of singal evts with m_s = 10 GeV passing m_inv cut: ', 
       mu_10_cutlist5.GetN()*w['10'])
print ('num of singal evts with m_s = 15 GeV passing m_inv cut: ', 
       mu_15_cutlist5.GetN()*w['15'])
print ('num of singal evts with m_s = 25 GeV passing m_inv cut: ', 
       mu_25_cutlist5.GetN()*w['25'])
print ('num of 2-fermion bkg evts passing m_inv cut: ', 
       mu_2f_cutlist5.GetN()*w['2f'])
print ('num of 4-fermion bkg evts passing m_inv cut: ', 
       mu_4f_cutlist5.GetN()*w['4f'])
print ('num of 4-fermion bkg evts passing m_inv cut: ', 
       mu_4fqq_cutlist5.GetN()*w['4fqq'])
# plot the events vs. var being cut, up to all cuts applied before
hs_sig_mu_5 = ROOT.THStack("hs_sig_mu_5","")
hs_bkg_mu_5 = ROOT.THStack("hs_bkg_mu_5","")
mu_5_xlow = 0
mu_5_xhigh = 100
mu_5_nbins = 10
mu_5_descrp = "Z #rightarrow e^{+}e^{-} vs. m_{mumu} @ 91.2 GeV"
hist_mu_0p5_5 = ROOT.TH1F("mu_0p5_m_inv",
mu_5_descrp, mu_5_nbins, mu_5_xlow, mu_5_xhigh)
hist_mu_5_5 = ROOT.TH1F("mu_5_m_inv",
mu_5_descrp, mu_5_nbins, mu_5_xlow, mu_5_xhigh)
hist_mu_25_5 = ROOT.TH1F("mu_25_m_inv",
mu_5_descrp, mu_5_nbins, mu_5_xlow, mu_5_xhigh)
hist_mu_2f_5 = ROOT.TH1F("mu_2f_m_inv",
mu_5_descrp, mu_5_nbins, mu_5_xlow, mu_5_xhigh)
hist_mu_4f_5 = ROOT.TH1F("mu_4f_m_inv",
mu_5_descrp, mu_5_nbins, mu_5_xlow, mu_5_xhigh)
hist_mu_4fqq_5 = ROOT.TH1F("mu_4fqq_m_inv",
mu_5_descrp, mu_5_nbins, mu_5_xlow, mu_5_xhigh)
muons['0p5'].Draw("m_inv>>mu_0p5_m_inv", mu_cut_4, "goff")
muons['5'].Draw("m_inv>>mu_5_m_inv", mu_cut_4, "goff")
muons['25'].Draw("m_inv>>mu_25_m_inv", mu_cut_4, "goff")
muons['2f'].Draw("m_inv>>mu_2f_m_inv", mu_cut_4, "goff")
muons['4f'].Draw("m_inv>>mu_4f_m_inv", mu_cut_4, "goff")
muons['4fqq'].Draw("m_inv>>mu_4fqq_m_inv", mu_cut_4, "goff")
#hist_mu_0p5_5.SetDirectory(0)
#hist_mu_5_5.SetDirectory(0)
#hist_mu_25_5.SetDirectory(0)
#hist_mu_2f_5.SetDirectory(0)
#hist_mu_4f_5.SetDirectory(0)
hist_mu_0p5_5.SetLineColor(ROOT.kRed)
hist_mu_0p5_5.SetLineWidth(2)
hist_mu_0p5_5.SetLineStyle(1)
hist_mu_5_5.SetLineColor(ROOT.kBlue+2)
hist_mu_5_5.SetLineWidth(2)
hist_mu_5_5.SetLineStyle(1)
hist_mu_25_5.SetLineColor(ROOT.kGreen+2)
hist_mu_25_5.SetLineWidth(2)
hist_mu_25_5.SetLineStyle(1)
hist_mu_2f_5.SetLineColor(ROOT.kBlack)
hist_mu_2f_5.SetFillColor(ROOT.kGreen)
hist_mu_2f_5.SetLineWidth(1)
hist_mu_2f_5.SetLineStyle(1)
hist_mu_4f_5.SetLineColor(ROOT.kBlack)
hist_mu_4f_5.SetFillColor(ROOT.kYellow)
hist_mu_4f_5.SetLineWidth(1)
hist_mu_4f_5.SetLineStyle(1)
hist_mu_4fqq_5.SetLineColor(ROOT.kBlack)
hist_mu_4fqq_5.SetFillColor(ROOT.kOrange)
hist_mu_4fqq_5.SetLineWidth(1)
hist_mu_4fqq_5.SetLineStyle(1)

hs_bkg_mu_5.SetMinimum(0)
hs_sig_mu_5.SetMinimum(0)
hs_bkg_mu_5.SetMaximum(120)
hs_sig_mu_5.SetMaximum(120)

hs_sig_mu_5.Add(hist_mu_0p5_5)
hs_sig_mu_5.Add(hist_mu_5_5)
hs_sig_mu_5.Add(hist_mu_25_5)
hs_bkg_mu_5.Add(hist_mu_2f_5)
hs_bkg_mu_5.Add(hist_mu_4f_5)
hs_bkg_mu_5.Add(hist_mu_4fqq_5)

ymin = []
ymax = []
xmin = []
xmax = []
#ROOT.gPad.SetLogy()
hs_bkg_mu_5.Draw("hist")
hs_bkg_mu_5.GetHistogram().SetXTitle('m_{mumu} [GeV]')
hs_bkg_mu_5.GetHistogram().SetYTitle('Events/10 GeV')
hs_bkg_mu_5.GetHistogram().SetTitleSize(0.05, "xy")
ROOT.gPad.Update()
ymin.append(ROOT.gPad.GetUymin())
ymax.append(ROOT.gPad.GetUymax())
xmin.append(ROOT.gPad.GetUxmin())
xmax.append(ROOT.gPad.GetUxmax())
hs_sig_mu_5.Draw("hist, nostack, same")
ROOT.gPad.Update()
ymin.append(ROOT.gPad.GetUymin())
ymax.append(ROOT.gPad.GetUymax())
xmin.append(ROOT.gPad.GetUxmin())
xmax.append(ROOT.gPad.GetUxmax())
linmu_mu_5_low = ROOT.TLine(mu_m_inv_cut_low, min(ymin),
                          mu_m_inv_cut_low, max(ymax))
linmu_mu_5_low.SetLineWidth(2)
linmu_mu_5_low.Draw("same")
linmu_mu_5_high = ROOT.TLine(mu_m_inv_cut_high, min(ymin),
                          mu_m_inv_cut_high, max(ymax))
linmu_mu_5_high.SetLineWidth(2)
linmu_mu_5_high.Draw("same")

arrow_len = (max(xmax) - min(xmin)) * 0.1 
arrow_mu_5_low = ROOT.TArrow(mu_m_inv_cut_low, max(ymax)*0.8,
                mu_m_inv_cut_low + arrow_len, max(ymax)*0.8, 0.005, "|>") 
arrow_mu_5_low.SetAngle(60)
arrow_mu_5_low.SetLineWidth(2)
arrow_mu_5_low.Draw()
arrow_mu_5_high = ROOT.TArrow(mu_m_inv_cut_high, max(ymax)*0.8,
                mu_m_inv_cut_high - arrow_len, max(ymax)*0.8, 0.005, "|>") 
arrow_mu_5_high.SetAngle(60)
arrow_mu_5_high.SetLineWidth(2)
arrow_mu_5_high.Draw()
#ROOT.gPad.Update()
hist_mu_0p5_5.Write()
hist_mu_5_5.Write()
hist_mu_25_5.Write()
hist_mu_2f_5.Write()
hist_mu_4f_5.Write()
hist_mu_4fqq_5.Write()

legend = ROOT.TLegend(0.1,0.6,0.6,0.85)
legend.AddEntry(hist_mu_0p5_1, "m_{s} = 0.5 GeV", "l")
legend.AddEntry(hist_mu_5_1, "m_{s} = 5 GeV", "l")
legend.AddEntry(hist_mu_25_1, "m_{s} = 25 GeV", "l")
legend.AddEntry(hist_mu_2f_1, "2 fermion", "f")
legend.AddEntry(hist_mu_4f_1, "4 fermion - 2#mu 2l", "f")
legend.AddEntry(hist_mu_4fqq_1, "4 fermion - 2#mu 2q", "f")
mu_title = ROOT.TLatex(0.1,0.9,"Z #rightarrow #mu^{+}#mu^{-} @ #sqrt{s} = 91.2 GeV")
mu_title.SetTextSize(0.05)
c_muon.cd(6)
legend.Draw()
mu_title.Draw()

c_muon.Print("../plots/ZTomumu_" + output_suffix + ".png")
cutflow_file.Close()

# plot the recoil mass for the muon channel 
mrec_file = ROOT.TFile("m_rec_muon.root","RECREATE")
mrec_file.cd()
c_muon_rec = ROOT.TCanvas()
c_muon_rec.cd()
hs_sig_mu_rec = ROOT.THStack("hs_sig_mu_rec","")
hs_bkg_mu_rec = ROOT.THStack("hs_bkg_mu_rec","")
mu_rec_xlow = -5
mu_rec_xhigh = 40
mu_rec_nbins = 18 
mu_rec_descrp = "Z #rightarrow #mu^{+}#mu^{-} vs. m_{mumu} @ 91.2 GeV"
hist_mu_0p5_rec = ROOT.TH1F("mu_0p5_m_rec",
mu_rec_descrp, mu_rec_nbins, mu_rec_xlow, mu_rec_xhigh)
hist_mu_2_rec = ROOT.TH1F("mu_2_m_rec",
mu_rec_descrp, mu_rec_nbins, mu_rec_xlow, mu_rec_xhigh)
hist_mu_5_rec = ROOT.TH1F("mu_5_m_rec",
mu_rec_descrp, mu_rec_nbins, mu_rec_xlow, mu_rec_xhigh)
hist_mu_10_rec = ROOT.TH1F("mu_10_m_rec",
mu_rec_descrp, mu_rec_nbins, mu_rec_xlow, mu_rec_xhigh)
hist_mu_15_rec = ROOT.TH1F("mu_15_m_rec",
mu_rec_descrp, mu_rec_nbins, mu_rec_xlow, mu_rec_xhigh)
hist_mu_25_rec = ROOT.TH1F("mu_25_m_rec",
mu_rec_descrp, mu_rec_nbins, mu_rec_xlow, mu_rec_xhigh)
hist_mu_2f_rec = ROOT.TH1F("mu_2f_m_rec",
mu_rec_descrp, mu_rec_nbins, mu_rec_xlow, mu_rec_xhigh)
hist_mu_4f_rec = ROOT.TH1F("mu_4f_m_rec",
mu_rec_descrp, mu_rec_nbins, mu_rec_xlow, mu_rec_xhigh)
hist_mu_4fqq_rec = ROOT.TH1F("mu_4fqq_m_rec",
mu_rec_descrp, mu_rec_nbins, mu_rec_xlow, mu_rec_xhigh)
hist_mu_0p5_rec.SetDefaultSumw2() 
hist_mu_2_rec.SetDefaultSumw2()
hist_mu_5_rec.SetDefaultSumw2()
hist_mu_10_rec.SetDefaultSumw2()
hist_mu_15_rec.SetDefaultSumw2()
hist_mu_25_rec.SetDefaultSumw2()
hist_mu_2f_rec.SetDefaultSumw2()
hist_mu_4f_rec.SetDefaultSumw2()
hist_mu_4fqq_rec.SetDefaultSumw2()
muons['0p5'].Draw("m_rec>>mu_0p5_m_rec", mu_cut_5, "goff")
muons['2'].Draw("m_rec>>mu_2_m_rec", mu_cut_5, "goff")
muons['5'].Draw("m_rec>>mu_5_m_rec", mu_cut_5, "goff")
muons['10'].Draw("m_rec>>mu_10_m_rec", mu_cut_5, "goff")
muons['15'].Draw("m_rec>>mu_15_m_rec", mu_cut_5, "goff")
muons['25'].Draw("m_rec>>mu_25_m_rec", mu_cut_5, "goff")
muons['2f'].Draw("m_rec>>mu_2f_m_rec", mu_cut_5, "goff")
muons['4f'].Draw("m_rec>>mu_4f_m_rec", mu_cut_5, "goff")
muons['4fqq'].Draw("m_rec>>mu_4fqq_m_rec", mu_cut_5, "goff")
#hist_mu_0p5_5.SetDirectory(0)
#hist_mu_5_5.SetDirectory(0)
#hist_mu_25_5.SetDirectory(0)
#hist_mu_2f_5.SetDirectory(0)
#hist_mu_4f_5.SetDirectory(0)
hist_mu_0p5_rec.SetLineColor(ROOT.kRed)
hist_mu_0p5_rec.SetLineWidth(2)
hist_mu_0p5_rec.SetLineStyle(1)
hist_mu_5_rec.SetLineColor(ROOT.kBlue+2)
hist_mu_5_rec.SetLineWidth(2)
hist_mu_5_rec.SetLineStyle(1)
hist_mu_25_rec.SetLineColor(ROOT.kGreen+2)
hist_mu_25_rec.SetLineWidth(2)
hist_mu_25_rec.SetLineStyle(1)
hist_mu_2f_rec.SetLineColor(ROOT.kBlack)
hist_mu_2f_rec.SetFillColor(ROOT.kGreen)
hist_mu_2f_rec.SetLineWidth(1)
hist_mu_2f_rec.SetLineStyle(1)
hist_mu_4f_rec.SetLineColor(ROOT.kBlack)
hist_mu_4f_rec.SetFillColor(ROOT.kYellow)
hist_mu_4f_rec.SetLineWidth(1)
hist_mu_4f_rec.SetLineStyle(1)
hist_mu_4fqq_rec.SetLineColor(ROOT.kBlack)
hist_mu_4fqq_rec.SetFillColor(ROOT.kOrange)
hist_mu_4fqq_rec.SetLineWidth(1)
hist_mu_4fqq_rec.SetLineStyle(1)

hs_bkg_mu_rec.SetMinimum(0)
hs_sig_mu_rec.SetMinimum(0)
hs_bkg_mu_rec.SetMaximum(50)
hs_sig_mu_rec.SetMaximum(50)

hs_sig_mu_rec.Add(hist_mu_0p5_rec)
hs_sig_mu_rec.Add(hist_mu_5_rec)
hs_sig_mu_rec.Add(hist_mu_25_rec)
hs_bkg_mu_rec.Add(hist_mu_2f_rec)
hs_bkg_mu_rec.Add(hist_mu_4f_rec)
hs_bkg_mu_rec.Add(hist_mu_4fqq_rec)

ymin = []
ymax = []
xmin = []
xmax = []
#ROOT.gPad.SetLogy()
hs_bkg_mu_rec.Draw("hist")
hs_bkg_mu_rec.GetHistogram().SetXTitle('m_{rec} [GeV]')
hs_bkg_mu_rec.GetHistogram().SetYTitle('Events/5 GeV')
hs_bkg_mu_rec.GetHistogram().SetTitleSize(0.05, "xy")
ROOT.gPad.Update()
ymin.append(ROOT.gPad.GetUymin())
ymax.append(ROOT.gPad.GetUymax())
xmin.append(ROOT.gPad.GetUxmin())
xmax.append(ROOT.gPad.GetUxmax())
hs_sig_mu_rec.Draw("hist, nostack, same")
ROOT.gPad.Update()
legend_rec = ROOT.TLegend(0.55,0.6,0.9,0.8)
legend_rec.AddEntry(hist_mu_0p5_rec, "m_{s} = 0.5 GeV", "l")
legend_rec.AddEntry(hist_mu_5_rec, "m_{s} = 5 GeV", "l")
legend_rec.AddEntry(hist_mu_25_rec, "m_{s} = 25 GeV", "l")
legend_rec.AddEntry(hist_mu_2f_rec, "2 fermion", "f")
legend_rec.AddEntry(hist_mu_4f_rec, "4 fermion - 2#mu 2l", "f")
legend_rec.AddEntry(hist_mu_4fqq_rec, "4 fermion - 2#mu 2q", "f")
legend_rec.Draw()
ROOT.gPad.Update()
c_muon_rec.Print("../plots/ZTomumu_rec_" + output_suffix + ".png")
file_mu_0p5_rec = ROOT.TFile("../combine/mu_0p5_mrec.root","RECREATE")
file_mu_2_rec = ROOT.TFile("../combine/mu_2_mrec.root","RECREATE")
file_mu_5_rec = ROOT.TFile("../combine/mu_5_mrec.root","RECREATE")
file_mu_10_rec = ROOT.TFile("../combine/mu_10_mrec.root","RECREATE")
file_mu_15_rec = ROOT.TFile("../combine/mu_15_mrec.root","RECREATE")
file_mu_25_rec = ROOT.TFile("../combine/mu_25_mrec.root","RECREATE")
file_mu_2f_rec = ROOT.TFile("../combine/mu_2f_mrec.root","RECREATE")
file_mu_4f_rec = ROOT.TFile("../combine/mu_4f_mrec.root","RECREATE")
file_mu_4fqq_rec = ROOT.TFile("../combine/mu_4fqq_mrec.root","RECREATE")
file_mu_tot_0p5_rec = ROOT.TFile("../combine/mu_tot_0p5_mrec.root","RECREATE")
file_mu_tot_2_rec = ROOT.TFile("../combine/mu_tot_2_mrec.root","RECREATE")
file_mu_tot_5_rec = ROOT.TFile("../combine/mu_tot_5_mrec.root","RECREATE")
file_mu_tot_10_rec = ROOT.TFile("../combine/mu_tot_10_mrec.root","RECREATE")
file_mu_tot_15_rec = ROOT.TFile("../combine/mu_tot_15_mrec.root","RECREATE")
file_mu_tot_25_rec = ROOT.TFile("../combine/mu_tot_25_mrec.root","RECREATE")
file_mu_0p5_rec.cd()
hist_mu_0p5_rec.Write()
file_mu_2_rec.cd()
hist_mu_2_rec.Write()
file_mu_5_rec.cd()
hist_mu_5_rec.Write()
file_mu_10_rec.cd()
hist_mu_10_rec.Write()
file_mu_15_rec.cd()
hist_mu_15_rec.Write()
file_mu_25_rec.cd()
hist_mu_25_rec.Write()
file_mu_2f_rec.cd()
hist_mu_2f_rec.Write()
file_mu_4f_rec.cd()
hist_mu_4f_rec.Write()
file_mu_4fqq_rec.cd()
hist_mu_4fqq_rec.Write()
hist_mu_tot_0p5_rec = ROOT.TH1F('tot_0p5',
                      mu_rec_descrp, mu_rec_nbins, mu_rec_xlow, mu_rec_xhigh)
hist_mu_tot_0p5_rec.Add(hist_mu_0p5_rec)
hist_mu_tot_0p5_rec.Add(hist_mu_2f_rec)
hist_mu_tot_0p5_rec.Add(hist_mu_4f_rec)
hist_mu_tot_0p5_rec.Add(hist_mu_4fqq_rec)
file_mu_tot_0p5_rec.cd()
hist_mu_tot_0p5_rec.Write()
hist_mu_tot_2_rec = ROOT.TH1F('tot_2',
                      mu_rec_descrp, mu_rec_nbins, mu_rec_xlow, mu_rec_xhigh)
hist_mu_tot_2_rec.Add(hist_mu_2_rec)
hist_mu_tot_2_rec.Add(hist_mu_2f_rec)
hist_mu_tot_2_rec.Add(hist_mu_4f_rec)
hist_mu_tot_2_rec.Add(hist_mu_4fqq_rec)
file_mu_tot_2_rec.cd()
hist_mu_tot_2_rec.Write()
hist_mu_tot_5_rec = ROOT.TH1F('tot_5',
                      mu_rec_descrp, mu_rec_nbins, mu_rec_xlow, mu_rec_xhigh)
hist_mu_tot_5_rec.Add(hist_mu_5_rec)
hist_mu_tot_5_rec.Add(hist_mu_2f_rec)
hist_mu_tot_5_rec.Add(hist_mu_4f_rec)
hist_mu_tot_5_rec.Add(hist_mu_4fqq_rec)
file_mu_tot_5_rec.cd()
hist_mu_tot_5_rec.Write()
hist_mu_tot_10_rec = ROOT.TH1F('tot_10',
                      mu_rec_descrp, mu_rec_nbins, mu_rec_xlow, mu_rec_xhigh)
hist_mu_tot_10_rec.Add(hist_mu_10_rec)
hist_mu_tot_10_rec.Add(hist_mu_2f_rec)
hist_mu_tot_10_rec.Add(hist_mu_4f_rec)
hist_mu_tot_10_rec.Add(hist_mu_4fqq_rec)
file_mu_tot_10_rec.cd()
hist_mu_tot_10_rec.Write()
hist_mu_tot_15_rec = ROOT.TH1F('tot_15',
                      mu_rec_descrp, mu_rec_nbins, mu_rec_xlow, mu_rec_xhigh)
hist_mu_tot_15_rec.Add(hist_mu_15_rec)
hist_mu_tot_15_rec.Add(hist_mu_2f_rec)
hist_mu_tot_15_rec.Add(hist_mu_4f_rec)
hist_mu_tot_15_rec.Add(hist_mu_4fqq_rec)
file_mu_tot_15_rec.cd()
hist_mu_tot_15_rec.Write()
hist_mu_tot_25_rec = ROOT.TH1F('tot_25',
                      mu_rec_descrp, mu_rec_nbins, mu_rec_xlow, mu_rec_xhigh)
hist_mu_tot_25_rec.Add(hist_mu_25_rec)
hist_mu_tot_25_rec.Add(hist_mu_2f_rec)
hist_mu_tot_25_rec.Add(hist_mu_4f_rec)
hist_mu_tot_25_rec.Add(hist_mu_4fqq_rec)
file_mu_tot_25_rec.cd()
hist_mu_tot_25_rec.Write()

