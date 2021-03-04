import ROOT
import numpy as np
import math

electron_mass = 0.000511
muon_mass = 0.10566
COME = 91 # center of mass energy for e+e- collision
E_res = 1 # energy resolution for histograms
xsec1 = 2.1859156934
xsec2 = 2000.0
xsec3 = 3.88
luminosity = 115.4
nevents_s = 300000.0
nevents_b = 1000000.0

filename1 = "ntuple.root"
filename2 = "ntuple_bkg.root"
filename3 = "ntuple_4lep_bkg.root"

rootfile1 = ROOT.TFile.Open(filename1)
rootfile2 = ROOT.TFile.Open(filename2)
rootfile3 = ROOT.TFile.Open(filename3)

key7 = 'rec_m_s'
key8 = 'rec_m_2lep_bkg'
key9 = 'rec_m_4lep_bkg'

m_recoil_mass_hists = ROOT.TFile("m_recoil_mass_hists.root","UPDATE")

hist_pixel_x = 800
hist_pixel_y = 600
num_hist_x = 1
num_hist_y = 1

canvas = ROOT.TCanvas("pt", "pt", hist_pixel_x * num_hist_x, hist_pixel_y * num_hist_y)
canvas.Divide(num_hist_x, num_hist_y)

rec_m_s = ROOT.TH1D(key7, 'Muon Di-lepton Recoil Mass;m rec;Events/GeV', 100, -10, 45)
rec_m_b_2 = ROOT.TH1D(key8, 'Muon Di-lepton Recoil Mass;m rec;Events/GeV', 100, -10, 45)
rec_m_b_4 = ROOT.TH1D(key9, 'Muon Di-lepton Recoil Mass;m rec;Events/GeV', 100, -10, 45)

def calculate_theta(eta):
	return 2 * np.arctan(math.exp(-eta))

def calculate_p(pt, theta):
	return pt / np.sin(theta)

def calculate_pL(pt, theta):
	return pt * np.cos(theta) / np.sin(theta)

def weight_factor(luminosity, xsec, nevents):
	return (luminosity * xsec) / nevents

sig_events = 0
bkg_events = 0
total_signal = 0
total_bkg_2 = 0
total_bkg_4 = 0
uncut_bkg_2 = 0
uncut_bkg_4 = 0 

