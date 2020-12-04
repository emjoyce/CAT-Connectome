'''
Emily Tenshaw
CAT-Card
Updated 12/1/2020

This file creates specific color options for GF input JSON files.
It is not the same as jsonNeurons, but the
'''

import CustomNeuronClassSet as CS
import json
import jsonNeurons as JN
import colour
from collections import defaultdict, OrderedDict


# creates a JSON file of the combination given by input variables
# first variable colors neurons
# second variable removes neurons that are unwanted
# Defaults to no neurons removed and color by synapse count
# color variables:
# 'Modality', 'SynapseCount', 'NoSingles', 'MoreThan9', 'Distribution' 'Default'
# creates JSON here "C:/Users/etens/Desktop/pyCharmOutputs/FAFB_GF"
# all of the functions below this are used by this main function
def createJSON(mySet, colorVariable='SynapseCount', colorVariable2='Default'):
    colorVariableDict = {'Modality': byModality, 'NoSingles': noSingles,
                         'MoreThan9': moreThanNine, 'SynapseCount': bySynapseCount,
                         'Distribution': byDistribution, 'Classification': byClassification,
                         'CombinedLetters': combineLetteredClasses, 'moreThan100': moreThan100}

    if colorVariable2 is 'NoSingles':
        mySetCopy = noSingles(mySet)
        colorVariableDict[colorVariable](mySetCopy)
        aListofNeurons = []
        for neuron in mySetCopy:
            if isinstance(neuron.curColor, str):
                neuron.curColor = neuron.curColor
            else:
                neuron.curColor = neuron.curColor.hex_l
            aNeuron = {
                "skeleton_id": neuron.skeletonID,
                "color": neuron.curColor,
                "opacity": 1
            }
            aListofNeurons.append(aNeuron)
        myJSON = json.dumps(aListofNeurons, separators=(', \n', ': '))
    elif colorVariable2 is 'MoreThan9':
        mySetCopy = moreThanNine(mySet)
        colorVariableDict[colorVariable](mySetCopy)
        aListofNeurons = []
        for neuron in mySetCopy:
            if isinstance(neuron.curColor, str):
                neuron.curColor = neuron.curColor
            else:
                neuron.curColor = neuron.curColor.hex_l
            aNeuron = {
                "skeleton_id": neuron.skeletonID,
                "color": neuron.curColor,
                "opacity": 1
            }
            aListofNeurons.append(aNeuron)
        myJSON = json.dumps(aListofNeurons, separators=(', \n', ': '))
    elif colorVariable2 is 'moreThan100':
        mySetCopy = moreThan100(mySet)
        colorVariableDict[colorVariable](mySetCopy)
        aListofNeurons = []
        for neuron in mySetCopy:
            if isinstance(neuron.curColor, str):
                neuron.curColor = neuron.curColor
            else:
                neuron.curColor = neuron.curColor.hex_l
            aNeuron = {
                "skeleton_id": neuron.skeletonID,
                "color": neuron.curColor,
                "opacity": 1
            }
            aListofNeurons.append(aNeuron)
        myJSON = json.dumps(aListofNeurons, separators=(', \n', ': '))
    elif colorVariable2 is 'CombinedLetters':
        mySetCopy = moreThanNine(mySet)
        colorVariableDict[colorVariable](mySetCopy)
        aListofNeurons = []
        for neuron in mySetCopy:
            if isinstance(neuron.curColor, str):
                neuron.curColor = neuron.curColor
            else:
                neuron.curColor = neuron.curColor.hex_l
            aNeuron = {
                "skeleton_id": neuron.skeletonID,
                "color": neuron.curColor,
                "opacity": 1
            }
            aListofNeurons.append(aNeuron)
        myJSON = json.dumps(aListofNeurons, separators=(', \n', ': '))
    else:
        colorVariableDict[colorVariable](mySet)
        aListofNeurons = []
        for neuron in mySet:
            if isinstance(neuron.curColor, str):
                neuron.curColor = neuron.curColor
            else:
                neuron.curColor = neuron.curColor.hex_l
            aNeuron = {
                "skeleton_id": neuron.skeletonID,
                "color": neuron.curColor,
                "opacity": 1
            }
            aListofNeurons.append(aNeuron)
        myJSON = json.dumps(aListofNeurons, separators=(', \n', ': '))

    copyNumber = 0
    fileName = colorVariable2 + '_' + colorVariable
    JN.makeJsonFile(myJSON, fileName)
    return


