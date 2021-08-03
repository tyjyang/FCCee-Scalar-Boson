from ntuplizer import *
from helper import *
from cutflow import *
import time
import ROOT
#-----------------
# Global Variables
#-----------------
delphes_path = '/scratch5/arapyan/fcc_ee/scalar_delphes_idea/'
delphes_file_list = {
'0p5':'eeZS_p5_photon500.root', 
'2':'eeZS_2_photon500.root', 
'5':'eeZS_5_photon500.root', 
'10':'eeZS_10_photon500.root',
'15':'eeZS_15_photon500.root',
'25':'eeZS_25_photon500.root'
#'ee2fermion_mutau.root',
#'ee4lepton_muon.root'
}
electron_PID = 11
muon_PID = 13
tau_PID = 15
photon_PID = 22
pythia_out_ID = 23

lumi = 115.4
#w = [get_normalization_factor(f, lumi) for f in delphes_file_list]

#delphes_file_list = ['eeTollS_0p5_inc.root']
ntuple_path = '../ntuples_in_prep'
particles =  ['particle']
var_to_wrt = ['pt', 'eta', 'alpha_sep', 'cos_theta', 'alpha',
              'p_mag', 'm_inv', 'm_rec','p_mag_missing', 'cos_theta_p_missing']  
ptcl_var_to_wrt = {'electron':var_to_wrt, 'muon':var_to_wrt}

load_delphes_lib()

ROOT.gROOT.SetBatch()
hist_pixel_x = 800
hist_pixel_y = 600
num_hist_x = 3
num_hist_y = 2
canvas = ROOT.TCanvas(
	"c_gen_photon", "canvas for gen photon origin in signal files",
	hist_pixel_x * num_hist_x, hist_pixel_y * num_hist_y
)
canvas.Divide(num_hist_x, num_hist_y)
hists = {}
photon_file = ROOT.TFile("gen_photon_origin.root", "RECREATE")
photon_file.cd()
for i, (key,delphes_file) in enumerate(delphes_file_list.items()):
	print canvas
	print i, key, delphes_file
	canvas.cd(i+1)
	hists[key] = ROOT.TH2S(key, key, 60, 0, 60, 300, -50, 250)#key, 'photon origin in sig ' + key)
	delphes_file_path = delphes_path + delphes_file
	print "checking gen photon origins in: ", delphes_file_path
	print "-------------------------------------------------------------------"
	evt_chain = load_delphes_file(delphes_file_path, particles)
	meson_cand = 0
	meson_evts = 0
	meson_evts_exclusive = 0
	for ievt, evt in enumerate(evt_chain):
		counter = 0
		#print 'Event number ', ievt, ": "
		#print "=============================="
		#print "Hard leptons excluding incoming: "
		for cand in evt.Particle:
			if cand.PID == photon_PID and cand.E > 0.5:
				hists[key].Fill(cand.Status, cand.M1)
				if cand.M1 > 100: meson_cand += 1
				if cand.M1 > 100 and counter == 0:
					counter += 1
					meson_evts += 1
		if ievt % 10000 == 0: print ievt
	hists[key].GetXaxis().SetTitle("Photon Pythia Status ID")
	hists[key].GetYaxis().SetTitle("Photon Mother ID")
	hists[key].Write()
	hists[key].Draw("COLZ")
	print 'meson cand in', key, meson_cand
	print 'mesion events in ', key, meson_evts
print "loop finished"
canvas.Print("../plots/gen_photon_origin.png")
