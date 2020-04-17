'''
JobIterator

Translate a dictionary containing parameter/list pairs (key/value) into a Cartesian product
of all combinations of possible parameter values.  

Internally, the Cartesian product is stored as a list of dictionaries (parameter/value pairs).  
This class allows for indexed access to this list.  In addition the values of a particular element
of the list can be added to the property list of an existing object.

Example:
# Dictionary of possible parameter values
p = {'rotation': range(20),
     'Ntraining': [1,2,3,5,10,18],
     'dropout': [None, .1, .2, .5]}

# Create job iterator
ji = JobIterator(p)

# Select the ith element of the Cartesian product list.
# Add properties to object obj; the names of these  properties
#  are the keys from p and the values are the specific combination
#  of values in the ith element
ji.set_attributes_by_index(i, obj)
            
'''
from itertools import product

class JobIterator():
    def __init__(self, params):
        '''
        Constructor
        
        @param params Dictionary of key/list pairs
        '''
        self.params = params
        # List of all combinations of parameter values
        self.product = list(dict(zip(params,x))for x in product(*params.values()) )
        # Iterator over the combinations 
        self.iter = (dict(zip(params,x))for x in product(*params.values()))
        
    def next(self):
        '''
        @return The next combination in the list
        '''
        return self.iter.next()
        
    def get_index(self, i):
        '''
        Return the ith combination of parameters
        
        @param i Index into the Cartesian product list
        @return The ith combination of parameters
        '''
        
        return self.product[i]

    def get_njobs(self):
        '''
        @return The total number of combinationss
        '''
        
        return len(self.product)
    
    def set_attributes_by_index(self, i, obj):
        '''
        For an arbitrary object, set the attributes to match the ith job parameters
        
        @param i Index into the Cartesian product list
        @param obj Arbitrary object (to be modified)
        '''
        
        # Fetch the ith combination of parameter values
        d = self.get_index(i)
        # Iterate over the parameters
        for k,v in d.items():
            setattr(obj, k, v)
    