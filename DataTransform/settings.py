import math
import time
import os
import numpy as np


# This is where you should put your midi files
source_folder = 'data/original/'

# fast way to import data once you have preprocessed them and saved in a pickle file
pickle_load_path = 'pickles/'

#------------------------------------
# Generation parameters
#------------------------------------

# Generation parameters
temperature = 1.0
sample_method = 'choice'
cutoff_sample_threshold = 0.0
number_of_tries = 1
#if there is velocity information (for every played note) but no held notes:
#then you can figure out which notes are played or held
#a note is held if the velocity is below a threshold, which is the following parameter

#------------------------------------
# Import parameters
#------------------------------------

velocity_threshold_such_that_it_is_a_played_note = 0.5
override_sampled_pitches_based_on_velocity_info = True
do_not_sample_in_evaluation = True


# Folder names or file names will be classified by those labels
classes = ['barock', 'classic'] #list of strings like 'Bach', 'Mozart'. Name a folder in your source_folder like that and make sure there are no files with that name

#whether to include unknown classes as a third class
include_unknown = False
if include_unknown:
    num_classes = len(classes) + 1
else:
    num_classes = len(classes)

#wheter to exclude files with tags from classes
only_unknown = False

#Wheter to run the evaluations on the train set
test_train_set = True


t = str(int(round(time.time())))

#activate the fast route to not always have to preprocess midi files
load_from_pickle_instead_of_midi = False

save_imported_midi_as_pickle = False
if save_imported_midi_as_pickle:
    pickle_store_folder = 'pickles/' + t + "/" #folder where pickles are stored (!= where loaded)
    if not os.path.exists(pickle_store_folder):
        os.makedirs(pickle_store_folder)

save_anything = True

split_equally_to_train_and_test = True
test_fraction = 0.1
save_preprocessed_midi = False
smaller_training_set_factor = 1.0 #multiply training set size by that factor (if higher than 1.0, will have unbalanced dataset if split_equally_to_train_and_test)

high_crop = 84 #where to cut off high notes. 84 = C6
low_crop = 24#where to cut off low notes. 24=C1
num_notes = 128 #constant for MIDI
new_num_notes = high_crop - low_crop #the actual number of pitches to use
SMALLEST_NOTE = 16 #set this to 16, if you want to include 16th notes as smallest notes. has to be a multiple of 4
MAXIMAL_NUMBER_OF_VOICES_PER_TRACK = 1 #will get overriden if there are less tracks than num_voices for a file
MAX_VELOCITY = 127.

max_songs = 100000 #if you want to reduce the maximum number of midi files to import, set this lower
equal_mini_songs = False #set this to true, if you want to remove imported songs if one class has higher
#we set this to True for MIDI-VAE, but think it's best for you to start with False

attach_instruments = False
include_only_monophonic_instruments = False

#the number of monophonic instrument tracks you want your final model to have
max_voices = 4

instrument_attach_method = '1hot-category' #'khot-instrument'
instrument_dim = 0

if instrument_attach_method == '1hot-category':
    instrument_dim = 16
elif instrument_attach_method == 'khot-category':
    instrument_dim = 4
elif instrument_attach_method == '1hot-instrument':
    instrument_dim = 128
elif instrument_attach_method == 'khot-instrument':
    instrument_dim = 7

#wheter to try song-completion, removing all but one track from the input and try to predict max_voice target pitches
song_completion = False


#------------------------------------
# VAE parameters (for vae_training and vae_evaluation)
#------------------------------------

input_length =  16
output_length = 16
lstm_size = 256
latent_dim = 256
batch_size = 256
learning_rate = 0.0002#1e-05 #1e-06
beta = 2
epsilon_std = 0.01
save_step = 10
shuffle_train_set = True
bidirectional = False
num_layers_encoder = 2
num_layers_decoder = 2
use_embedding = False
embedding_dim = 0
decode = True
optimizer = 'Adam' #Adam, #RMSprop
vae_loss = 'categorical_crossentropy'
activity_regularizer = None
reset_states = False
include_composer_feature = False
if include_composer_feature:
    composer_length = num_classes
