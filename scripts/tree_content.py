# import ROOT in batch mode
import sys,os
oldargv = sys.argv[:]
import ROOT

ROOT.gSystem.Load("libDelphes.so")
ROOT.gInterpreter.Declare('#include "classes/DelphesClasses.h"');


#example at https://cp3.irmp.ucl.ac.be/projects/delphes/browser/git/examples/Example1.py?rev=3a73e6df42bd9bbe5268a096139d21c13875c199
rootfile = '/home/tianyu/FCC-ee/scripts/../samples/eeTollS_5_inc.root'
chain = ROOT.TChain("Delphes")
chain.Add(rootfile)

chain.SetBranchStatus("Electron*", 1)
chain.SetBranchStatus("Muon*", 1)

i = 0

# create a ROOT Ntuple object to store all events
ntuple_electron = ROOT.TNtuple("electron", "electron ntuple", "iev:electron_pt:electron_eta:electron_phi")
ntuple_muon = ROOT.TNtuple("muon", "muon ntuple", "iev:muon_pt:muon_eta:muon_phi")
#tree= ROOT.TTree()
#electron_pt = []
#tree.Branch('electron_pt', ROOT.addressof(electron_pt), 'tree/F')

# loop over events
for entry in chain:
	print(i)
	
	# create arrays to store particle data in each event
	#electron_pt = []
	#electron_eta = []
	# loop over particles in each event
	for electron in entry.Electron:
		ntuple_electron.Fill(i, electron.PT, electron.Eta, electron.Phi)
	
	# write arrays for each event to the ntuple tree
	# tree.Fill()
	#ntuple.Fill(electron_pt)

	for muon in entry.Muon:
		ntuple_muon.Fill(i, muon.PT, muon.Eta, muon.Phi)
	i = i + 1

output = ROOT.TFile('ntuple.root', 'recreate')
ntuple_electron.Write()
ntuple_muon.Write()
output.Close()

# next: how to fill electron, muon, etc in tntuples? -- maybe try using multiple ntuples in one file 
