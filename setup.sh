export CMSSW_VER=CMSSW_10_6_12
export DELPHES_FOLDER=Delphes-3.4.2

# get the full directory of the setup script.
export REPO_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $REPO_DIR

export OCAML_BIN=$REPO_DIR/../ocaml-4.12.0/bin
export PATH=$OCAML_BIN:$PATH
# setup environment for delphes
#source /cvmfs/sft.cern.ch/lcg/views/LCG_99/x86_64-centos7-gcc10-opt/setup.sh
source /cvmfs/sft.cern.ch/lcg/views/LCG_88/x86_64-slc6-gcc49-opt/setup.sh
source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.06.00/x86_64-centos7-gcc49-opt/root/bin/thisroot.sh

# install delphes
if [ -d "$DELPHES_FOLDER" ]; then
	echo Delphes already setup. 
else
	echo Delphes not found under current directory, compiling new instance...
	wget http://cp3.irmp.ucl.ac.be/downloads/Delphes-3.4.2.tar.gz
	tar -zxf ${DELPHES_FOLDER}.tar.gz
	cd $DELPHES_FOLDER 
	make -j 8 || echo Delphes failed to compile. Try exit and run setup from a clean shell.
	cd .. && rm ${DELPHES_FOLDER}.tar.gz 
fi

# setup CMSSW for accessing the software stack (e.g. git, python)
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -d $CMSSW_VER/src ]; then
	echo $CMSSW_VER already setup 
else
	echo Fetching $CMSSW_VER
	cmsrel $CMSSW_VER
fi
cd $CMSSW_VER/src && cmsenv && cd -

# overwrite CMSSW enviroment
#source /cvmfs/sft.cern.ch/lcg/views/LCG_99/x86_64-centos7-gcc10-opt/setup.sh
source /cvmfs/sft.cern.ch/lcg/views/LCG_88/x86_64-slc6-gcc49-opt/setup.sh
source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.06.00/x86_64-centos7-gcc49-opt/root/bin/thisroot.sh

# export delphes and python library paths
export DELPHES_PATH=$REPO_DIR/Delphes-3.4.2
export LD_LIBRARY_PATH="$DELPHES_PATH:$LD_LIBRARY_PATH"
export PYTHONPATH="$PYTHONPATH:$REPO_DIR/lib"
