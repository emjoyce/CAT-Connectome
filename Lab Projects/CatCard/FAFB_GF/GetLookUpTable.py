'''
Emily Tenshaw & Jason Polsky
CAT-Card
Updated 12/1/2020

Pulls annotation data for GF Input neurons
Unsure why needed - mostly written by Jason
'''

import config
import requests
import json
import GetAnnotationsRemoveExtraneousInfo as GARI

token = config.token
auth = config.CatmaidApiTokenAuth(token)

project_id = config.project_id
object_ids = [134]
created_by = [134]
annotated_with = [863792]

headers = config.CatmaidApiTokenAuth(token)


# returns dictionary containing a lookup table with int(annotation id) as key and annotation string/name as value
def getLookUpTable():
    allAnnotations = requests.get(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/'.format(project_id),
        auth=auth
    )

    someData = json.loads(allAnnotations.content.decode('utf-8'))

    # print(someData)
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


# used in custom GF neuron class and new set
def getLookUpTableSkID_Name(annotation = None):
    relevantDict = GARI.getAllSkeletonInfo(annotation)
    SkIDLookUpNeuronName = {}
    #returns dictionary containing SkID : neuron name pairs
    for d in relevantDict:

        if d["type"] == 'neuron':
            SkIDLookUpNeuronName[((d['skeleton_ids'])[0])] = d['name']

    return SkIDLookUpNeuronName


# used in custom GF neuron class
def setAnnotationLookUpTable(SKID):

    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/forskeletons'.format(project_id),
        auth = auth,
        data={'skeleton_ids[0]': SKID}
    )
    myData = json.loads(response.content)
    myAnnotations = myData['annotations']


    a = []
    for i in myAnnotations:
        a.append(myAnnotations[i])
    return a