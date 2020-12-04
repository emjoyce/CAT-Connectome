import DnAutosegClassSet as DNCS
import colour
import json
import os
from collections import defaultdict

def createCSVFiles(DNSet):
    DNa = []
    DNb = []
    DNc = []
    DNd = []
    DNg = []
    DNp = []

    misca = []
    miscb = []
    miscc = []
    miscd = []
    miscg = []
    miscp = []


    for i in DNSet:
        for anno in i.annotations:
            if "DNa type" in anno:
                DNa.append(i)
            if "DNb type" in anno:
                DNb.append(i)
            if "DNc type" in anno:
                DNc.append(i)
            if "DNd type" in anno:
                DNd.append(i)
            if "DNg type" in anno:
                DNg.append(i)
            if "DNp type" in anno:
                DNp.append(i)
            if "miscellaneous DNa" in anno:
                misca.append(i)
            if "miscellaneous DNb" in anno:
                miscb.append(i)
            if "miscellaneous DNc" in anno:
                miscc.append(i)
            if "miscellaneous DNd" in anno:
                miscd.append(i)
            if "miscellaneous DNg" in anno:
                miscg.append(i)
            if "miscellaneous DNp" in anno:
                miscp.append(i)

    DNa = DNCS.DnAutoseg_set(DNa)
    DNb = DNCS.DnAutoseg_set(DNb)
    DNc = DNCS.DnAutoseg_set(DNc)
    DNd = DNCS.DnAutoseg_set(DNd)
    DNg = DNCS.DnAutoseg_set(DNg)
    DNp = DNCS.DnAutoseg_set(DNp)

    misca = DNCS.DnAutoseg_set(misca)
    miscb = DNCS.DnAutoseg_set(miscb)
    miscc = DNCS.DnAutoseg_set(miscc)
    miscd = DNCS.DnAutoseg_set(miscd)
    miscg = DNCS.DnAutoseg_set(miscg)
    miscp = DNCS.DnAutoseg_set(miscp)

    return DNa, DNb, DNc, DNd, DNg, DNp, misca, miscb, miscc, miscd, miscg, miscp




def makeJsonByClass(mySet):
    typeList = []
    for i in mySet:
        if i.classification not in typeList:
            typeList.append(i.classification)
    red = colour.Color("red")
    blue = colour.Color("blue")
    colorList = list(blue.range_to(red, len(typeList)))
    classColor = dict(zip(typeList, colorList))

    typeDict = defaultdict(list)
    for i in mySet:
        for j in typeList:
            if i.classification == j:
                typeDict[j].append(i)

    for type, neurons in typeDict.items():
        aListOfNeurons = []
        for neuron in neurons:
            mySKID = neuron.skeletonID
            aNeuron = {
                "skeleton_id": mySKID,
                "color": classColor[neuron.classification].hex_l,
                "opacity": 1
            }
            aListOfNeurons.append(aNeuron)
        myJSON = json.dumps(aListOfNeurons, separators=(', \n', ': '))
        filename = str(type) + ".json"
        pathVar = "C:/Users/etens/Desktop/pyCharmOutputs/"
        myPath = os.path.normpath(pathVar)
        if not os.path.isdir(myPath):
            os.makedirs(myPath)
        finalFileName = os.path.join(myPath, filename)

        c = open(finalFileName, 'w')
        c.write(myJSON)
        c.close()
        print("JSON saved as {}".format(str(finalFileName)))
    return


def createJson(inputSet, filename):
    blue = colour.Color("blue").hex
    aListOfNeurons = []

    for neuron in inputSet:
        mySKID = neuron.skeletonID
        aNeuron = {
            "skeleton_id": mySKID,
            "color": blue,
             "opacity": 1
            }
        aListOfNeurons.append(aNeuron)
    myJSON = json.dumps(aListOfNeurons, separators=(', \n', ': '))
    filename = filename + ".json"
    pathVar = "C:/Users/etens/Desktop/pyCharmOutputs/"
    myPath = os.path.normpath(pathVar)
    if not os.path.isdir(myPath):
        os.makedirs(myPath)
    finalFileName = os.path.join(myPath, filename)

    c = open(finalFileName, 'w')
    c.write(myJSON)
    c.close()
    print("JSON saved as {}".format(str(finalFileName)))
    return



'''
import AscendingNeuronClassSet as ANCS
import checkV14
ANSet = ANCS.builder()
checkV14.checkV14SKID(ANSet)
ANCS.makeCSV(ANSet)


import DnAutosegClassSet as DNCS
import checkV14
DNSet = DNCS.builder()
checkV14.checkV14SKID(DNSet)
DNCS.makeCSV(DNSet)


import PullTypedDNs as PTD
DNa, DNb, DNc, DNd, DNg, DNp, misca, miscb, miscc, miscd, miscg, miscp = PTD.createCSVFiles(DNSet)
DNCS.makeCSV(DNa, "TypedDNa.csv")
DNCS.makeCSV(DNp, "TypedDNp.csv")
DNCS.makeCSV(DNg, "TypedDNg.csv")
DNCS.makeCSV(DNb, "TypedDNb.csv")
DNCS.makeCSV(DNc, "TypedDNc.csv")
DNCS.makeCSV(misca, "MiscDNa.csv")
DNCS.makeCSV(miscp, "MiscDNp.csv")
DNCS.makeCSV(miscg, "MiscDNg.csv")
DNCS.makeCSV(miscc, "MiscDNc.csv")
DNCS.makeCSV(miscb, "MiscDNb.csv")

PTD.makeJsonByClass(DNa)
PTD.makeJsonByClass(DNp)
PTD.makeJsonByClass(DNg)
PTD.createJson(misca, "MiscA")
PTD.createJson(miscg, "MiscG")
PTD.createJson(miscp, "MiscP")
'''