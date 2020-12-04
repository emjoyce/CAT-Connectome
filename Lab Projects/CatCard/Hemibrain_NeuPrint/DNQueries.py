"""
Emily Tenshaw
CAT-Card
12/1/2020

**Always check which server is connected and up to date
Queries used to pull DN data relevant to DNs
One main query that is user entry based
Queries likely not updated
"""
import neuprint as neu
import pandas as pd
import HopQueries as HQ

# 13000 server
# client = neu.Client('emdata1.int.janelia.org:13000/?dataset=hemibrain', token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtaWx5dGVuc2hhd0BnbWFpbC5jb20iLCJsZXZlbCI6InJlYWR3cml0ZSIsImltYWdlLXVybCI6Imh0dHBzOi8vbGg0Lmdvb2dsZXVzZXJjb250ZW50LmNvbS8tdmhYaGxhYjFxcFEvQUFBQUFBQUFBQUkvQUFBQUFBQUFBQUEvQUNIaTNyZWcwN21uZHVkQ2RpWVRkeFJGWGdONmlnMENOZy9waG90by5qcGc_c3o9NTA_c3o9NTAiLCJleHAiOjE3NjM3NzA2MTR9.xNL4c8vg8tN4KKrLUiHEgy_9Wlf4tDoGCXEKlLs8lLU')
# test server
client = neu.Client('neuprint-test.janelia.org', dataset='hemibrain',
                    token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtaWx5dGVuc2hhd0BnbWFpbC5jb20iLCJsZXZlbCI6InJlYWR3cml0ZSIsImltYWdlLXVybCI6Imh0dHBzOi8vbGg0Lmdvb2dsZXVzZXJjb250ZW50LmNvbS8tdmhYaGxhYjFxcFEvQUFBQUFBQUFBQUkvQUFBQUFBQUFBQUEvQUtGMDVuRFRUOHBhUHFCT3dMNk5nblZHVENIR2xGWEp0QS9waG90by5qcGc_c3o9NTA_c3o9NTAiLCJleHAiOjE3NjQ5ODIyODh9.UjUHbKZQpReYOShvtKMzZWxJE-saJ4FWN6iD9hAcZaQ')

'''
A user based command to run single hop queries to the GF.
This allows the user to easily grab only the data they want
'''


def DN_ROI_Main():
    print('\nUse the answers in parentheses to answer, otherwise will not run properly'
          '\nExample Circuit: x -> target\n'
          'Runs off a list of targeted DNs'
          'Most important to save is the last file - file with percentages')
    DNType = input('\nEnter the DN Type: (ex: DNa, DNp..)   ')
    DNType = str(DNType)

    print("\nrunning DN one hop query...")
    # original results = queryResults
    queryResults = DN_ROIInfo_OneHop(DNType)
    print('\nRemoving irrelevant data...')
    queryResults2 = removeIrrelevant(queryResults)
    if queryResults2.empty:
        print("\nEmpty data frame, try a different query")
        return
    print1 = input('\nWould you like to save query results? (y/n):   ')
    HQ.toCSV(print1, queryResults2)

    print('finding ROI synapse weight for input body query...')
    # minmax is inputBodies with the PRE/POST changed to roi_connectivity_weight
    queryResults3 = comparePrePost(queryResults2)
    print4 = input('\nquery removes the PRE and POST columns from the input bodies query and changes the '
                   'column to roi_connectivity_weight, returning whichever has the higher value'
                   '\nWould you like to save the updated results? (y/n):   ')
    HQ.toCSV(print4, queryResults3)

    print('\nReorganzing data...')
    queryResults4 = reorgQuery(queryResults3)
    print5 = input('\nReorganizing only rearranges columns.'
                   '\nWould you like to save the reorganized data? (y/n):   ')
    HQ.toCSV(print5, queryResults4)

    print('\nAdding weights...')
    queryResults5 = addWeights(queryResults4)
    print6 = input('\nWould you like to save the added data? (y/n):   ')
    HQ.toCSV(print6, queryResults5)

    print('\nAdding percentage columns...')
    queryResults6 = addPercentageColumns(queryResults5)
    print7 = input('\nWould you like to save the cytoscape file with percentages? (y/n):   ')
    HQ.toCSV(print7, queryResults6)

    return


'''
The following queries can be run by user depending on how many hops needed.

'''


def DN_ThreeHop_Main():
    print('\nUse the answers in parentheses to answer, otherwise will not run properly'
          '\nExample Circuit: x -> y -> z -> target\n'
          'Runs off a list of targeted DNs')
    ROI = input('\nEnter the targeted ROI:   ')
    ROI = str(ROI)
    DNType = input('\nEnter the DN Type: (ex: DNa, DNp..)   ')
    DNType = str(DNType)

    print("\nrunning DN three hop query...")
    # original results = queryResults
    queryResults = Target_DNROI_ThreeHop(ROI, DNType)
    if queryResults.empty:
        print("\nEmpty data frame, try a different query")
        return
    print1 = input('\nWould you like to save query results? (y/n):   ')
    HQ.toCSV(print1, queryResults)

    print('\ngetting input bodies...')
    # original input bodies = inputBodies
    inputBodies = HQ.getInputBodies(queryResults, ROI)
    print2 = input('\nWould you like to save the input body query results? (y/n):   ')
    HQ.toCSV(print2, inputBodies)

    print('\nfinding mismatched bodies...'
          '\nquery removes bodies that are not annotated from original ROI two hop query')
    # queryResults2 is queryResults with mismatched bodies removed
    queryResults2, inputBodies2 = HQ.mismatchedBodies(queryResults, inputBodies)
    print3 = input('\nWould you like to save the mismatched body results? (y/n):   ')
    HQ.toCSV(print3, queryResults2)

    print('finding ROI synapse weight for input body query...')
    # minmax is inputBodies with the PRE/POST changed to roi_connectivity_weight
    minmax = HQ.compareMinMax(inputBodies2)
    print4 = input('\nquery removes the PRE and POST columns from the input bodies query and changes the '
                   'column to roi_connectivity_weight, returning whichever has the higher value'
                   '\nWould you like to save the updated results? (y/n):   ')
    HQ.toCSV(print4, minmax)

    print('\nrunning statistics for threshold values...')
    statistics = HQ.findStatistics(queryResults2, minmax)
    print('\n' + str(statistics))

    HQ.displayOptions(queryResults2, minmax, statistics, ROI)

    return


def DN_TwoHop_Main():
    print('\nUse the answers in parentheses to answer, otherwise will not run properly'
          '\nExample Circuit: x -> y -> target\n'
          'Runs off a list of targeted DNs')
    ROI = input('\nEnter the targeted ROI:   ')
    ROI = str(ROI)
    DNType = input('\nEnter the DN Type: (ex: DNa, DNp..)   ')
    DNType = str(DNType)

    print("\nrunning DN two hop query...")
    # original results = queryResults
    queryResults = Target_DNROI_TwoHop(ROI, DNType)
    if queryResults.empty:
        print("\nEmpty data frame, try a different query")
        return
    print1 = input('\nWould you like to save query results? (y/n):   ')
    HQ.toCSV(print1, queryResults)

    print('finding ROI synapse weight for input body query...')
    # minmax is inputBodies with the PRE/POST changed to roi_connectivity_weight
    queryResults2 = HQ.compareMinMax(queryResults)
    print4 = input('\nquery removes the PRE and POST columns from the input bodies query and changes the '
                   'column to roi_connectivity_weight, returning whichever has the higher value'
                   '\nWould you like to save the updated results? (y/n):   ')
    HQ.toCSV(print4, queryResults2)

    print('\nrunning statistics for threshold values...')
    statistics = HQ.findStatistics2(queryResults2)
    print('\n' + str(statistics))

    HQ.displayOptions2(queryResults2, statistics, ROI)

    return


def DN_OneHop_Main():
    print('\nUse the answers in parentheses to answer, otherwise will not run properly'
          '\nExample Circuit: x -> target\n'
          'Runs off a list of targeted DNs')
    ROI = input('\nEnter the targeted ROI:   ')
    ROI = str(ROI)
    DNType = input('\nEnter the DN Type: (ex: DNa, DNp..)   ')
    DNType = str(DNType)

    print("\nrunning DN one hop query...")
    # original results = queryResults
    queryResults = Target_DNROI_OneHop(ROI, DNType)
    if queryResults.empty:
        print("\nEmpty data frame, try a different query")
        return
    print1 = input('\nWould you like to save query results? (y/n):   ')
    HQ.toCSV(print1, queryResults)

    print('finding ROI synapse weight for input body query...')
    # minmax is inputBodies with the PRE/POST changed to roi_connectivity_weight
    queryResults2 = HQ.compareMinMax(queryResults)
    print4 = input('\nquery removes the PRE and POST columns from the input bodies query and changes the '
                   'column to roi_connectivity_weight, returning whichever has the higher value'
                   '\nWould you like to save the updated results? (y/n):   ')
    HQ.toCSV(print4, queryResults2)

    print('\nrunning statistics for threshold values...')
    statistics = HQ.findStatistics2(queryResults2)
    print('\n' + str(statistics))

    HQ.displayOptions3(queryResults2, statistics, ROI)

    return


'''
work in progress

def loop_Through_AllROI():
    print('\nLong process, loops through all ROIs and does reorg for each.'
          '\nQueries all CX ROIs - core, small, large - and adds them to same file')
    ROIs = ['PB', 'EB', 'FB', 'NO', 'AB(R)', 'ROB', 'RUB', 'GA', 'BU(R)', 'LAL(R)', 'IPS(R)', 'SPS(R)',
            'WED(R)', 'AB(L)', 'BU(L)', 'LAL(L)', 'SPS(L)']
    hops = input('\nEnter the number of hops: (1, 2, or 3)   ')
    if hops == '1':
        DNType = input('\nEnter the DN Type: (ex: DNa, DNp..)   ')
        DNType = str(DNType)
        queryResultsFinal = pd.DataFrame()
        for ROI in ROIs:
            queryResults1 = Target_DNROI_OneHop(ROI, DNType)
            queryResults = queryResults.append(queryResults1)
            if queryResults1.empty:
                print("\nEmpty data frame, moving to next ROI")
            
            else:
                print1 = input('\nWould you like to save query results? (y/n):   ')
                HQ.toCSV(print1, queryResults)
        
                print('finding ROI synapse weight for input body query...')
                # minmax is inputBodies with the PRE/POST changed to roi_connectivity_weight
                queryResults2 = HQ.compareMinMax(queryResults)
                print4 = input('\nquery removes the PRE and POST columns from the input bodies query and changes the '
                               'column to roi_connectivity_weight, returning whichever has the higher value'
                               '\nWould you like to save the updated results? (y/n):   ')
                HQ.toCSV(print4, queryResults2)
        
                print('\nrunning statistics for threshold values...')
                statistics = HQ.findStatistics2(queryResults2)
                print('\n' + str(statistics))
        
                HQ.displayOptions3(queryResults2, statistics, ROI)
            
        return




#works but you cannot use ROI as a node label -- working on it
#prob not the best, returns a ton of data
def DN_All_CX_ROI_Main():
    print('Queries all CX ROIs - core, small, large - and adds them to same file')
    ROIs = ['PB','EB', 'FB', 'NO', 'AB(R)', 'ROB', 'RUB', 'GA', 'BU(R)', 'LAL(R)', 'IPS(R)', 'SPS(R)',
            'WED(R)', 'AB(L)', 'BU(L)', 'LAL(L)', 'SPS(L)']
    hops = input('\nEnter the number of hops: (1, 2, or 3)   ')

    if hops == '1':
        DNType = input('\nEnter the DN Type: (ex: DNa, DNp..)   ')
        DNType = str(DNType)
        queryResults = pd.DataFrame()
        for ROI in ROIs:
            queryResults1 = Target_DNROI_OneHop(ROI, DNType)
            queryResults = queryResults.append(queryResults1)
            if queryResults1.empty:
                print("\nEmpty data frame, moving to next ROI")

        if queryResults.empty:
            print("\nEmpty data frame")
            return

        print1 = input('\nWould you like to save query results? (y/n):   ')
        HQ.toCSV(print1, queryResults)

        print('finding ROI synapse weight for input body query...')
        # minmax is inputBodies with the PRE/POST changed to roi_connectivity_weight
        queryResults2 = HQ.compareMinMax(queryResults)
        print4 = input('\nquery removes the PRE and POST columns from the input bodies query and changes the '
                       'column to roi_connectivity_weight, returning whichever has the higher value'
                       '\nWould you like to save the updated results? (y/n):   ')
        HQ.toCSV(print4, queryResults2)

        print('\nrunning statistics for threshold values...')
        statistics = HQ.findStatistics2(queryResults2)
        print('\n' + str(statistics))

        HQ.displayOptions3(queryResults2, statistics, ROI)

        return

    if hops == '2':
        DNType = input('\nEnter the DN Type: (ex: DNa, DNp..)   ')
        DNType = str(DNType)
        queryResults = pd.DataFrame()
        for ROI in ROIs:
            queryResults1 = Target_DNROI_TwoHop(ROI, DNType)
            queryResults = queryResults.append(queryResults1)
            if queryResults1.empty:
                print("\nEmpty data frame, moving to next ROI")


        if queryResults.empty:
            print("\nEmpty data frame")
            return

        print1 = input('\nWould you like to save query results? (y/n):   ')
        HQ.toCSV(print1, queryResults)

        print('finding ROI synapse weight for input body query...')
        # minmax is inputBodies with the PRE/POST changed to roi_connectivity_weight
        queryResults2 = HQ.compareMinMax(queryResults)
        print4 = input('\nquery removes the PRE and POST columns from the input bodies query and changes the '
                       'column to roi_connectivity_weight, returning whichever has the higher value'
                       '\nWould you like to save the updated results? (y/n):   ')
        HQ.toCSV(print4, queryResults2)

        print('\nrunning statistics for threshold values...')
        statistics = HQ.findStatistics2(queryResults2)
        print('\n' + str(statistics))

        HQ.displayOptions2(queryResults2, statistics, ROI)

        return

    if hops == '3':
        DNType = input('\nEnter the DN Type: (ex: DNa, DNp..)   ')
        DNType = str(DNType)
        queryResults = pd.DataFrame()
        for ROI in ROIs:
            queryResults1 = Target_DNROI_ThreeHop(ROI, DNType)
            queryResults = queryResults.append(queryResults1)
            if queryResults1.empty:
                print("\nEmpty data frame, moving to next ROI")

        if queryResults.empty:
            print("\nEmpty data frame")
            return

        print1 = input('\nWould you like to save query results? (y/n):   ')
        HQ.toCSV(print1, queryResults)

        print('\ngetting input bodies...')
        # original input bodies = inputBodies
        inputBodies = HQ.getInputBodies(queryResults, ROI)
        print2 = input('\nWould you like to save the input body query results? (y/n):   ')
        HQ.toCSV(print2, inputBodies)

        print('\nfinding mismatched bodies...'
              '\nquery removes bodies that are not annotated from original ROI two hop query')
        # queryResults2 is queryResults with mismatched bodies removed
        queryResults2, inputBodies2 = HQ.mismatchedBodies(queryResults, inputBodies)
        print3 = input('\nWould you like to save the mismatched body results? (y/n):   ')
        HQ.toCSV(print3, queryResults2)

        print('finding ROI synapse weight for input body query...')
        # minmax is inputBodies with the PRE/POST changed to roi_connectivity_weight
        minmax = HQ.compareMinMax(inputBodies2)
        print4 = input('\nquery removes the PRE and POST columns from the input bodies query and changes the '
                       'column to roi_connectivity_weight, returning whichever has the higher value'
                       '\nWould you like to save the updated results? (y/n):   ')
        HQ.toCSV(print4, minmax)

        print('\nrunning statistics for threshold values...')
        statistics = HQ.findStatistics(queryResults2, minmax)
        print('\n' + str(statistics))

        HQ.displayOptions(queryResults2, minmax, statistics, ROI)

        return

    return
'''


# ------------------------------------------------------------------

# DN Queries
# All of the DN Body IDs at the time of file creation are in lists
# This hasn't been updated so it might not return results properly
# The only thing that should change is the actual query & body ID lists
# These first 3 do not need to be run individually
def Target_DNROI_TwoHop(roi, DNType):
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
                                 ' MATCH (input:`hemibrain_Neuron`)-[w1:ConnectsTo]->(TargetInput:`hemibrain_Neuron`)-[w2:ConnectsTo]->(Target:`hemibrain_Neuron`)'
                                 ' WHERE Target.bodyId = DN AND NOT apoc.convert.fromJsonMap(w1.roiInfo)["' + roi + '"] IS NULL'
                                                                                                                    ' RETURN input.bodyId, input.type, input.instance, input.status, w1.weight as '
                                                                                                                    'input_weight, apoc.convert.fromJsonMap(w1.roiInfo)["' + roi + '"].pre as PRE, '
                                                                                                                                                                                   ' apoc.convert.fromJsonMap(w1.roiInfo)["' + roi + '"].post as POST, TargetInput.bodyId, TargetInput.type, '
                                                                                                                                                                                                                                     'TargetInput.instance, TargetInput.status, w2.weight as Target_weight, '
                                                                                                                                                                                                                                     'Target.bodyId, Target.type, Target.instance, Target.status'
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
            query = (
                    ' MATCH (input:`hemibrain_Neuron`)-[w1:ConnectsTo]->(TargetInput:`hemibrain_Neuron`)-[w2:ConnectsTo]->(Target:`hemibrain_Neuron`)'
                    ' WHERE Target.bodyId = ' + str(
                i) + ' AND NOT apoc.convert.fromJsonMap(w1.roiInfo)["' + roi + '"] IS NULL'
                                                                               ' RETURN input.bodyId, input.type, input.instance, input.status, w1.weight as '
                                                                               'input_weight, apoc.convert.fromJsonMap(w1.roiInfo)["' + roi + '"].pre as PRE, '
                                                                                                                                              ' apoc.convert.fromJsonMap(w1.roiInfo)["' + roi + '"].post as POST, TargetInput.bodyId, TargetInput.type, '
                                                                                                                                                                                                'TargetInput.instance, TargetInput.status, w2.weight as Target_weight, '
                                                                                                                                                                                                'Target.bodyId, Target.type, Target.instance, Target.status')
            queryResults1 = client.fetch_custom(query)

            queryResults = queryResults.append(queryResults1)

    return queryResults


def Target_DNROI_ThreeHop(roi, DNType):
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
                                 ' MATCH (interneuron:Neuron)-[w2:ConnectsTo]->(TargetInput:Neuron)-[w3:ConnectsTo]->(Target:Neuron)'
                                 ' WHERE Target.bodyId = DN AND NOT apoc.convert.fromJsonMap(interneuron.roiInfo)["' + roi + '"].post IS NULL'
                                                                                                                             ' RETURN interneuron.bodyId, interneuron.type, interneuron.instance, interneuron.status, w2.weight as '
                                                                                                                             'interneuron_weight, TargetInput.bodyId, TargetInput.type, TargetInput.instance, TargetInput.status, w3.weight as Target_weight, '
                                                                                                                             'Target.bodyId, Target.type, Target.instance, Target.status'
    )

    queryResults = client.fetch_custom(query)

    if DNType == "DNp":
        DNp1 = [2307027729, 5813024015, 1565846637, 1405231475, 1466998977, 5813023322, 1100404581, 1226887763,
                5813026936]
        DNp2 = [5813020512, 5813095193, 1815895547, 1684204798, 1498383456, 1498033920, 1507933560, 5813068840,
                1344249576]
        DNp3 = [821201495, 1100404634, 1072063538, 1043117106, 1135837629, 1006984280, 5813050455, 984030630, 981000564]
        DNp4 = [5813078134, 1405300548, 1344253853, 1405300499, 1436330964, 1229107423, 1044218225, 5813047199,
                5813048234]
        DNp5 = [512851433, 1281324958, 887195902, 1745333830, 1197234751, 1436703256, 1467357251, 1467694006, 451689001,
                1039335355]
        query1 = (
                'WITH ' + str(DNs) + ' AS DNS'
                                     ' UNWIND DNS as DN'
                                     ' MATCH (interneuron:Neuron)-[w2:ConnectsTo]->(TargetInput:Neuron)-[w3:ConnectsTo]->(Target:Neuron)'
                                     ' WHERE Target.bodyId = DN AND NOT apoc.convert.fromJsonMap(interneuron.roiInfo)["' + roi + '"].post IS NULL'
                                                                                                                                 ' RETURN interneuron.bodyId, interneuron.type, interneuron.instance, interneuron.status, w2.weight as '
                                                                                                                                 'interneuron_weight, TargetInput.bodyId, TargetInput.type, TargetInput.instance, TargetInput.status, w3.weight as Target_weight, '
                                                                                                                                 'Target.bodyId, Target.type, Target.instance, Target.status'
        )
        queryResults1 = client.fetch_custom(query1)

        query2 = (
                'WITH ' + str(DNs) + ' AS DNS'
                                     ' UNWIND DNS as DN'
                                     ' MATCH (interneuron:Neuron)-[w2:ConnectsTo]->(TargetInput:Neuron)-[w3:ConnectsTo]->(Target:Neuron)'
                                     ' WHERE Target.bodyId = DN AND NOT apoc.convert.fromJsonMap(interneuron.roiInfo)["' + roi + '"].post IS NULL'
                                                                                                                                 ' RETURN interneuron.bodyId, interneuron.type, interneuron.instance, interneuron.status, w2.weight as '
                                                                                                                                 'interneuron_weight, TargetInput.bodyId, TargetInput.type, TargetInput.instance, TargetInput.status, w3.weight as Target_weight, '
                                                                                                                                 'Target.bodyId, Target.type, Target.instance, Target.status'
        )
        queryResults2 = client.fetch_custom(query2)
        query3 = (
                'WITH ' + str(DNs) + ' AS DNS'
                                     ' UNWIND DNS as DN'
                                     ' MATCH (interneuron:Neuron)-[w2:ConnectsTo]->(TargetInput:Neuron)-[w3:ConnectsTo]->(Target:Neuron)'
                                     ' WHERE Target.bodyId = DN AND NOT apoc.convert.fromJsonMap(interneuron.roiInfo)["' + roi + '"].post IS NULL'
                                                                                                                                 ' RETURN interneuron.bodyId, interneuron.type, interneuron.instance, interneuron.status, w2.weight as '
                                                                                                                                 'interneuron_weight, TargetInput.bodyId, TargetInput.type, TargetInput.instance, TargetInput.status, w3.weight as Target_weight, '
                                                                                                                                 'Target.bodyId, Target.type, Target.instance, Target.status'
        )
        queryResults3 = client.fetch_custom(query3)
        query4 = (
                'WITH ' + str(DNs) + ' AS DNS'
                                     ' UNWIND DNS as DN'
                                     ' MATCH (interneuron:Neuron)-[w2:ConnectsTo]->(TargetInput:Neuron)-[w3:ConnectsTo]->(Target:Neuron)'
                                     ' WHERE Target.bodyId = DN AND NOT apoc.convert.fromJsonMap(interneuron.roiInfo)["' + roi + '"].post IS NULL'
                                                                                                                                 ' RETURN interneuron.bodyId, interneuron.type, interneuron.instance, interneuron.status, w2.weight as '
                                                                                                                                 'interneuron_weight, TargetInput.bodyId, TargetInput.type, TargetInput.instance, TargetInput.status, w3.weight as Target_weight, '
                                                                                                                                 'Target.bodyId, Target.type, Target.instance, Target.status'
        )
        queryResults4 = client.fetch_custom(query4)
        query5 = (
                'WITH ' + str(DNs) + ' AS DNS'
                                     ' UNWIND DNS as DN'
                                     ' MATCH (interneuron:Neuron)-[w2:ConnectsTo]->(TargetInput:Neuron)-[w3:ConnectsTo]->(Target:Neuron)'
                                     ' WHERE Target.bodyId = DN AND NOT apoc.convert.fromJsonMap(interneuron.roiInfo)["' + roi + '"].post IS NULL'
                                                                                                                                 ' RETURN interneuron.bodyId, interneuron.type, interneuron.instance, interneuron.status, w2.weight as '
                                                                                                                                 'interneuron_weight, TargetInput.bodyId, TargetInput.type, TargetInput.instance, TargetInput.status, w3.weight as Target_weight, '
                                                                                                                                 'Target.bodyId, Target.type, Target.instance, Target.status'
        )
        queryResults5 = client.fetch_custom(query5)
        queryResults = queryResults1.append(queryResults2)
        queryResults = queryResults.append(queryResults3)
        queryResults = queryResults.append(queryResults4)
        queryResults = queryResults.append(queryResults5)

    return queryResults


