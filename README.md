# Setup
To use this repo,
```bash
git clone https://github.com/tyjyang/FCCee-Scalar-Boson -b dev-justin
cd FCCee-Scalar-Boson
source setup.sh
```
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
selection from final state particles.

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

