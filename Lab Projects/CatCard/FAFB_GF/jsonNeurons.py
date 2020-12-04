'''
Emily Tenshaw & Jason Polsky
CAT-Card
Updated 12/1/2020


This file allows you to make JSON files with GF input set data.
You can add new functions to retrieve the data/JSON format you want.
Ex: change color, opacity, neurons in JSON etc.
'''
import CustomNeuronClassSet as CN
import json
import os
import colour
import datetime
import subsetCreator as SC
now = datetime.datetime.now()

# dumps info into a JSON but doesn't save the JSON file - helper function for makeJsonFile
def makeJson(mySet):
    aListOfNeurons = []
    for item in mySet:
        mySKID = item.skeletonID
        aNeuron = {
        "skeleton_id": mySKID,
        "color": "#00eee5",
        "opacity": 1
        }
        aListOfNeurons.append(aNeuron)
    
    myJSON = json.dumps(aListOfNeurons, separators=(', \n', ': '))
    return myJSON

# dumps JSON data into a file, can be used with any JSON creator methods to make a file
# does not create own JSON like makePlainJSON does
def makeJsonFile(myJSON, filename):
    pathVar = "C:/Users/etens/Desktop/pyCharmOutputs/FAFB_GF"
    myFile = str(filename)
    myPath = "{}/".format(pathVar)
    myPath = os.path.normpath(myPath)
    if not os.path.isdir(myPath):
        os.makedirs(myPath)
    finalFileName = os.path.join(myPath, filename)

    myFileCheck = finalFileName + ".json"
    c = open(myFileCheck, 'w')
    c.write(myJSON)
    c.close()
    print("JSON saved as {}".format(str(myFile)))
    return

# makes a JSON file quickly for  GF Input set rather than typing the lines to make a JSON each time
# call this function to save json file to computer;  work on naming protocol(if not annotations, etc...)
# must enter a file name - directs to pycharm outputs FAFB GF folder
# should work for any GF Input set regardless of info/colors/data
# doesn't take in other JSON data - creates own JSON dump
def makePlainJSON(mySet, filename = "plainGFInputJSON"):
    if type(mySet) is not CN.GFIN_set:
        mySet = CN.buildFromSkidList(mySet)
    myData = makeJson(mySet)
    copyNumber = 0
    pathVar = "C:/Users/etens/Desktop/pyCharmOutputs/FAFB_GF"
    myFile = str(filename)
    myPath = "{}/{}/".format(pathVar, str(filename))
    myPath = os.path.normpath(myPath)
    finalFileName = os.path.join(myPath, filename)

    myFileCheck = finalFileName + ".json"
    c = open(myFileCheck, 'w')
    c.write(myData)
    c.close()
    print("JSON saved as {}".format(str(myFile)))
    return


'''
JSON creator examples - can make colors, opacity, etc. different
Can change data based off what you are looking for
'''

# creates JSON data based off the synaptic gradient onto the GF
def makeJsonSynapticColorGradient(mySet):
    mySet = SC.sortBySynL2H(mySet)
    aListOfNeurons = []
    #numInSet = mySet.numNeurons
    #myIncrement = int(16777000 / numInSet)
    red = colour.Color("red")
    blue = colour.Color("blue")
    allColors = list(blue.range_to(red, mySet.numNeurons + 1))
    curColor = 0
    for item in mySet:
        mySKID = item.skeletonID
        synCount = item.GF1synapseCount
        curColor += 1
        myColor = allColors[curColor].hex_l
        item.curColor = myColor
        aNeuron = {
        "skeleton_id": mySKID,
        "color": myColor,
        "opacity": 1
        }
        aListOfNeurons.append(aNeuron)
    
    myJSON = json.dumps(aListOfNeurons, separators=(', \n', ': '))
    return myJSON


# creates a JSON where each classification is colored differently
# has many similar colors due to the number of classifications
# does not create a file just JSON data
def makeJsonFlatColorByClass(mySet):
    myClassList = []
    for i in mySet:
        if i.classification not in myClassList:
            myClassList.append(i.classification)
    red = colour.Color("red")
    blue = colour.Color("blue")
    colorList = list(blue.range_to(red, len(myClassList)))
    classColor = dict(zip(myClassList, colorList))
    aListOfNeurons = []
    for i in mySet:
        mySKID = i.skeletonID
        aNeuron = {
            "skeleton_id": mySKID,
            "color": classColor[i.classification].hex_l,
            "opacity": 1
        }
        aListOfNeurons.append(aNeuron)

    myJSON = json.dumps(aListOfNeurons, separators=(', \n', ': '))
    return myJSON