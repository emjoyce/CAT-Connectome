"""
Emily Tenshaw
CAT-Card
12/2/2020

Creates an ascending neuron set object with ascending neuron objects
Subset and file creation (JSON/CSV) functions are also in this file
"""

import AscendingNeuronClass
import NeuronObjectData
import numpy as np
import config
import requests
from collections import defaultdict
import json
import os
import datetime
import csv
now = datetime.datetime.now()


#dn_autoseg_exploration
#annotation = 217283624
#descending neuron
#annotation = 2998068

#Putative_Ascending
#annotation = 217284386
#Ascending Neuron
#annotation = 3552044


token = config.token
project_id = config.project_id

#Creates the ascending neuron set - object that holds the data
class AscendingSet(object):

    def __init__(self, container=None):
        super().__init__()
        if container is None:
            self.container = []
        else:
            self.container = container

        self.numNeurons = self._getNumNeurons()
        self.groupName = None
        self.allAnnotations = self._setAllAnnotations()
        self.varCheck = []
        self.allConnectorInfo = None


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
        # returns subset of type DnAutoseg_Set
        elif isinstance(index, slice):
            x = AscendingSet(self.container[index])
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
        return value in self.container_

    def __repr__(self):
        return str(self.container)

    def __add__(self, otherList):
        myList = []
        for i in self.container:
            myList.append(i)
        if isinstance(otherList, AscendingNeuronClass.AscendingNeuron):
            myList.append(otherList)
            added = subSetBuilder(myList)
            for i in vars(self).keys():
                if i is not 'numNeurons' and i is not 'container' and i is not 'percentTotalSynapses':
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
        if isinstance(otherList, AscendingNeuronClass.AscendingNeuron):
            myList.remove(otherList)
        else:
            for i in otherList.container:
                myList.remove(i)
        subtracted = subSetBuilder(myList)
        return subtracted

    '''def append(self, argument):
        if isinstance(argument, int):
            self += argument
        elif isinstance(argument, slice):
            pass
        pass'''

    # input should be skeletonID of neuron of interest, function returns the index that can be called on neuron set to get info about that
    # neuron
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

    '''def __str__(self.connectorInfo):
        anteriorCount = len(self.ConnectorInfo['anterior'])
        medialCount = len(self.ConnectorInfo['medial'])
        lateralCount = len(self.ConnectorInfo['lateral'])
        somaTractCount = len(self.ConnectorInfo['soma tact'])

        myString = 'Anterior Synapse Count: {}, medial Synapse count: {}, lateral Synapse Count: {}, soma synapse Count: {}'.format(anteriorCount, medialCount, lateralCount, somaTractCount)
        return myString'''


    # returns the number of neurons in the current group
    def _getNumNeurons(self):
        numNeurons = len(self)
        return numNeurons

    def _setAllAnnotations(self):
        annotationList = []
        for neuron in self:
            for annotation in neuron.annotations:
                if annotation not in annotationList:
                    annotationList.append(annotation)
        return annotationList


    # input is an object of type GFIN_set and result is population of the skeletonNodes attribute for each GFinput neuron in the set
    def updateSkeletonNodes(self):
        for i in self:
            if i.skeletonNodes is None:
                i.getSkeletonNodes()
            else:
                continue
        self.varCheck.append('skeletonNodes')
        return self

    def getAllSkeletonNodes(self):
        for i in self:
            i.getSkeletonNodes()
        self.varCheck.append('skeletonNodes')
        return self

    def getGroupNumber(self):
        classes = defaultdict(list)
        indexed = defaultdict(list)
        num = 1
        for neuron in self:
            classes[neuron.classification].append(neuron)

        for type in classes.values():
            for neuron in type:
                neuron.groupNumber = num
            num = num + 1
        return
    # note that the api endpoint in use here requires entity ids which equals neuron id, not skeleton ID
    # LEFT HEMISPHERE == 1223085
    def correctAnnotations(self):
        mySet = NeuronObjectData.removeSomaless(self)
        rightHem = []
        leftHem = []
        for item in mySet:
            if item.soma[0] < 500000:
                rightHem.append(item.skeletonID + 1)
            elif item.soma[0] > 550000:
                leftHem.append(item.skeletonID + 1)
        responseOne = requests.post(
            'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/remove'.format(project_id),
            auth=config.CatmaidApiTokenAuth(token),
            data={'entity_ids': rightHem, 'annotation_ids': [1223085]}
        )
        responseOne = json.loads(responseOne.content)
        print(responseOne)
        responseTwo = requests.post(
            'https://neuropil.janelia.org/tracing/fafb/v14-seg-li-190805.0/{}/annotations/remove'.format(project_id),
            auth=config.CatmaidApiTokenAuth(token),
            data={'entity_ids': leftHem, 'annotation_ids': [1167304]}
        )
        responseTwo = json.loads(responseTwo.content)
        print(responseTwo)
        return

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
                'https://neuropil.janelia.org/tracing/fafb/v14-seg-li-190805.0/{}/annotations/add'.format(project_id),
                auth=config.CatmaidApiTokenAuth(token),
                data={'skeleton_ids': mySkids, 'annotations': newAnnotation}
            )
        else:
            response = requests.post(
                'https://neuropil.janelia.org/tracing/fafb/v14-seg-li-190805.0/{}/annotations/add'.format(project_id),
                auth=config.CatmaidApiTokenAuth(token),
                data={'annotations': newAnnotation, 'meta_annotations': metaAnnotations}
            )

        myResults = json.loads(response.content)
        print(myResults)
        return

    def allMyVars(self):
        allVars = dir(self)
        allSigVars = []
        for i in allVars:
            if "__" not in i:
                allSigVars.append(i)
        return allSigVars

