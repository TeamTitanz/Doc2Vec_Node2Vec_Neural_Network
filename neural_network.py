#
# Imports
#
import numpy as np
import pickle as p

#
# Transfer functions
#

def sgm(x, Derivative=False):
    if not Derivative:
        return 1.0 / (1.0 + np.exp(-x))
    else:
        out = sgm(x)
        return out * (1.0 - out)

def linear(x, Derivative=False):
    if not Derivative:
        return x
    else:
        return 1.0

def gaussian(x, Derivative=False):
    if not Derivative:
        return np.exp(-x**2)
    else:
        return -2*x*np.exp(-x**2)

def tanh(x, Derivative=False):
    if not Derivative:
        return np.tanh(x)
    else:
        return 1.0 - np.tanh(x)**2

def truncLinear(x, Derivative=False):
    if not Derivative:
        y = x.copy()
        y[y < 0] = 0
        return y
    else:
        return 1.0

#
# Classes
#
class BackPropagationNetwork:
    """A back-propagation network"""
    
    #
    # Class methods
    #
    def __init__(self, layerSize, layerFunctions=None):
        """Initialize the network"""
        
        self.layerCount = 0
        self.shape = None
        self.weights = []
        self.tFuncs = []
        
        # Layer info
        self.layerCount = len(layerSize) - 1
        self.shape = layerSize
        
        if layerFunctions is None:
            lFuncs = []
            for i in range(self.layerCount):
                if i == self.layerCount - 1:
                    lFuncs.append(TransferFunctions.linear)
                else:
                    lFuncs.append(TransferFunctions.sgm)
        else:
            if len(layerSize) != len(layerFunctions):
                raise ValueError("Incompatible list of transfer functions.")
            elif layerFunctions[0] is not None:
                raise ValueError("Input layer cannot have a transfer function.")
            else:
                lFuncs = layerFunctions[1:]
        
        self.tFuncs = lFuncs
        
        # Data from last Run
        self._layerInput = []
        self._layerOutput = []
        self._previousWeightDelta = []
        
        # Create the weight arrays
        for (l1,l2) in zip(layerSize[:-1], layerSize[1:]):
            self.weights.append(np.random.normal(scale=0.01, size = (l2, l1+1)))
            self._previousWeightDelta.append(np.zeros((l2, l1+1)))
    
    #
    # Run method
    #
    def Run(self, input):
        """Run the network based on the input data"""
        
        lnCases = input.shape[0]
        
        # Clear out the previous intermediate value lists
        self._layerInput = []
        self._layerOutput = []
        
        # Run it!
        for index in range(self.layerCount):
            # Determine layer input
            if index == 0:
                layerInput = self.weights[0].dot(np.vstack([input.T, np.ones([1, lnCases])]))
            else:
                layerInput = self.weights[index].dot(np.vstack([self._layerOutput[-1], np.ones([1, lnCases])]))
            
            self._layerInput.append(layerInput)
            self._layerOutput.append(self.tFuncs[index](layerInput))
        
        return self._layerOutput[-1].T
                 
    #
    # TrainEpoch method
    #
    def TrainEpoch(self, input, target, trainingRate = 0.2, momentum = 0.5):
        """This method trains the network for one epoch"""
        
        delta = []
        lnCases = input.shape[0]
        
        # First run the network
        self.Run(input)
        
        # Calculate our deltas
        for index in reversed(range(self.layerCount)):
            if index == self.layerCount - 1:
                # Compare to the target values
                output_delta = self._layerOutput[index] - target.T
                error = np.sum(output_delta**2)
                delta.append(output_delta * self.tFuncs[index](self._layerInput[index], True))
            else:
                # Compare to the following layer's delta
                delta_pullback = self.weights[index + 1].T.dot(delta[-1])
                delta.append(delta_pullback[:-1, :] * self.tFuncs[index](self._layerInput[index], True))
            
        # Compute weight deltas
        for index in range(self.layerCount):
            delta_index = self.layerCount - 1 - index
            
            if index == 0:
                layerOutput = np.vstack([input.T, np.ones([1, lnCases])])
            else:
                layerOutput = np.vstack([self._layerOutput[index - 1], np.ones([1, self._layerOutput[index - 1].shape[1]])])
            
            curWeightDelta = np.sum(\
                                 layerOutput[None,:,:].transpose(2, 0 ,1) * delta[delta_index][None,:,:].transpose(2, 1, 0)\
                                 , axis = 0)
            
            weightDelta = trainingRate * curWeightDelta + momentum * self._previousWeightDelta[index]
            
            self.weights[index] -= weightDelta
            
            self._previousWeightDelta[index] = weightDelta
        
        return error

#
# If run as a script, create a test object
#
if __name__ == "__main__":

    ###################Reading Files#######################################
    dimensionsInput = 0
    inputArr = []
    docIdArr = []

    dimensionsOutput = 0
    outputArr = []
    docIdArrNode2Vec = dict()


    with open("doc2vec.txt") as f:
        content = f.readlines()
        numberOfVectors = 0
        
        for i in range(len(content)):
            if i == 0:
                numberOfVectors = content[i].split(" ")[0]
                dimensionsInput = content[i].split(" ")[1] 
            else:
                input = []
                data = content[i].split(" ")
                docIdArr.append(data[0])

                for j in range(int(dimensionsInput)):
                    input.append(float(data[j+1]))
                inputArr.append(input)
                


    with open("node2vec.txt") as f:
        content = f.readlines()
        numberOfVectors = 0
        dimensions = 0
        outputArr = []
        
        for i in range(len(content)):
            if i == 0:
                numberOfVectors = content[i].split(" ")[0]
                dimensionsOutput = content[i].split(" ")[1] 
            else:
                output = []
                data = content[i].split(" ")

                for j in range(int(dimensionsOutput)):
                    output.append(float(data[j+1]))
                docIdArrNode2Vec[data[0]] = output
                
    for i in range(len(docIdArr)):
        outputArr.append(docIdArrNode2Vec[docIdArr[i]])

    ################End Reading Files##############################
    
    lvInput =  np.array(inputArr)
    lvTarget = np.array(outputArr)
    lFuncs = [None, sgm, sgm]
    
    bpn = BackPropagationNetwork((int(dimensionsInput),int(dimensionsInput),int(dimensionsOutput)), lFuncs)
    
    lnMax = 1000000
    lnErr = 1e-6
    for i in range(lnMax+1):
        err = bpn.TrainEpoch(lvInput, lvTarget, momentum = 0.9)
        if i % 5000 == 0 and i > 0:
            print("Iteration {0:6d}K - Error: {1:0.6f}".format(int(i/1000), err))
        if err <= lnErr:
            print("Desired error reached. Iter: {0}".format(i))
            break

    #save model to file
    model_file = open('model.pickle', 'w') 
    p.dump(bpn, model_file)

##    #open model file
##    model_file = open('model.pickle', 'r') 
##    bpn = p.load(model_file)
        
    # Display output
    lvTest =  np.array([[0.657,0.878,0.865]])
    lvOutput = bpn.Run(lvTest)
    print(lvOutput)
