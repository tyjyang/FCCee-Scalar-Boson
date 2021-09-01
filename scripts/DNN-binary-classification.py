
import uproot 
import pandas as pd
import numpy as np
from collections import OrderedDict
ntuple_dir = '../ntuples_IDEA_500MeV_w_RECO_photons/'

sig_ntuple_filenames = OrderedDict([                                               
('0p5',('eeZS_p5_photon500:electron-muon:pt-eta-phi-cos_theta-alpha-'              
       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')),               
('2'  ,('eeZS_2_photon500:electron-muon:pt-eta-phi-cos_theta-alpha-'               
       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')),               
('5'  ,('eeZS_5_photon500:electron-muon:pt-eta-phi-cos_theta-alpha-'               
       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')),               
('10' ,('eeZS_10_photon500:electron-muon:pt-eta-phi-cos_theta-alpha-'              
       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')),               
('15' ,('eeZS_15_photon500:electron-muon:pt-eta-phi-cos_theta-alpha-'              
       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')),               
('25' ,('eeZS_25_photon500:electron-muon:pt-eta-phi-cos_theta-alpha-'              
       'p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root'))                
])                                                                                 
bkg_ntuple_filenames = OrderedDict([                                               
('2f-mutau'   ,('ee2fermion_mutau_photon500:electron-muon:pt-eta-phi-cos_theta-'   
                'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')),
('2f-e'       ,('ee2fermion_electron_photon500:electron-muon:pt-eta-phi-cos_theta-'
                'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')),
('4f-2mutau2l',('ee4lepton_mutau_photon500:electron-muon:pt-eta-phi-cos_theta-'    
                'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')),
('4f-2e2l',    ('ee4lepton_electron_photon500:electron-muon:pt-eta-phi-cos_theta-' 
                'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')),
('4f-2mutau2q',('ee4lepquark_mutau_photon500:electron-muon:pt-eta-phi-cos_theta-'  
                'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')),
('4f-2e2q',    ('ee4eequark_electron_photon500:electron-muon:pt-eta-phi-cos_theta-'
                'alpha-p_mag-m_inv-m_rec-p_mag_missing-cos_theta_p_missing.root')) 
])                                                                                 

sig_ntuple_files = OrderedDict()
bkg_ntuple_files = OrderedDict()
sig_trees = OrderedDict()
bkg_trees = OrderedDict()
for key, f in sig_ntuple_filenames.items():
	sig_filepath = ntuple_dir + f
	sig_ntuple_files[key] = uproot.open(sig_filepath)
	sig_trees[key] = OrderedDict()
	sig_trees[key]['electron'] = sig_ntuple_files[key]['electron'].arrays(
		outputtype = pd.DataFrame
	)
	sig_trees[key]['muon'] = sig_ntuple_files[key]['muon'].arrays(
		outputtype = pd.DataFrame
	)
for key, f in bkg_ntuple_filenames.items():
	bkg_filepath = ntuple_dir + f 
	bkg_ntuple_files[key] = uproot.open(bkg_filepath)
	bkg_trees[key] = OrderedDict()
	bkg_trees[key]['electron'] = bkg_ntuple_files[key]['electron'].arrays(
		outputtype = pd.DataFrame
	)
	bkg_trees[key]['muon'] = bkg_ntuple_files[key]['muon'].arrays(
		outputtype = pd.DataFrame
	)

# aggregate final state channels + make col for target
sig_arrays = OrderedDict()
for prod_chn, trees in sig_trees.items():
	sig_arrays[prod_chn] = pd.concat([trees['electron'], trees['muon']])
bkg_arrays = OrderedDict()
bkg_arrays['2f'] = pd.concat(
	[
		bkg_trees['2f-mutau']['electron'],
		bkg_trees['2f-mutau']['muon'],
		bkg_trees['2f-e']['electron'],
		bkg_trees['2f-e']['muon']
		
	]
)
bkg_arrays['4f-4l'] = pd.concat(
	[
		bkg_trees['4f-2mutau2l']['electron'],
		bkg_trees['4f-2mutau2l']['muon'],
		bkg_trees['4f-2e2l']['electron'],
		bkg_trees['4f-2e2l']['muon']
		
	]
)
bkg_arrays['4f-2l2q'] = pd.concat(
	[
		bkg_trees['4f-2mutau2q']['electron'],
		bkg_trees['4f-2mutau2q']['muon'],
		bkg_trees['4f-2e2q']['electron'],
		bkg_trees['4f-2e2q']['muon'] 
	]
)


sig = sig_arrays['0p5']
bkg = bkg_arrays['2f']
sig_nevts = len(sig.index)
bkg_nevts = len(bkg.index)
sig['isSignal'] = np.full(sig_nevts, 1)
bkg['isSignal'] = np.full(bkg_nevts, 0)
input_vars = list(sig.columns.values)
for x in ['cos_theta_1', 'cos_theta_2', 'p_mag_1', 'p_mag_2', 'isSignal']:
	input_vars.remove(x) 
sig_input = sig[input_vars]
bkg_input = bkg[input_vars]
sig_target = sig['isSignal']
bkg_target = bkg['isSignal']
X = pd.concat([sig_input, bkg_input])
Y = pd.concat([sig_target, bkg_target])

#print(len(X.index))
#print(len(Y.index))
#print(sig_input)
#print(bkg_target)
np.random.seed(7)
tts = np.random.rand(len(X)) > 0.2
#print(tts)
X_train = X[tts]
X_test = X[~tts]
Y_train = Y[tts]
Y_test = Y[~tts]
print(X_train)
print(X_test)
print(X_train.shape[0])
#'''
# baseline keras model
from keras.models import Sequential, Model
from keras.optimizers import SGD
from keras.layers import Input, Conv2D, MaxPool2D, Flatten, Dropout, Dense, BatchNormalization, Concatenate, Convolution1D, LSTM, Reshape
from keras.regularizers import l1,l2
from keras.utils import np_utils
from keras import optimizers
import keras
import tensorflow as tf

model = keras.Sequential([
	keras.layers.Flatten(input_shape=X.shape),
	keras.layers.Dense(64, activation=tf.nn.relu),
	keras.layers.Dense(64, activation=tf.nn.relu),
	keras.layers.Dense(64, activation=tf.nn.relu),
	keras.layers.Dense(64, activation=tf.nn.relu),
	keras.layers.Dense(32, activation=tf.nn.relu),
	keras.layers.Dense(8, activation=tf.nn.relu),
	keras.layers.Dense(1, activation=tf.nn.sigmoid),
])
model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])
model.summary()

model.fit(X_train, Y_train, epochs=50, batch_size=2048)
test_loss, test_acc = model.evaluate(X_test, Y_test)
print("accurary: ", test_acc)

#'''