'''
Color and sorting functions
To be used in main function above
'''


# colors input neurons by their classification
def byClassification(mySet):
    classes = defaultdict(list)
    for neuron in mySet:
        classes[neuron.classification].append(neuron)
    red = colour.Color("red")
    blue = colour.Color("blue")
    allColors = list(blue.range_to(red, len(classes)))
    curColor = -1
    for k, v in classes.items():
        curColor = curColor + 1
        for neuron in v:
            neuron.curColor = allColors[curColor]
    return


# colors input neurons by their modality
def byModality(mySet):
    mySet.findModality()
    for neuron in mySet:
        if neuron.modality == 'VPN':
            neuron.curColor = 'rgb(255,0,0)'
        if neuron.modality == 'Other Visual':
            neuron.curColor = 'rgb(255,128,0)'
        if neuron.modality == 'Visual Interneuron':
            neuron.curColor = 'rgb(255,255,0)'
        if neuron.modality == 'JONeuron':
            neuron.curColor = 'rgb(127,255,0)'
        if neuron.modality == 'Mechanosensory Interneuron':
            neuron.curColor = 'rgb(34,139,34)'
        if neuron.modality == 'Non-Visual Interneuron':
            neuron.curColor = 'rgb(0,255,255)'
        if neuron.modality == 'Ascending Neuron':
            neuron.curColor = 'rgb(30, 144, 255)'
        if neuron.modality == 'Descending Neuron':
            neuron.curColor = 'rgb(138,43,226)'
    return


# only neurons that have 100 or more synapses
def moreThan100(mySet):
    mySetCopy = []
    for neuron in mySet:
        if neuron.GF1synapseCount > 99:
            mySetCopy.append(neuron)
    mySetCopy = CS.GFIN_set(mySetCopy)
    return mySetCopy


# colors neurons in a gradient by exact synapse count
def bySynapseCount(mySet):
    synapseCounts = defaultdict(list)
    for neuron in mySet:
        synapseCounts[neuron.GF1synapseCount].append(neuron)
    red = colour.Color("red")
    blue = colour.Color("blue")
    allColors = list(blue.range_to(red, len(synapseCounts)))
    synapseCounts = OrderedDict(sorted(synapseCounts.items(), key=lambda item: float(item[0])))
    curColor = -1
    for k, v in synapseCounts.items():
        curColor = curColor + 1
        for neuron in v:
            neuron.curColor = allColors[curColor]
    return


# colors neurons by distribution
def byDistribution(mySet):
    for item in mySet:
        if item.distribution is "Anterior":
            item.curColor = 'rgb(220,20,60)'
        elif item.distribution is "AnteriorDescending":
            item.curColor = "rgb(0,100,0)"
        elif item.distribution is "AnteriorLateral":
            item.curColor = "rgb(0,255,255)"
        elif item.distribution is "AnteriorLateralSoma":
            item.curColor = "rgb(255,0,255)"
        elif item.distribution is "AnteriorMedial":
            item.curColor = "rgb(107,142,35)"
        elif item.distribution is "AnteriorMedialLateral":
            item.curColor = "rgb(0,255,0)"
        elif item.distribution is "AnteriorMedialLateralSoma":
            item.curColor = "rgb(0,0,255)"
        elif item.distribution is "AnteriorMedialSoma":
            item.curColor = "rgb(139,69,19)"
        elif item.distribution is "Descending":
            item.curColor = "rgb(70,130,180)"
        elif item.distribution is "Lateral":
            item.curColor = "rgb(255,165,0)"
        elif item.distribution is "LateralSoma":
            item.curColor = "rgb(147,112,219)"
        elif item.distribution is "Medial":
            item.curColor = "rgb(255,255,0)"
        elif item.distribution is "MedialDescending":
            item.curColor = "rgb(218,165,32)"
        elif item.distribution is "MedialLateral":
            item.curColor = "rgb(105,105,105)"
        elif item.distribution is "MedialLateralSoma":
            item.curColor = "rgb(128,0,128)"
        elif item.distribution is "MedialSoma":
            item.curColor = "rgb(250,128,114)"
        elif item.distribution is "Soma":
            item.curColor = "rgb(255,255,255)"
        else:
            item.curColor = "rgb(0,0,0)"
    return


