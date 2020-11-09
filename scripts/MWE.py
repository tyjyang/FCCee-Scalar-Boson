import ROOT
ROOT.gSystem.Load("libDelphes")

rootfile = '../samples/eeTollS_5_inc.root'
chain = ROOT.TChain("Delphes")
chain.Add(rootfile)
reader = ROOT.ExRootTreeReader(chain)