def Target_DNROI_OneHop(roi, DNType):
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
                                 ' WHERE Target.bodyId = DN AND NOT apoc.convert.fromJsonMap(w1.roiInfo)["' + roi + '"] IS NULL'
                                                                                                                    ' RETURN input.bodyId, input.type, input.instance, input.status, w1.weight as '
                                                                                                                    'input_weight, apoc.convert.fromJsonMap(w1.roiInfo)["' + roi + '"].pre as PRE, '
                                                                                                                                                                                   ' apoc.convert.fromJsonMap(w1.roiInfo)["' + roi + '"].post as POST,'
                                                                                                                                                                                                                                     ' Target.bodyId, Target.type, Target.instance, Target.status'
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
                    ' WHERE Target.bodyId = ' + str(
                i) + ' AND NOT apoc.convert.fromJsonMap(w1.roiInfo)["' + roi + '"] IS NULL'
                                                                               ' RETURN input.bodyId, input.type, input.instance, input.status, w1.weight as '
                                                                               'input_weight, apoc.convert.fromJsonMap(w1.roiInfo)["' + roi + '"].pre as PRE, '
                                                                                                                                              ' apoc.convert.fromJsonMap(w1.roiInfo)["' + roi + '"].post as POST,'
                                                                                                                                                                                                ' Target.bodyId, Target.type, Target.instance, Target.status')

            queryResults1 = client.fetch_custom(query2)
            queryResults = queryResults.append(queryResults1)

    return queryResults