# removes single synapse neurons
def noSingles(mySet):
    mySetCopy = []
    for neuron in mySet:
        if neuron.GF1synapseCount > 1:
            mySetCopy.append(neuron)
    mySetCopy = CS.GFIN_set(mySetCopy)

    return mySetCopy


# removes neurons with less than 10 synapses
def moreThanNine(mySet):
    mySetCopy = []
    for neuron in mySet:
        if neuron.GF1synapseCount > 9:
            mySetCopy.append(neuron)
    mySetCopy = CS.GFIN_set(mySetCopy)

    return mySetCopy


# combines classifications of lettered groups
def combineLetteredClasses(mySet):
    mySetCopy = mySet
    for neuron in mySetCopy:
        if neuron.classification == "Unclassified GF input neuron - type 13b":
            neuron.classification = "Unclassified GF input neuron - type 13"
    for neuron in mySet:
        if neuron.classification == "Unclassified GF input neuron - type 13c":
            neuron.classification = "Unclassified GF input neuron - type 13"
    for neuron in mySet:
        if neuron.classification == "Unclassified GF input neuron - type 21b":
            neuron.classification = "Unclassified GF input neuron - type 21a"
    for neuron in mySet:
        if neuron.classification == "Unclassified GF input neuron - type 22b":
            neuron.classification = "Unclassified GF input neuron - type 22"
    for neuron in mySet:
        if neuron.classification == "Unclassified GF input neuron - type 23b":
            neuron.classification = "Unclassified GF input neuron - type 23a"
    for neuron in mySet:
        if neuron.classification == "Unclassified GF input neuron - type 24b":
            neuron.classification = "Unclassified GF input neuron - type 24a"
    for neuron in mySet:
        if neuron.classification == "Unclassified GF input neuron - type 24c":
            neuron.classification = "Unclassified GF input neuron - type 24a"
    for neuron in mySet:
        if neuron.classification == "Unclassified GF input neuron - type 24d":
            neuron.classification = "Unclassified GF input neuron - type 24a"
    for neuron in mySet:
        if neuron.classification == "Unclassified GF input neuron - type 24e":
            neuron.classification = "Unclassified GF input neuron - type 24a"
    for neuron in mySet:
        if neuron.classification == "Unclassified GF input neuron - type 27b":
            neuron.classification = "Unclassified GF input neuron - type 27a"
    for neuron in mySet:
        if neuron.classification == "Unclassified GF input neuron - type 2b":
            neuron.classification = "Unclassified GF input neuron - type 2a"
    for neuron in mySet:
        if neuron.classification == "Unclassified GF input neuron - type 61b":
            neuron.classification = "Unclassified GF input neuron - type 61a"
    for neuron in mySet:
        if neuron.classification == "Unclassified GF input neuron - type 62b":
            neuron.classification = "Unclassified GF input neuron - type 62"
    for neuron in mySet:
        if neuron.classification == "Unclassified GF input neuron - type 64b":
            neuron.classification = "Unclassified GF input neuron - type 64a"
    for neuron in mySet:
        if neuron.classification == "Unclassified GF input neuron - type 66b":
            neuron.classification = "Unclassified GF input neuron - type 66a"
    for neuron in mySet:
        if neuron.classification == "Unclassified GF input neuron - type 72b":
            neuron.classification = "Unclassified GF input neuron - type 72a"
    return mySetCopy
