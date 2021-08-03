import ROOT
import numpy
import time
from ntuplizer import *
from helper import *
from collections import OrderedDict


#-----------------
# Global Variables
#-----------------
delphes_path = '/scratch5/arapyan/fcc_ee/scalar_delphes_idea/'
delphes_file_list = OrderedDict([
('0p5','eeZS_p5_photon500.root'), 
('2','eeZS_2_photon500.root'), 
('5','eeZS_5_photon500.root'), 
('10','eeZS_10_photon500.root'),
('15','eeZS_15_photon500.root'),
('25','eeZS_25_photon500.root')
#'ee2fermion_mutau.root',
#'ee4lepton_muon.root'
])
#delphes_file_list = ['eeTollS_0p5_inc.root']
ntuple_path = '../ntuples'
photon_PID = 22
pythia_out_ID = [1]
load_delphes_lib()
ROOT.gROOT.SetBatch()
photon_pt_reco = OrderedDict()
photon_E_reco = OrderedDict()
photon_eta_reco = OrderedDict()
hist_pixel_x = 800
hist_pixel_y = 600
num_hist_x = 3
num_hist_y = 2
canvas_pt = ROOT.TCanvas(
	"c_pt", "canvas for reco photon pt",
	hist_pixel_x * num_hist_x, hist_pixel_y * num_hist_y
)
canvas_E = ROOT.TCanvas(
	"c_E", "canvas for reco photon E",
	hist_pixel_x * num_hist_x, hist_pixel_y * num_hist_y
)
canvas_eta = ROOT.TCanvas(
	"c_eta", "canvas for reco photon eta",
	hist_pixel_x * num_hist_x, hist_pixel_y * num_hist_y
)
canvas_pt.Divide(num_hist_x, num_hist_y)
canvas_E.Divide(num_hist_x, num_hist_y)
canvas_eta.Divide(num_hist_x, num_hist_y)
i_pad = 0
evt_chain = OrderedDict()
for key, delphes_file in delphes_file_list.items():
	i_pad += 1
	delphes_file_path = delphes_path + delphes_file
	evt_chain[key] = load_delphes_file(delphes_file_path, 'photon')
	photon_pt_reco[key] = ROOT.TH1I(key+'_pt',key,20,0,20)
	photon_pt_reco[key].GetYaxis().SetTitle("Number of Photon / 1 GeV")
	photon_pt_reco[key].GetXaxis().SetTitle("Photon PT [GeV]")
	photon_E_reco[key] = ROOT.TH1I(key+'_E',key,20,0,20)
	photon_E_reco[key].GetYaxis().SetTitle("Number of Photon / 1 GeV")
	photon_E_reco[key].GetXaxis().SetTitle("Photon Energy [GeV]")
	photon_eta_reco[key] = ROOT.TH1I(key+'_eta',key,20,-5,5)
	photon_eta_reco[key].GetYaxis().SetTitle("Number of Photon / 0.5")
	photon_eta_reco[key].GetXaxis().SetTitle("Photon Eta")
	for ievt, evt in enumerate(evt_chain[key]):
		for photon in evt.Photon:
			photon_E_reco[key].Fill(photon.E)
			photon_pt_reco[key].Fill(photon.PT)
			photon_eta_reco[key].Fill(photon.Eta)
		if (ievt + 1) % 10000 == 0:
			print ievt + 1, 'have been processed'
	canvas_E.cd(i_pad)
	photon_E_reco[key].Draw()
	canvas_eta.cd(i_pad)
	photon_eta_reco[key].Draw()
	canvas_pt.cd(i_pad)
	photon_pt_reco[key].Draw()
canvas_E.Print("../plots/signal_RECO_photon_E_dist.png")
canvas_pt.Print("../plots/signal_RECO_photon_pt_dist.png")
canvas_eta.Print("../plots/signal_RECO_photon_eta_dist.png")
