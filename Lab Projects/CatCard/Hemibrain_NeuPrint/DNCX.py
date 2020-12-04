"""
Emily Tenshaw
CAT-Card
12/1/2020

**Always check which server is connected and up to date
Queries used to pull DN data relevant to the CX
Queries likely not updated -- easier ways to pull CX data now?
"""

import neuprint as neu

# 13000 server
# client = neu.Client('emdata1.int.janelia.org:13000/?dataset=hemibrain', token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtaWx5dGVuc2hhd0BnbWFpbC5jb20iLCJsZXZlbCI6InJlYWR3cml0ZSIsImltYWdlLXVybCI6Imh0dHBzOi8vbGg0Lmdvb2dsZXVzZXJjb250ZW50LmNvbS8tdmhYaGxhYjFxcFEvQUFBQUFBQUFBQUkvQUFBQUFBQUFBQUEvQUNIaTNyZWcwN21uZHVkQ2RpWVRkeFJGWGdONmlnMENOZy9waG90by5qcGc_c3o9NTA_c3o9NTAiLCJleHAiOjE3NjM3NzA2MTR9.xNL4c8vg8tN4KKrLUiHEgy_9Wlf4tDoGCXEKlLs8lLU')
# test server
client = neu.Client('neuprint-test.janelia.org', dataset='hemibrain',
                    token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtaWx5dGVuc2hhd0BnbWFpbC5jb20iLCJsZXZlbCI6InJlYWR3cml0ZSIsImltYWdlLXVybCI6Imh0dHBzOi8vbGg0Lmdvb2dsZXVzZXJjb250ZW50LmNvbS8tdmhYaGxhYjFxcFEvQUFBQUFBQUFBQUkvQUFBQUFBQUFBQUEvQUtGMDVuRFRUOHBhUHFCT3dMNk5nblZHVENIR2xGWEp0QS9waG90by5qcGc_c3o9NTA_c3o9NTAiLCJleHAiOjE3NjQ5ODIyODh9.UjUHbKZQpReYOShvtKMzZWxJE-saJ4FWN6iD9hAcZaQ')


# pulls ROI info for a specific DN type
# used for cytoscape graphs
def dn_roi_info_oh(DNType):
    DNType = str(DNType)
    DNs = []
    if DNType == "DNa":
        DNs = [1170939344, 1140245595, 1139909038, 1262014782, 1262356170, 1627618361, 1074782432, 1192848260,
               1038420643, 707116522, 1222928995]
    if DNType == "DNb":
        DNs = [1904885509, 1477239390, 5813022608, 1963869286, 1037393225, 944974703, 1406966879, 1715999506,
               5813068635, 5813078116]
    if DNType == "DNd":
        DNs = [5813012529, 5813020864, 5813026404, 5813077405]

    query = (
            'WITH ' + str(DNs) + ' AS DNS'
                                 ' UNWIND DNS as DN'
                                 ' MATCH (input:`hemibrain_Neuron`)-[w1:ConnectsTo]->(Target:`hemibrain_Neuron`)'
                                 ' WHERE Target.bodyId = DN'
                                 ' RETURN input.bodyId, input.type, input.instance, input.status, input.pre AS presyn, w1.weight as '
                                 'input_weight, '
                                 'apoc.convert.fromJsonMap(w1.roiInfo)["LAL(R)"].pre AS LALR,'
                                 'apoc.convert.fromJsonMap(w1.roiInfo)["LAL(L)"].pre AS LALL,'
                                 'apoc.convert.fromJsonMap(w1.roiInfo)["IPS(R)"].pre AS IPS,'
                                 'apoc.convert.fromJsonMap(w1.roiInfo)["SPS(R)"].pre AS SPSR,'
                                 'apoc.convert.fromJsonMap(w1.roiInfo)["SPS(L)"].pre AS SPSL,'
                                 'apoc.convert.fromJsonMap(w1.roiInfo)["WED(R)"].pre AS WED,'
                                 'w1.roiInfo, Target.bodyId, Target.type, Target.instance, Target.status, Target.post AS postsyn'
    )

    queryResults = client.fetch_custom(query)

    if DNType == "DNp":
        DNs = [2307027729, 5813024015, 1565846637, 1405231475, 1466998977, 5813023322, 1100404581, 1226887763,
               5813026936,
               5813020512, 5813095193, 1815895547, 1684204798, 1498383456, 1498033920, 1507933560, 5813068840,
               1344249576, 981000564,
               821201495, 1100404634, 1072063538, 1043117106, 1135837629, 1006984280, 5813050455, 984030630,
               5813078134, 1405300548, 1344253853, 1405300499, 1436330964, 1229107423, 1044218225, 5813047199,
               5813048234,
               512851433, 1281324958, 887195902, 1745333830, 1197234751, 1436703256, 1467357251, 1467694006, 451689001,
               1039335355]
        for i in DNs:
            query2 = (
                    ' MATCH (input:`hemibrain_Neuron`)-[w1:ConnectsTo]->(Target:`hemibrain_Neuron`)'
                    ' WHERE Target.bodyId = ' + str(i) + ' '
                                                         ' RETURN input.bodyId, input.type, input.instance, input.status, input.pre AS presyn, w1.weight as '
                                                         'input_weight, '
                                                         'apoc.convert.fromJsonMap(w1.roiInfo)["LAL(R)"].pre AS LALR,'
                                                         'apoc.convert.fromJsonMap(w1.roiInfo)["LAL(L)"].pre AS LALL,'
                                                         'apoc.convert.fromJsonMap(w1.roiInfo)["IPS(R)"].pre AS IPS,'
                                                         'apoc.convert.fromJsonMap(w1.roiInfo)["SPS(R)"].pre AS SPSR,'
                                                         'apoc.convert.fromJsonMap(w1.roiInfo)["SPS(L)"].pre AS SPSL,'
                                                         'apoc.convert.fromJsonMap(w1.roiInfo)["WED(R)"].pre AS WED,'
                                                         'w1.roiInfo, Target.bodyId, Target.type, Target.instance, Target.status, Target.post AS postsyn')

            queryResults1 = client.fetch_custom(query2)
            queryResults = queryResults.append(queryResults1)
    queryResults2 = queryResults.reset_index(drop=True)
    return queryResults2


# removes DNs that don't have any CX data or are only connected to orhpans
def remove_irrelevant(queryResults):
    queryResults = queryResults.fillna({'LALR': 0,
                                        'LALL': 0, 'IPS': 0, 'SPSR': 0, 'SPSL': 0, 'WED': 0})

    cols = ['LALR', 'LALL', 'IPS', 'SPSR', 'SPSL', 'WED']
    queryResults2 = queryResults[(queryResults[cols] != 0).any(axis=1)]

    queryResults3 = queryResults2.drop(queryResults2.index[queryResults2['input.status'] == 'Assign'])
    queryResults4 = queryResults3.drop(queryResults3.index[queryResults3['input.status'] == 'Orphan'])
    queryResults5 = queryResults4.drop(queryResults4.index[queryResults4['input.status'] == 'Unimportant'])
    queryResults6 = queryResults5.reset_index()
    return queryResults6
