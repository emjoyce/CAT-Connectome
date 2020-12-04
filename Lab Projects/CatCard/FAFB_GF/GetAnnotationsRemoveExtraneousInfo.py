'''
Emily Tenshaw & Jason Polsky
CAT-Card
Updated 12/1/2020

This file connects to FAFB and pulls skeleton nodes of input neurons.
Used for GF analysis.
Unlikely to need to run any of these individually.
'''

import config
import requests
import json
import GetLookUpTable as GLT

token = config.token
auth = config.CatmaidApiTokenAuth(token)
project_id = config.project_id
object_ids = [134]
created_by = [134]
annotated_with = [863792]


#returns Dictionary containing: SkID, neuron name, type, and neuron ID
def getAllSkeletonInfo(annotation = None):
    if annotation is None:
        annotation = 863792
    elif type(annotation) is not int:
        annotation = int(GLT.getAnnotationID(str(annotation)))
    else:
        annotation = annotation

    response = requests.post(
            'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/query-targets'.format(project_id),
            auth = auth,
            data={'annotated_with': annotation}

    )

    myData = json.loads(response.content.decode('utf-8'))

    relevantDict = {}
    relevantDict = myData['entities']

    return relevantDict


#calls function above and returns list containing only lists (of length 1) of single int, each of which is a SKID
def getListOfSkeletonIDs(annotation = None):

    relevantDict = getAllSkeletonInfo(annotation)
    SkidList = []


    for d in relevantDict:
        if d['type'] == 'neuron':
            SkidList.append(d['skeleton_ids'])

    return SkidList

#calls function above and returns single list of ints, each of which is a skid
def getListOfSkID_int(annotation = None):
    aList = getListOfSkeletonIDs(annotation)
    aNewList = []
    for i in aList:
        aNewList.append(i[0])

    return aNewList


#returns dictionary with each key being a skelID and each value being a list of their annotation IDs
def getDictOfNeuronsWithIDs():

    SkidList = getListOfSkeletonIDs()

    newResponse = requests.post(
            'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/forskeletons'.format(project_id),
            auth = auth,
            data={'skeleton_ids': SkidList}
    )
    #print(type(newResponse))
    #print(newResponse.text)

    thisData = json.loads(newResponse.content.decode('utf-8'))

    Annotations4ThisNeuron = {}
    myNeurons = {}
    myNeurons = thisData['skeletons']
    tempList = []

    #print(myNeurons)

    for i in myNeurons:
        for d in myNeurons[i]:
            tempList.append(d['id'])
        Annotations4ThisNeuron[i] = tempList
        tempList = []


    return Annotations4ThisNeuron


def getName(SKID):
    a = GLT.setAnnotationLookUpTable(SKID)
    b = str(a[0])

    c = GLT.getLookUpTableSkID_Name(b)
    myName = c[SKID]
    return myName

# returns dictionary with each key being a skelID and each value being a list of annotation Strings
def convertID2String():
    myDict = getDictOfNeuronsWithIDs()
    AnnotationLookUpTable = GLT.getLookUpTable()
    myNewDict = {}
    ListOfAnnotations = []
    for i in myDict:
        for e in myDict[i]:
            ListOfAnnotations.append(AnnotationLookUpTable[e])
            # e = AnnotationLookUpTable[e]
            # print(e)
        myNewDict[i] = ListOfAnnotations
        ListOfAnnotations = []
    return myNewDict

def getMyAnnotations():
    myNeuronswithAnnotations = convertID2String()
    return myNeuronswithAnnotations

'''
meta annotations
'''

# used in get annotations remove extraneous info
# connects to FAFB and gets meta annotations if exist
def getMetaAnnotationList(mySet):
    '''

    :param mySet: obj of type GFIN_Set
    :return: myMetaAnnotationList: list of annotationsIds for all of GF1 input neuron meta annotations
    '''
    user = 134
    #annotation = 'testMetaAnnotation'
    mySkeletons = []
    for i in mySet:
        mySkeletons.append(i.skeletonID)
    myMetaAnnotationList = []

    metaTest = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/skeleton/annotationlist'.format(project_id),
        auth=auth,
        data={'metaannotations': 1, 'skeleton_ids[]': mySkeletons}
    )

    metaTestResults = json.loads(metaTest.content)

    myInfo= metaTestResults['metaannotations']

    #myMetaAnnotationList is a list of annotation id for all meta annotations
    for i in myInfo:
        for item in myInfo[i]['annotations']:
            myMetaAnnotationList.append(item['id'])
    return myMetaAnnotationList


# annotation should be a string meta annotation
# used in custom GF neuron class
def queryByMetaAnnotation(annotation):
    #annotation = 'testMetaAnnotation'
    myAnnotationList = []
    if type(annotation) is not int:
        annotation = int(GLT.getAnnotationID(str(annotation)))
    else:
        annotation = annotation

    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/query-targets'.format(project_id),
        auth=auth,
        data={'annotated_with': annotation, 'with_annotations': True, 'types': ['neuron', 'annotation']}

    )

    myData = json.loads(response.content.decode('utf-8'))

    myInfo = myData['entities']

    #myInfo is a list of dicts with annotation id, name, and type as key, value pairs - this loop returns list of annotation names
    for i in myInfo:
        myAnnotationList.append(i['name'])

    return myAnnotationList

