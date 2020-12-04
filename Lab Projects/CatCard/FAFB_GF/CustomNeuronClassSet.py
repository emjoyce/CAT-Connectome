'''
Emily Tenshaw & Jason Polsky
CAT-Card
Updated 11/30/2020

This file allows user to create an input set of giant fiber input neurons.
Each input neuron is presynaptic to the GF at least once.
The GF input set has characteristics and attributes that are added intially
and many that can be added later on.
New attributes can be added.
'''

import MyCustomGFNeuronClass
import numpy as np
import statistics as stat
import getSkeletonNodesNew as SN
import config
import exportToCSV as E2C
import csv
import requests
import json
from requests.auth import AuthBase

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


'''
GFIN_Set = Giant Fiber Input Set
'''


# creates a GFIN_set object
class GFIN_set(object):

    def __init__(self, container=None):
        super().__init__()
        if container is None:
            self.container = []
        else:
            self.container = container

        self.skeletonID = 4947529
        self.AllGF1Synapses = self._GF1Synapses()
        self.AllGF2Synapses = self._GF2Synapses()
        self.numNeurons = self._getNumNeurons()
        self.groupName = None
        self.medianSyn = None
        self.minSyn = None
        self.maxSyn = None
        self.connectorInfo = None  # should be a dictionary with the branches as keys and connectorIDs as values
        self.numSynapsesByBranch = None
        self.allSynapseCoordinates = None  # will be filled with the coordinate points in format: {conID:x,y,z}
        self.allAnnotations = self._setAllAnnotations()
        self.varCheck = []
        self.allConnectorInfo = None
        self.branchCoordinates = None
        self.neuroDistroAdvanced = []
        self.modality = None
        self.BiUni = None
        self.IpsiContraMid = None
        self.groupNumber = None
        self.morphology = None

    def __len__(self):
        return len(self.container)

    # allows for indexing/slicing using either the index (nums lessthan 10,000) or the skid(nums greater than 10,000)
    def __getitem__(self, index):
        if isinstance(index, int):
            if index < 10000:
                return self.container[index]
            else:
                for i in self:
                    if i.skeletonID == index:
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
        if isinstance(otherList, MyCustomGFNeuronClass.GFinputNeuron):
            myList.append(otherList)
            added = subSetBuilder(myList)
            for i in vars(self).keys():
                if i is not 'numNeurons' and i is not 'container':
                    setattr(added, i, getattr(self, i))
            return added
        else:
            for i in otherList.container:
                myList.append(i)
            added = subSetBuilder(myList)
            for i in vars(self).keys():
                if i is not 'numNeurons' and i is not 'container' and 'percent' not in i:
                    setattr(added, i, getattr(self, i))
            if self.groupName != None:
                if otherList.groupName != None:
                    added.groupName = str(self.groupName) + str(otherList.groupName)
                    return added
                else:
                    added.groupName = str(self.groupName)
                    return added
            elif otherList.groupName != None:
                added.groupName = str(otherList.groupName)
                return added

        return added

    def __sub__(self, otherList):
        myList = []
        for i in self.container:
            myList.append(i)
        if isinstance(otherList, MyCustomGFNeuronClass.GFinputNeuron):
            myList.remove(otherList)
        else:
            for i in otherList.container:
                myList.remove(i)
        subtracted = subSetBuilder(myList)
        return subtracted

    # input should be skeletonID of neuron of interest, function returns the index that can be called on neuron set to get info about that
    def index(self, skeletonID):
        count = 0
        for i in self:
            if i.skeletonID == skeletonID:
                return count
            elif not isinstance(skeletonID, int):
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

    '''
        General info about set
    '''

    # Used in creating a set or info for set
    # Sets total GF1 Synapse Count
    def _GF1Synapses(self):
        curSyn = 0
        for item in self:
            curSyn += item.GF1synapseCount
        return curSyn

    # Sets total GF2 Synapse Count
    def _GF2Synapses(self):
        curSyn = 0
        for item in self:
            curSyn += item.GF2synapseCount
        return curSyn

    # returns the number of neurons in the current group
    def _getNumNeurons(self):
        numNeurons = len(self)
        return numNeurons

    # median syn count
    def _medSyn(self):
        myMedLst = []
        myMed = 0
        for i in self:
            myMedLst.append(i.GF1synapseCount)
        myMed = stat.median(myMedLst)
        self.medianSyn = myMed
        return myMed

    def _setAllAnnotations(self):
        annotationList = []
        for neuron in self:
            for annotation in neuron.annotations:
                if annotation not in annotationList and 'type' not in annotation:
                    annotationList.append(annotation)
        return annotationList

    # gets min and max syn count
    def minMax(self):
        myOrderedList = SC.sortBySynH2L(self)
        self.minSyn = myOrderedList[-1].GF1synapseCount
        self.maxSyn = myOrderedList[0].GF1synapseCount
        return self

    '''
        Pulls data from FAFB
    '''

    # provides all neurons in the set with a list of x,y,z coordinates for their respective soma attributes. not part of builder because it can be computationally heavy (i.e. many server requests so slow)
    def updateSomata(self):
        for i in self:
            if i.soma is None:
                i.soma = i.getSomaNode()
            else:
                continue
        self.varCheck.append('soma')
        return self

    # gets connector links for each GF branch
    def getConnectors(self):
        myBranches = ['lateral', 'medial', 'anterior', 'soma tract', 'descending tract']
        myConnectors = {}
        myConCount = {}
        connectorInfo = SN.getAllConnectorInfo()
        while len(myBranches) is not 0:
            branch = myBranches.pop()
            myConnectors[branch] = SN.getConnectorsByBranch(branch=branch, connectorInfo=connectorInfo)
            myConCount[branch] = len(myConnectors[branch])
        self.connectorInfo = myConnectors
        self.numSynapsesByBranch = myConCount
        self.varCheck.append('connectors')
        return self

    # gets the information for connectors (pulls from FAFB server)
    def getConnectorInfo(self, polarity='postsynaptic'):
        self.allConnectorInfo = getAllConnectorInfo(skeletonID=self.skeletonID, polarity=polarity)
        return self.allConnectorInfo

    # gets xyz coordinates of branches
    def getBranchCoordinates(self):
        self.branchCoordinates = SN.findBranchCoordinates(self)
        return self.branchCoordinates


    # gets skeleton nodes of all inputs
    def getAllSkeletonNodes(self):
        for i in self:
            i.getSkeletonNodes()
        self.varCheck.append('skeletonNodes')
        return self

    '''
        Add data via annotations
    '''
    # get input synapse count for each branch
    def getAllGFINSynByBranch(self):
        if self.connectorInfo is None:
            self.getConnectors()
        branches = ['soma tract', 'medial', 'anterior', 'lateral', 'descending tract']
        GFsynapses = self.connectorInfo
        tempCount = 0
        for i in self:
            i.getConnectorIDs()
            for item in branches:
                for x in i.connectorIDs:
                    if x in GFsynapses[item]:
                        tempCount += 1
                        i.synLocation[x] = i.connectorIDs[x]
                i.synapsesByBranch[item] = tempCount
                tempCount = 0

        self.varCheck.append('synByBranch')
        return self

    # find neuropils that each input neuron innervates
    def findNeuropils(self):
        myNeuropils = ['AL_L', 'AL_R', 'AME_L', 'AME_R', 'AMMC_L', 'AMMC_R', 'AOTU_L', 'AOTU_R', 'ATL_L', 'ATL_R',
                       'AVLP_L', 'AVLP_R', 'BU_L', 'BU_R', 'CAN_L', 'CAN_R', 'CRE_L', 'CRE_R', 'EB', 'EPA_L', 'EPA_R',
                       'FB', 'FLA_L',
                       'FLA_R', 'GA_L', 'GA_R', 'GNG', 'GOR_L', 'GOR_R', 'IB_L', 'IB_R', 'ICL_L', 'ICL_R', 'IPS_L',
                       'IPS_R',
                       'LAL_L', 'LAL_R', 'LH_L', 'LH_R', 'LO_L', 'LO_R', 'LOP_L', 'LOP_R', 'MB_CA_L', 'MB_CA_R',
                       'MB_LAC_L', 'MB_LAC_R', 'MB_ML_L', 'MB_ML_R', 'MB_PED_L', 'MB_PED_R', 'MB_VL_L', 'MB_VL_R',
                       'MB_whole_L',
                       'MB_whole_R', 'ME_L', 'ME_R', 'NO', 'PB', 'PLP_L', 'PLP_R', 'PRW', 'PVLP_L', 'PVLP_R', 'SAD',
                       'SCL_L', 'SCL_R', 'SIP_L', 'SIP_R', 'SLP_L', 'SLP_R', 'SMP_L', 'SMP_R', 'SPS_L', 'SPS_R',
                       'VES_L', 'VES_R', 'WED_L', 'WED_R']
        for i in self:
            for abc in myNeuropils:
                if abc in i.annotations:
                    i.neuropils.update({abc: 1})
                else:
                    i.neuropils.update({abc: 0})
        return self

    # find
    def findNeuropilsByDistribution(self):
        neuropils = {'AL_L': 0, 'AL_R': 0, 'AME_L': 0, 'AME_R': 0, 'AMMC_L': 0, 'AMMC_R': 0, 'AOTU_L': 0, 'AOTU_R': 0,
                     'ATL_L': 0, 'ATL_R': 0,
                     'AVLP_L': 0, 'AVLP_R': 0, 'BU_L': 0, 'BU_R': 0, 'CAN_L': 0, 'CAN_R': 0, 'CRE_L': 0, 'CRE_R': 0,
                     'EB': 0, 'EPA_L': 0, 'EPA_R': 0,
                     'FB': 0, 'FLA_L': 0,
                     'FLA_R': 0, 'GA_L': 0, 'GA_R': 0, 'GNG': 0, 'GOR_L': 0, 'GOR_R': 0, 'IB_L': 0, 'IB_R': 0,
                     'ICL_L': 0,
                     'ICL_R': 0, 'IPS_L': 0,
                     'IPS_R': 0,
                     'LAL_L': 0, 'LAL_R': 0, 'LH_L': 0, 'LH_R': 0, 'LO_L': 0, 'LO_R': 0, 'LOP_L': 0, 'LOP_R': 0,
                     'MB_CA_L': 0, 'MB_CA_R': 0,
                     'MB_LAC_L': 0, 'MB_LAC_R': 0, 'MB_ML_L': 0, 'MB_ML_R': 0, 'MB_PED_L': 0, 'MB_PED_R': 0,
                     'MB_VL_L': 0,
                     'MB_VL_R': 0,
                     'MB_whole_L': 0,
                     'MB_whole_R': 0, 'ME_L': 0, 'ME_R': 0, 'NO': 0, 'PB': 0, 'PLP_L': 0, 'PLP_R': 0, 'PRW': 0,
                     'PVLP_L': 0,
                     'PVLP_R': 0, 'SAD': 0,
                     'SCL_L': 0, 'SCL_R': 0, 'SIP_L': 0, 'SIP_R': 0, 'SLP_L': 0, 'SLP_R': 0, 'SMP_L': 0, 'SMP_R': 0,
                     'SPS_L': 0, 'SPS_R': 0,
                     'VES_L': 0, 'VES_R': 0, 'WED_L': 0, 'WED_R': 0}

        myNeuropils = ['AL_L', 'AL_R', 'AME_L', 'AME_R', 'AMMC_L', 'AMMC_R', 'AOTU_L', 'AOTU_R', 'ATL_L', 'ATL_R',
                       'AVLP_L', 'AVLP_R', 'BU_L', 'BU_R', 'CAN_L', 'CAN_R', 'CRE_L', 'CRE_R', 'EB', 'EPA_L', 'EPA_R',
                       'FB', 'FLA_L',
                       'FLA_R', 'GA_L', 'GA_R', 'GNG', 'GOR_L', 'GOR_R', 'IB_L', 'IB_R', 'ICL_L', 'ICL_R', 'IPS_L',
                       'IPS_R',
                       'LAL_L', 'LAL_R', 'LH_L', 'LH_R', 'LO_L', 'LO_R', 'LOP_L', 'LOP_R', 'MB_CA_L', 'MB_CA_R',
                       'MB_LAC_L', 'MB_LAC_R', 'MB_ML_L', 'MB_ML_R', 'MB_PED_L', 'MB_PED_R', 'MB_VL_L', 'MB_VL_R',
                       'MB_whole_L',
                       'MB_whole_R', 'ME_L', 'ME_R', 'NO', 'PB', 'PLP_L', 'PLP_R', 'PRW', 'PVLP_L', 'PVLP_R', 'SAD',
                       'SCL_L', 'SCL_R', 'SIP_L', 'SIP_R', 'SLP_L', 'SLP_R', 'SMP_L', 'SMP_R', 'SPS_L', 'SPS_R',
                       'VES_L', 'VES_R', 'WED_L', 'WED_R']
        distributions = {'Anterior': neuropils, 'Medial': neuropils, 'Lateral': neuropils, 'Descending': neuropils,
                         'Soma': neuropils, 'AnteriorMedial': neuropils, 'AnteriorLateral': neuropils,
                         'AnteriorSoma': neuropils, 'AnteriorDescending': neuropils, 'MedialLateral': neuropils,
                         'MedialSoma': neuropils, 'MedialDescending': neuropils,
                         'LateralSoma': neuropils, 'LateralDescending': neuropils, 'SomaDescending': neuropils,
                         'AnteriorMedialLateral': neuropils, 'AnteriorMedialSoma': neuropils,
                         'AnteriorMedialDescending': neuropils,
                         'AnteriorLateralSoma': neuropils, 'AnteriorLateralDescending': neuropils,
                         'AnteriorSomaDescending': neuropils,
                         'MedialLateralSoma': neuropils, 'MedialLateralDescending': neuropils,
                         'MedialSomaDescending': neuropils,
                         'LateralSomaDescending': neuropils,
                         'AnteriorMedialLateralSoma': neuropils, 'AnteriorMedialLateralDescending': neuropils,
                         'AnteriorMedialSomaDescending': neuropils,
                         'AnteriorLateralSomaDescending': neuropils, 'MedialLateralSomaDescending': neuropils,
                         'AllBranches': neuropils}

        for key in distributions.keys():
            distributions[key] = distributions['Anterior'].copy()

        for neuron in self:
            for abc in neuron.annotations:
                if abc in myNeuropils:
                    distributions[neuron.distribution][abc] += 1

        self.neuroDistroAdvanced = distributions
        return

    # find branch distributions for input neurons
    # finds which branches each neuron synapses on - ex: medial, or anterior & medial
    def findBranchDistributions(self):

        for neuron in self:
            neuron.synapsesByBranch['medial']
            neuron.synapsesByBranch['lateral']
            neuron.synapsesByBranch['descending tract']
            neuron.synapsesByBranch['soma tract']
            neuron.synapsesByBranch['anterior']

        for neuron in self:
            if neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'Medial'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'Anterior'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'Descending'
            if neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'Lateral'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'Soma'

            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'AnteriorMedial'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'AnteriorLateral'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'AnteriorSoma'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'AnteriorDescending'

            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'MedialLateral'
            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'MedialSoma'
            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'MedialDescending'

            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'LateralSoma'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'LateralDescending'

            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'SomaDescending'

            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'AnteriorMedialLateral'
            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'AnteriorMedialSoma'
            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'AnteriorMedialDescending'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'AnteriorLateralSoma'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'AnteriorLateralDescending'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'AnteriorSomaDescending'

            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'MedialLateralSoma'
            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'MedialLateralDescending'
            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'MedialSomaDescending'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'LateralSomaDescending'

            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'AnteriorMedialLateralSoma'
            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'AnteriorMedialLateralDescending'
            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'AnteriorMedialSomaDescending'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'AnteriorLateralSomaDescending'
            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'MedialLateralSomaDescending'

            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'AllBranches'

        return

    # assigns modality of each input neuron based off annotations
    def findModality(self):
        for i in self:
            if "Descending Neuron" in i.annotations:
                i.modality = "Descending Neuron"

            elif "Ascending Neuron" in i.annotations:
                i.modality = "Ascending Neuron"

            elif "Visual" in i.annotations:
                i.modality = "VPN"

            elif "JONeuron" in i.annotations:
                i.modality = "JONeuron"

            elif "Other Visual" in i.annotations:
                i.modality = "Other Visual"

            elif "Non-Visual_Interneuron" in i.annotations:
                i.modality = "Non-Visual Interneuron"

            elif "Visual_Interneuron" in i.annotations:
                i.modality = "Visual Interneuron"

            elif "Mechanosensory Interneuron" in i.annotations:
                i.modality = "Mechanosensory Interneuron"

            elif "Neuron Fragment" in i.annotations:
                i.modality = "Unknown"
            else:
                i.modality = "Unknown"
        return

    # assigns morphology of each input neuron
    # bi/unilateral, ipsi/contralateral, projection/local
    def findMorphology(self):
        for neuron in self:
            if "Unclassified GF input neuron - Fragment" in neuron.annotations:
                neuron.morphology = "Fragment"
            elif "Bilateral" in neuron.annotations:
                if "Ipsilateral" in neuron.annotations:
                    if "projection neuron" in neuron.annotations:
                        neuron.morphology = "BiIpsiProject"
                    elif "local neuron" in neuron.annotations:
                        neuron.morphology = "BiIpsiLocal"
                elif "contralateral" in neuron.annotations:
                    if "projection neuron" in neuron.annotations:
                        neuron.morphology = "BiContraProject"
                elif "midLine" in neuron.annotations:
                    if "projection neuron" in neuron.annotations:
                        neuron.morphology = "BiMidProject"
                    elif "local neuron" in neuron.annotations:
                        neuron.morphology = "BiMidLocal"
                else:
                    if "projection neuron" in neuron.annotations:
                        neuron.morphology = "BiProject"
                    elif "local neuron" in neuron.annotations:
                        neuron.morphology = "BiLocal"
            elif "Unilateral" in neuron.annotations:
                if "projection neuron" in neuron.annotations:
                    neuron.morphology = "UniProject"
                elif "local neuron" in neuron.annotations:
                    neuron.morphology = "UniLocal"
        return

    # assigns bilateral or unilateral to the input neuron
    def findBiUni(self):
        for i in self:
            if "Bilateral" in i.annotations:
                i.BiUni = "Bilateral"
            elif "Unclassified GF input neuron - Fragment" in i.annotations:
                i.BiUni = "Fragment"
            else:
                i.BiUni = "Unilateral"
        return

    # assigns the soma hemisphere in reference to the GF soma as ipsi/contralateral
    def findIpsiContraMid(self):
        for i in self:
            if "Ipsilateral" in i.annotations:
                i.IpsiContraMid = "Ipsilateral"
            elif "contralateral" in i.annotations:
                i.IpsiContraMid = "Contralateral"
            elif "midLine" in i.annotations:
                i.IpsiContraMid = "MidLine"
            else:
                i.IpsiContraMid = "No Soma"
        return

    '''
        Helper or misc. functions
    '''

    # helper used in creating subsets
    def combineAllSynLocations(self):
        mySet = self
        AllSyn = {}
        count = 0
        if bool(mySet[0].synLocation) == False:
            self.getAllGFINSynByBranch()
        for i in mySet:
            for z in i.synLocation:
                x = z
                while x in AllSyn:
                    x = str(z)
                    x += str(count)
                    x = int(x)
                    count += 1
                AllSyn[x] = i.synLocation[z]
        self.allSynapseCoordinates = AllSyn
        self.varCheck.append('synLocation')
        return self

    # adds data before exporting to a csv file
    def e2c(self):
        if 'soma' not in self.varCheck:
            self.updateSomata()
        if 'partners' not in self.varCheck:
            self.getNumPartnersBySkid()
        if 'synByBranch' not in self.varCheck:
            self.getAllGFINSynByBranch()
        E2C.makeCSV(self, 'saveWithSomaAndBranches')
        return

    # creates a summary of all data
    def createSummary(self):
        mySet = self
        myClassList = []
        # for i in mySet:
        while len(mySet) > 0:
            # if i.classification not in myClassList[i.classification]:
            # myClassList[i.classification] = 1
            tempGroup = createGroupByClassification(mySet, mySet[0].classification)
            tempGroup.minMax()
            tempGroup._medSyn()
            tempGroup._avgSyn()
            myClassList.append(tempGroup)
            myNewSet = []
            for item in mySet:
                if item.classification != mySet[0].classification:
                    myNewSet.append(item)
            a = subSetBuilder(myNewSet)
            mySet = a

            # for item in tempGroup:
            #   mySet -= item
            # print(len(mySet))
            # else:
            #   myClassList[i.i.classification] += 1
        # for item in myClassList:
        #     #print(item.numNeurons, type(item.numNeurons))
        #     if item.numNeurons == 0:
        #         myClassList.remove(item)
        #         #print('yes')
        #     else:
        #         print(item, ': no')
        #     if item.numNeurons is None:
        #         myClassList.remove(item)
        return myClassList

    # add new annotation to all input neurons
    def addAnnotation(self, newAnnotation, addToSkeletons=True, metaAnnotations=None):
        """

        :param newAnnotation: array of string - to be added to catmaid annotation of neurons (if looking for bulk annotations: set from GFIN objects
        :param addToSkeletons: default is true - if false, will create annotation and annotate it with a meta_annotation
        :param metaAnnotations: default is none - should be array[string] if desired
        :return: print out:  success or error (with error message), annotations added (name and id), neuron ids, and list of any new annotations
        """
        if addToSkeletons is True:
            mySkids = []
            for item in self:
                mySkids.append(item.skeletonID)

            response = requests.post(
                'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/add'.format(project_id),
                auth=config.CatmaidApiTokenAuth(token),
                data={'skeleton_ids': mySkids, 'annotations': newAnnotation}
            )
        else:
            response = requests.post(
                'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/add'.format(project_id),
                auth=config.CatmaidApiTokenAuth(token),
                data={'annotations': newAnnotation, 'meta_annotations': metaAnnotations}
            )

        myResults = json.loads(response.content)
        print(myResults)
        return

    # moves data into a pandas dataframe instead of a set
    def makeDataFrame(self):

        myWriter = csv.writer()
        myRows0 = ['Neuron Name', 'skeletonID', 'GF1 Synapse Count', 'GF2 Synapse Count',
                   'classification', 'hemisphere', 'cellBodyRind', 'somaHemisphere', 'commissure', 'numLC4Syn',
                   'numLPLC2Syn', 'numLC6Syn', 'numLPLC1Syn', 'numLPC1Syn', 'numLC28Syn', 'numLLPC1Syn',
                   'numLPLC3Syn', 'lateral branch', 'medial branch', 'anterior branch', 'soma tract',
                   'descending tract']
        myRows = myRows0 + self.allAnnotations
        myWriter.writerow(myRows)
        for item in self:
            theseAnnotations = []
            for annotation in self.allAnnotations:
                if annotation in item.annotations:
                    theseAnnotations.append(1)
                else:
                    theseAnnotations.append(0)
            curRow = [item.neuronName, item.skeletonID, item.GF1synapseCount, item.GF2synapseCount,
                      item.classification, item.hemisphere, item.cellBodyRind,
                      item.somaSide, item.commissure, item.postsynapticToLC4, item.postsynapticToLPLC2,
                      item.postsynapticToLC6, item.postsynapticToLPLC1, item.postsynapticToLPC1,
                      item.postsynapticToLC28, item.postsynapticToLLPC1, item.postsynapticToLPLC3,
                      item.synapsesByBranch['lateral'], item.synapsesByBranch['medial'],
                      item.synapsesByBranch['anterior'], item.synapsesByBranch['soma tract'],
                      item.synapsesByBranch['descending tract']]
            fullRow = curRow + theseAnnotations
        myWriter.writerow(fullRow)

        return myWriter


'''
Build a set 
Builder defaults to GF but can be used as a base for other neurons
Takes all inputs and pulls their attributes/data then puts them into a set
'''


# call this to build a GFIN_set from all GF1 input neurons
def builder():
    mySet = GFIN_set(np.array(MyCustomGFNeuronClass.builder()))
    mySet._medSyn()
    mySet.minMax()
    return mySet


#builds a GF input set from a speific list of inputs
def buildFromSkidList(myList):
    mySet = GFIN_set(np.array(MyCustomGFNeuronClass.buildFromSkidList(myList)))
    return mySet
