# Setup
To use this repo,
```bash
git clone https://github.com/tyjyang/FCCee-Scalar-Boson
cd FCCee-Scalar-Boson
source setup.sh
```
It should be noted here that you'd have to **remove any CMSSW setup** and start 
from a clean shell before `setup.sh` can properly install delphes.

# Modules
This repository provides pre-written functions that aims to modularize the 
analysis process and allow easy customization of the analysis workflow.

Functions are grouped into python files under the `lib` folder. 
- `helper.py`: The helper functions including calculation of variables such as
acoplanarity, selection of particle subsets of size n from all N candidates, 
and string parsing. It also includes dictionaries for generation level
information for the delphes files, and other physical constants.
- `ntuplizer.py`: Functions used to extract the information of interest from 
delphes files and write them into ntuple files. This include loading the delphes
data, creating and opening the ntuple trees for writing, and functions to make
selections on final state particles.

# Writing Scripts
We use the event loop model, where we look at all information from one event at
once before moving to the next event (row by row). The scripts call functions 
from the `lib` files, and by putting in customary parameters into those 
function, one can quickly implement analysis procedures for different physics
purposes.

Any script should contain the following elements:
- Import files under `lib`. e.g. `from ntuplizer import *`
- Call `load_delphes_lib()` to access the delphes-formatted data.
- Customary variables like delphes filename and particles/variables of interest.
- An event loop to go through all the events within a delphes file.

Other optional components include:
- Pre-select particle candidates to be written into the ntuple tree, by calling
the selection functions under `lib/ntuplizer.py` with customary parameters.
- Efficiency counters for those selection functions.

Below are more detailed documentation. Read until this point to learn the basic
use of the code.
---

# Variables

## As arguments in selection functions
We require that each selection and cut function takes only one variable at a
time. That variable could be either contained in the delphes sample already, or
to be calculated in the fly. No matter what the case is, we always, at the end,
single out one variable for selection.
## variable case
We use snake-case for all particle variables in our code. In order to access
variable data in delphes, we have to convert variables in our case to the 
delphes format. 
## variable calculation
To calculate the variables on demand, we call the calculation functions in
`lib/helper.py`. The functions are called by the dictionary `calc_var_func_call`
where it links the variable name to its calculation function. Arguments of the
functions are linked to the variable name in another dict `calc_var_func_args`.
## Variable options
- delphes
    - "pt"
    - "eta"
    - "phi"
    - "charge"
    - "energy"
- calculated
    - "theta"
    - "phi_a"
    - "alpha"
    - "cos_theta"
    - "m_inv"
    - "m_rec"

# Particle Candidates
Particles within a delphes event are stored as TTree objects, each containing 
one particle type. 
Within each particle tree, individual particles are arranged in a sequential order. 
We assign to each individual particle an index counting from zero, based on the 
order it's stored in the delphes file. 
For calculation of certain variables, a group of N particles might be needed.
We call this group of N particle a "candidate". Note that the N particles do not
need to be of the same type.

To access the particle candidates, we use `ptcl_cand` dictionaries of the form:
 `OrderedDict([('particle_type_1',[indices1]), ('particle_type_2',[indices2])])`. 
Note that we use the ordered dictionary for reasons that will become clear later.
For convenience, when multiple candidate groups are all of the same particle 
type, we will put them together in a dictionary of the form:
`{'particle":[ [idx1], [idx2], ...]}`. When calculating for variables, we then
dissemble it into dictionaries with values containing only one list of indices.

We usually pass a group of N particle for calculation of multiple variables at
once, as it fits the data format to be written to the ntuple trees, which are
rectangular arrays of floats. One issue with this approach is that different 
variables takes in differnt number of particles to calculate. For example, it 
takes two particles to calculate the invariant mass on the lepton pair, while it
only takes one to calculate the forward angle theta from the pseudorapidity eta.
Also, like in this example, we want to calculate theta twice, for each particle.
For this reason, when the number of particles it takes to calculate a variable 
(n) differs from the number of particles in the candidate group passed in (N). 
We do the following:
- If `(N mod n) == 0`, we divide the N particles into groups of size n. And for
each group, we calculate the variable
- If `(N mod n) == r != 0 and N > n`, we ignore the last `r` particles, can do
the same thing as above for the `N-r` particles. 
- If `N < n`, we return an error message.
Note that since both the division of the groups and the discard of the remaining
particles depend on the order of the dictionary passed in, we have to use 
OrderedDict, as said before.
