import ROOT
import numpy
import time
from ntuplizer import *
from helper import *
from cutflow import *

# load ROOT ntuples
ntuple_path = '../ntuples/'
ntuple_sig_files = [('eeTollS_0p5_inc:electron-muon:pt-eta-phi-cos_theta-'
                     'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root'),
                    ('eeTollS_5_inc:electron-muon:pt-eta-phi-cos_theta-'
                     'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root'),
                    ('eeTollS_25_inc:electron-muon:pt-eta-phi-cos_theta-'
                     'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')]
ntuple_bkg_files = [('eeTo2fermion:electron-muon:pt-eta-phi-cos_theta-'
                     'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root'),
                    ('four_lepton:electron-muon:pt-eta-phi-cos_theta-'
                     'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')]
ntuple_sig_filepath = []
ntuple_bkg_filepath = []
for f in ntuple_sig_files: ntuple_sig_filepath.append(ntuple_path + f)
for f in ntuple_bkg_files: ntuple_bkg_filepath.append(ntuple_path + f)
sig = {}
bkg = {}
sig['0p5'] = ROOT.TFile.Open(ntuple_sig_filepath[0])
sig['5']   = ROOT.TFile.Open(ntuple_sig_filepath[1])
sig['25']  = ROOT.TFile.Open(ntuple_sig_filepath[2])
bkg['2f']  = ROOT.TFile.Open(ntuple_bkg_filepath[0])
bkg['4f']  = ROOT.TFile.Open(ntuple_bkg_filepath[1])
# get normalization factors for the ntuple files
lumi = 115.4
w = {}
w['0p5'] = get_normalization_factor(ntuple_sig_files[0], lumi)
w['5'] = get_normalization_factor(ntuple_sig_files[1], lumi)
w['25'] = get_normalization_factor(ntuple_sig_files[2], lumi)
w['2f'] = get_normalization_factor(ntuple_bkg_files[0], lumi)
w['4f'] = get_normalization_factor(ntuple_bkg_files[1], lumi)
# load electron/muon trees from the ntuple files
electrons = {}
muons = {}
for key, value in sig.items():
	electrons[key] = getattr(value, "electron")
	electrons[key].SetWeight(w[key])
	muons[key] = value.Get("muon")
	muons[key].SetWeight(w[key])
for key, value in bkg.items():
	electrons[key] = value.Get("electron")
	electrons[key].SetWeight(w[key])
	muons[key] = value.Get("muon")
	muons[key].SetWeight(w[key])
print ('normalized num of Z-> ee from singal with m_s = 0.5 GeV: ',
       electrons['0p5'].GetEntries()*w['0p5'])
# specifying the cuts in the cutflow
electron_cuts = {}
muon_cuts = {}
cut_names = ['anlge','momentum','alpha','m_inv','cos_theat_p_missing']
#electron_cuts['angle'] = (
#"(leading_cos_theta < 0.9 && leading_cos_theta > -0.9) &&"
#"(trailing_cos_theta < 0.9 && trailing_cos_theta > -0.9)")
electron_cuts['angle'] = (
"(leading_eta < 1.47 && leading_eta > -1.47) &&"
"(trailing_eta < 1.47 && trailing_eta > -1.47)")

muon_cuts['angle'] = (
"(leading_cos_theta < 0.94 && leading_cos_theta > -0.94) &&"
"(trailing_cos_theta < 0.94 && trailing_cos_theta>-0.94)")

electron_cuts['momentum'] = "leading_p_mag > 27 && trailing_p_mag > 20"
muon_cuts['momentum'] = "leading_p_mag > 30 && trailing_p_mag > 20"

electron_cuts['alpha'] = "alpha > 0.11 && alpha < 2.0"
muon_cuts['alpha'] = electron_cuts['alpha']

electron_cuts['m_inv'] = "m_inv > 20 && m_inv < 100"
muon_cuts['m_inv'] = electron_cuts['m_inv']

