import numpy as np
from ntuplizer import *

path_delphes_file = "../samples/eeTo2fermion.root"
load_delphes_lib()
chain = load_delphes_file(path_delphes_file, ["photon"])
n_evt = 0
n_pass = 0
for event in chain:
	E = []
	for photon in event.Photon:
		E.append(photon.E)
	n_evt += 1
	if len(E) == 0:
		n_pass += 1
	else:
		E_max = max(E)
		if E_max < 10:
			n_pass += 1
			print E_max
print str(n_pass) + "/" + str(n_evt) + " events has highest photon energy less than 10 GeV"
