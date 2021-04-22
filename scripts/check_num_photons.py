import ROOT
import numpy
import time
from ntuplizer import *
from helper import *



#-----------------
# Global Variables
#-----------------
delphes_path = '/uscms/home/tyang/nobackup/data/FCCee-Scalar-Boson-delphes-samples/'
delphes_file_list = ['eeTollS_0p5_inc.root', 'eeTollS_5_inc.root', 'eeTollS_25_inc.root',
                     '2fermion_whizard.root', 'four_lepton.root']
#delphes_file_list = ['eeTollS_0p5_inc.root']
ntuple_path = '../ntuples'
particles =  ['particle', 'photon']
photon_PID = 22
load_delphes_lib()

delphes_file_path = delphes_path + delphes_file_list[3]
evt_chain = load_delphes_file(delphes_file_path, particles)
reco_photon_num = ROOT.TH1I("reco_photon_num","number of reco photons",10,0,10)
reco_photon_num.GetXaxis().SetTitle("Number of Photons in a Event")
reco_photon_num.GetYaxis().SetTitle("Events")
gen_photon_num = ROOT.TH1I("gen_photon_num","number of gen photons",10,0,10)
gen_photon_num.GetXaxis().SetTitle("Number of Photons in a Event")
gen_photon_num.GetYaxis().SetTitle("Events")
for evt in evt_chain:
	reco_photon_num.Fill(get_num_ptcl(evt,'photon'))
	num_gen_photon = 0
	for gen_particle in evt.Particle:
		if gen_particle.PID == photon_PID:
			num_gen_photon += 1
	gen_photon_num.Fill(num_gen_photon)
c1 = ROOT.TCanvas("","",1200,450)
c1.Divide(2,1)
c1.cd(1)
reco_photon_num.Draw()
c1.cd(2)
gen_photon_num.Draw()
c1.SaveAs("../plots/num_photons_2f_whizard.pdf")
