"""
Emily Tenshaw
CAT-Card
12/2/2020

This file looks at the SKID of neurons in autoseg and checks to see if they are in V14 of FAFB.
"""

import DnAutosegClass
import DnAutosegClassSet
import config
import requests
import json
import NeuronObjectData
import re
token = config.token
auth = config.CatmaidApiTokenAuth(token)

project_id = config.project_id

#run after pulling neurons of interest
#compares SKIDs in autoseg to V14
def checkV14SKID(neuronSet):
    skids = []
    v14skids = []
    for i in neuronSet:
        if i not in skids:
            skids.append(i.skeletonID)
    for skid in skids:
        response = requests.get(
            'https://neuropil.janelia.org/tracing/fafb/v14/{}/skeletons/{}/root'.format(project_id, skid),
            auth=auth  # ,
        )
        if response.status_code == 200:
            v14skids.append(skid)

    for i in neuronSet:
        if i.skeletonID in v14skids:
            i.existV14 = "True"

    return
