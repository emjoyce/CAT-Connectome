"""
Emily Tenshaw
CAT-Card
12/2/2020

Creates a class of descending neuron objects in the autoseg instance.
Uses a builder function to pull data using "Putative_Descendind" and "Descending Neuron" annotations in FAFB autoseg
"""
import config
import NeuronObjectData
import re
token = config.token
auth = config.CatmaidApiTokenAuth(token)

project_id = config.project_id

#dn_autoseg_exploration
#annotation = 217283624
#descending neuron
#annotation = 2998068
#Putative_Descending
#annotation = 217431412

#creates DN neuron object
class DescendingNeuron(object):

    def __init__(self, skeletonID):
        self.skeletonID = skeletonID
        self.annotations = []
        self.neuronName = ''
        self.classification = ''
        self.dnType = None
        self.status = None
        self.hemisphere = None
        self.ID = None
        self.existV14 = None
        self.dtSide = ''

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

    def getSomaNode(self):
        self.soma = NeuronObjectData.getSoma(self)
        return self.soma

    def getSkeletonNodes(self):
        self.skeletonNodes = NeuronObjectData.getAllNodes(self)
        return self.skeletonNodes

def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

#builds DN neuron
def builder(myList):
    # sets list of all skeleton IDs
    mySkels = myList

    myAnnotations = NeuronObjectData.getMyAnnotations(2998068)
    myAnnotations2 = NeuronObjectData.getMyAnnotations(217431412)
    myAnnotations3 = merge_dicts(myAnnotations, myAnnotations2)

    # creates a dictionary with key-value pairs of int(skelID) and and str(neuron name)
    myNames = NeuronObjectData.getLookUpTableSkID_Name(2998068)
    myNames2 = NeuronObjectData.getLookUpTableSkID_Name(217431412)
    myNames3 = merge_dicts(myNames, myNames2)

    # creates empty list to be filled with all instances
    myNeurons = []

    # creates list of of all instances while setting each instance's name and skeletonID to be an element from mySkls
    for i in mySkels:
        x = DescendingNeuron(i)
        myNeurons.append(x)

    # converts skeletonID attribute to string for use as dictionary key then adds all available synapses from
    # dictionary of synapses and all       available annotations from dictionary of annotations
    for elem in myNeurons:
        y = elem.skeletonID
        z = str(y)
        if z in myAnnotations3:
            elem.annotations = myAnnotations3[z]
            p = elem.annotations
            #DNp10 Non-Visual Input ClusterA
            DNTypeReg = re.compile(r'^.*DN[a-z][0-9](?!Interneuron)(?!Exploration)(?!presynaptic)(?!postsynaptic)(?!.*Non-Visual)')
            DNNewType = re.compile(r'DN[a-z] type')
            DNPutative = re.compile(r'putative_DN[a-z]$')

            idType = list(filter(DNTypeReg.match, p))
            newType = list(filter(DNNewType.match, p))
            putType = list(filter(DNPutative.match, p))

            if len(idType) != 0:
                elem.classification = str(idType[0])
            elif len(newType) != 0:
                elem.classification = str(newType[0])
            elif len(putType) != 0:
                elem.classification = str(putType[0])

            if "putative_Descending" in p:
                elem.classification = "putative_Descending"
            elif "DNa" in p:
                elem.dnType = "DNa"
            elif "DNb" in p:
                elem.dnType = "DNb"
            elif "DNc" in p:
                elem.dnType = "DNc"
            elif "DNd" in p:
                elem.dnType = "DNd"
            elif "DNg" in p:
                elem.dnType = "DNg"
            elif "DNp" in p:
                elem.dnType = "DNp"
            elif "DNx" in p:
                elem.dnType = "DNx"

            if "Typed DN" in p:
                elem.ID = "Typed DN"
            elif "miscellaneous DNa" in p:
                elem.ID = "Miscellaneous DNa"
            elif "miscellaneous DNp" in p:
                elem.ID = "Miscellaneous DNp"
            elif "miscellaneous DNg" in p:
                elem.ID = "Miscellaneous DNg"
            if elem.ID is None:
                if "Identified DN" in p:
                    elem.ID = "Identified DN"
                elif "Unidentified DN" in p:
                    elem.ID = "Unidentified DN"

            if 'RIGHT HEMISPHERE' in p:
                elem.hemisphere = "RIGHT HEMISPHERE"
            elif 'LEFT HEMISPHERE' in p:
                elem.hemisphere = "LEFT HEMISPHERE"
            elif 'midLine' in p:
                elem.hemisphere = "midLine"
            elif 'FindSoma' in p:
                elem.hemisphere = 'FindSoma'


            if elem.hemisphere is not None:
                elem.status = "Complete"

            if "duplicate - manual" in p:
                elem.status = "duplicate - manual"
            elif "duplicate - auto" in p:
                elem.status = "duplicate - auto"
            elif "check FC" in p:
                elem.status = "Check FC"
            elif 'Putative_Ascending' in p:
                elem.status = 'Putative_Ascending'
            elif 'Halted' in p or 'Halted Neuron' in p:
                elem.status = 'Halted'
            elif 'unclear FW' in p:
                elem.status = 'unclear FW'
            elif 'no FW soma' in p:
                elem.status = 'no FW soma'
            elif 'FindSoma' in p:
                elem.status = 'FindSoma'

            if 'check DT' in p:
                elem.dtSide = 'check DT'
            elif 'double DT' in p:
                elem.dtSide = "double DT"
            elif 'left DT' in p:
                elem.dtSide = 'Left'
            elif 'right DT' in p:
                elem.dtSide = 'Right'

            if y in myNames3:
                elem.neuronName = myNames3[y]


        removeAnno = re.compile("Merged: Google")
        newAnno = [ann for ann in elem.annotations if not removeAnno.search(ann)]
        elem.annotations = newAnno

    for neuron in myNeurons:
        classif = str(neuron.classification)
        neuron.classification = classif.replace("_", " ")

    return myNeurons






