import ROOT
import numpy
import time
from ntuplizer import *
from helper import *



#-----------------
# Global Variables
#-----------------
delphes_path = '/'
delphes_file_list = [#'eeTollS_0p5_inc.root', 
                     #'eeTollS_5_inc.root', 
                     #'eeTollS_25_inc.root',
                     #'ee2fermion_mutau.root',
                     #'four_lepton.root',
                     'eeZS_p5_photon500.root',
                     #'ee4lepton_muon'
                    ]
#delphes_file_list = ['eeTollS_0p5_inc.root']
ntuple_path = '../ntuples'
particles =  ['photon','particle']
photon_PID = 22
pythia_out_ID = [1]
load_delphes_lib()

delphes_file_path = delphes_path + delphes_file_list[0]
evt_chain = load_delphes_file(delphes_file_path, particles)
photon_E_reco = ROOT.TH1I("photon_E_reco","Energy of RECO Photon",40,0,20)
photon_E_reco.GetYaxis().SetTitle("Number of Photon / 1 GeV")
photon_E_reco.GetXaxis().SetTitle("Photon Energy [GeV]")
photon_E_gen = ROOT.TH1I("photon_E_gen","Energy of GEN Photon",40,0,20)
photon_E_gen.GetYaxis().SetTitle("Number of Photon / 1 GeV")
photon_E_gen.GetXaxis().SetTitle("Photon Energy [GeV]")

for ievt, evt in enumerate(evt_chain):
	for photon in evt.Photon:
		photon_E_reco.Fill(photon.E)
	for photon in evt.Particle:
		if photon.PID == photon_PID and photon.Status in pythia_out_ID:
			photon_E_gen.Fill(photon.E)
	if (ievt + 1) % 10000 == 0:
		print ievt + 1, 'have been processed'

c1 = ROOT.TCanvas("","",1200,450)
c1.Divide(2,1)
c1.cd(1)
photon_E_reco.Draw()
c1.cd(2)
photon_E_gen.Draw()
c1.SaveAs("../plots/E_photon_sig_0p5_IDEA_500MeV.pdf")
