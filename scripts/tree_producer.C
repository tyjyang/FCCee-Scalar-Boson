#include "ExRootAnalysis/ExRootTreeReader.h"   //   -  Include needed delphes headers
#include "classes/DelphesClasses.h"            //   |
using namespace std;

void tree_producer() {
	TString rootfile = "../samples/eeTollS_5_inc.root";
	TChain chain("Delphes");
	chain.Add(rootfile);
    ExRootTreeReader *reader = new ExRootTreeReader(&chain);
	return 0;
}

