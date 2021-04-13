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
                     'eeTo2fermion.root', 'four_lepton.root']
#delphes_file_list = ['eeTollS_0p5_inc.root']
ntuple_path = '../ntuples'
particles =  ['electron', 'muon', 'photon']
var_to_wrt = ['pt', 'eta', 'phi', 'cos_theta', 'alpha',
              'p_mag', 'm_inv', 'm_rec','p_mag_missing', 'cos_theta_p_missing']  
ptcl_var_to_wrt = {'electron':var_to_wrt, 'muon':var_to_wrt}

load_delphes_lib()

delphes_file_path = delphes_path + delphes_file_list[0]
evt_chain = load_delphes_file(delphes_file_path, particles)
e_num = ROOT.TH1I("num_e","number of electrons",5,0,5)
mu_num = ROOT.TH1I("num_mu","number of muons",5,0,5)
for evt in evt_chain:
	e_num.Fill(get_num_ptcl(evt,'electron'))
	mu_num.Fill(get_num_ptcl(evt,'muon'))
c1 = ROOT.TCanvas()
e_num.SetLineColor(ROOT.kRed)
mu_num.SetLineColor(ROOT.kBlue)
e_num.Draw()
mu_num.Draw("SAME")
c1.SaveAs("../plots/num_leptons_sig_0p5.pdf")