# ------------------------------------------------------------------

'''
Additional queries and functions
'''


def pullDNs(DNType=None):
    if DNType is None:
        query = (
            'MATCH (input:Neuron)-[w1:ConnectsTo]->(DN:Neuron)'
            ' WHERE (DN.type CONTAINS "DNa" OR DN.type CONTAINS "DNb" '
            'OR DN.type CONTAINS "DNc" OR DN.type CONTAINS "DNd" '
            'OR DN.type CONTAINS "DNp" OR DN.type CONTAINS "DNg")  '
            'AND NOT DN.type CONTAINS "ovi"'
            ' RETURN input.bodyId, input.type, w1, DN.bodyId, DN.type'
        )
    queryResults = client.fetch_custom(query)
    queryResults.to_csv("DNCompare\qr.csv")
    return queryResults


def getP16P17():
    query = (
        'MATCH (input:Neuron)-[w1:ConnectsTo]->(DN:Neuron)'
        ' WHERE (DN.type = "DNp16" OR DN.type = "DNp17" OR DN.type = "DNp16/17")'
        ' RETURN input.bodyId, input.type, w1.weight, DN.bodyId, DN.type'
    )
    queryResults = client.fetch_custom(query)
    queryResults.to_csv("DNCompare\p16p17.csv")
    return queryResults


def DN_ROIInfo_OneHop(DNType):
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
                                 ' RETURN input.bodyId, input.type, input.instance, input.status, input.pre AS nPre, w1.weight as '
                                 'input_weight, '
                                 'apoc.convert.fromJsonMap(w1.roiInfo)["LAL(R)"].pre AS LALR_PRE,'
                                 'apoc.convert.fromJsonMap(w1.roiInfo)["LAL(R)"].post AS LALR_POST,'
                                 'apoc.convert.fromJsonMap(w1.roiInfo)["LAL(L)"].pre AS LALL_PRE,'
                                 'apoc.convert.fromJsonMap(w1.roiInfo)["LAL(L)"].post AS LALL_POST,'
                                 'apoc.convert.fromJsonMap(w1.roiInfo)["IPS(R)"].pre AS IPS_PRE,'
                                 'apoc.convert.fromJsonMap(w1.roiInfo)["IPS(R)"].post AS IPS_POST,'
                                 'apoc.convert.fromJsonMap(w1.roiInfo)["SPS(R)"].pre AS SPSR_PRE,'
                                 'apoc.convert.fromJsonMap(w1.roiInfo)["SPS(R)"].post AS SPSR_POST,'
                                 'apoc.convert.fromJsonMap(w1.roiInfo)["SPS(L)"].pre AS SPSL_PRE,'
                                 'apoc.convert.fromJsonMap(w1.roiInfo)["SPS(L)"].post AS SPSL_POST,'
                                 'apoc.convert.fromJsonMap(w1.roiInfo)["WED(R)"].pre AS WED_PRE,'
                                 'apoc.convert.fromJsonMap(w1.roiInfo)["WED(R)"].post AS WED_POST,'
                                 'w1.roiInfo, Target.bodyId, Target.type, Target.instance, Target.status, Target.post AS nPost'
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
                                                         ' RETURN input.bodyId, input.type, input.instance, input.status, input.pre AS nPre, w1.weight as '
                                                         'input_weight, '
                                                         'apoc.convert.fromJsonMap(w1.roiInfo)["LAL(R)"].pre AS LALR_PRE,'
                                                         'apoc.convert.fromJsonMap(w1.roiInfo)["LAL(R)"].post AS LALR_POST,'
                                                         'apoc.convert.fromJsonMap(w1.roiInfo)["LAL(L)"].pre AS LALL_PRE,'
                                                         'apoc.convert.fromJsonMap(w1.roiInfo)["LAL(L)"].post AS LALL_POST,'
                                                         'apoc.convert.fromJsonMap(w1.roiInfo)["IPS(R)"].pre AS IPS_PRE,'
                                                         'apoc.convert.fromJsonMap(w1.roiInfo)["IPS(R)"].post AS IPS_POST,'
                                                         'apoc.convert.fromJsonMap(w1.roiInfo)["SPS(R)"].pre AS SPSR_PRE,'
                                                         'apoc.convert.fromJsonMap(w1.roiInfo)["SPS(R)"].post AS SPSR_POST,'
                                                         'apoc.convert.fromJsonMap(w1.roiInfo)["SPS(L)"].pre AS SPSL_PRE,'
                                                         'apoc.convert.fromJsonMap(w1.roiInfo)["SPS(L)"].post AS SPSL_POST,'
                                                         'apoc.convert.fromJsonMap(w1.roiInfo)["WED(R)"].pre AS WED_PRE,'
                                                         'apoc.convert.fromJsonMap(w1.roiInfo)["WED(R)"].post AS WED_POST,'
                                                         'w1.roiInfo, Target.bodyId, Target.type, Target.instance, Target.status, Target.post AS nPost')

            queryResults1 = client.fetch_custom(query2)
            queryResults = queryResults.append(queryResults1)
    queryResults2 = queryResults.reset_index(drop=True)
    return queryResults2


def removeIrrelevant(queryResults):
    queryResults = queryResults.fillna({'LALR_PRE': 0,
                                        'LALR_POST': 0, 'LALL_PRE': 0, 'LALL_POST': 0, 'IPS_PRE': 0, 'IPS_POST': 0,
                                        'SPSR_PRE': 0,
                                        'SPSR_POST': 0, 'SPSL_PRE': 0, 'SPSL_POST': 0, 'WED_PRE': 0, 'WED_POST': 0})

    cols = ['LALR_PRE', 'LALR_POST', 'LALL_PRE', 'LALL_POST', 'IPS_PRE', 'IPS_POST', 'SPSR_PRE',
            'SPSR_POST', 'SPSL_PRE', 'SPSL_POST', 'WED_PRE', 'WED_POST']
    queryResults2 = queryResults[(queryResults[cols] != 0).any(axis=1)]

    queryResults3 = queryResults2.drop(queryResults2.index[queryResults2['input.status'] == 'Assign'])
    queryResults4 = queryResults3.drop(queryResults3.index[queryResults3['input.status'] == 'Orphan'])
    queryResults5 = queryResults4.drop(queryResults4.index[queryResults4['input.status'] == 'Unimportant'])

    return queryResults5


def comparePrePost(queryResults):
    for index, row in queryResults.iterrows():
        preV11 = row["LALR_PRE"]
        postV11 = row["LALR_POST"]
        if postV11 < 11:
            queryResults.loc[index, 'LALR_POST'] = preV11

        preV12 = row["LALL_PRE"]
        postV12 = row["LALL_POST"]
        if postV12 < preV12:
            queryResults.loc[index, 'LALL_POST'] = preV12

        preV13 = row["IPS_PRE"]
        postV13 = row["IPS_POST"]
        if postV13 < preV13:
            queryResults.loc[index, 'IPS_POST'] = preV13

        preV14 = row["SPSR_PRE"]
        postV14 = row["SPSR_POST"]
        if postV14 < preV14:
            queryResults.loc[index, 'SPSR_POST'] = preV14

        preV15 = row["SPSL_PRE"]
        postV15 = row["SPSL_POST"]
        if postV15 < preV15:
            queryResults.loc[index, 'SPSL_POST'] = preV15

        preV16 = row["WED_PRE"]
        postV16 = row["WED_POST"]
        if postV16 < preV16:
            queryResults.loc[index, 'WED_POST'] = preV16

    toDrop = ['LALR_PRE',
              'LALL_PRE', 'IPS_PRE', 'SPSR_PRE',
              'SPSL_PRE', 'WED_PRE']

    queryResults2 = queryResults.drop(toDrop, axis=1)

    queryResults2 = queryResults2.rename({'LALR_POST': 'LALR'}, axis=1)
    queryResults2 = queryResults2.rename({'LALL_POST': 'LALL'}, axis=1)
    queryResults2 = queryResults2.rename({'IPS_POST': 'IPS'}, axis=1)
    queryResults2 = queryResults2.rename({'SPSR_POST': 'SPSR'}, axis=1)
    queryResults2 = queryResults2.rename({'SPSL_POST': 'SPSL'}, axis=1)
    queryResults2 = queryResults2.rename({'WED_POST': 'WED'}, axis=1)

    return queryResults2


def reorgQuery(queryResults):
    columns = ['input.bodyId', 'input.type', 'input.instance', 'input.status', 'nPre', "Input",
               'weight', 'LALR', 'LALL', 'IPS', 'SPSR',
               'SPSL', 'WED', 'output.bodyId', 'output.type', 'output.instance',
               'output.status', 'nPost', 'Output']

    reorgDF = pd.DataFrame()
    row1 = []  # inter -> GFIN

    for index, row in queryResults.iterrows():
        row1 = [row['input.bodyId'], row['input.type'], row['input.instance'],
                row['input.status'], row['nPre'], None, row['input_weight'],
                row['LALR'],
                row['LALL'], row['IPS'], row['SPSR'], row['SPSL'], row['WED'], row['Target.bodyId'],
                row['Target.type'], row['Target.instance'], row['Target.status'], row['nPost'], None]

        reorgDF = reorgDF.append([row1], ignore_index=True)

    reorgDF.columns = columns

    for index, row in reorgDF.iterrows():
        if row['input.type'] is not None:
            reorgDF.loc[index, 'Input'] = row['input.type']
        elif row['input.instance'] is not None:
            reorgDF.loc[index, 'Input'] = row['input.instance']
        else:
            reorgDF.loc[index, 'Input'] = row['input.bodyId']

        if row['output.type'] is not None:
            reorgDF.loc[index, 'Output'] = row['output.type']
        elif row['output.instance'] is not None:
            reorgDF.loc[index, 'Output'] = row['output.instance']
        else:
            reorgDF.loc[index, 'Output'] = row['output.bodyId']

    reorgDF = reorgDF.drop_duplicates()
    return reorgDF