'''
    def makeDataFrame(self):
        myDataFrame = {}
        myAttributeNames = ['Neuron Name', 'skeletonID', 'GF1 Synapse Count', 'GF2 Synapse Count', 'percent total synapses',
                   'classification', 'hemisphere', 'cellBodyRind', 'somaHemisphere', 'commissure', 'numLC4Syn',
                   'numLPLC2Syn',
                   'numLC6Syn', 'numLPLC1Syn', 'numLPC1Syn', 'numLC28Syn', 'numLLPC1Syn', 'numLPLC3Syn',
                   'lateral branch',
                   'medial branch', 'anterior branch', 'soma tract', 'descending tract']
        myAttributes = [globals()neuronName, skeletonID, GF1synapseCount, GF2synapseCount, percentTotalSynapse, classification, hemisphere, cellBodyRind, somaSide, commissure, postsynapticToLC4, postsynapticToLPLC2, postsynapticToLC6, postsynapticToLPLC1, postsynapticToLPC1, postsynapticToLC28, postsynapticToLLPC1, postsynapticToLPLC3, synapsesByBranch['lateral'], synapsesByBranch['medial'], synapsesByBranch['anterior'], synapsesByBranch['soma tract'], synapsesByBranch['descending tract']]
        for attribute in myAttributeNames:
            myDataFrame[attribute] = []
        for neuron in self:
            for attribute in myAttributeNames:
                myDataFrame[attribute].append()
        return myDataFrame
    '''

''' def makeDataFrame(self):

        myWriter = csv.writer()
        myRows0 = ['Neuron Name', 'skeletonID', 'GF1 Synapse Count', 'GF2 Synapse Count', 'percent total synapses',
                   'classification', 'hemisphere', 'cellBodyRind', 'somaHemisphere', 'commissure', 'numLC4Syn',
                   'numLPLC2Syn', 'numLC6Syn', 'numLPLC1Syn', 'numLPC1Syn', 'numLC28Syn', 'numLLPC1Syn',
                   'numLPLC3Syn', 'lateral branch', 'medial branch', 'anterior branch', 'soma tract',
                   'descending tract']
        myRows = myRows0 + mySet.allAnnotations
        myWriter.writerow(myRows)
        for item in self:
            theseAnnotations = []
            for annotation in self.allAnnotations:
                if annotation in item.annotations:
                    theseAnnotations.append(1)
                else:
                    theseAnnotations.append(0)
            curRow = [item.neuronName, item.skeletonID, item.GF1synapseCount, item.GF2synapseCount,
                      item.percentTotalSynapse, item.classification, item.hemisphere, item.cellBodyRind,
                      item.somaSide, item.commissure, item.postsynapticToLC4, item.postsynapticToLPLC2,
                      item.postsynapticToLC6, item.postsynapticToLPLC1, item.postsynapticToLPC1,
                      item.postsynapticToLC28, item.postsynapticToLLPC1, item.postsynapticToLPLC3,
                      item.synapsesByBranch['lateral'], item.synapsesByBranch['medial'],
                      item.synapsesByBranch['anterior'], item.synapsesByBranch['soma tract'],
                      item.synapsesByBranch['descending tract']]
            fullRow = curRow + theseAnnotations
        myWriter.writerow(fullRow)

        return myWriter'''

