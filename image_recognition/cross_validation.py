'''
Author: Alan Lee
File to perform cross validation on the OU SuperComputer
'''
from load_data import *
from networks import *
from job_control import *
import argparse
import pickle

def generate_fname(args):
    '''
    Generate the base file name for output files/directories.
    
    The approach is to encode the key experimental parameters in the file name.  This
    way, they are unique and easy to identify after the fact.
    '''
    #Convolutional Size
    conv_str = '_'.join(str(x) for x in args.conv_size)

    # Number of Filters
    filters_str = '_'.join(str(x) for x in args.conv_nfilters)

    # Pooling
    pooling_str = '_'.join(str(x) for x in args.pooling)

    # Hidden unit configuration
    dense_str = '_'.join(str(x) for x in args.dense)
    
    # Dropout
    if args.dropout is None:
        dropout_str = ''
    else:
        dropout_str = 'drop_%0.2f_'%(args.dropout)
        
    # L2 regularization
    if args.L2_regularizer is None:
        regularizer_str = ''
    else:
        regularizer_str = 'L2_%0.6f'%(args.L2_regularizer)
    
    # Put it all together
    return "%s/ABET_conv_size_%s_filters_%s_pool_%s_dense_%s_drop_%s_l2_%s"%(args.results_path,
                                                                        conv_str, 
                                                                        filters_str, 
                                                                        pooling_str, 
                                                                        dense_str, 
                                                                        dropout_str, 
                                                                        regularizer_str)

def augment_args(args):
    '''
     This control uses a varied set of hyperparameters to find the best set.
    '''
    index = args.exp_idx
    p = {'conv_size':[[3,3,3], [3,3,5],[3,5,5]],
         'conv_nfilters':[[5,5,5],[5,10,10],[5,10,15]],
         'pooling':[[2,2,2],[2,4,4],[4,4,4]],
         'dense':[[10,5,3],[100,10],[200,10]],
         'dropout':[.1,.2,.5],
         'L2_regularizer':[.0001, .001,.01]}
    
    ji = JobIterator(p)
    n_jobs = ji.get_njobs()
    assert(index >= 0 and index < n_jobs), "EXP_IND: Must be less than the number of total jobs"
    ji.set_attributes_by_index(index, args)

def execute_exp(args=None):
    if args is None:
        parser = create_parser()
        args = parser.parse_args([])
    augment_args(args)
        
    ins_train = np.load(args.dataset + '/ins_train.npy')
    outs_train = np.load(args.dataset + '/outs_train.npy')
    ins_val = np.load(args.dataset + '/ins_val.npy')
    outs_val = np.load(args.dataset + '/outs_val.npy')
        
    convolutions = zip(args.conv_nfilters, args.conv_size)
    model = create_classifier_network((ins_train.shape[1],ins_train.shape[2]),
                                  1,
                                  convolutions,
                                  args.pooling,
                                  args.dense,
                                  lrate=args.lrate,
                                  p_dropout=args.dropout,
                                  lambda_l2=args.L2_regularizer)
    
    early_stopping_cb = keras.callbacks.EarlyStopping(patience=args.patience,
                                                      restore_best_weights=True,
                                                      min_delta=args.min_delta)
    
    generator = training_set_generator_images(ins_train, outs_train, batch_size=args.batch)

    
    print('fitting model')
    # Learn
    history = model.fit_generator(generator,
                                  epochs=args.epochs,
                                  steps_per_epoch=2,
                                  verbose=args.verbose>=2,
                                  use_multiprocessing=False,
                                  validation_data=(ins_val, outs_val), 
                                  callbacks=[early_stopping_cb])
    
    # Generate log data
    print('generating data')
    results = {}
    results['args'] = args
    results['predict_validation_eval'] = model.evaluate(ins_val, outs_val)
    results['history'] = history.history
    
    # Save results
    fbase = generate_fname(args)
    results['fname_base'] = fbase
    fp = open("%s_results.pkl"%(fbase), "wb")
    pickle.dump(results, fp)
    fp.close()
    
    # Save Model
    model.save("%s_model"%(fbase))
    
def create_parser():
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(description='ABET Scanner')
    parser.add_argument('-epochs', type=int, default=100, help='Training epochs')
    parser.add_argument('-dataset', type=str, default='data', help='Data set file')
    parser.add_argument('-results_path', type=str, default='./results', help='Results directory')
    parser.add_argument('-conv_size', nargs='+', type=int, default=[3, 3], help='Size of the convolutional layer (sequence of ints)')
    parser.add_argument('-conv_nfilters', nargs='+', type=int, default=[10,15], help='Number of filters for each covolutional layer')
    parser.add_argument('-pooling', nargs='+', type=int, default=[2, 2], help='A list of pooling sizes after each convolutional layer (sequence of ints)')
    parser.add_argument('-dense', nargs='+', type=int, default=[100, 10,3], help='Number of units per dense layers after convolution (sequence of ints)')
    parser.add_argument('-dropout', type=float, default=.30, help='Dropout rate')
    parser.add_argument('-lrate', type=float, default=0.001, help="Learning rate")
    parser.add_argument('-L2_regularizer', type=float, default=None, help="L2 regularization parameter")
    parser.add_argument('-min_delta', type=float, default=0.01, help="Minimum delta for early termination")
    parser.add_argument('-patience', type=int, default=35, help="Patience for early termination")
    parser.add_argument('-verbose', '-v', action='count', default=0, help="Verbosity level") 
    parser.add_argument('-batch', type=int, default=100, help="Batch Size")
    parser.add_argument('-exp_idx', type=int, default=1, help='Experiment Index')
    return parser

def check_args(args):
    assert (args.dropout is None or (args.dropout > 0.0 and args.dropout < 1)), "Dropout must be between 0 and 1"
    assert (args.lrate > 0.0 and args.lrate < 1), "Lrate must be between 0 and 1"
    assert (args.L2_regularizer is None or (args.L2_regularizer > 0.0 and args.L2_regularizer < 1)), "L2_regularizer must be between 0 and 1"
    
#################################################################
if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    check_args(args)
    execute_exp(args)
