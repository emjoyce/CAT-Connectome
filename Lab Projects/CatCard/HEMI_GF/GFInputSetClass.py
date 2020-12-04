'''
Emily Tenshaw
CAT-Card
12/1/2020

This is the hemibrain equivalent of the FAFB GF class set.
Still a work in progress as the hemibrain doesn't have annotaitons.
'''

import numpy as np
import GFInputNeuronClass as GFN


# Builds an object for a set of GF input neurons in the hemibrain
# min/max syn, subset builder?
class GFIN_set(object):

    def __init__(self, container=None):
        super().__init__()
        if container is None:
            self.container = []
        else:
            self.container = container

        self.bodyId = 2307027729
        self.AllGF1Synapses = self._GF1Synapses()
        self.numBodies = self._getNumBodies()
        self.minSyn = None
        self.maxSyn = None
        self.synapsesByBranch = {}
        self.numBranchInputs = {}

    def __len__(self):
        return len(self.container)

    # allows for indexing/slicing using either the index (nums lessthan 10,000) or the skid(nums greater than 10,000)
    def __getitem__(self, index):
        if isinstance(index, int):
            if index < 10000:
                return self.container[index]
            else:
                for i in self:
                    if i.bodyId == index:
                        return i
        # returns subset of type GFIN_set
        elif isinstance(index, slice):
            x = GFIN_set(self.container[index])
            return x
        else:
            raise TypeError

    def __setitem__(self, index, value):
        if index <= len(self.container):
            self.container[index] = value
        else:
            raise IndexError()

    def __getslice__(self, i, j):
        return self.container[max(0, i):max(0, j):]

    def __contains__(self, value):
        return value in self.container

    def __repr__(self):
        return str(self.container)

    def __add__(self, otherList):
        myList = []
        for i in self.container:
            myList.append(i)
        if isinstance(otherList, GFN.GFinputNeuron):
            myList.append(otherList)
            added = subSetBuilder(myList)
            for i in vars(self).keys():
                if i is not 'numBodies' and i is not 'container':
                    setattr(added, i, getattr(self, i))
            return added
        else:
            for i in otherList.container:
                myList.append(i)
            added = subSetBuilder(myList)
            for i in vars(self).keys():
                if i is not 'numBodies' and i is not 'container':
                    setattr(added, i, getattr(self, i))
            '''if self.groupName != None:
                if otherList.groupName != None:
                    added.groupName = str(self.groupName) + str(otherList.groupName)
                    return added
                else:
                    added.groupName = str(self.groupName)
                    return added
            elif otherList.groupName != None:
                added.groupName = str(otherList.groupName)
                return added'''
        return added

    # input should be skeletonID of neuron of interest, function returns the index that can be called on neuron set to get info about that
    # neuron
    def index(self, bodyId):
        count = 0
        for i in self:
            if i.bodyId == bodyId:
                return count
            elif not isinstance(bodyId, int):
                print("Index only for integers")
                break
            else:
                count += 1

    def __str__(self):
        this = ""
        for item in self:
            this += str(item)
            this += "\n"
        return this

    def _GF1Synapses(self):
        curSyn = 0
        for item in self:
            # print(item.bodyId)
            # print(item.GF1synapseCount)
            curSyn = curSyn + item.GF1synapseCount
        return curSyn

    def _getNumBodies(self):
        numBodies = len(self)
        return numBodies

    def minMax(self):
        myOrderedList = sortBySynH2L(self)
        self.minSyn = myOrderedList[-1].GF1synapseCount
        self.maxSyn = myOrderedList[0].GF1synapseCount
        return self

    def getSynapsesByBranch(self):
        if len(self.synapsesByBranch) == 0:
            medial = 0
            lateral = 0
            descending = 0
            soma = 0
            anterior = 0
            for i in self:
                if i.synapsesByBranch != {}:
                    medial = medial + i.synapsesByBranch['medial']
                    lateral = lateral + i.synapsesByBranch['lateral']
                    soma = soma + i.synapsesByBranch['soma']
                    descending = descending + i.synapsesByBranch['descending']
                    anterior = anterior + i.synapsesByBranch['anterior']
                else:
                    i.getSynapsesByBranch()
                    medial = medial + i.synapsesByBranch['medial']
                    lateral = lateral + i.synapsesByBranch['lateral']
                    soma = soma + i.synapsesByBranch['soma']
                    descending = descending + i.synapsesByBranch['descending']
                    anterior = anterior + i.synapsesByBranch['anterior']
            self.synapsesByBranch['medial'] = medial
            self.synapsesByBranch['lateral'] = lateral
            self.synapsesByBranch['descending'] = descending
            self.synapsesByBranch['anterior'] = anterior
            self.synapsesByBranch['soma'] = soma

        return


# builds from an input list of neurons
def builder(list):
    GFInputSet = GFIN_set(np.array(list))
    return GFInputSet


# unsure if works
def subSetBuilder(fullSet):
    mySubSet = GFIN_set(np.array(fullSet))
    if isinstance(fullSet, GFIN_set):
        if mySubSet.numSynapsesByBranch is not None:
            mySubSet.numSynapsesByBranch = {}
            branches = ['soma tract', 'medial', 'anterior', 'lateral', 'descending tract']
            for x in branches:
                if x not in mySubSet.numSynapsesByBranch:
                    mySubSet.numSynapsesByBranch[x] = 0
                for i in mySubSet:
                    mySubSet.numSynapsesByBranch[x] += i.synapsesByBranch[x]
        return mySubSet
    else:
        return mySubSet


# sorts neurons from low to high synapse counts
def sortBySynH2L(mySet):
    H2L = sorted(mySet, key=GFN.GFinputNeuron.getGF1synapseCount, reverse=True)
    mySortedList = subSetBuilder(H2L)
    return mySortedList
