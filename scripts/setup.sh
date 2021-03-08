source /cvmfs/cms.cern.ch/cmsset_default.sh
cd ~/FCC-ee/CMSSW_10_6_12/src && cmsenv && cd -

source /cvmfs/sft.cern.ch/lcg/views/LCG_88/x86_64-slc6-gcc49-opt/setup.sh
source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.06.00/x86_64-centos7-gcc49-opt/root/bin/thisroot.sh
#source /cvmfs/sft.cern.ch/lcg/views/LCG_92/x86_64-slc6-gcc62-opt/setup.sh
export DELPHES_PATH=/home/tianyu/FCC-ee/Delphes-3.4.2
export LD_LIBRARY_PATH="$DELPHES_PATH:$LD_LIBRARY_PATH"
export PYTHONPATH="$PYTHONPATH:/home/tianyu/FCC-ee/lib"
