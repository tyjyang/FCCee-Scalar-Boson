# Setup
To use this repo,
```bash
git clone https://github.com/tyjyang/FCCee-Scalar-Boson
cd FCCee-Scalar-Boson
source scripts/setup.sh
```
Add `from ntuplizer import *` to access functions under `lib`

[TODO: modify `__init.py__` under `lib` so the user doesn't need to import all
files in the library.]

Make sure to call `load_delphes_lib()` in order for ROOT to understand data
in the delphes files.

# Filename
## ntuple files
We name our ntuple files in the following format:

`[delphes_file_name]:part1_var11_var12-part2-var21-var22.root`

- the colon `:` is to separate the delphes file name with the actual 
ntuple content
- the dash `-` is to separate ntuple trees, each containing info of one
particle
- underscore sign `_` is to separate variables for the same particle

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

# Selection
## Criteria
Selection criteria is passed in as a dict to the event chain of a delphes file.
The criteria takes the format:
`{"criteria":"part1-part2_var"}`
