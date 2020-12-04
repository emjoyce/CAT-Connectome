import config
import json
import requests
import itertools

token = config.token
auth = config.CatmaidApiTokenAuth(token)

project_id = config.project_id

#dn_autoseg_exploration
#annotation = 217283624
#descending neuron
#annotation = 2998068

#Putative_Ascending
#annotation = 217284386
#Ascending Neuron
#annotation = 3552044



#Old GetLookUpTable
# coding: utf-8

# returns dictionary containing a lookup table with int(annotation id) as key and annotation string/name as value
def getLookUpTable():
    token = config.token
    auth = config.CatmaidApiTokenAuth(token)

    project_id = config.project_id
    #object_ids = [134]
    #created_by = [134]
    #annotated_with = [863792]
    headers = config.CatmaidApiTokenAuth(token)


    allAnnotations = requests.get(
            'https://neuropil.janelia.org/tracing/fafb/v14-seg-li-190805.0/{}/annotations/'.format(project_id),
            auth = auth
    )

    someData = json.loads(allAnnotations.content.decode('utf-8'))

    #print(someData)
    AnnotationLookUpTable = {}
    AnnotationLookUpTable = someData["annotations"]

    myLookUpTable = {}

    for d in AnnotationLookUpTable:
        myLookUpTable[d['id']] = d['name']

    return myLookUpTable

def getAnnotationID(myAnnotation):
    c = getLookUpTable()
    for i in c:
        if c[i] == str(myAnnotation):
            return i
    return

# calls function above and returns list containing only lists (of length 1) of single int, each of which is a SKID
def getListOfSkeletonIDs(annotation):
    relevantDict = getAllSkeletonInfo(annotation)
    SkidList = []

    for d in relevantDict:
        if d['type'] == 'neuron':
            SkidList.append(d['skeleton_ids'])

    return SkidList


#input is a single object of type myCustomGFNeuron, output is a list of floats representing the x,y, and z coordinate of the soma in catmaid.
def getSoma(myNeur):
    skeletonID = myNeur.skeletonID
    response = requests.get(
            'https://neuropil.janelia.org/tracing/fafb/v14-seg-li-190805.0/1/skeletons/{}/node-overview'.format(skeletonID),
    )
    myDict = json.loads(response.content)
    somaAndCoordinates = [None] * 3
    a = None
    for i in myDict[2]:
        #print(i)
        if 'soma' in i:
            a = i[0]
            #print(i)
    for item in myDict[0]:
        if a is None:
            print(myNeur, 'has no soma')
            break                                   #break might break this code consider removing if it stops working
        elif a in item:
            somaAndCoordinates[0] = item[3]
            somaAndCoordinates[1] = item[4]
            somaAndCoordinates[2] = item[5]
    #somaAndCoordinates[myNeur.skeletonID] = z
    return somaAndCoordinates

def getMyAnnotations2():
    myNeuronswithAnnotations = convertID2String()

    return myNeuronswithAnnotations


def getAllSkeletonInfo(annotation):
    if type(annotation) is not int:
        annotation = int(getAnnotationID(str(annotation)))
    else:
        annotation = annotation

    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14-seg-li-190805.0/{}/annotations/query-targets'.format(project_id),
        auth=auth,
        data={'annotated_with': annotation}

    )

    myData = json.loads(response.content.decode('utf-8'))

    relevantDict = {}
    relevantDict = myData['entities']

    return relevantDict

#makes list of lists into single list of body IDs
def getListOfSkID_int(annotation):
    aList = getListOfSkeletonIDs(annotation)
    aNewList = []
    for i in aList:
        aNewList.append(i[0])

    return aNewList

#defaults to descending neuron annotation unless specified
def getLookUpTableSkID_Name(annotation):
    relevantDict = getAllSkeletonInfo(annotation)
    SkIDLookUpNeuronName = {}

    # returns dictionary containing SkID : neuron name pairs
    for d in relevantDict:

        if d["type"] == 'neuron':
            SkIDLookUpNeuronName[((d['skeleton_ids'])[0])] = d['name']

    return SkIDLookUpNeuronName


# returns dictionary with each key being a skelID and each value being a list of their annotation IDs
def getDictOfNeuronsWithIDs(annotation):
    SkidList = getListOfSkeletonIDs(annotation)

    newResponse = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14-seg-li-190805.0/{}/annotations/forskeletons'.format(project_id),
        auth=auth,
        data={'skeleton_ids': SkidList}
    )
    # print(type(newResponse))
    # print(newResponse.text)

    thisData = json.loads(newResponse.content.decode('utf-8'))

    Annotations4ThisNeuron = {}
    myNeurons = {}
    myNeurons = thisData['skeletons']
    tempList = []

    # print(myNeurons)

    for i in myNeurons:
        for d in myNeurons[i]:
            tempList.append(d['id'])
        Annotations4ThisNeuron[i] = tempList
        tempList = []

    return Annotations4ThisNeuron


# returns dictionary with each key being a skelID and each value being a list of annotation Strings
def convertID2String(annotation):
    myDict = getDictOfNeuronsWithIDs(annotation)
    AnnotationLookUpTable = getLookUpTable()
    myNewDict = {}
    ListOfAnnotations = []

    for i in myDict:
        for e in myDict[i]:
            ListOfAnnotations.append(AnnotationLookUpTable[e])
            33# e = AnnotationLookUpTable[e]
            # print(e)
        myNewDict[i] = ListOfAnnotations
        ListOfAnnotations = []

    return myNewDict


def setAnnotationLookUpTable(SKID):
    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14-seg-li-190805.0/{}/annotations/forskeletons'.format(project_id),
        auth=auth,
        data={'skeleton_ids[0]': SKID}
    )
    myData = json.loads(response.content)
    myAnnotations = myData['annotations']

    a = []
    for i in myAnnotations:
        a.append(myAnnotations[i])
    return a


def getName(SKID):
    a = setAnnotationLookUpTable(SKID)
    b = str(a[0])

    c = getLookUpTableSkID_Name(b)
    myName = c[SKID]
    return myName


#Old GetListOfSkIDAndAnnotations
def getMyAnnotations(annotation):
    myNeuronswithAnnotations = convertID2String(annotation)

    return myNeuronswithAnnotations


def getAllNodes(myNeuron):
    mySkid = myNeuron.skeletonID
    # mySkids = GAREI.getListOfSkID_int()

    # mySkid=str(mySkids[0])
    # mySkid = 4947529

    mySkid = str(mySkid)

    response = requests.get(
        'https://neuropil.janelia.org/tracing/fafb/v14-seg-li-190805.0/{}/skeletons/{}/compact-detail'.format(project_id, mySkid),
        auth=auth  # ,
        # data = {'skeleton_id' : mySkid}
    )

    skelInfo = json.loads(response.content)
    skelInfo = skelInfo[0]
    myCoordinates = []
    for i in skelInfo:
        myNode = [i[3], i[4], i[5]]
        myCoordinates.append(myNode)

    # return newList
    return myCoordinates


#can be used in other functions to remove neurons that do not have a soma in order to avoid error
def removeSomaless(mySet):
    for item in mySet:
        for i in item.soma:
            if i is None:
                print("{} removed because its soma could not be found".format(item.skeletonID))
                mySet -= item #mySet[mySet.index(i.skeletonID)]
                break
    return mySet