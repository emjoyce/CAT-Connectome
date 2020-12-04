'''
Emily Tenshaw & Jason Polsky
CAT-Card
Updated 12/1/2020


This file contains functions that help to pull skeleton nodes of input neurons.
Unlikely to need any of these functions directly
'''


import requests
import json
import config

token = config.token
auth = config.CatmaidApiTokenAuth(token)
project_id = config.project_id

'''
Used directly in getSkeletonNodesNew
'''
# connects to FAFB - helper to pull skeleton nodes
def getVolumeIDs():
    response = requests.get(
            'https://neuropil.janelia.org/tracing/fafb/v14/1/volumes/'.format(project_id), 
            auth = auth
    )

    myData = json.loads(response.content)

    volumeDict = {}
    
    for i in myData:
        currentName = i['name']
        currentID = i['id']
        volumeDict[currentID] = currentName
    return volumeDict

# used in skeleton nodes file
# returns list of strings of volume ids
def getVolumeIDintList():
    myVols = getVolumeIDs()
    volList = list(myVols.values())
    return volList



'''
Functions below help functions above run
'''
# helper function
# return dictionary containing only ITO nomenclature neuropils (with 1 of each neuropil)
def filterVolumes():
    myVols = getVolumeIDs()
    myVols = neuropilLookUp(myVols)
    filteredVols = {}
    for i in myVols:
        #if ('_R' in i or '_L' in i) and (len(i) <= 10) and ('v14' not in i):
        if ('_R' in i or '_L' in i or len(i)<5) and (len(i)<=10) and not('v14' in i):
            filteredVols[i] = myVols[i]
    return filteredVols

# helper function
# reverse above dictionary, so as to have a means to look up neuropil name based upon volume id
def neuropilLookUp(myDict = None):
    if myDict is None:
        myDict = filterVolumes()
    myLookUp = {v: k for k, v in myDict.items()}
    return myLookUp

# helper function
# returns list of int of Volume ids
def getFilteredVolumeIDList():
    myVols = filterVolumes()
    volList = list(myVols.values())
    return volList

