import os, sys
os.system('export PYTHONPATH="/home/tianyu/FCC-ee/lib"')
args = sys.argv[:]
from ntuplizer import *

# convert command line argument into a python dict for particle variable data
import json
particle_variable = json.loads(args[2])

load_delphes()
delphes_to_ntuple(args[1], particle_variable)