else:
    composer_length = 0
include_composer_decoder = True
composer_weight = 0.1
if include_composer_decoder:
    num_composers = num_classes
else:
    num_composers = 0
split_lstm_vector = True
output_length *= max_voices
if not song_completion:
    input_length *= max_voices
else:
    max_voices = 1
history = True

include_silent_note = True
if use_embedding:
    assert(include_silent_note)
if include_silent_note:
    silent_dim = 1
else:
    silent_dim = 0
activation = 'softmax'
cell_type = 'GRU' #can be 'GRU', 'LSTM', SimpleRNN
silent_weight = 1.0 #set to 1.0 if disabled
teacher_force = False

epsilon_factor = 0.0 # set to nonzero if you really know what you are doing
#epsilon_factor = np.log(epsilon_std * epsilon_std)
#use epsilon_factor to scale the log_var by adding epsilon_factor to it
#this makes sure that sigma of the prior is at the same scale as the sigma that will be used to calculate z

extra_layer = True
lstm_activation = 'tanh'
lstm_state_activation = 'tanh'
decoder_additional_input = False
decoder_additional_input_dim = 0
decoder_input_composer = False
if decoder_input_composer:
    decoder_additional_input = True
    decoder_additional_input_dim += num_classes
signature_vector_length = 15
append_signature_vector_to_latent = False
if append_signature_vector_to_latent:
    decoder_additional_input = True
    decoder_additional_input_dim += signature_vector_length

# use instrument roll encoder and decoder
meta_instrument= True
meta_instrument_dim = instrument_dim
meta_instrument_length = max_voices
meta_instrument_activation = 'softmax'
meta_instrument_weight = 0.1

if not attach_instruments:
    instrument_dim = 0

signature_decoder = False
signature_dim = signature_vector_length
signature_activation = 'tanh'
signature_weight = 1.0

# use additional decoder at pitch output or instrument output to enforce mutual information with z
composer_decoder_at_notes_output=False
composer_decoder_at_notes_weight=1.0
composer_decoder_at_notes_activation='softmax'
composer_decoder_at_instrument_output=False
composer_decoder_at_instrument_weight=1.0
composer_decoder_at_instrument_activation='softmax'

if composer_decoder_at_notes_output or composer_decoder_at_instrument_output or include_composer_decoder:
    num_composers = num_classes
else:
    num_composers = 0

input_dim = new_num_notes + composer_length + silent_dim + instrument_dim
output_dim = new_num_notes+silent_dim + instrument_dim

# use velocity roll
meta_velocity=True
meta_velocity_length=output_length
meta_velocity_activation='sigmoid'
meta_velocity_weight=1.0

#use held notes roll
meta_held_notes=False
meta_held_notes_length=output_length
meta_held_notes_activation='softmax'
meta_held_notes_weight=0.1

combine_velocity_and_held_notes=False
if combine_velocity_and_held_notes:
    meta_held_notes = False

# use next pitch roll
meta_next_notes=False
meta_next_notes_output_length=output_length
meta_next_notes_weight=0.1
meta_next_notes_teacher_force=False #Not implemented in vae_training or vae_evaluation

activation_before_splitting='tanh'

epochs = 20
test_step = 1
verbose = True
show_plot = True
save_plot = True

load_previous_checkpoint = False
previous_epoch = 10
previous_checkpoint_path = 'models/autoencode/vae/1654423828-_ls_inlen_64_outlen_64_beta_2_lr_0.0002_lstmsize_256_latent_256_trainsize_216_testsize_25_epsstd_0.01/'


prior_mean=0.0
prior_std=1.0


#------------------------------------
# Additional stuff
#------------------------------------

