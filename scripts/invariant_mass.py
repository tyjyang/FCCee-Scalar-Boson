import ROOT
import numpy as np

electron_mass = 0.000511
muon_mass = 0.10566
COME = 91 # center of mass energy for e+e- collision
E_res = 1 # energy resolution for histograms

filename = "ntuple.root"

rootfile = ROOT.TFile.Open(filename)
#electron = rootfile.Get("electron")

iev_prev = 0
num_of_electrons = 0
electron_pt = []
electron_eta = []
electron_phi = []
key = 'lepton_inv_m'
c = ROOT.TCanvas("canvas_" + key, "canvas_" + key)
inv_m = ROOT.TH1D(key, key, COME/E_res, 0, COME)

for entries in rootfile.electron:
	iev = entries.iev
	# move to next particle within an event
	if iev == iev_prev:
		num_of_electrons += 1
		electron_pt.append(entries.electron_pt)
		electron_eta.append(entries.electron_eta)
		electron_phi.append(entries.electron_phi)
	else:
		# reached end of an event, calculate inv mass
		if num_of_electrons >= 2:
			# we select the highest pt leptons
			## find index of max pt electron
			i_max = np.argmax(electron_pt)
			## change max pt to 0 to find index of 2nd max pt  
			electron_pt_max_removed = electron_pt
			electron_pt_max_removed[i_max] = 0
			i_second_max = np.argmax(electron_pt_max_removed)
			lep1 = ROOT.TLorentzVector(0,0,0,0)
			lep2 = ROOT.TLorentzVector(0,0,0,0)
			lep1.SetPtEtaPhiM(electron_pt[i_max], electron_eta[i_max],
							electron_phi[i_max], electron_mass)
			lep2.SetPtEtaPhiM(electron_pt[i_second_max], electron_eta[i_second_max], 
							electron_phi[i_second_max], electron_mass)
			# calculate inv mass from these 2 leptons
			inv_m.Fill((lep1+lep2).M())
		iev_prev = iev
		num_of_electrons = 1
		electron_pt = [entries.electron_pt]
		electron_eta = [entries.electron_eta]
		electron_phi = [entries.electron_phi]

iev_prev = 0
num_of_muons = 0
muon_pt = []
muon_eta = []
muon_phi = []
for entries in rootfile.muon:
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
			muon_pt_max_removed = muon_pt
			muon_pt_max_removed[i_max] = 0
			i_second_max = np.argmax(muon_pt_max_removed)
			lep1 = ROOT.TLorentzVector(0,0,0,0)
			lep2 = ROOT.TLorentzVector(0,0,0,0)
			print(muon_pt)
			print(i_max, i_second_max)
			print(muon_pt[i_max], muon_pt[i_second_max])
			lep1.SetPtEtaPhiM(muon_pt[i_max], muon_eta[i_max],
							muon_phi[i_max], muon_mass)
			lep2.SetPtEtaPhiM(muon_pt[i_second_max], muon_eta[i_second_max], 
							muon_phi[i_second_max], muon_mass)
			print(lep1.Pt(), lep1.Eta(), lep1.Phi(), lep1.M())
			print(lep2.Pt(), lep2.Eta(), lep2.Phi(), lep2.M())
			print((lep1+lep2).M())
			print('=================')
			# calculate inv mass from these 2 leptons
			inv_m.Fill((lep1+lep2).M())
		iev_prev = iev
		num_of_muons = 1
		muon_pt = [entries.muon_pt]
		muon_eta = [entries.muon_eta]
		muon_phi = [entries.muon_phi]


inv_m.Draw()
c.SaveAs(key+".pdf")