def addWeights(queryResults):
    queryResults['Count'] = queryResults.groupby(['Input'])['Output'].transform('count')

    f = {
        'Input': 'first',
        'Output': 'first',
        'nPre': 'sum',
        'Count': 'first',
        'weight': 'sum',
        'LALR': 'sum',
        'LALL': 'sum',
        'IPS': 'sum',
        'SPSR': 'sum',
        'SPSL': 'sum',
        'WED': 'sum',
        'nPost': 'nunique',
        'input.type': 'last', 'input.instance': 'last', 'output.type': 'last', 'output.instance': 'last'
    }
    g = queryResults.groupby(['Input', 'Output'])
    v1 = g.agg(f)
    v2 = g.agg(lambda x: x.drop_duplicates(['Count'], keep='first').nPost.sum())
    fileDF = pd.concat([v1, v2.to_frame('nPost')], 1)

    '''fileDF = queryResults.groupby(['Input', 'Output'], as_index=False).agg(
         {'input.type': 'last', 'input.instance': 'last', 'nPre': 'sum', 'weight': 'sum',
          'LALR': 'sum',
          'LALL': 'sum', 'IPS': 'sum',  'SPSR': 'sum','SPSL': 'sum','WED': 'sum',
          'output.type': 'last', 'output.instance': 'last', 'Count': 'first', 'nPost': 'nunique'})
      '''
    fileDF = fileDF[['input.type', 'input.instance', 'Input', 'Count', 'weight',
                     'LALR', 'LALL', 'IPS', 'SPSR',
                     'SPSL', 'WED', 'output.type', 'output.instance', 'Output']]
    return fileDF


def addPercentageColumns(queryResults):
    lalr_per = []
    lall_per = []
    ips_per = []
    spsr_per = []
    spsl_per = []
    wed_per = []
    totalROI = []
    ROI_per = []

    for index, row in queryResults.iterrows():
        lalr = queryResults.loc[index, 'LALR']
        lall = queryResults.loc[index, 'LALL']
        ips = queryResults.loc[index, 'IPS']
        spsr = queryResults.loc[index, 'SPSR']
        spsl = queryResults.loc[index, 'SPSL']
        wed = queryResults.loc[index, 'WED']
        weight = queryResults.loc[index, 'weight']

        summedROI = lalr + lall + ips + spsr + spsl + wed
        totalROI.append(summedROI)
        roiper = (summedROI / weight) * 100
        ROI_per.append(roiper)

        if lalr == 0:
            lalr_per.append(0)
        else:
            roi_percent = (lalr / weight) * 100
            lalr_per.append(roi_percent)

        if lall == 0:
            lall_per.append(0)
        else:
            roi_percent = (lall / weight) * 100
            lall_per.append(roi_percent)

        if ips == 0:
            ips_per.append(0)
        else:
            roi_percent = (ips / weight) * 100
            ips_per.append(roi_percent)

        if spsr == 0:
            spsr_per.append(0)
        else:
            roi_percent = (spsr / weight) * 100
            spsr_per.append(roi_percent)

        if spsl == 0:
            spsl_per.append(0)
        else:
            roi_percent = (spsl / weight) * 100
            spsl_per.append(roi_percent)

        if wed == 0:
            wed_per.append(0)
        else:
            roi_percent = (wed / weight) * 100
            wed_per.append(roi_percent)

    queryResults['LALR_PER'] = lalr_per
    queryResults['LALL_PER'] = lall_per
    queryResults['IPS_PER'] = ips_per
    queryResults['SPSR_PER'] = spsr_per
    queryResults['SPSL_PER'] = spsl_per
    queryResults['WED_PER'] = wed_per
    queryResults['CX_Weight'] = totalROI
    queryResults['CX_PER'] = ROI_per
    columns = ['input.type', 'input.instance', 'input.Pre', 'Input',
               'weight', 'LALR', 'LALR_PER', 'LALL', 'LALL_PER', 'IPS', 'IPS_PER', 'SPSR', 'SPSR_PER',
               'SPSL', 'SPSL_PER', 'WED', 'WED_PER', 'CX_Weight', 'CX_PER', 'output.type', 'output.instance',
               'output.Post'
               'Output']

    queryResults = queryResults.reindex(columns=columns)

    return queryResults


def addPercentageColumns2(queryResults):
    lalr_per = []
    lall_per = []
    ips_per = []
    spsr_per = []
    spsl_per = []
    wed_per = []

    for index, row in queryResults.iterrows():
        lalr = queryResults.loc[index, 'LALR']
        lall = queryResults.loc[index, 'LALL']
        ips = queryResults.loc[index, 'IPS']
        spsr = queryResults.loc[index, 'SPSR']
        spsl = queryResults.loc[index, 'SPSL']
        wed = queryResults.loc[index, 'WED']
        weight = queryResults.loc[index, 'weight']

        if lalr == 0:
            lalr_per.append(0)
        else:
            roi_percent = (lalr / weight) * 100
            lalr_per.append(roi_percent)

        if lall == 0:
            lall_per.append(0)
        else:
            roi_percent = (lall / weight) * 100
            lall_per.append(roi_percent)

        if ips == 0:
            ips_per.append(0)
        else:
            roi_percent = (ips / weight) * 100
            ips_per.append(roi_percent)

        if spsr == 0:
            spsr_per.append(0)
        else:
            roi_percent = (spsr / weight) * 100
            spsr_per.append(roi_percent)

        if spsl == 0:
            spsl_per.append(0)
        else:
            roi_percent = (spsl / weight) * 100
            spsl_per.append(roi_percent)

        if wed == 0:
            wed_per.append(0)
        else:
            roi_percent = (wed / weight) * 100
            wed_per.append(roi_percent)

    queryResults['LALR_PER'] = lalr_per
    queryResults['LALL_PER'] = lall_per
    queryResults['IPS_PER'] = ips_per
    queryResults['SPSR_PER'] = spsr_per
    queryResults['SPSL_PER'] = spsl_per
    queryResults['WED_PER'] = wed_per

    columns = ['input.bodyId', 'input.type', 'input.instance', 'input.status',
               'weight', 'LALR', 'LALR_PER', 'LALL', 'LALL_PER', 'IPS', 'IPS_PER', 'SPSR', 'SPSR_PER',
               'SPSL', 'SPSL_PER', 'WED', 'WED_PER', 'Target.bodyId', 'Target.type', 'Target.instance',
               'Target.status']

    queryResults = queryResults.reindex(columns=columns)

    return queryResults


