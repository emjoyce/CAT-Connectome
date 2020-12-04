"""
Emily Tenshaw
CAT-Card
12/1/2020

Functions to try and build bounding boxes for each GF branch.
There is an issue where synapses are located on multiple branches.
WORK IN PROGRESS
Query hasn't been updated since neuprint updates.
*** MAKE SURE that the client is CORRECT for data wanting pulled. The hemibrain websites update frequently.
"""


import neuprint as neu
from collections import defaultdict

#client = neu.Client('emdata1.int.janelia.org:13000', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtaWx5dGVuc2hhd0BnbWFpbC5jb20iLCJsZXZlbCI6InJlYWR3cml0ZSIsImltYWdlLXVybCI6Imh0dHBzOi8vbGg0Lmdvb2dsZXVzZXJjb250ZW50LmNvbS8tdmhYaGxhYjFxcFEvQUFBQUFBQUFBQUkvQUFBQUFBQUFBQUEvQUNIaTNyZWcwN21uZHVkQ2RpWVRkeFJGWGdONmlnMENOZy9waG90by5qcGc_c3o9NTA_c3o9NTAiLCJleHAiOjE3NTc5NzcyMTR9.uoMuun4AQ82VI7qUjO7f0G5CKOUX4KqAIF89CkQN4do')
client = neu.Client('https://neuprint.janelia.org', dataset = 'hemibrain:v1.1', token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtaWx5dGVuc2hhd0BnbWFpbC5jb20iLCJsZXZlbCI6InJlYWR3cml0ZSIsImltYWdlLXVybCI6Imh0dHBzOi8vbGg0Lmdvb2dsZXVzZXJjb250ZW50LmNvbS8tdmhYaGxhYjFxcFEvQUFBQUFBQUFBQUkvQUFBQUFBQUFBQUEvQUNIaTNyZWcwN21uZHVkQ2RpWVRkeFJGWGdONmlnMENOZy9waG90by5qcGc_c3o9NTA_c3o9NTAiLCJleHAiOjE3NTc5NzcyMTR9.uoMuun4AQ82VI7qUjO7f0G5CKOUX4KqAIF89CkQN4do')

#needs to be tweaked a bit so that synapses are not repeated - xyz coords need edited
'''
Example script from library
takes upstream neurons that synapse onto target in the bounding box identified by coordinates

WITH [975518615] AS TARGETS
MATCH (n:`hemibrain-Neuron`)-[:Contains]->(:SynapseSet)-[Contains]->(s:`hemibrain-PostSyn`)<-[:SynapsesTo]-(:`hemibrain-PreSyn`)<-[:Contains]-(:SynapseSet)<-[:Contains]-(m:`hemibrain-Neuron`)
WHERE n.bodyId IN TARGETS AND s.location.x >= 10614 AND s.location.x <= 18066
AND s.location.y >= 15685 AND s.location.y <= 21315
AND s.location.z >= 11845 AND s.location.z<= 19405
RETURN DISTINCT m.bodyId ORDER BY m.bodyId DESC

'''

#Medial Branch
'''
(15731, 20757, 28912)
15951, 19136, 22816
check
'''
def medialQuery():
    medialQuery = ('WITH [2307027729] AS TARGETS'
    ' MATCH (n:`hemibrain-Neuron`)-[:Contains]->(:SynapseSet)-[Contains]->(s:`hemibrain-PostSyn`)<-[:SynapsesTo]-(p:`hemibrain-PreSyn`)<-[:Contains]-(:SynapseSet)<-[:Contains]-(m:`hemibrain-Neuron`)'
    ' WHERE n.bodyId IN TARGETS AND s.location.x > 15710' 
    #' AND s.location.y < 25824'
    ' AND s.location.z <= 25824'
    ' RETURN DISTINCT m.bodyId, s.location.x AS X, s.location.y AS Y, s.location.z AS Z ORDER BY m.bodyId DESC')

    medialBranch = client.fetch_custom(medialQuery)
    return medialBranch

# Lateral Branch
'''
done
(14874, 20854, 24576)
(12452, 24712, 30416)
(14260, 18279, 26672)
(14341, 23670, 30720)
(14874, 20850, 24576)
'''
def lateralQuery():
    lateralQuery = ('WITH [2307027729] AS TARGETS'
                    ' MATCH (n:`hemibrain-Neuron`)-[:Contains]->(:SynapseSet)-[Contains]->(s:`hemibrain-PostSyn`)<-[:SynapsesTo]-(p:`hemibrain-PreSyn`)<-[:Contains]-(:SynapseSet)<-[:Contains]-(m:`hemibrain-Neuron`)'
                    ' WHERE n.bodyId IN TARGETS AND s.location.x <= 15710'
                    #' AND s.location.y >= 18297 AND s.location.y <= 24712'
                    ' AND s.location.z > 24576 AND s.location.z < 30720'
                    ' RETURN DISTINCT m.bodyId, s.location.x AS X, s.location.y AS Y, s.location.z AS Z ORDER BY m.bodyId DESC')

    lateralBranch = client.fetch_custom(lateralQuery)
    return lateralBranch

# Soma Tract
'''
done
(15032, 20883, 24608)
(10819, 10900, 18960)
(14874, 20854, 24576)
'''
def somaQuery():
    somaQuery = ('WITH [2307027729] AS TARGETS'
                 ' MATCH (n:`hemibrain-Neuron`)-[:Contains]->(:SynapseSet)-[Contains]->(s:`hemibrain-PostSyn`)<-[:SynapsesTo]-(p:`hemibrain-PreSyn`)<-[:Contains]-(:SynapseSet)<-[:Contains]-(m:`hemibrain-Neuron`)'
                 ' WHERE n.bodyId IN TARGETS AND s.location.x <= 15032'
                # ' AND s.location.y <= 20854'
                 ' AND s.location.z<= 24676'
                 ' RETURN DISTINCT m.bodyId, s.location.x AS X, s.location.y AS Y, s.location.z AS Z ORDER BY m.bodyId DESC')

    somaBranch = client.fetch_custom(somaQuery)
    return somaBranch

# Descending Tract
'''
done
(15984, 20609, 27392)
(16164, 20760, 28944)
(22365, 13017, 33328)
'''
def descendingQuery():
    descendingQuery = ('WITH [2307027729] AS TARGETS'
                       ' MATCH (n:`hemibrain-Neuron`)-[:Contains]->(:SynapseSet)-[Contains]->(s:`hemibrain-PostSyn`)<-[:SynapsesTo]-(p:`hemibrain-PreSyn`)<-[:Contains]-(:SynapseSet)<-[:Contains]-(m:`hemibrain-Neuron`)'
                       ' WHERE n.bodyId IN TARGETS AND s.location.x > 15710'
                       #' AND s.location.y <= 20760'
                       ' AND s.location.z > 25824'
                       ' RETURN DISTINCT m.bodyId, s.location.x AS X, s.location.y AS Y, s.location.z AS Z ORDER BY m.bodyId DESC')

    descendingBranch = client.fetch_custom(descendingQuery)
    return descendingBranch

# Anterior Branch
'''
done
(14345, 23670, 30720)
(14236, 26260, 35232)
(14349, 25680, 34336)
'''
def anteriorQuery():
    anteriorQuery = ('WITH [2307027729] AS TARGETS'
                     ' MATCH (n:`hemibrain-Neuron`)-[:Contains]->(:SynapseSet)-[Contains]->(s:`hemibrain-PostSyn`)<-[:SynapsesTo]-(p:`hemibrain-PreSyn`)<-[:Contains]-(:SynapseSet)<-[:Contains]-(m:`hemibrain-Neuron`)'
                     ' WHERE n.bodyId IN TARGETS'
                     #' AND s.location.x >= 15916 AND s.location.x <= 21847'
                     #' AND s.location.y >= 23670'
                     ' AND s.location.z >= 30720'
                     ' RETURN DISTINCT m.bodyId, s.location.x AS X, s.location.y AS Y, s.location.z AS Z ORDER BY m.bodyId DESC')

    anteriorBranch = client.fetch_custom(anteriorQuery)
    return anteriorBranch


def makeBranchDict(branch):
    tempDict = branch.to_dict('record')
    synapseDict = defaultdict(list)
    for dict in tempDict:
        bodyId = dict['m.bodyId']
        synapseDict[bodyId].append(dict)
    branchDict = defaultdict(list)
    for k, v in synapseDict.items():
        for coord in v:
            x = coord['X']
            y = coord['Y']
            z = coord['Z']
            xyz = '(' + str(x) + ',' + str(y) + ',' + str(z) + ')'
            branchDict[k].append(xyz)
    return branchDict

#returns a dictionary of synapses by bodyId
def getSynByBranch(branch):
    if branch is 'medial':
        medialBranch = medialQuery()
        medialDict = makeBranchDict(medialBranch)
        return medialDict
    if branch is 'lateral':
        lateralBranch = lateralQuery()
        lateralDict = makeBranchDict(lateralBranch)
        return lateralDict
    if branch is 'soma':
        somaBranch = somaQuery()
        somaDict = makeBranchDict(somaBranch)
        return somaDict
    if branch is 'descending':
        descendingBranch = descendingQuery()
        descendingDict = makeBranchDict(descendingBranch)
        return descendingDict
    if branch is 'anterior':
        anteriorBranch = anteriorQuery()
        anteriorDict = makeBranchDict(anteriorBranch)
        return anteriorDict



def neuronSynapseLocation(neuron):
    bodyId = str(neuron.bodyId)
    descendingQuery = ('WITH [2307027729] AS TARGETS'
                       ' MATCH (n:`hemibrain-Neuron`)-[:Contains]->(:SynapseSet)-[Contains]->(s:`hemibrain-PostSyn`)<-[:SynapsesTo]-(p:`hemibrain-PreSyn`)<-[:Contains]-(:SynapseSet)<-[:Contains]-(m:`hemibrain-Neuron`)'
                       ' WHERE n.bodyId IN TARGETS AND m.bodyId = '+ bodyId + ' AND s.location.x > 15710'
                       ' AND s.location.z > 27392'
                       ' RETURN DISTINCT m.bodyId, s.location.x AS X, s.location.y AS Y, s.location.z AS Z')
    descendingBranch = client.fetch_custom(descendingQuery)
    anteriorQuery = ('WITH [2307027729] AS TARGETS'
                     ' MATCH (n:`hemibrain-Neuron`)-[:Contains]->(:SynapseSet)-[Contains]->(s:`hemibrain-PostSyn`)<-[:SynapsesTo]-(p:`hemibrain-PreSyn`)<-[:Contains]-(:SynapseSet)<-[:Contains]-(m:`hemibrain-Neuron`)'
                       ' WHERE n.bodyId IN TARGETS AND m.bodyId = '+ bodyId +' AND s.location.z >= 30720'
                     ' RETURN DISTINCT m.bodyId, s.location.x AS X, s.location.y AS Y, s.location.z AS Z')
    anteriorBranch = client.fetch_custom(anteriorQuery)
    somaQuery = ('WITH [2307027729] AS TARGETS'
                 ' MATCH (n:`hemibrain-Neuron`)-[:Contains]->(:SynapseSet)-[Contains]->(s:`hemibrain-PostSyn`)<-[:SynapsesTo]-(p:`hemibrain-PreSyn`)<-[:Contains]-(:SynapseSet)<-[:Contains]-(m:`hemibrain-Neuron`)'
                ' WHERE n.bodyId IN TARGETS AND m.bodyId = '+ bodyId + ' AND s.location.x <= 15032'
                 ' AND s.location.z<= 24676'
                 ' RETURN DISTINCT m.bodyId, s.location.x AS X, s.location.y AS Y, s.location.z AS Z')
    somaBranch = client.fetch_custom(somaQuery)
    lateralQuery = ('WITH [2307027729] AS TARGETS'
                    ' MATCH (n:`hemibrain-Neuron`)-[:Contains]->(:SynapseSet)-[Contains]->(s:`hemibrain-PostSyn`)<-[:SynapsesTo]-(p:`hemibrain-PreSyn`)<-[:Contains]-(:SynapseSet)<-[:Contains]-(m:`hemibrain-Neuron`)'
                    ' WHERE n.bodyId IN TARGETS AND m.bodyId = '+ bodyId + ' AND s.location.x <= 15710'
                    ' AND s.location.z > 24576 AND s.location.z< 30720'
                    ' RETURN DISTINCT m.bodyId, s.location.x AS X, s.location.y AS Y, s.location.z AS Z')
    lateralBranch = client.fetch_custom(lateralQuery)
    medialQuery = ('WITH [2307027729] AS TARGETS'
                   ' MATCH (n:`hemibrain-Neuron`)-[:Contains]->(:SynapseSet)-[Contains]->(s:`hemibrain-PostSyn`)<-[:SynapsesTo]-(p:`hemibrain-PreSyn`)<-[:Contains]-(:SynapseSet)<-[:Contains]-(m:`hemibrain-Neuron`)'
                   ' WHERE n.bodyId IN TARGETS AND m.bodyId = '+ bodyId + ' AND s.location.x > 15710'
                   ' AND s.location.z <= 25824'
                   ' RETURN DISTINCT m.bodyId, s.location.x AS X, s.location.y AS Y, s.location.z AS Z')
    medialBranch = client.fetch_custom(medialQuery)
    if not anteriorBranch.empty:
        neuron.annotations.append('Input to GF1 Anterior')
    if not medialBranch.empty:
        neuron.annotations.append('Input to GF1 Medial')
    if not lateralBranch.empty:
        neuron.annotations.append('Input to GF1 Lateral')
    if not somaBranch.empty:
        neuron.annotations.append('Input to GF1 Soma')
    if not descendingBranch.empty:
        neuron.annotations.append('Input to GF1 Descending')

    synDict = {'medial': medialBranch, 'lateral': lateralBranch, 'descending': descendingBranch, 'soma': somaBranch,
               'anterior': anteriorBranch}

    return synDict