for file in [rootfile1, rootfile2, rootfile3]:
	iev_prev = 0
	num_of_muons = 0
	muon_pt = []
	muon_eta = []
	muon_phi = []

	for entries in file.muon:
		iev = entries.iev
		# move to next particle within an event
		if iev == iev_prev:
			num_of_muons += 1
			muon_pt.append(entries.muon_pt)
			muon_eta.append(entries.muon_eta)
			muon_phi.append(entries.muon_phi)
		else:
			# reached end of an event, calculate inv mass
			if num_of_muons >= 2:
				# we select the highest pt leptons
				## find index of max pt muon
				i_max = np.argmax(muon_pt)
				## change max pt to 0 to find index of 2nd max pt  
				muon_pt_max_removed = muon_pt[:]
				muon_pt_max_removed[i_max] = 0
				i_second_max = np.argmax(muon_pt_max_removed)
				lep1 = ROOT.TLorentzVector(0,0,0,0)
				lep2 = ROOT.TLorentzVector(0,0,0,0)
				lep1.SetPtEtaPhiM(muon_pt[i_max], muon_eta[i_max],
								muon_phi[i_max], muon_mass)
				lep2.SetPtEtaPhiM(muon_pt[i_second_max], muon_eta[i_second_max], 
								muon_phi[i_second_max], muon_mass)
				pair = lep1 + lep2
				inv_m = pair.M()
				pt = pair.Pt()
				dphi = abs(muon_phi[i_max] - muon_phi[i_second_max])
				while dphi > np.pi:
					dphi = abs(dphi - 2.0 * np.pi)
				acpl = np.pi - dphi
				costheta1 = np.cos( 2 * np.arctan(np.exp(-muon_eta[i_max])))
				costheta2 = np.cos( 2 * np.arctan(np.exp(-muon_eta[i_second_max])))
				rec_m = COME ** 2 + pair.M() ** 2 - 2 * COME * pair.E()
				if rec_m > 0:
					recoil_m = (np.sqrt(abs(COME ** 2 + pair.M() ** 2 - 2 * COME * pair.E())))
				if rec_m < 0:
					recoil_m = (np.sqrt(abs(COME ** 2 + pair.M() ** 2 - 2 * COME * pair.E()))) * -1
				abp1 = muon_pt[i_max] * np.cosh(muon_eta[i_max])
				abp2 = muon_pt[i_second_max] * np.cosh(muon_eta[i_second_max])
				if (inv_m > 30):
					if (acpl > 0.15) and (costheta1 < 0.90) and (costheta2 < 0.95) and (abp1 > 27) and (abp2 > 25):
						if file == rootfile1:
							rec_m_s.Fill(recoil_m, (3.0 /10)*weight_factor(luminosity, xsec1, nevents_s))
							sig_events += 1
							total_signal += 1
						if file == rootfile2:
							rec_m_b_2.Fill(recoil_m, (3.0 /10) *weight_factor(luminosity, xsec2, nevents_b))
							bkg_events += 1
							total_bkg_2 += 1
						if file == rootfile3:
							rec_m_b_4.Fill(recoil_m, (3.0/10) *weight_factor(luminosity, xsec3, nevents_b))
							bkg_events += 1
							total_bkg_4 += 1
					else: 
						if file == rootfile1: 
							total_signal += 1
						if file == rootfile2:
							uncut_bkg_2 += 1
							total_bkg_2 += 1
						if file == rootfile3:
							uncut_bkg_4 += 1
							total_bkg_4 += 1
			iev_prev = iev
			num_of_muons = 1
			muon_pt = [entries.muon_pt]
			muon_eta = [entries.muon_eta]
			muon_phi = [entries.muon_phi]

#efficiency of cuts
#uncut_bkg = (float(uncut_bkg_2) * (3.0/10) * float(weight_factor(luminosity, xsec2, nevents_b))) + (float(uncut_bkg_4) * (3.0/10) * float(weight_factor(luminosity, xsec3, nevents_b)))
#total_bkg = (float(total_bkg_2) * (3.0/10) * float(weight_factor(luminosity, xsec2, nevents_b))) + (float(total_bkg_4) * (3.0/10) * float(weight_factor(luminosity, xsec3, nevents_b)))
#effs = float(sig_events) / float(total_signal)
#effb = uncut_bkg / total_bkg 

print len(rec_m_s)
print len(rec_m_b_2)
print len(rec_m_b_4)

#print sig_events
#print total_signal
#print uncut_bkg
#print total_bkg
#print effs
#print effb

rec_m_s.SetLineColor(ROOT.kRed)
rec_m_s.SetMinimum(0)
rec_m_b_2.SetLineColor(ROOT.kBlue)
rec_m_b_2.SetMinimum(0)
rec_m_b_4.SetLineColor(ROOT.kBlack)
rec_m_b_4.SetMinimum(0)

canvas.cd(1)
rec_m_s.Draw("HIST")
rec_m_b_2.Draw("HIST SAME")
rec_m_b_4.Draw("HIST SAME")

canvas.cd(1).SaveAs("rec_m.root")
rec_m_s.SaveAs("m_rec_m_s.root")
rec_m_b_2.SaveAs("m_rec_m_b_2.root")
rec_m_b_4.SaveAs("m_rec_m_b_4.root")

m_recoil_mass_hists.Append(canvas)
m_recoil_mass_hists.Write()

canvas.SaveAs("m_rec_m_w_cuts.pdf")