'''

WITH [1476868405,5813069570,1041666949,1128676181,1437302815,916543308,734814622,761368439,1663021115,1448794542,5813054853,1353375816,1565937074,5813040731,1597287219,1224875671,974771466,1760327095,5813069773,2005894552,978432050,1539508448,7112616299,1130424306,1224523027,5813056435,1284373356,1811426935,1345285966,5813063356,1535791554,1252582215,978392510,5813078104,5813093048,234630133,1716034527,5813078298,1501708149,1633441295,1347638401,1286937453,976506780,1970745542,5813043077,7112622044,1687321237,5813023473,943472763,1252116913,882922539,1498405457,2071241779,1937924009,1469291436,705234668,1746373639,5813060067,1099458986,1779231120,5813077478,1683941579,943472755,1963869636,5813056759,1665775343,1593936440,1780426473,2092402876,1626948732,1561351296,1317074822,1101716795,925811326,1344258473,1560471374,1469663014,5813041426,1220416666,1375366517,1899441465,1748648841,853286239,1570836367,1352676736,1255121271,5812999580,1561895849,2155841352,1911888093,5813042688,5813042734,1722764125,5813054604,1405978277,2032849765,1313879738,2031020433,943468720,5813024852,1723723098,5813078030,2099569651,976260443,5813024040,1869417384,2005001716,1822686129,2003495133,1253230158,1595922256,1659016060,1963221329,1844223096,1851730931,5813054870,5813050004,1664178250,2213205667,1748990082,5813078085,1695463406,853251409,1850310331,2127897469,1482333122,1963212919,1345277432,1788546780,1344543578,5813015327,1442266942,5813023569,1252945743,5813050030,5813046185,855672976,5813054790,2071582363,1756886387,2065530054,1632720433,5812982885,1810399489,5813069184,821197679,5813014572,1821606693,5813022711,945315639,2035181503,2222414812,1006310611,1694130627,5813001697,5813004425,859489809,2316502686,1319134018,1011025640,2253750781,1251511957,5813047976,1756134129,5813054946,1288788976,2094811748,2213193150,1913014120,5813023364,2025278394,1900456006,2094540274,2035181876,2003459912,1916459566,1605847231,1967637295,1467720711,1467707486,1941078806,1470357908,1591427572,5813022696,5901225755,1873846312,1934975261,1847984002,1723157449,1560458336,1693798828,1657616545,1468782618,1283868229,1809035068,949429988,1751105563,1847603298,1562914024,5901227238,1717588520,1821378236,1384043823,1228878598,5813049412,1438744622,1260949706,1132104170,5813049414,1652832941,1008663435,1500762388,823602025,2038510343,5813040566,2003132270,1409959713,5813023742,1654969939,1100481731,5813017654,1349835835,1564619820,5813023540,1314351013,5813023296,1694479261,1622138907,1623283156,1655677643,5813061029,1622636076,5813019100,1715956393,2350615474,1879385017,1375224482,1626663832,1695187208,1728911520,5813023536,5813069300,1882040130,5812998127,1848277193,1938260447,1605156604,1530450586,1817293538,977214624,1685896788,5813067963,1971772981,1730617033,1315382485,1349689713,5813054573,1808750324,2090076660,5813018687,5813027081,1782857355,2126870445,5813055290,1625330222,5813020534,1197571795,1344663917,1910048384,1722143176,1500516375,5813024082,1777301335,1777383178,1073428001,5812989437,2035185775,1843596950,1751761966,1744966885,2159938376,1653179621,2471712152,1354027391,1099912501,1686083021,5813023379,5813024119,5813088421,1498064190,1144756508,1808400948,1379187792,1101708390,1282507669,1226029729,1652850041,1809065227,1344353292,1405991898,2335981561,1698938870,5813038338,1787510154,5901200701,2034123290,5813020611,1562564656,2407867458,1191211539,943468639,1692127088,1886098460,1252548351,1197455013,1561550434,5813023541,1690805490,2278992475,976857019,1469131844,5812989761,1197455268,1791025538,1971773455,5813049447,1846661932,1343943385,2055954745,1505494924,2031032549,1777982603,5813023621,5813027973,5813034553,1316711568,5813088863,1035005380,5813069246,2065132470,1591881564,2402467880,1468756050,5812983097,5813034263,1684653520,1839068739,1658679205,1971450344,1197847302,1686350580,1908023418,977067748,1193495797,1698606868,1286298090,5813020535,5812998853,1656027753,1820682425,1634477964,1446765621,1938661479,5812992250,1602376300,2065158112,5813040398,1436676834,1668529983,2128981133,5813024031,1292316735,1658449693,5813050292,1654880399,946045327,1102412245,1806686675,1912336507,5813025737,5813078530,1813256823,1946057040,1510652444,1286298117,1852408123,977420970,1594562431,5812991852,1503271121,1353000905,1255272167,1007644534,1906630034,1559430025,1729287518,1664040834,5813090128,1721862006,1223499592,2306280422,1931132940,1348653495,1532285104,1656688710,1695506907,1908348376,1530196161,2026284088,1163627494,1907946099,2097932975,1469162241,1005170831,2067580245,1688039474,5813055586,2122198727,1222187110,1849921277,2126590043,1407053514,1625619163,1808430432,5813015973,5812991413,1720062431,5813032485,1535217437,1905632454,1813887867,1837695505,2098891635,1872525553,1842504580,2287181377,5812994051,1719695040,5813025342,1839042968,1132436808,1902140615,5813057792,2397381991,5812994362,1162806267,1728281815,1343860874,1879018709,1782209927,1882053559,2003136306,1237179690,5813046229,1780137360,5813054879,1623593998,1130972852,2281713090,2120770637,2283421947,1375254283,5813049499,2035544474,1686708380,2126184462,1908693784,1876570170,1593599640,1727945284,1626706688,1685331892,1252548299,1099946957,5812998107,5812986051,2001102862,1935273146,2350624167,1848942178,1844270370,1656929646,2097194758,2318552939,1936287309,1653179935,5813023559,2303944501,1718671546,2155565007,1473293683,1665766998,1476795191,1283660957,1843437693,1968000090,1972132164,1847984369,1967581085,5901227197,1760662977,1102049230,2002463568,1658640107,5812991315,1561568025,1625001528,5813024114,2245259630,5813001051,2094138238,1534573856,2088065129,1877304375,1470898034,1972796796,1590465360,2040594780,5813077842,5813034870,5813027282,2157551264,1378440243,1601621046,2005126021,1405927201,2158907111,2030039667,5813022641,1876907399,1635146965,2400416963,1750786551,1720321321,2093801621,2033087464,1723519812,5812986708,2281362835,1782136429,1222912120,1842168046,5812998969,1253636394,1751139866,1596699439,2032767961,1899428740,5813078166,1808404988,1822659562,1288449787,5813033960,1253295510,2185275180,1344214794,1849559181,1316375063,1908628383,1969727562,5813101875,5812979878,5813091075,1821714375,2063514352,2028718812,1659970036,5812994710,5813025435,1664843299,1132233355,1714937661,1813525105,5901200047,2099569065,1448065211,2005877512,1510661643,1782136083,1909642789,2150820948,5813066087,1604789908,1780469741,1535885253,1628810150,5813079567,2588024447,1448065029,5813024215,1782447437,2001392064,1263404948,883448423,1499493438,1224634211,2346523468,5901219755,5812981760,1072551052,1379161800,1875288491,1407866159,1626690698,5813043649,1655898470,1846627221,983063787,5901194016,1969048938,5813063158,1294102958,1812838782,1376782262,1933239983,7112613364,1876280875,2129956780,1344604087,1751437657,1812838427,5813002043,1014107332,1725156961,2190537640,5813056727,2247646756,2188262179,1841503959,1656753288,1504359286,5813068067,1995948310,1409091354,1942438892,1807070681,2003814063,1655894101,5813076242,1606468352,1374986768,1005857038,1633445474,1846619304,1756895140,2089769667,5813034093,830419511,1287883039,1943467273,2001052107,1470232668,1374960533,1994239151,1872214454,1873889329,1564326588,5812994851,5813025893,5813049951,1604448421,5813116551,2339034013,1815290414,1933576680,1942789501,5813005266,1999087154,1224638842,1530869443,5813066706,5812998738,1814945420,5813003831,1344690604,5813049469,1751438143,1347621238,1964210397,1748071079,1996288874,5813055501,1842517867,2092062449,1963186391,1720109208,5813023274,1875249255,1405996432,2119751823,1786232660,5813134575,948778197,1870781346,1852408408,5813046308,1067624754,1378086827,5812991332,5812986121,5813075790,5812988816,2178414823,1812510378,2001056720,2315134158,1325138101,1747362459,5813033507,1843549956,1005861838,5813041673,1655285118,2127219419,1591143952,5813042525,1469550473,1937232797,2222029255,5812998867,1908261361,1685664303,1716332090,1813473103,1346736764,1874809041,1559776646,917742834,1633441251,5813060959,2188943821,2038868436,2118710680,1191535849,2439951854,1566740157,1754852671,5813035436,2312427844,1748092323,1163263948,2339343788,1685578450,5813038696,913274888,2252015475,1534116722,1076168044,1938670346,1625001708,2117670301,1652864087,2150116801,1594285902,1594506747,2157624106,1809838239,1480452227,1870764460,5812989439,5813042858,1285335879,1695865038,1407774293,5813014960,1469792462,1316716161,2059369205,5813033673,1008102252,1314315388,5813048696,1501267296,1378664781,5813082734,5813003907,1723351932,1787541322,2273583250,1348817469,2187648590,5813045940,1563255713,1904928514,2032085700,5813045737,2187921545,5813018073,1563250587,5812983254,1256723567,2060453610,1286026697,2035901946,2340030368,5813077751,1904924344,1345519875,1839042586,2157214957,5813005683,1995287885,1726201288,1563609967,1590129206,1627065724,1224523160,1101535258,1562897038,2280698303,946559704,1566247458,1904237771,5812989467,2156488795,1996988813,2150078062,1130770083,1687054079,2222370777,1133611276,2217592277,5812987925,1193953231,5813024731,1778700368,1072897134,5812990515,1467322976,5813042697,2156179226,2276937710,1468804008,1776010374,1602536144,1907298315,1409475218,1438027519,2189350360,5813124111,1936624406,1659283187,1747302427,1964270330,1130839155,5813054811,1380188301,1871152557,2340440276,1469002817,1162905915,5901217787,1469537787,1903499460,946905479,5812994035,1469550353,1933231152,1812748071,1562119933,1600334745,1605791730,1534458003,2221369836,1846316360,915696610,2216219383,1590815333,2309751059,1566744035,1530144633,5813061253,2153799451,5812997805,1695533265,1665844590,1016110766,1528732782,1693802528,5813023125,1138937616,5812998596,1633816833,794963206,1873889648,5813061403,1655376026,1479099705,1691742475,1683863486,5812997477,1108230557,1665499507,5813000747,5813023857,5813023114,5901197339,2317866981,1815286177,2346518646,1995667667,2130345064,5812979814,2283085439,5812996228,2256095175,1751248370,1721240702,2211824095,1728536671,5812992016,5813070612,2159968084,5813130686,1499178204,5813034273,1660339929,1905572376,1438174304,1286021768,5813023033,1751001365,2091789969,5813002077,2129611646,1973755375,2285813681,1471885748,2063854706,1637564462,2189022388,1438174338,5813027984,2065530259,5812986045,1653212967,5813078213,1810550032,1562120152,5813023881,5813078263,1503763552,2096525840,5812995586,5812994425,5812987924,1688924058,2401435296,884661350,1904583419,5813038604,1719746297,2027997296,5813018498,5812991885,5813037990,5813002424,1498746552,1874606508,1655238396,2336999725,1749033352,2091038685,1873625919,2027993252,1964581509,5813108261,5813039797,946390419,1468463081,1621142227,5812999846,1562227659,5812989026,1192507554,1623931398,5901225371,1628476465,1500917990,1695166397,2401150367,1688712195,1573440021,5813003536,2092062712,1500555271,5812996420,1878107121,1694496394,2183548192,2216910652,5812989382,1811577917,5812998957,1841499336,5812979783,5813034775,1283647649,5812995833,916370662,1440743192,1099010048,1656740247,2161647993,5813065112,5812992618,1070146061,1840121811,1996284762,2036498470,1531866895,1313905469,5812988959,1686026927,5813017646,2156649101,1566354821,5813038759,1654693980,1966648442,884661504,2436520099,2001056645,5812986972,5813037790,1286022101,5813038903,1068994212,1883098187,5812997031,1656364716,915696699,1783647366,1750454026,1905981799,1745273115,5813024094,1996276338,1747803113,2188270624,2284777374,2283771964,2093815177,5812993357,2374170073,1717756410,1846312261,2093431411,5813045768,5813061243,1999415279,1751096979,5813018119,5813033747,5813091082,5813005243,5812987589,1162905778,1933593754,1563617879,5813039535,1256386272,2032815776,1750902590,1381730321,5813025583,5813033835,1622859930,1406280995,1560471255,2182196710,1872124298,5813039123,2407945658,1592262161,1478620516,1439712335,2001422290,1132933054,2248021984,1658972262,2402450060,5813068189,1623650456,5813004745,2121119984,5812999477,1842267946,1407765779,1532928624,1996647762,1686712709,1655337173,5813056593,1683868547,2248947045,2058402281,1529085894,1872775428,1530899439,1656023681,1469891498,5813046122,1687050068,1749504150,1963877612,1505356659,1500162417,2129309327,1689328797,5812988405,2181488757,2406162924,2277701377,5813033723,5813037795,1808767510,5813056212,2125846639,5813078115,1871532839,1717411399,5813078114,1349499382,1468790547,1500158203,5813077684,5812994867,5813001550,1995590514,1654663456,5812998783,1533662775,5813003517,5812991337,1590461238,5813045448,1782244099,5813075395,1561559061,5813040315,1562931914,5813050443,5812999299,1687770608,5813022574,5813039502,1811919315,2312061045,1407757139,1872650691,2280724051,1502291034,1974087530,1376036364,1409026182,2129637904,977594832,5813133782,1406720961,2379241728,1876255327,1440402110,5813068653,2024245818,2401146033,1503987363,5813003016,2215205210,915696619,5813003435,5813041477,1375698772,2376910449,1132781911,5813077635,2128963940,5813033551,5813081213,2243895171,5812991046,2085673135,1563273220,1378090884,2156964857,1595253465,1656057916,1440696132,5813132579,5812987942,2025615467,2118382327,1410408294,2024272365,5812994487,2060345336,5813016209,1689152871,2001729289,2060344704,2058700750,1225890479,5813000511,1564352389,1814953746,5812991005,5812997348,1316716006,1901475587,1842927881,1501052182,5813038546,5813134706,2156519827,1812562435,2089057858,1314315452,1468152779,1689860552,5813004305,5813002022,1438515327,5812998585,1933909052,1934249887,2058376157,2148415825,2191711688,2316136396,5813039132,5901230859,1656014505,5813023127,5812986976,5812992017,2180784913,1687434359,5813096637,2277684527,1687079534,1816962418,2212549305,1653519769,1750743372,1690887935,1841174731,1008076549,5813057058,2024246148,1781942315,5813038446,1439184683,1844236961,2432151002,5813018632,5813018593,5813004828,5813042972,1870500807,1437759879,5813039371,1715253935,1779110125,1596755473,1348657162,5812999872,5813132447,2249714389,2312061664,1839785485,5813049242,5813023783,5813015301,1408828544,2373780839,1996280532,1872620129,5812993458,1721240571,5813133785,1717109639,1747798369,1599686170,1684710373,5813034501,5813041775,2118369504,5901196573,1721236164,2436891088,5813024722,5813017641,5812991865,1876596684,5813003198,5813078362,5813134789,1814332334,1933908336,1693803175,5901223691,1718745444,1623944414,1533239844,1966424592,5813002140,5813038490,1597606096,5812979109,5813078093,2182524994,5812994902,2284466784,1846287327,1843895701,2583587128,1997338282,2348561000,2312427432,5813023041,5813068950,2275949006,1687093099,5813057102,5813002565,2254502886,1964201443,5813018589,1563277160,1812562562,5813038752,2025593887,5813023817,2090132523,2124771755,5813049434,5813020649,5812992738,2058372255,1658999076,5901201758,1472590575,2531717931,5813004249,1850387882,2375866722,1623969940,2031723595,2311391945,1813986890,1686721312,5812986633,5813038777,2244555593,5813024451,2312069510,2311016539,2088026100,1781246563,1720071190,2029077413,5813077999,5813022613,1687783641,1903236942,2310342081,2311724063,2185194087,2344476804,5813132712,1469140571,1814958335,1564628545,1655345798,1813987473,2213564071,1563636121,1565383980,2217605269,1283276379,2117683608,2308710960,1592896173,5813041065,1437112312,2246239650,2340099260,2336995230,5813039374,1593616818,5813034651,1873224553,5813001082,1531918364,5813002432,1592943744,1780546879,1501517596,1838041169,2308646162,1749162676,1563855943,1686717182,5813060278,2092165398,2312061442,5812993036,5812993457,2120817758,5813078241,5813038475,5813056666,2221006570,5813023546,2340026876,1594890089,2149745451,5813060878,1779856681,5813038541,2278383644,2120136250,2343199299,1840467739,5813077865,2284807575,2492536784,2475454732,1870789706,2372084239,1686751696,2343156264,2342422247,5813038267,1810580351,2179762114,5812999437,1876631200,1596401558,1627112460,5812992235,1937695081,2028753383,5813002032,2404496363,5813039722,5813006183,2431473321,1845699184,1933896378,1838032536,1657801572,5901224333,2211521637,5813054499,5812992723,1379847347,2347559483,2130691134,1783298104,1656740700,1745963981,1319483566,2340712309,5813038905,2281371439,5813015930,1844313671,2149464834,2151411794,1967353179,1932466737,1963501366,2149719339,1842526788,1721581800,1838036863,1628477081,2283779961,5813017650,5813075779,1686070081,5813063192,1559439781,2432180871,5813038837,1996773419,2432155897,5813017860,1813202110,2182874516,2152491275,1623624129,5901231902,1620823217,2222397330,2436209437,7112615304,1596065645,1652548418,5813041375,2246308774,5813024744,2310359693,2059753549,5813000519,1717786453,5813033781,1684956434,5813023871,1564292319,5812998712,5813038906,2088423168,2375213707,1809458494,2401150401,2247689624,2178414590,1810551011,2181829180,1658484182,2312773821,2089053349,1685738074,2406533539,2214863872,1837717428,1656372783,1595391795,2400753470,5813130658,2399069460,5812999923,1621513552,2025619087,1717459194,2119457888,2366023053,5813050623,5813015188,1621176797,1448936559,1627790809,2057388508,1566407394,5813026034,1562288882,5813078290,5813001591,2342167835,2348219908,5813005666,5812998004,2241529876,1686427978,1869399561,5812990524,2304285962,7112614754,1869455870,1810550446,2400083913,5812988887,2147738016,5812990098,1534685724,1656398741,5813034475,2247949829,2370418236,1750570033,1994286272,5901225372,1652203469,1564006393,1811950126,5813020646,2280668038,2246671250,1750212459,1932211919,2334638926,1748467542,2090110724,1812566846,5813082939,2148049503,2060798098,1656058147,2181138590,1873656659,1749797577,5812990355,1687433915,1687804713,1688128959,2060431324,2118417323,1779558612,1746779719,2212208618,1749162427,5813001481,1623317979,2185935358,1871179081,2242902602,5812989289,1720899019,2346479755,5812988001,1838036922,5813023987,5901200665,2372801921,1593992578,5813038431,1656093410,5813000516,5813133000,1657120016,1659507432,1655034500,5813037791,5813038382,1718127469,1999401813,1687702265,5813078214,2150484350,1719164189,1746675840,1314669561,1811246114,2093171975,1781946209,5813000975,1620826621,5813002523,1966329732,2346160645,1873997304,1719163681,5812993925,1595395994,5812994060,2222715952,1779519905,1750565451,5813000594,1779899884,1717104823,2277342913,2179455426,1716413593,5901204675,5813025296,1593992598,2460794777,2283452403,1779506824,1906392527,1471933591,5812993934,5812994041,2023594721,1621522314,1500922137,1593948891,2466558043,1779511362,1593656205,5812990905,1562655335,1620827499,1844348020,1814341233,2338356274,5813026035,2436890966,5812993571,5813038666,1719522837,1841939610,5813045859,1596721601,5813039010,2463207135,1844330910,2471668812,1750902461,2214263703,2149802152,1595727903,1658825581,1565383248,1688499784,1906051860,2343804208,1747772834,5813066774,1657465217,1595382980,2183569998,2182214341,1689851475,2179118446,1689864214,2023581146,2400438479,2187325736,1657124205,2214237474,5812993459,1841939139,1718814572,2241201988,5813018077,2057729027,1656783036,2496224062,2436550143,1941774381,1812259993,2343497168,1807727436,2118058680,1596065504,5812994240,2467584598,1781604785,5812999500,1565720549,1597783309,2179809026,5813018529,1317777798,2406870893,1656779367,5901207095,2337699359,1780578152,1812976487,2467585289,1905736077,2150834255,5812989336,2274628555,5813018494,2182891953,1690201269,1716746142,1620481312,2057379019,2467243729,2308059127,2436895063,1441239823,2118081080,1874247787,1875037700,1997113551,1934698326,2183237483,1904717322,1904695413,2121504231,1411227744,1937772298,2371410849,1621509291,1938121770,1748852526,1628813848,1814336245,1808059613,1318114392,1875046343,1935044694,1843298973,1873333324,2029854401,1657124557,1873306797,1872637247,1748489576,5812989470,5812987018,2085668597,2304290227,1317773914,2214940679,1655717210,5812996338,1593652193,1597442123,1626089599,2028489982,1778147384,1931180286,1658134823,1717813180,1659511878,1780551317,2054629455,1780240736,1627108382,1810568018,1657806171,1682534118,1687476632,2497920308,1596065498,2149805998,2272573720,1968380862,2057388664,1656067031,1503650287,5813003833,2246666567,1690542682,1810896185,1530554338,5813005810,1840566687,1874360576,5812992289,1720899418,1812964263,1875037963,1998478132,1842280306,1627104245,2147712522,2214267909,1752262601,2304963685,2210153187,2086005821,2277338990,1532979951,1748855817,1720890958,2242224537,5813023544,1748140276,5812996247,1874014714,2525920614,2276997744,1935722166,1781591871,1410541029,1750216769,1844011242,1564697543,1748139502,1658825368,1626759083,2028831591,1656739926,1441234885,1564352184,1720891058,1651516352,1690546952,1781928985,1627099503,1657120027,1627790954,1658143429,1810209970,2149111552,2148770439,1657120245,1841585634,1813317888,1471597236,5813038306,1656071051,1717812886,2119799321,1931175946,1842984397,1657115734,1811249542,1781255141,1905058567,1501608269,1627790559,5813015675,2245988607,1744625035,2153195416,1874359903,1812981012,1779516126,1873673996,2088764226,5901214260,2214949355,5812991396,1874019609,2277697085,2246990636,1720886160,2274960451,1871847421,5813076764,2245989330,1905714316,1875038106,1810563788,1810908522,1967102834,1690546191,1719862833,1724988395,1813313897,1472274632,1471933630,1875387471,1874360267,1906388025,1904704230,1721236616,1690542426,1872305031,2240842714,1904355095,5812991478,5813042974,1535030453,1721231895,2028153326,5812997954,2307341817,2183556381,1689860171,1689165255,1874015206,2210153183,2243916598,1873686479,1874696475,1750203103,2501680073,5813018078,1992905220,2338044856,1659852993,1748856416,2085659875,1748860738,5813133191,1844006906,1811271172,2028835602,1905740004,1874701283,1843649372,1841253043,1998141585,1875046962,1992883608,2030194821,1659166942,5813049972,1780569487,1750569835,1875379185,1807044623,5813004255,1968470786,2306677208,1871602050,1874705188,2027807867,1503646648,1874368687,1688500239,2147737859,2275642874,1534685707,1998145286,1534349154,1875046513,1472279097,1813318126,1813321847,1996428133,1782287129,1871255746,1658829589,2272227925,1997459475,1965738312,1809187178,5813066367,2337371147,1874701344,1751252141,1996427669,1905049137,1658829619,1905050167,2028839270,1440221188,1565379582,2028498600,1658138943,1811616649,1874019271,2241538301,1719526156,1936080499,1935756269,1565724942,1842306997,2085322581,2028490294,1565715956,1750906559,1905062329] AS INP
MATCH (n:Neuron)
WHERE n.bodyId in INP
RETURN n.bodyId, n.size, apoc.convert.fromJsonMap(n.roiInfo)["LAL(R)"].pre AS LALR_PRE, apoc.convert.fromJsonMap(n.roiInfo)["LAL(R)"].post AS LALR_POST,
                            apoc.convert.fromJsonMap(n.roiInfo)["LAL(L)"].pre AS LALL_PRE,
                            apoc.convert.fromJsonMap(n.roiInfo)["LAL(L)"].post AS LALL_POST,
                            apoc.convert.fromJsonMap(n.roiInfo)["IPS(R)"].pre AS IPS_PRE,
                            apoc.convert.fromJsonMap(n.roiInfo)["IPS(R)"].post AS IPS_POST,
                            apoc.convert.fromJsonMap(n.roiInfo)["SPS(R)"].pre AS SPSR_PRE,
                            apoc.convert.fromJsonMap(n.roiInfo)["SPS(R)"].post AS SPSR_POST,
                            apoc.convert.fromJsonMap(n.roiInfo)["SPS(L)"].pre AS SPSL_PRE,
                            apoc.convert.fromJsonMap(n.roiInfo)["SPS(L)"].post AS SPSL_POST,
                            apoc.convert.fromJsonMap(n.roiInfo)["WED(R)"].pre AS WED_PRE,
                            apoc.convert.fromJsonMap(n.roiInfo)["WED(R)"].post AS WED_POST
'''

