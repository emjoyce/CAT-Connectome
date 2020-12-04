"""
Emily Tenshaw
CAT-Card
12/1/2020

This is the hemibrain equivalent of the FAFB GF neuron class.
Still a work in progress as the hemibrain doesn't have annotaitons.
"""

import branchBoundingBox as BB

#Work in progress
class GFinputNeuron(object):

    def __init__(self, bodyId):
        self.bodyId = bodyId
        self.type = ''
        self.GF1synapseCount = int
        self.classification = None
        self.synapsesByBranch = {}
        self.instance = ''
        self.status = ''
        self.somaHemisphere = ''


    def __repr__(self):
        return '{}'.format(self.bodyId)

    def __str__(self):
        return "{}: Type = {}, GF1 synapse count = {} \n".format(self.bodyId, self.type, self.GF1synapseCount)
    def __iter__(self):
        for attr in dir(self):
            if not attr.startswith("__") and 'percent' not in attr:
                yield attr

    def getBodyId(self):
        return self.bodyId

    def getGF1synapseCount(self):
        return self.GF1synapseCount

    def getBodyType(self):
        return self.type

    def getBodyInstance(self):
        return self.instance

    def getBodyStatus(self):
        return self.status

    # work in progress - need to update the bounding box areas for branches
    def getSynapsesByBranch(self):
        synDict = BB.neuronSynapseLocation(self)
        self.synapsesByBranch['medial'] = (len(synDict['medial']))
        self.synapsesByBranch['descending'] = (len(synDict['descending']))
        self.synapsesByBranch['lateral'] = (len(synDict['lateral']))
        self.synapsesByBranch['anterior'] = (len(synDict['anterior']))
        self.synapsesByBranch['soma'] = (len(synDict['soma']))
        return

    # returns the classification - dependent on CSV file
    def getClassification(self):
        return self.classification


#builds from the returned array in queryDataFrameToArray
#need another builder to build from a different array, set, ect.
def buildFromArrayItem(i):
    neuron = GFinputNeuron(i[0])
    neuron.type = i[1]
    neuron.instance = i[2]
    neuron.status = i[3]
    neuron.GF1synapseCount = i[4]
    neuron.classification = i[5]
    neuron.somaHemisphere = i[6]
    return neuron