instrument_names = [
#piano
'Acoustic Grand Piano',
'Bright Acoustic Piano',
'Electric Grand Piano',
'Honky-tonk Piano',
'Electric Piano 1',
'Electric Piano 2',
'Harpsichord',
'Clavinet',
#chromatic percussion
'Celesta',
'Glockenspiel',
'Music Box',
'Vibraphone',
'Marimba',
'Xylophone',
'Tubular Bells',
'Dulcimer',
#Organs
'Drawbar Organ',
'Percussive Organ',
'Rock Organ',
'Church Organ',
'Reed Organ',
'Accordion',
'Harmonica',
'Tango Accordion',
#Guitar
'Acoustic Guitar (nylon)',
'Acoustic Guitar (steel)',
'Electric Guitar (jazz)',
'Electric Guitar (clean)',
'Electric Guitar (muted)',
'Overdriven Guitar',
'Distortion Guitar',
'Guitar Harmonics',
#Bass[edit]
'Acoustic Bass',
'Electric Bass (finger)',
'Electric Bass (pick)',
'Fretless Bass',
'Slap Bass 1',
'Slap Bass 2',
'Synth Bass 1',
'Synth Bass 2',
#Strings[edit]
'Violin',
'Viola',
'Cello',
'Contrabass',
'Tremolo Strings',
'Pizzicato Strings',
'Orchestral Harp',
'Timpani',
#Ensemble[edit]
'String Ensemble 1',
'String Ensemble 2',
'Synth Strings 1',
'Synth Strings 2',
'Choir Aahs',
'Voice Oohs',
'Synth Choir',
'Orchestra Hit',
#Brass[edit]
'Trumpet',
'Trombone',
'Tuba',
'Muted Trumpet',
'French Horn',
'Brass Section',
'Synth Brass 1',
'Synth Brass 2',
#Reed[edit]
'Soprano Sax',
'Alto Sax',
'Tenor Sax',
'Baritone Sax',
'Oboe',
'English Horn',
'Bassoon',
'Clarinet',
#Pipe[edit]
'Piccolo',
'Flute',
'Recorder',
'Pan Flute',
'Blown bottle',
'Shakuhachi',
'Whistle',
'Ocarina',
#Synth Lead[edit]
'Lead 1 (square)',
'Lead 2 (sawtooth)',
'Lead 3 (calliope)',
'Lead 4 (chiff)',
'Lead 5 (charang)',
'Lead 6 (voice)',
'Lead 7 (fifths)',
'Lead 8 (bass + lead)',
#Synth Pad[edit]
'Pad 1 (new age)',
'Pad 2 (warm)',
'Pad 3 (polysynth)',
'Pad 4 (choir)',
'Pad 5 (bowed)',
'Pad 6 (metallic)',
'Pad 7 (halo)',
'Pad 8 (sweep)',
#Synth Effects[edit]
'FX 1 (rain)',
'FX 2 (soundtrack)',
'FX 3 (crystal)',
'FX 4 (atmosphere)',
'FX 5 (brightness)',
'FX 6 (goblins)',
'FX 7 (echoes)',
'FX 8 (sci-fi)',
#Ethnic[edit]
'Sitar',
'Banjo',
'Shamisen',
'Koto',
'Kalimba',
'Bagpipe',
'Fiddle',
'Shanai',
#Percussive[edit]
'Tinkle Bell',
'Agogo',
'Steel Drums',
'Woodblock',
'Taiko Drum',
'Melodic Tom',
'Synth Drum',
'Reverse Cymbal',
#Sound effects[edit]
'Guitar Fret Noise',
'Breath Noise',
'Seashore',
'Bird Tweet',
'Telephone Ring',
'Helicopter',
'Applause',
'Gunshot'
]

instrument_category_names = [
'piano',
'chromatic percussion',
'organs',
'guitar',
'bass',
'strings',
'ensemble',
'brass',
'reed',
'pipe',
'synth lead',
'synth pad',
'synth effects',
'ethnic',
'percussive',
'sound effects',
]