'''
def addWeights(queryResults):
    queryResults['Count'] = queryResults.groupby(['Input'])['Output'].transform('count')

    f = {
        'Input' : 'first',
        'Output': 'first',
        'nPre': 'sum',
        'Count' : 'first',
        'weight': 'sum',
        'LALR': 'sum',
        'LALL': 'sum',
        'IPS': 'sum',
        'SPSR': 'sum',
        'SPSL': 'sum',
        'WED': 'sum',
        'nPost': 'nunique',
        'input.type': 'last', 'input.instance': 'last', 'output.type': 'last', 'output.instance': 'last'
    }
    g = queryResults.groupby(['Input', 'Output'])
    v1 = g.agg(f)
    v2 = g.agg(lambda x: x.drop_duplicates(['Count'], keep='first').nPost.sum())
    fileDF = pd.concat([v1, v2.to_frame('nPost')], 1)


    fileDF = queryResults.groupby(['Input', 'Output'], as_index=False).agg(
         {'input.type': 'last', 'input.instance': 'last', 'nPre': 'sum', 'weight': 'sum',
          'LALR': 'sum',
          'LALL': 'sum', 'IPS': 'sum',  'SPSR': 'sum','SPSL': 'sum','WED': 'sum',
          'output.type': 'last', 'output.instance': 'last', 'Count': 'first', 'nPost': 'nunique'})

    fileDF = fileDF[['input.type', 'input.instance', 'Input', 'nPre', 'Count', 'weight',
                      'LALR', 'LALL', 'IPS',  'SPSR',
                      'SPSL', 'WED', 'output.type', 'output.instance', 'Output', 'nPost']]
    return fileDF
'''

