# setup CMSSW
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc700
cmsrel CMSSW_10_2_13
cd CMSSW_10_2_13/src
cmsenv

# clone Combine from GitHub
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit

cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v8.1.0

cd $CMSSW_BASE/src

# load necessary components from CombineHarvester
bash <(curl -s https://raw.githubusercontent.com/cms-analysis/CombineHarvester/master/CombineTools/scripts/sparse-checkout-https.sh)

# compile 
scramv1 b clean; scramv1 b -j 8

# clone tutorial
cd $CMSSW_BASE/src
git clone https://gitlab.cern.ch/adewit/combinetutorial-2020
cd combinetutorial-2020
