"""
Emily Tenshaw
CAT-Card
12/2/2020

Creates a class of ascending neuron objects in the autoseg instance.
Uses a builder function to pull data using "Ascending Neuron" and "Putative_Ascending" annotations in FAFB autoseg
"""

import config
import NeuronObjectData
import re

token = config.token
auth = config.CatmaidApiTokenAuth(token)

project_id = config.project_id


# dn_autoseg_exploration
# annotation = 217283624
# descending neuron
# annotation = 2998068

# Putative_Ascending
# annotation = 217284386
# Ascending Neuron
# annotation = 3552044

# creates the AN object - AN class is a set on AN objects
# lists and holds properties of an AN
class AscendingNeuron(object):

    def __init__(self, skeletonID):
        self.neuronName = ""
        self.skeletonID = skeletonID
        self.annotations = []
        self.classification = ''
        self.status = None
        self.existV14 = None

    def __repr__(self):
        return '{}'.format(self.neuronName)

    def __str__(self):
        return "Name: {}, " \
               "skeleton ID = {}, " \
               "DN Type = {}".format(self.neuronName, self.skeletonID, self.dnType)

    def __iter__(self):
        for attr in dir(self):
            if not attr.startswith("__") and 'percent' not in attr:
                yield attr

        '''
        def __getitem__(self, item):
            return self.item
        '''

    def getSkID(self):
        return self.skeletonID

    def getAnnotations(self):
        myAnnotations = NeuronObjectData.getMyAnnotations()
        y = self.skeletonID
        z = str(y)
        if z in myAnnotations:
            self.annotations = myAnnotations[z]
        return self.annotations

    def getNeuronName(self):
        y = self.skeletonID
        z = str(y)
        myNames = NeuronObjectData.getLookUpTableSkID_Name()
        if y in myNames:
            self.neuronName = myNames[y]
        return self.neuronName

    def getSkeletonNodes(self):
        self.skeletonNodes = NeuronObjectData.getAllNodes(self)
        return self.skeletonNodes


# via stack overflow https://stackoverflow.com/questions/38987/how-do-i-merge-two-dictionaries-in-a-single-expression-in-python
def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


# builds a neuron object
def builder(myList):
    # sets list of all skeleton IDs
    mySkels = myList

    myAnnotations = NeuronObjectData.getMyAnnotations(217284386)
    myAnnotations2 = NeuronObjectData.getMyAnnotations(3552044)

    myAnnotations3 = merge_dicts(myAnnotations, myAnnotations2)

    # creates a dictionary with key-value pairs of int(skelID) and and str(neuron name)
    myNames = NeuronObjectData.getLookUpTableSkID_Name(217284386)
    myNames2 = NeuronObjectData.getLookUpTableSkID_Name(3552044)
    # creates empty list to be filled with all instances
    myNeurons = []

    # creates list of of all instances while setting each instance's name and skeletonID to be an element from mySkls
    for i in mySkels:
        x = AscendingNeuron(i)
        myNeurons.append(x)

    # converts skeletonID attribute to string for use as dictionary key then adds all available synapses from
    # dictionary of synapses and all       available annotations from dictionary of annotations
    for elem in myNeurons:
        y = elem.skeletonID
        z = str(y)
        if z in myAnnotations3:
            elem.annotations = myAnnotations3[z]
            p = elem.annotations

            if "Descending Neuron" in p:
                elem.classification = "Descending"
                elem.status = "Descending Neuron"
            elif "Ascending Neuron" in p:
                elem.classification = "Ascending"
                elem.status = "Ascending Neuron"
            elif "Putative_Ascending" in p:
                elem.classification = 'Ascending'
                elem.status = "Putative_Ascending"

            if "merges larger DN" in p:
                elem.status = "Merges into larger DN"
            elif "merges existing DN" in p:
                elem.status = "Merges into existing DN"
            elif 'Halted' in p or 'Halted Neuron' in p:
                elem.status = 'Halted'
            elif 'FindSoma' in p:
                elem.status = 'FindSoma'

            if y in myNames:
                elem.neuronName = myNames[y]
            if y in myNames2:
                elem.neuronName = myNames2[y]

        removeAnno = re.compile("Merged: Google")
        newAnno = [ann for ann in elem.annotations if not removeAnno.search(ann)]
        elem.annotations = newAnno

    return myNeurons