'''
this version contains irrelevant ROIs
def DN_ROIInfo_OneHop(DNType):
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
            'WITH '+str(DNs)+' AS DNS'
            ' UNWIND DNS as DN'
            ' MATCH (input:`hemibrain_Neuron`)-[w1:ConnectsTo]->(Target:`hemibrain_Neuron`)'
            ' WHERE Target.bodyId = DN'
            ' RETURN input.bodyId, input.type, input.instance, input.status, w1.weight as '
            'input_weight, '
                            'apoc.convert.fromJsonMap(w1.roiInfo)["PB"].pre AS PB_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["PB"].post AS PB_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["EB"].pre AS EB_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["EB"].post AS EB_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["FB"].pre AS FB_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["FB"].post AS FB_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["NO"].pre AS NO_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["NO"].post AS NO_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["AB(R)"].pre AS ABR_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["AB(R)"].post AS ABR_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["AB(L)"].pre AS ABL_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["AB(L)"].post AS ABL_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["ROB(R)"].pre AS ROB_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["ROB(R)"].post AS ROB_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["RUB(R)"].pre AS RUB_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["RUB(R)"].post AS RUB_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["GA(R)"].pre AS GA_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["GA(R)"].post AS GA_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["BU(R)"].pre AS BUR_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["BU(R)"].post AS BUR_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["BU(L)"].pre AS BUL_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["BU(L)"].post AS BUL_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["LAL(R)"].pre AS LALR_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["LAL(R)"].post AS LALR_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["LAL(L)"].pre AS LALL_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["LAL(L)"].post AS LALL_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["IPS(R)"].pre AS IPS_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["IPS(R)"].post AS IPS_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["SPS(R)"].pre AS SPSR_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["SPS(R)"].post AS SPSR_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["SPS(L)"].pre AS SPSL_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["SPS(L)"].post AS SPSL_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["WED(R)"].pre AS WED_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["WED(R)"].post AS WED_POST,'
                             'w1.roiInfo, Target.bodyId, Target.type, Target.instance, Target.status'
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
            ' WHERE Target.bodyId = '+str(i)+' '
            ' RETURN input.bodyId, input.type, input.instance, input.status, w1.weight as '
            'input_weight, '
                            'apoc.convert.fromJsonMap(w1.roiInfo)["PB"].pre AS PB_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["PB"].post AS PB_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["EB"].pre AS EB_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["EB"].post AS EB_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["FB"].pre AS FB_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["FB"].post AS FB_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["NO"].pre AS NO_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["NO"].post AS NO_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["AB(R)"].pre AS ABR_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["AB(R)"].post AS ABR_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["AB(L)"].pre AS ABL_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["AB(L)"].post AS ABL_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["ROB(R)"].pre AS ROB_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["ROB(R)"].post AS ROB_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["RUB(R)"].pre AS RUB_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["RUB(R)"].post AS RUB_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["GA(R)"].pre AS GA_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["GA(R)"].post AS GA_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["BU(R)"].pre AS BUR_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["BU(R)"].post AS BUR_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["BU(L)"].pre AS BUL_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["BU(L)"].post AS BUL_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["LAL(R)"].pre AS LALR_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["LAL(R)"].post AS LALR_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["LAL(L)"].pre AS LALL_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["LAL(L)"].post AS LALL_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["IPS(R)"].pre AS IPS_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["IPS(R)"].post AS IPS_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["SPS(R)"].pre AS SPSR_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["SPS(R)"].post AS SPSR_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["SPS(L)"].pre AS SPSL_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["SPS(L)"].post AS SPSL_POST,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["WED(R)"].pre AS WED_PRE,'
                            'apoc.convert.fromJsonMap(w1.roiInfo)["WED(R)"].post AS WED_POST,'
                            'w1.roiInfo, Target.bodyId, Target.type, Target.instance, Target.status')

            queryResults1 = client.fetch_custom(query2)
            queryResults = queryResults.append(queryResults1)
    queryResults2 = queryResults.reset_index(drop=True)
    return queryResults2

def removeIrrelevant(queryResults):

    queryResults = queryResults.fillna({'PB_PRE':0, 'PB_POST':0, 'EB_PRE':0, 'EB_POST':0, 'FB_PRE':0,
           'FB_POST':0, 'NO_PRE':0, 'NO_POST':0, 'ABR_PRE':0, 'ABR_POST':0, 'ABL_PRE':0,
           'ABL_POST':0, 'ROB_PRE':0, 'ROB_POST':0, 'RUB_PRE':0, 'RUB_POST':0, 'GA_PRE':0,
           'GA_POST':0, 'BUR_PRE':0, 'BUR_POST':0, 'BUL_PRE':0, 'BUL_POST':0, 'LALR_PRE':0,
           'LALR_POST':0, 'LALL_PRE':0, 'LALL_POST':0, 'IPS_PRE':0, 'IPS_POST':0, 'SPSR_PRE':0,
           'SPSR_POST':0, 'SPSL_PRE':0, 'SPSL_POST':0, 'WED_PRE':0, 'WED_POST':0})

    cols = ['PB_PRE', 'PB_POST', 'EB_PRE', 'EB_POST', 'FB_PRE',
           'FB_POST', 'NO_PRE', 'NO_POST', 'ABR_PRE', 'ABR_POST', 'ABL_PRE',
           'ABL_POST', 'ROB_PRE', 'ROB_POST', 'RUB_PRE', 'RUB_POST', 'GA_PRE',
           'GA_POST', 'BUR_PRE', 'BUR_POST', 'BUL_PRE', 'BUL_POST', 'LALR_PRE',
           'LALR_POST', 'LALL_PRE', 'LALL_POST', 'IPS_PRE', 'IPS_POST', 'SPSR_PRE',
           'SPSR_POST', 'SPSL_PRE', 'SPSL_POST', 'WED_PRE', 'WED_POST']
    queryResults2 = queryResults[(queryResults[cols] != 0).any(axis=1)]

    queryResults3 = queryResults2.drop(queryResults2.index[queryResults2['input.status'] == 'Assign'])
    queryResults4 = queryResults3.drop(queryResults3.index[queryResults3['input.status'] == 'Orphan'])
    queryResults5 = queryResults4.drop(queryResults4.index[queryResults4['input.status'] == 'Unimportant'])

    return queryResults5


def comparePrePost(queryResults):

    for index, row in queryResults.iterrows():
        preV = row["PB_PRE"]
        postV = row["PB_POST"]
        if postV < preV:
            queryResults.loc[index, 'PB_POST'] = preV

        preV1 = row["EB_PRE"]
        postV1 = row["EB_POST"]
        if postV1 < preV1:
            queryResults.loc[index, 'EB_POST'] = preV1

        preV2 = row["FB_PRE"]
        postV2 = row["FB_POST"]
        if postV2 < preV2:
            queryResults.loc[index, 'FB_POST'] = preV2

        preV3 = row["NO_PRE"]
        postV3 = row["NO_POST"]
        if postV3 < preV3:
            queryResults.loc[index, 'NO_POST'] = preV3

        preV4 = row["ABR_PRE"]
        postV4 = row["ABR_POST"]
        if postV4 < preV4:
            queryResults.loc[index, 'ABR_POST'] = preV4

        preV5 = row["ABL_PRE"]
        postV5 = row["ABL_POST"]
        if postV5 < preV5:
            queryResults.loc[index, 'ABL_POST'] = preV5

        preV6 = row["ROB_PRE"]
        postV6 = row["ROB_POST"]
        if postV6 < preV6:
            queryResults.loc[index, 'ROB_POST'] = preV6

        preV7 = row["RUB_PRE"]
        postV7 = row["RUB_POST"]
        if postV7 < preV7:
            queryResults.loc[index, 'RUB_POST'] = preV7

        preV8 = row["GA_PRE"]
        postV8 = row["GA_POST"]
        if postV8 < preV8:
            queryResults.loc[index, 'GA_POST'] = preV8

        preV9 = row["BUR_PRE"]
        postV9 = row["BUR_POST"]
        if postV9 < preV9:
            queryResults.loc[index, 'BUR_POST'] = preV9

        preV10 = row["BUL_PRE"]
        postV10 = row["BUL_POST"]
        if postV10 < preV10:
            queryResults.loc[index, 'BUL_POST'] = preV10

        preV11 = row["LALR_PRE"]
        postV11 = row["LALR_POST"]
        if postV11 < 11:
            queryResults.loc[index, 'LALR_POST'] = preV11

        preV12 = row["LALL_PRE"]
        postV12 = row["LALL_POST"]
        if postV12 < preV12:
            queryResults.loc[index, 'LALL_POST'] = preV12

        preV13 = row["IPS_PRE"]
        postV13 = row["IPS_POST"]
        if postV13 < preV13:
            queryResults.loc[index, 'IPS_POST'] = preV13

        preV14 = row["SPSR_PRE"]
        postV14 = row["SPSR_POST"]
        if postV14 < preV14:
            queryResults.loc[index, 'SPSR_POST'] = preV14

        preV15 = row["SPSL_PRE"]
        postV15 = row["SPSL_POST"]
        if postV15 < preV15:
            queryResults.loc[index, 'SPSL_POST'] = preV15

        preV16 = row["WED_PRE"]
        postV16 = row["WED_POST"]
        if postV16 < preV16:
            queryResults.loc[index, 'WED_POST'] = preV16

    toDrop = ['PB_PRE', 'EB_PRE', 'FB_PRE',
              'NO_PRE', 'ABR_PRE', 'ABL_PRE',
              'ROB_PRE', 'RUB_PRE', 'GA_PRE',
              'BUR_PRE', 'BUL_PRE', 'LALR_PRE',
              'LALL_PRE', 'IPS_PRE', 'SPSR_PRE',
              'SPSL_PRE', 'WED_PRE']

    queryResults2 = queryResults.drop(toDrop, axis=1)

    queryResults2 = queryResults2.rename({'PB_POST': 'PB'}, axis=1)
    queryResults2 = queryResults2.rename({'EB_POST': 'EB'}, axis=1)
    queryResults2 = queryResults2.rename({'NO_POST': 'NO'}, axis=1)
    queryResults2 = queryResults2.rename({'FB_POST': 'FB'}, axis=1)
    queryResults2 = queryResults2.rename({'ABR_POST': 'ABR'}, axis=1)
    queryResults2 = queryResults2.rename({'ABL_POST': 'ABL'}, axis=1)
    queryResults2 = queryResults2.rename({'ROB_POST': 'ROB'}, axis=1)
    queryResults2 = queryResults2.rename({'RUB_POST': 'RUB'}, axis=1)
    queryResults2 = queryResults2.rename({'GA_POST': 'GA'}, axis=1)
    queryResults2 = queryResults2.rename({'BUR_POST': 'BUR'}, axis=1)
    queryResults2 = queryResults2.rename({'BUL_POST': 'BUL'}, axis=1)
    queryResults2 = queryResults2.rename({'LALR_POST': 'LALR'}, axis=1)
    queryResults2 = queryResults2.rename({'LALL_POST': 'LALL'}, axis=1)
    queryResults2 = queryResults2.rename({'IPS_POST': 'IPS'}, axis=1)
    queryResults2 = queryResults2.rename({'SPSR_POST': 'SPSR'}, axis=1)
    queryResults2 = queryResults2.rename({'SPSL_POST': 'SPSL'}, axis=1)
    queryResults2 = queryResults2.rename({'WED_POST': 'WED'}, axis=1)

    return queryResults2


def addPercentageColumns(queryResults):
    pb_per = []
    eb_per = []
    fb_per = []
    no_per = []
    abr_per = []
    abl_per = []
    rob_per = []
    rub_per = []
    ga_per = []
    bur_per = []
    bul_per = []
    lalr_per = []
    lall_per = []
    ips_per = []
    spsr_per = []
    spsl_per = []
    wed_per = []
    totalROI = []
    ROI_per = []

    for index, row in queryResults.iterrows():
        pb = queryResults.loc[index, 'PB']
        eb = queryResults.loc[index, 'EB']
        fb = queryResults.loc[index, 'FB']
        no = queryResults.loc[index, 'NO']
        abr = queryResults.loc[index, 'ABR']
        abl = queryResults.loc[index, 'ABL']
        rob = queryResults.loc[index, 'ROB']
        rub = queryResults.loc[index, 'RUB']
        ga = queryResults.loc[index, 'GA']
        bur = queryResults.loc[index, 'BUR']
        bul = queryResults.loc[index, 'BUL']
        lalr = queryResults.loc[index, 'LALR']
        lall = queryResults.loc[index, 'LALL']
        ips = queryResults.loc[index, 'IPS']
        spsr = queryResults.loc[index, 'SPSR']
        spsl = queryResults.loc[index, 'SPSL']
        wed = queryResults.loc[index, 'WED']
        weight = queryResults.loc[index, 'weight']

        summedROI = pb + eb + fb + no + abr + abl + rob + rub + ga + bur + bul + lalr + lall + ips + spsr + spsl + wed
        totalROI.append(summedROI)
        roiper = (summedROI/weight) * 100
        ROI_per.append(roiper)

        if pb == 0:
            pb_per.append(0)
        else:
            roi_percent = (pb / weight) * 100
            pb_per.append(roi_percent)

        if eb == 0:
            eb_per.append(0)
        else:
            roi_percent = (eb / weight) * 100
            eb_per.append(roi_percent)

        if fb == 0:
            fb_per.append(0)
        else:
            roi_percent = (fb / weight) * 100
            fb_per.append(roi_percent)

        if no == 0:
            no_per.append(0)
        else:
            roi_percent = (no / weight) * 100
            no_per.append(roi_percent)

        if abr == 0:
            abr_per.append(0)
        else:
            roi_percent = (abr / weight) * 100
            abr_per.append(roi_percent)

        if abl == 0:
            abl_per.append(0)
        else:
            roi_percent = (abl / weight) * 100
            abl_per.append(roi_percent)

        if rob == 0:
            rob_per.append(0)
        else:
            roi_percent = (rob / weight) * 100
            rob_per.append(roi_percent)

        if rub == 0:
            rub_per.append(0)
        else:
            roi_percent = (rub / weight) * 100
            rub_per.append(roi_percent)

        if ga == 0:
            ga_per.append(0)
        else:
            roi_percent = (ga / weight) * 100
            ga_per.append(roi_percent)

        if bur == 0:
            bur_per.append(0)
        else:
            roi_percent = (bur / weight) * 100
            bur_per.append(roi_percent)

        if bul == 0:
            bul_per.append(0)
        else:
            roi_percent = (bul / weight) * 100
            bul_per.append(roi_percent)

        if lalr == 0:
            lalr_per.append(0)
        else:
            roi_percent = (lalr / weight) * 100
            lalr_per.append(roi_percent)

        if lall == 0:
            lall_per.append(0)
        else:
            roi_percent = (lall / weight) * 100
            lall_per.append(roi_percent)

        if ips == 0:
            ips_per.append(0)
        else:
            roi_percent = (ips / weight) * 100
            ips_per.append(roi_percent)

        if spsr == 0:
            spsr_per.append(0)
        else:
            roi_percent = (spsr / weight) * 100
            spsr_per.append(roi_percent)

        if spsl == 0:
            spsl_per.append(0)
        else:
            roi_percent = (spsl / weight) * 100
            spsl_per.append(roi_percent)

        if wed == 0:
            wed_per.append(0)
        else:
            roi_percent = (wed / weight) * 100
            wed_per.append(roi_percent)

    queryResults['PB_PER'] = pb_per
    queryResults['EB_PER'] = eb_per
    queryResults['FB_PER'] = fb_per
    queryResults['NO_PER'] = no_per
    queryResults['ABR_PER'] = abr_per
    queryResults['ABL_PER'] = abl_per
    queryResults['ROB_PER'] = rob_per
    queryResults['RUB_PER'] = rub_per
    queryResults['GA_PER'] = ga_per
    queryResults['BUR_PER'] = bur_per
    queryResults['BUL_PER'] = bul_per
    queryResults['LALR_PER'] = lalr_per
    queryResults['LALL_PER'] = lall_per
    queryResults['IPS_PER'] = ips_per
    queryResults['SPSR_PER'] = spsr_per
    queryResults['SPSL_PER'] = spsl_per
    queryResults['WED_PER'] = wed_per
    queryResults['CX_Weight'] = totalROI
    queryResults['CX_PER'] = ROI_per
    columns = ['input.type', 'input.instance', 'Input',
       'weight', 'PB', 'PB_PER', 'EB', 'EB_PER', 'FB', 'FB_PER', 'NO', 'NO_PER', 'ABR', 'ABR_PER',
        'ABL', 'ABL_PER', 'ROB', 'ROB_PER', 'RUB', 'RUB_PER', 'GA', 'GA_PER', 'BUR', 'BUR_PER',
        'BUL', 'BUL_PER', 'LALR', 'LALR_PER', 'LALL', 'LALL_PER', 'IPS', 'IPS_PER', 'SPSR', 'SPSR_PER',
        'SPSL', 'SPSL_PER', 'WED', 'WED_PER', 'CX_Weight', 'CX_PER', 'output.type', 'output.instance',
       'Output']

    queryResults = queryResults.reindex(columns=columns)

    return queryResults

def reorgQuery(queryResults):
    columns = ['input.bodyId', 'input.type', 'input.instance', 'input.status', "Input",
               'weight', 'PB', 'EB', 'FB', 'NO', 'ABR',  'ABL', 'ROB', 'RUB',
                'GA', 'BUR',  'BUL',  'LALR', 'LALL', 'IPS',  'SPSR',
                'SPSL','WED', 'output.bodyId', 'output.type', 'output.instance',
               'output.status', 'Output']

    reorgDF = pd.DataFrame()
    row1 = []  # inter -> GFIN

    for index, row in queryResults.iterrows():
        row1 = [row['input.bodyId'], row['input.type'], row['input.instance'],
                row['input.status'], None, row['input_weight'],
                row['PB'], row['EB'], row['FB'], row['NO'], row['ABR'], row['ABL'],
                row['ROB'], row['RUB'], row['GA'], row['BUR'], row['BUL'], row['LALR'],
                row['LALL'], row['IPS'], row['SPSR'], row['SPSL'], row['WED'], row['Target.bodyId'],
                row['Target.type'], row['Target.instance'], row['Target.status'], None]

        reorgDF = reorgDF.append([row1], ignore_index=True)

    reorgDF.columns = columns

    for index, row in reorgDF.iterrows():
        if row['input.type'] is not None:
            reorgDF.loc[index, 'Input'] = row['input.type']
        elif row['input.instance'] is not None:
            reorgDF.loc[index, 'Input'] = row['input.instance']
        else:
            reorgDF.loc[index, 'Input'] = row['input.bodyId']

        if row['output.type'] is not None:
            reorgDF.loc[index, 'Output'] = row['output.type']
        elif row['output.instance'] is not None:
            reorgDF.loc[index, 'Output'] = row['output.instance']
        else:
            reorgDF.loc[index, 'Output'] = row['output.bodyId']

    reorgDF = reorgDF.drop_duplicates()
    return reorgDF

def addWeights(queryResults):

    fileDF = queryResults.groupby(['Input', 'Output'], as_index=False).agg(
        {'input.type': 'last', 'input.instance': 'last', 'weight': 'sum',
         'PB': 'sum', 'EB': 'sum', 'FB': 'sum', 'NO': 'sum', 'ABR': 'sum',  'ABL': 'sum',
         'ROB': 'sum', 'RUB': 'sum', 'GA': 'sum', 'BUR': 'sum',  'BUL': 'sum',  'LALR': 'sum',
         'LALL': 'sum', 'IPS': 'sum',  'SPSR': 'sum','SPSL': 'sum','WED': 'sum',
         'output.type': 'last', 'output.instance': 'last'})
    fileDF = fileDF[['input.type', 'input.instance', "Input", 'weight',
                     'PB', 'EB', 'FB', 'NO', 'ABR',  'ABL', 'ROB', 'RUB',
                     'GA', 'BUR',  'BUL',  'LALR', 'LALL', 'IPS',  'SPSR',
                     'SPSL', 'WED', 'output.type', 'output.instance', 'Output']]
    return fileDF




def addPercentageColumns2(queryResults):
    pb_per = []
    eb_per = []
    fb_per = []
    no_per = []
    abr_per = []
    abl_per = []
    rob_per = []
    rub_per = []
    ga_per = []
    bur_per = []
    bul_per = []
    lalr_per = []
    lall_per = []
    ips_per = []
    spsr_per = []
    spsl_per = []
    wed_per = []

    for index, row in queryResults.iterrows():
        pb = queryResults.loc[index, 'PB']
        eb = queryResults.loc[index, 'EB']
        fb = queryResults.loc[index, 'FB']
        no = queryResults.loc[index, 'NO']
        abr = queryResults.loc[index, 'ABR']
        abl = queryResults.loc[index, 'ABL']
        rob = queryResults.loc[index, 'ROB']
        rub = queryResults.loc[index, 'RUB']
        ga = queryResults.loc[index, 'GA']
        bur = queryResults.loc[index, 'BUR']
        bul = queryResults.loc[index, 'BUL']
        lalr = queryResults.loc[index, 'LALR']
        lall = queryResults.loc[index, 'LALL']
        ips = queryResults.loc[index, 'IPS']
        spsr = queryResults.loc[index, 'SPSR']
        spsl = queryResults.loc[index, 'SPSL']
        wed = queryResults.loc[index, 'WED']
        weight = queryResults.loc[index, 'weight']

        if pb == 0:
            pb_per.append(0)
        else:
            roi_percent = (pb / weight) * 100
            pb_per.append(roi_percent)

        if eb == 0:
            eb_per.append(0)
        else:
            roi_percent = (eb / weight) * 100
            eb_per.append(roi_percent)

        if fb == 0:
            fb_per.append(0)
        else:
            roi_percent = (fb / weight) * 100
            fb_per.append(roi_percent)

        if no == 0:
            no_per.append(0)
        else:
            roi_percent = (no / weight) * 100
            no_per.append(roi_percent)

        if abr == 0:
            abr_per.append(0)
        else:
            roi_percent = (abr / weight) * 100
            abr_per.append(roi_percent)

        if abl == 0:
            abl_per.append(0)
        else:
            roi_percent = (abl / weight) * 100
            abl_per.append(roi_percent)

        if rob == 0:
            rob_per.append(0)
        else:
            roi_percent = (rob / weight) * 100
            rob_per.append(roi_percent)

        if rub == 0:
            rub_per.append(0)
        else:
            roi_percent = (rub / weight) * 100
            rub_per.append(roi_percent)

        if ga == 0:
            ga_per.append(0)
        else:
            roi_percent = (ga / weight) * 100
            ga_per.append(roi_percent)

        if bur == 0:
            bur_per.append(0)
        else:
            roi_percent = (bur / weight) * 100
            bur_per.append(roi_percent)

        if bul == 0:
            bul_per.append(0)
        else:
            roi_percent = (bul / weight) * 100
            bul_per.append(roi_percent)

        if lalr == 0:
            lalr_per.append(0)
        else:
            roi_percent = (lalr / weight) * 100
            lalr_per.append(roi_percent)

        if lall == 0:
            lall_per.append(0)
        else:
            roi_percent = (lall / weight) * 100
            lall_per.append(roi_percent)

        if ips == 0:
            ips_per.append(0)
        else:
            roi_percent = (ips / weight) * 100
            ips_per.append(roi_percent)

        if spsr == 0:
            spsr_per.append(0)
        else:
            roi_percent = (spsr / weight) * 100
            spsr_per.append(roi_percent)

        if spsl == 0:
            spsl_per.append(0)
        else:
            roi_percent = (spsl / weight) * 100
            spsl_per.append(roi_percent)

        if wed == 0:
            wed_per.append(0)
        else:
            roi_percent = (wed / weight) * 100
            wed_per.append(roi_percent)

    queryResults['PB_PER'] = pb_per
    queryResults['EB_PER'] = eb_per
    queryResults['FB_PER'] = fb_per
    queryResults['NO_PER'] = no_per
    queryResults['ABR_PER'] = abr_per
    queryResults['ABL_PER'] = abl_per
    queryResults['ROB_PER'] = rob_per
    queryResults['RUB_PER'] = rub_per
    queryResults['GA_PER'] = ga_per
    queryResults['BUR_PER'] = bur_per
    queryResults['BUL_PER'] = bul_per
    queryResults['LALR_PER'] = lalr_per
    queryResults['LALL_PER'] = lall_per
    queryResults['IPS_PER'] = ips_per
    queryResults['SPSR_PER'] = spsr_per
    queryResults['SPSL_PER'] = spsl_per
    queryResults['WED_PER'] = wed_per

    columns = ['input.bodyId', 'input.type', 'input.instance', 'input.status',
       'weight', 'PB', 'PB_PER', 'EB', 'EB_PER', 'FB', 'FB_PER', 'NO', 'NO_PER', 'ABR', 'ABR_PER',
        'ABL', 'ABL_PER', 'ROB', 'ROB_PER', 'RUB', 'RUB_PER', 'GA', 'GA_PER', 'BUR', 'BUR_PER',
        'BUL', 'BUL_PER', 'LALR', 'LALR_PER', 'LALL', 'LALL_PER', 'IPS', 'IPS_PER', 'SPSR', 'SPSR_PER',
        'SPSL', 'SPSL_PER', 'WED', 'WED_PER', 'Target.bodyId', 'Target.type', 'Target.instance',
       'Target.status']

    queryResults = queryResults.reindex(columns=columns)

    return queryResults'''
