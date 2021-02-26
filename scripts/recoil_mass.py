import ROOT
import numpy as np

electron_mass = 0.000511
muon_mass = 0.10566
COME = 91 # center of mass energy for e+e- collision
E_res = 1 # energy resolution for histograms

filename = "../ntuples/ntuple.root"

rootfile = ROOT.TFile.Open(filename)
key1 = 'lepton_inv_m'
key2 = 'recoil_m'

hist_pixel_x = 800
hist_pixel_y = 600
num_hist_x = 1
num_hist_y = 2
c = ROOT.TCanvas("canvas", "canvas", hist_pixel_x * num_hist_x, hist_pixel_y * num_hist_y)
c.Divide(num_hist_x, num_hist_y)
inv_m = ROOT.TH1D(key1, key1, COME/E_res, 0, COME)
recoil_m = ROOT.TH1D(key2, key2, 20, 0, 10)

iev_prev = 0
num_of_electrons = 0
#electron_pt = getattr(rootfile, "electron")
electron_pt = [getattr(entries, "electron_pt") for entries in getattr(rootfile, "electron")]
print electron_pt
electron_eta = []
electron_phi = []
'''
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
			electron_pt_max_removed = electron_pt[:]
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
			recoil_m.Fill(COME ** 2 + ((lep1+lep2).M()) ** 2 - 2 * COME * (lep1+lep2).E())
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
			muon_pt_max_removed = muon_pt[:]
			muon_pt_max_removed[i_max] = 0
			i_second_max = np.argmax(muon_pt_max_removed)
			lep1 = ROOT.TLorentzVector(0,0,0,0)
			lep2 = ROOT.TLorentzVector(0,0,0,0)
			lep1.SetPtEtaPhiM(muon_pt[i_max], muon_eta[i_max],
							muon_phi[i_max], muon_mass)
			lep2.SetPtEtaPhiM(muon_pt[i_second_max], muon_eta[i_second_max], 
							muon_phi[i_second_max], muon_mass)
			# calculate inv mass from these 2 lepton
			inv_m.Fill((lep1+lep2).M())
			recoil_m.Fill(COME ** 2 + ((lep1+lep2).M()) ** 2 - 2 * COME * (lep1+lep2).E())
		iev_prev = iev
		num_of_muons = 1
		muon_pt = [entries.muon_pt]
		muon_eta = [entries.muon_eta]
		muon_phi = [entries.muon_phi]

c.cd(1)
inv_m.Draw()
c.cd(2)
recoil_m.Draw()
c.SaveAs("../plots/canvas.pdf")
'''