electron_cuts['cos_theta_p_missing'] = (
"p_mag_missing<=2 || (p_mag_missing>2&&"
"(cos_theta_p_missing<0.98||cos_theta_p_missing>-0.98))")
muon_cuts['cos_theta_p_missing'] = electron_cuts['cos_theta_p_missing']

hist_pixel_x = 800
hist_pixel_y = 600
num_hist_x = 2
num_hist_y = 3
c_electron = ROOT.TCanvas("electron_cutflow","cutflow plots for Z -> ee at 91.2 GeV",
                           hist_pixel_x * num_hist_x, hist_pixel_y * num_hist_y)
c_electron.Divide(num_hist_x, num_hist_y)

c_electron.cd(1)
electrons['0p5'].Draw(">>e_cut1",electron_cuts['angle'],"entrylist")
e_cut1 = ROOT.gDirectory.Get("e_cut1")
print 'num of evts passing angle cut: ', e_cut1.GetN()*w['0p5']
hist_e1 = ROOT.TH1F("e_angle","Z->ee vs. cos(#theta) @ 91.2 GeV",
                     20,-1,1)
hist_e1.SetXTitle('cos(#theta)')
hist_e1.SetYTitle('Events')
hist_e1.SetOption("HIST") # suppress error bars
hist_e1.SetStats(ROOT.kFALSE) # turn off stats box
hist_e1.SetLineColor(ROOT.kRed)
hist_e1.SetLineWidth(1)
hist_e1.SetLineStyle(1)
electrons['0p5'].Draw("leading_cos_theta>>e_angle")

c_electron.cd(2)
electrons['0p5'].Draw(">>e_cut2",electron_cuts['angle']+'&&'+electron_cuts['momentum'],"entrylist")
e_cut2 = ROOT.gDirectory.Get("e_cut2")
print 'num of evts passing momentum cut: ', e_cut2.GetN()*w['0p5']
hist_e2 = ROOT.TH1F("e_momentum","Z->ee vs. |p_1| @ 91.2 GeV",
                     50,0,50)
hist_e2.SetXTitle('|p_1|')
hist_e2.SetYTitle('Events/1 GeV')
hist_e2.SetOption("HIST") # suppress error bars
hist_e2.SetStats(ROOT.kFALSE) # turn off stats box
hist_e2.SetLineColor(ROOT.kRed)
hist_e2.SetLineWidth(1)
hist_e2.SetLineStyle(1)
electrons['0p5'].Draw("leading_p_mag",electron_cuts['angle'])

'''
c_electron.cd(1)
ROOT.gPad.SetLogy() 
electrons['0p5'].Draw(">>e_cut1",electron_cuts['alpha'],"entrylist")
e_cut1 = ROOT.gDirectory.Get("e_cut1")
print 'num of evts passing alpha cut: ', e_cut1.GetN()*w['0p5']
hist_e1 = ROOT.TH1F("e_alpha","Z->ee vs. Modified Acoplanarity @ 91.2 GeV",
                     30,0,3)
hist_e1.SetXTitle('#alpha [rad]')
hist_e1.SetYTitle('Events/0.1 rad')
hist_e1.SetOption("HIST") # suppress error bars
hist_e1.SetLineColor(ROOT.kRed)
hist_e1.SetLineWidth(1)
hist_e1.SetLineStyle(1)
electrons['0p5'].Draw("alpha>>e_alpha")
#hist_e1 = ROOT.gDirectory.Get("hist_e1")
'''

c_electron.SaveAs("../plots/test.pdf")
#evtlist = [int(evtList.GetEntry(i)) for i in range(evtList.GetN())]
#electrons['0p5'].SetEntryList(evtList)
#electrons['0p5'].Draw('m_rec')
#i = 0
#for i,evt in enumerate(electrons['0p5']):
	#print getattr(evt, "leading_pt")
#	if i in evtList:
#		i += 1
#print i
#print tree.GetEntry(10)
#electron_m_rec = [ for i in evtList]
#print len(electron_m_rec)

