'''
Emily Tenshaw & Jason Polsky
CAT-Card
Updated 12/1/2020

This file connects to FAFB and pulls connector data for GF input sets.
'''
import config
import requests
import json

token = config.token
auth = config.CatmaidApiTokenAuth(token)
project_id = config.project_id


# Gets all GF1 synaptic partners
# used in custom GF neuron class
def getGF1Partners(skeleton_id=4947529):
    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/skeletons/connectivity'.format(project_id),
        auth=auth,
        data={'source_skeleton_ids[]': [ skeleton_id ], 'boolean_op': "OR"}

    )

    myNeurons = json.loads(response.content.decode('utf-8'))

    return myNeurons

# returns a dictionary of SkelIds mapped to synapse count with GF1; defaults to GF1, but can be set to other neurons
# as well
# used in custom GF neuron class
def removeExtra(skeleton_id='4947529'):
    myNeurons = getGF1Partners(int(skeleton_id))
    IncomingPartners = {}
    IncomingPartners = myNeurons['incoming']
    AllSynapses = {}

    # removes all seed nodes
    for i in IncomingPartners:
        d = IncomingPartners[ i ]

        # if d['num_nodes'] > 4:
        e = d[ 'skids' ]
        tempList = e[ skeleton_id ]
        AllSynapses[ i ] = tempList[ 4 ]
        tempList = [ ]

    return AllSynapses

