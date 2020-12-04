'''
Oct 15, 2018
Emily Tenshaw
New Class to make a set for any neuron. Use the builder function and the SKID of the neuron of intereset.
This will create a set like the GF input set for ANY neuron - helpful for DNs, etc.
'''

import GetAnnotationsRemoveExtraneousInfo as GARI
import getSkeletonNodesNew as SN
import GetLookUpTable as GLT
import requests
import json
import config

token = config.token
auth = config.CatmaidApiTokenAuth(token)
project_id = config.project_id

class neuronSet(object):

    def __init__(self, skeletonID, container=None):
        super().__init__()
        if container is None:
            self.container = []
        else:
            self.container = container

        self.skeletonID = skeletonID
        self.synapseCount = int()
        self.annotations = []
        self.neuronName = ''
        self.soma = None
        self.skeletonNodes = None
        self.connectorIDs = None

    def __repr__(self):
        return '{}'.format(self.neuronName)

    def __iter__(self):
        for attr in dir(self):
            if not attr.startswith("__") and 'percent' not in attr:
                yield attr

    def __len__(self):
        return len(self.container)

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.container[index]
        elif isinstance(index,
                        slice):  # bug: if subSet is defined multiple times, percent total shifts to percent of previous group

            # returns subset of type GFIN_set
            x = neuronSet(self.container[index])
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

    def __repr__(self):
        return '{}'.format(self.neuronName)

    def __str__(self):
        return "{}: skeleton ID = {}, synapse count = {}, annotations = {} \n".format(self.neuronName,
                                                                                      self.skeletonID,
                                                                                      self.synapseCount,
                                                                                      self.annotations)
    def getSkID(self):
        return self.skeletonID

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

    def getSynapseCount(self):
        mySynCount = 0
        for i in self:
           # print("item", item)
            mySynCount += self[i].synapseCount
            return mySynCount

    def getAnnotations(self):
        myAnnotations = GARI.getMyAnnotations()
        y = self.skeletonID
        z = str(y)
        if z in myAnnotations:
            self.annotations = myAnnotations[z]
        return self.annotations

    def getNeuronName(self):
        y = self.skeletonID
        z = str(y)
        myNames = GLT.getLookUpTableSkID_Name()
        if y in myNames:
            self.neuronName = myNames[y]
        return self.neuronName

    def getSomaNode(self):
        self.soma = SN.getSoma(self)
        return self.soma

    def getSkeletonNodes(self):
        self.skeletonNodes = SN.getAllNodes(self)
        return self.skeletonNodes

    # returns a dict with keys as connectorIDs and values as x,y,z coordinate points
    def getConnectorIDs(self):
        self.connectorIDs = SN.getAllConnectors(skeletonID=self.skeletonID, polarity='presynaptic')
        return self.connectorIDs

    # gets the total number of nodes that make up a given skeleton
    def getNumNodes(self):
        if self.numNodes is None:
            self.getSkeletonNodes()
        numNodes = len(self.nodes)
        return numNodes

    def getAllConnectorInfo(skeletonID=None, polarity=None):
        if skeletonID is None:
            mySkid = 4947529
        else:
            mySkid = skeletonID
        if polarity is None:
            relation_type = 'postsynaptic'
        else:
            relation_type = polarity

        # gets connector ID for all nodes in given skeleton (output: {links:[[skleton ID, Connector ID, X, Y, Z, Confidence, User ID, TNID, Date Created, Date Modified]], tags:[...]
        response = requests.get(
            'https://neuropil.janelia.org/tracing/fafb/v14/{}/connectors/links/?skeleton_ids[0]={}&relation_type={}_to&with_tags=true'.format(
                project_id, mySkid, relation_type)  # ,
            # auth = auth,
            # data = {'skeleton_ids' : mySkid, 'relation_type' : 'postsynaptic_to'}
        )
        connectorInfo = json.loads(response.content)
        # print(connectorInfo)
        return connectorInfo

    def getSkidSomaDict(self):
        skeletonID = self.skeletonID
        response = requests.get(
            'https://neuropil.janelia.org/tracing/fafb/v14/1/skeletons/{}/node-overview'.format(skeletonID),
        )
        myDict = json.loads(response.content)
        somaAndCoordinates = {}
        for i in myDict[2]:
            if 'checkedTBar' in i:
                a = i[0]
        for i in myDict[0]:
            if a in i:
                somaAndCoordinates['x'] = i[3]
                somaAndCoordinates['y'] = i[4]
                somaAndCoordinates['z'] = i[5]
        # somaAndCoordinates[myNeur.skeletonID] = z
        return somaAndCoordinates


def builder(SKID=None):
    if SKID is None:
        # sets list of all skeleton IDs
        mySkels = GARI.getListOfSkID_int()

        for i in mySkels:
            mySkels.append(int(i))

        myNeurons = []

        for i in mySkels:
            x = neuronSet(i)
            myNeurons.append(x)

    else:
        SKID = int(SKID)
        myNeurons = []
        x = neuronSet(SKID)
        myNeurons.append(x)

    myAnnotations = GARI.getMyAnnotations()

    myNames = GLT.getLookUpTableSkID_Name()

    return myNeurons
