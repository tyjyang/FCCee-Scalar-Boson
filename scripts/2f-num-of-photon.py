import numpy as np
from ntuplizer import *

path_delphes_file = "../samples/eeTo2fermion.root"
load_delphes_lib()
chain = load_delphes_file(path_delphes_file, ["photon"])
n_evt = 0
n_0 = 0
n_2 = 0
n_3 = 0
n_g_3 = 0
for event in chain:
	i = 0
	E = []
	for photon in event.Photon:
		i = i + 1
		E.append(photon.E)
	if i == 0:
		n_0 += 1
	elif i == 2:
		n_2 += 1
	elif i == 3:
		n_3 += 1
	else:
		n_g_3 += 1
	n_evt += 1
print str(n_0) + "/" + str(n_evt) + " events contains 0 photons"
print str(n_2) + "/" + str(n_evt) + " events contains 2 photons"
print str(n_3) + "/" + str(n_evt) + " events contains 3 photons"
print str(n_g_3) + "/" + str(n_evt) + " events contains more than 3 photons"
