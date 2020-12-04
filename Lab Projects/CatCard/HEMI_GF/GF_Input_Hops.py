"""
Emily Tenshaw
CAT-Card
12/1/2020

Hop queries for GF hemibrian inputs
one hop = input -> GF input -> GF
two hop = input1 -> input2 -> GF input -> GF

These were used to make various cytoscape graphs for Gwyneth.
*** MAKE SURE that the client is CORRECT for data wanting pulled. The hemibrain websites update frequently.
Query hasn't been changed since neuprint update
"""

import neuprint as neu

#client = neu.Client('emdata1.int.janelia.org:13000', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtaWx5dGVuc2hhd0BnbWFpbC5jb20iLCJsZXZlbCI6InJlYWR3cml0ZSIsImltYWdlLXVybCI6Imh0dHBzOi8vbGg0Lmdvb2dsZXVzZXJjb250ZW50LmNvbS8tdmhYaGxhYjFxcFEvQUFBQUFBQUFBQUkvQUFBQUFBQUFBQUEvQUNIaTNyZWcwN21uZHVkQ2RpWVRkeFJGWGdONmlnMENOZy9waG90by5qcGc_c3o9NTA_c3o9NTAiLCJleHAiOjE3NTc5NzcyMTR9.uoMuun4AQ82VI7qUjO7f0G5CKOUX4KqAIF89CkQN4do')
#client = neu.Client('neuprint-test.janelia.org', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtaWx5dGVuc2hhd0BnbWFpbC5jb20iLCJsZXZlbCI6InJlYWR3cml0ZSIsImltYWdlLXVybCI6Imh0dHBzOi8vbGg0Lmdvb2dsZXVzZXJjb250ZW50LmNvbS8tdmhYaGxhYjFxcFEvQUFBQUFBQUFBQUkvQUFBQUFBQUFBQUEvQUNIaTNyZWcwN21uZHVkQ2RpWVRkeFJGWGdONmlnMENOZy9waG90by5qcGc_c3o9NTA_c3o9NTAiLCJleHAiOjE3NTc5OTE1NDd9.gJYc4liCa--E41xZMsJjVYKT69Ugldrk29UmMwAl5G0')
client = neu.Client('https://neuprint.janelia.org', dataset = 'hemibrain:v1.1', token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtaWx5dGVuc2hhd0BnbWFpbC5jb20iLCJsZXZlbCI6InJlYWR3cml0ZSIsImltYWdlLXVybCI6Imh0dHBzOi8vbGg0Lmdvb2dsZXVzZXJjb250ZW50LmNvbS8tdmhYaGxhYjFxcFEvQUFBQUFBQUFBQUkvQUFBQUFBQUFBQUEvQUNIaTNyZWcwN21uZHVkQ2RpWVRkeFJGWGdONmlnMENOZy9waG90by5qcGc_c3o9NTA_c3o9NTAiLCJleHAiOjE3NTc5NzcyMTR9.uoMuun4AQ82VI7qUjO7f0G5CKOUX4KqAIF89CkQN4do')


#query that gets connect info specific to a given ROI
def ROITwoHop(roi):
    query = (
            'MATCH (input:Neuron)<-[:From]-(c:ConnectionSet)-[:To]->(interneuron:Neuron)-[w2:ConnectsTo]->(GFInput:Neuron)-[w3:ConnectsTo]->(GF:Neuron)'
            ' WHERE GF.bodyId = 2307027729 AND NOT apoc.convert.fromJsonMap(c.roiInfo)["' + roi + '"] IS NULL'
            ' RETURN input.name, input.bodyId, input.type, input.status, input.roiInfo, apoc.convert.fromJsonMap(c.roiInfo)["' + roi + '"].pre as PRE, apoc.convert.fromJsonMap(c.roiInfo)["' + roi + '"].post as POST, '
            ' c.roiInfo, interneuron.name, interneuron.bodyId, interneuron.type, interneuron.status, interneuron.roiInfo, '
            'w2.weight as interneuron_weight, GFInput.name, GFInput.bodyId, GFInput.type, GFInput.status, w3.weight as GF_weight, GF.name, GF.bodyId, GF.type, GF.status'
    )
    queryResults = client.fetch_custom(query)
    file = roi + "TwoHop.csv"
    queryResults.to_csv(file, sep='\t', index=False)
    return queryResults


#looks at GF Input to GF Input connections
def GFInputConnect():
    query = (
    ' MATCH (GF:Neuron)<-[w1:ConnectsTo]-(input:Neuron)-[w2:ConnectsTo]->(GFInput:Neuron)-[w3:ConnectsTo]->(GF:Neuron)'
    ' WHERE GF.bodyId = 2307027729'
    ' RETURN input.bodyId, input.name, input.type, input.status, w1.weight as input_To_GF, w2.weight AS input_To_GFInput, '
    'GFInput.bodyId, GFInput.name, GFInput.type, GFInput.status, w3.weight AS GFIN_To_GF, GF.bodyId '
    )
    queryResults = client.fetch_custom(query)
    file = "testing.csv"
    queryResults.to_csv(file, sep='\t', index=False)
    return queryResults


#-----------------------------------------------------------------------------------------------------------------------


#CSVM2

#has not been updated
#query that gets connect info NOT specific to a given ROI
def allROIInputs():
    query = (
    'MATCH (input:Neuron)-[w:ConnectsTo]->(interneuron:Neuron)-[w2:ConnectsTo]->(GFInput:Neuron)-[w3:ConnectsTo]->(GF:Neuron)'
    ' WHERE GF.bodyId = 2307027729 AND (input.MB OR input.AB OR input.PB OR input.NO OR input.FB OR input.EB)'
    ' RETURN input.name, input.bodyId, input.type, w.weight as input_weight, input.roiInfo, interneuron.name, interneuron.bodyId, interneuron.type,'
    ' w2.weight as interneuron_weight, interneuron.roiInfo, GFInput.name, GFInput.bodyId, GFInput.type, w3.weight as GFInput_weight'
    )
    queryResults = client.fetch_custom(query)
    file = "allROIInputs.csv"
    queryResults.to_csv(file, sep='\t', index=False)
    return queryResults


#has not been updated
def interneuronQuery(typeName):
    query = (
    ' MATCH (input:Neuron)-[w:ConnectsTo]->(interneuron:Neuron)-[w2:ConnectsTo]->(GFInput:Neuron)-[w3:ConnectsTo]->(GF:Neuron)'
    ' WHERE GF.bodyId = 2307027729 AND (input.type CONTAINS "'+str(typeName)+'" OR interneuron.type CONTAINS "'+str(typeName)+'")'
    ' RETURN input.name, input.bodyId, input.type, w.weight as input_weight, interneuron.name, interneuron.bodyId, interneuron.type,'
    ' w2.weight as interneuron_weight, GFInput.name, GFInput.bodyId, GFInput.type, w3.weight as GFInput_weight'
    )
    queryResults = client.fetch_custom(query)
    file = str(typeName) + "_Query.csv"
    queryResults.to_csv(file, sep='\t', index=False)
    return queryResults




#----------------------------------------------------------------------------------------------------------------------

#testing -- not yet updated


#1072059176, 792326206, 1166186949, 1411737459, 5813021112, 1103102334, 1628973439, 1785511781, 1910328899, 1876993474, 5812980291, 1102412245, 2126296267, 2127219419, 5813068925
def test():
    query = (
        'WITH [1072059176,792326206,1166186949,1411737459,5813021112,1072059176, 792326206, 1166186949, 1411737459, 5813021112, 1103102334, 1628973439, 1785511781, 1910328899, 1876993474, 5812980291, 1102412245, 2126296267, 2127219419, 5813068925] AS TARGETS'
        ' UNWIND TARGETS AS TARGET'
        ' MATCH (interneuron:Neuron)-[w2:ConnectsTo]->(GFInput:Neuron)-[w3:ConnectsTo]->(GF:Neuron)'
        ' WHERE GF.bodyId = 2307027729 AND GFInput.bodyId = TARGET' 
    ' RETURN interneuron.name, interneuron.bodyId, interneuron.type,'
    ' w2.weight as interneuron_weight, GFInput.name, GFInput.bodyId, GFInput.type, w3.weight as GFInput_weight'
    )
    queryResults = client.fetch_custom(query)
    file = "test.csv"
    queryResults.to_csv(file, sep='\t', index=False)
    return queryResults


#one hop queries

#mushroom body
def getMBOneHop():
    query = ('MATCH (input:`Neuron`)<-[:From]-(c:ConnectionSet)-[:To]->(GFInput:`Neuron`)-[w:ConnectsTo]->(GF:`Neuron`)'
            ' WHERE GF.bodyId=2307027729 AND NOT apoc.convert.fromJsonMap(c.roiInfo)["MB (right)"] IS NULL'
            ' RETURN input.name, input.bodyId, input.type, input.pre, input.post, apoc.convert.fromJsonMap(input.roiInfo)["MB (right)"].pre as roi_weight_pre, apoc.convert.fromJsonMap(input.roiInfo)["MB (right)"].post as roi_weight_post,'
             'apoc.convert.fromJsonMap(c.roiInfo)["MB (right)"].pre as PRE, apoc.convert.fromJsonMap(c.roiInfo)["MB (right)"].post as POST, c.roiInfo,'
             ' GFInput.name, GFInput.bodyId, GFInput.type, GFInput.pre, GFInput.post, w.weight AS GF_weight, GF.bodyId, GF.name, GF.type')
    queryResults = client.fetch_custom(query)
    queryResults.to_csv('MB_OneHop.csv', sep='\t', index=False)
    return queryResults


def GFInputConnect():
    query = (
    ' MATCH (GF:Neuron)<-[w1:ConnectsTo]-(input:Neuron)-[w2:ConnectsTo]->(GFInput:Neuron)-[w3:ConnectsTo]->(GF:Neuron)'
    ' WHERE GF.bodyId = 2307027729'
    ' RETURN input.bodyId, input.name, input.type, input.status, w1.weight as input_To_GF, w2.weight AS input_To_GFInput, '
    'GFInput.bodyId, GFInput.name, GFInput.type, GFInput.status, w3.weight AS GFIN_To_GF, GF.bodyId '
    )
    queryResults = client.fetch_custom(query)
    file = "GFInputToInput.csv"
    queryResults.to_csv(file, sep='\t', index=False)
    return queryResults