#builds the AN set by using "Putative_Ascending" and "Ascending Neuron"
#annotations - if they aren't annotated the neuron won't be pulled
def builder():
    ascending_skidlist = NeuronObjectData.getListOfSkID_int(217284386)
    putative_skidlist = NeuronObjectData.getListOfSkID_int(3552044)
    skidList = []
    for i in ascending_skidlist:
        skidList.append(i)
    for i in putative_skidlist:
        if i not in skidList:
            skidList.append(i)
    mySet = AscendingSet(np.array(AscendingNeuronClass.builder(skidList)))
    return mySet

#creates subset
def subSetBuilder(fullSet):
    mySubSet = AscendingSet(np.array(fullSet))
    if isinstance(fullSet, AscendingSet):
        if fullSet.groupName != None:
            mySubSet.groupName = fullSet.groupName
        return mySubSet
    else:
        return mySubSet

#makes an AN JSON file
def makeANJSON(ANSet):
    if type(ANSet) is not AscendingSet:
        ANSet = builder()
    data = makeJson(ANSet)

    copy = 0
    myFile = str(ANSet)
    myFileCheck = myFile + ".json"
    while os.path.isfile(myFileCheck) == True:
        copy += 1
        # myFile += str(copyNumber)
        myFileCheck = myFile + '_' + str(copy) + '.json'
    myFile += '.json'
    c = open(myFile, 'w')
    c.write(data)
    c.close()
    print("JSON saved as {}".format(str(myFile)))
    return


def makeJson(ANSet):
    aListOfNeurons = []
    for item in ANSet:
        mySKID = item.skeletonID
        aNeuron = {
            "skeleton_id": mySKID,
            "color": "#00eee5",
            "opacity": 1
        }
        aListOfNeurons.append(aNeuron)

    myJSON = json.dumps(aListOfNeurons, separators=(', \n', ': '))
    return myJSON

#makes the CSV we use for ANs
def makeCSV(ANSet, formatType='saveGeneral'):
    formatTypeDict = {'saveGeneral': saveGeneral}
    copyNumber = 0
    saveCount = 0
    nameVar = "AscendingNeurons"
    myFileName = str(nameVar)
    pathVar = "C:/Users/etens/Desktop/pyCharmOutputs"
    myPath = os.path.normpath(pathVar)

    if not os.path.isdir(myPath):
        os.makedirs(myPath)

    fileName = str(now.year) + str(now.month) + str(now.day)
    fileName += myFileName
    finalFileName = os.path.join(myPath, fileName)

    myFile = str(finalFileName)
    myFileCheck = myFile + ".csv"
    myBaseFile = myFile
    while os.path.isfile(myFileCheck) == True:
        copyNumber += 1
        myFileCheck = myFile + "_" + str(copyNumber)
        myBaseFile = myFileCheck
        myFileCheck += '.csv'
    myFile = myFileCheck
    args = [myFile, ANSet]
    formatTypeDict[formatType](args)
    return

#format to save the CSV file
def saveGeneral(args):
    myFile = args[0]
    mySet = args[1]
    with open(myFile, 'w', newline='') as outfile:
        myWriter = csv.writer(outfile)
        myWriter.writerow(
            ['Neuron Name', 'SKID', 'SKID in V14?', 'Annotation Info', 'Specific Annotation', 'Annotations'])
        for item in mySet:
            myWriter.writerow(
                [item.neuronName, item.skeletonID, item.existV14, item.classification,
                 item.status, item.annotations])
    return

