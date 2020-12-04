"""
Emily Tenshaw
CAT-Card
12/1/2020


Pulls synapse coordiantes for hemibrain inputs to GF.
*** MAKE SURE that the client is CORRECT for data wanting pulled. The hemibrain websites update frequently.
Query hasn't been changed since neuprint update
"""
import neuprint as neu

client = neu.Client('https://neuprint.janelia.org', dataset = 'hemibrain:v1.1', token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtaWx5dGVuc2hhd0BnbWFpbC5jb20iLCJsZXZlbCI6InJlYWR3cml0ZSIsImltYWdlLXVybCI6Imh0dHBzOi8vbGg0Lmdvb2dsZXVzZXJjb250ZW50LmNvbS8tdmhYaGxhYjFxcFEvQUFBQUFBQUFBQUkvQUFBQUFBQUFBQUEvQUNIaTNyZWcwN21uZHVkQ2RpWVRkeFJGWGdONmlnMENOZy9waG90by5qcGc_c3o9NTA_c3o9NTAiLCJleHAiOjE3NTc5NzcyMTR9.uoMuun4AQ82VI7qUjO7f0G5CKOUX4KqAIF89CkQN4do')

def queryCoordinates(inputSet):
    bodyIDs = []
    for i in inputSet:
        bodyIDs.append(i.bodyId)
    bodyIDs_string = ','.join(str(i) for i in bodyIDs)
    query = ('WITH [' + bodyIDs_string + '] as TARGETS'
             ' MATCH (input:Neuron)-[:Contains]->(:SynapseSet)-[:Contains]->'
             '(:Synapse)-[:SynapsesTo]->(s:Synapse)<-[:Contains]-(:SynapseSet)'
             '<-[:Contains]-(output:Neuron)'
             ' WHERE input.bodyId IN TARGETS AND output.bodyId = 2307027729'
             ' RETURN DISTINCT input.bodyId, s.location.x AS X, s.location.y AS Y, s.location.z AS Z'
             ' ORDER BY s.location.x DESC'
             )

    queryResults = client.fetch_custom(query)
    queryResults.to_csv("C:/Users/etens/Desktop/pyCharmOutputs/HEMI_GF/inputSynapseCoords.csv")
    return queryResults

