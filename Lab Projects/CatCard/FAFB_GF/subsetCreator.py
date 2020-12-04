'''
Emily Tenshaw
CAT-Card
12/1/2020

This file shows examples of creating a sub set and groups for GF input sets.
All of the examples were used previously by Card Lab for various reason.
New functions like these can be made for specific purposes.
Sorting functions are included because they technically create a subset.
'''
import numpy as np
import config
from requests.auth import AuthBase
import CustomNeuronClassSet as CS
import MyCustomGFNeuronClass as CN

# create token from config file
token = config.token
project_id = config.project_id

# authorizes catmaid
class CatmaidApiTokenAuth(AuthBase):
    """Attaches HTTP X-Authorization Token headers to the given Request."""

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['X-Authorization'] = 'Token {}'.format(self.token)
        return r

# sorts neurons from low to high synapse counts
def sortBySynL2H(mySet):
    L2H = sorted(mySet, key=CN.GFinputNeuron.getGF1synapse)
    mySortedList = subSetBuilder(L2H)
    if mySet.groupName != None:
        mySortedList.groupName = mySet.groupName
    return mySortedList


# sorts neurons from low to high synapse counts
def sortBySynH2L(mySet):
    H2L = sorted(mySet, key=CN.GFinputNeuron.getGF1synapse, reverse=True)
    mySortedList = subSetBuilder(H2L)
    if mySet.groupName != None:
        mySortedList.groupName = mySet.groupName
    return mySortedList


# returns a subset based upon annotation: mySet = GFIN_set instance, annotation = string annotation, annotation can also be a list of annotation strings
def createGroupByAnnotation(mySet, annotation):
    myNewSet = []
    if isinstance(annotation, str):
        for item in mySet:
            for i in item.annotations:
                if i == annotation:
                    myNewSet.append(item)
                    continue
    elif isinstance(annotation, list):
        for item in mySet:
            for i in item.annotations:
                if i in annotation:
                    if item not in myNewSet:
                        myNewSet.append(item)
                        # continue
    a = subSetBuilder(myNewSet)
    if type(annotation) == list:
        tempName = ', '.join(annotation)
        annotation = tempName
    if mySet.groupName is None:
        a.groupName = annotation
    elif mySet.groupName == "None":
        a.groupName = annotation

    else:
        a.groupName = mySet.groupName + "_" + annotation
    print("There are {} neurons with annotation {}: \n".format(len(a), a.groupName))
    return a


# returns a subset based upon classification: mySet = GFIN_set instance, classification = string classification
def createGroupByClassification(mySet, classification):
    myNewSet = []
    for item in mySet:
        if item.classification == classification:
            myNewSet.append(item)
    a = subSetBuilder(myNewSet)
    # print(a.numNeurons)

    if mySet.groupName is None or mySet.groupName is 'GF1 Input Neurons':
        a.groupName = classification
    elif mySet.groupName == "None" or mySet.groupName == 'GF1 Input Neurons':
        a.groupName = classification

    else:
        a.groupName = mySet.groupName + "_" + classification
    # print(a.groupName, ":", len(a), "/n")

    # print("There are {} neurons with classification {}: \n".format(len(a), a.groupName))
    return a


# returns a subset based upon annotation that neurons do NOT have: mySet = GFIN_set instance, annotation = string annotation
def createGroupByNotAnnotation(mySet, annotation):
    myNewSet = mySet
    for item in mySet:
        if annotation in item.annotations:
            myNewSet -= item
            continue
    a = subSetBuilder(myNewSet)
    if myNewSet.groupName is not None:
        myNewSet.groupName += 'not' + str(annotation)
    else:
        myNewSet.groupName = 'not' + str(annotation)

    print("There are {} neurons left without annotation {}: \n".format(len(myNewSet), annotation))
    return a


# returns a subset based upon synCount: mySet = GFIN_set instance, synNumber = Number of Synapses(or less) that you want results to have
def subBySynLT(mySet, synNumber):
    myNewSet = []
    for item in mySet:
        if item.GF1synapseCount <= synNumber:
            myNewSet.append(item)
            continue
    x = subSetBuilder(myNewSet)
    if mySet.groupName != None:
        x.groupName = str(mySet.groupName) + "with" + str(synNumber) + "synapses"
    print("{} of these neurons have {} or less synapses \n".format(len(myNewSet), synNumber))
    return x


# returns a subset based upon synCount: mySet = GFIN_set instance, synNumber = Number of Synapses(or greater) that you want results to have
def subBySynGT(mySet, synNumber):
    myNewSet = []
    for item in mySet:
        if item.GF1synapseCount >= synNumber:
            myNewSet.append(item)
            continue
    x = subSetBuilder(myNewSet)
    if mySet.groupName != None:
        x.groupName = str(mySet.groupName) + "with" + str(synNumber) + "synapses"
    print("{} of these neurons have {} or more synapses \n".format(len(myNewSet), synNumber))
    return x


def subSetBuilder(fullSet):
    mySubSet = CS.GFIN_set(np.array(fullSet))
    if isinstance(fullSet, CS.GFIN_set):
        if fullSet.groupName != None:
            mySubSet.groupName = fullSet.groupName
        if mySubSet.allSynapseCoordinates is not None:
            mySubSet.combineAllSynLocations()
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

# use to fix add
def subSetBuilderNew(fullSet):
    mySubSet = CS.GFIN_set(np.array(fullSet))
    for i in fullSet:
        for item in i:
            setattr(mySubSet[i.skeletonID], item, (getattr(i, item)))
    return mySubSet
