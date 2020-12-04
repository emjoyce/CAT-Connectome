"""
Emily Tenshaw
CAT-Card
12/2/2020

**Always check which server is connected and up to date
NeuPrint queries that are relevant to a target body ID and a target ROI.
They have different "hop" amounts - number of interneurons between target and input
"""

import neuprint as neu
import pandas as pd
import numpy as np
from collections import defaultdict
import statistics

# 13000 server
# client = neu.Client('emdata1.int.janelia.org:13000/?dataset=hemibrain', token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtaWx5dGVuc2hhd0BnbWFpbC5jb20iLCJsZXZlbCI6InJlYWR3cml0ZSIsImltYWdlLXVybCI6Imh0dHBzOi8vbGg0Lmdvb2dsZXVzZXJjb250ZW50LmNvbS8tdmhYaGxhYjFxcFEvQUFBQUFBQUFBQUkvQUFBQUFBQUFBQUEvQUNIaTNyZWcwN21uZHVkQ2RpWVRkeFJGWGdONmlnMENOZy9waG90by5qcGc_c3o9NTA_c3o9NTAiLCJleHAiOjE3NjM3NzA2MTR9.xNL4c8vg8tN4KKrLUiHEgy_9Wlf4tDoGCXEKlLs8lLU')
# test server
client = neu.Client('neuprint-test.janelia.org', dataset='hemibrain:v1.0.1',
                    token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtaWx5dGVuc2hhd0BnbWFpbC5jb20iLCJsZXZlbCI6InJlYWR3cml0ZSIsImltYWdlLXVybCI6Imh0dHBzOi8vbGg0Lmdvb2dsZXVzZXJjb250ZW50LmNvbS8tdmhYaGxhYjFxcFEvQUFBQUFBQUFBQUkvQUFBQUFBQUFBQUEvQUtGMDVuRFRUOHBhUHFCT3dMNk5nblZHVENIR2xGWEp0QS9waG90by5qcGc_c3o9NTA_c3o9NTAiLCJleHAiOjE3NjQ5ODIyODh9.UjUHbKZQpReYOShvtKMzZWxJE-saJ4FWN6iD9hAcZaQ')

'''
These MAIN functions should be run by user and are dependent on other functions in the file
'''
# main functions
def twoHopMain():
    print('\nUse the answers in parentheses to answer, otherwise will not run properly'
          '\nExample Circuit: x -> y -> target\n')
    target = input('\nEnter the targeted body ID:   ')
    ROI = input('\nEnter the targeted ROI:   ')
    ROI = str(ROI)

    print("\nrunning two hop query...")
    # original results = queryResults
    queryResults = Target_ROI_TwoHop(target, ROI)
    if queryResults.empty:
        print("\nEmpty data frame, try a different query")
        return
    print1 = input('\nWould you like to save query results? (y/n):   ')
    toCSV(print1, queryResults)

    print('finding ROI synapse weight for input body query...')
    # minmax is inputBodies with the PRE/POST changed to roi_connectivity_weight
    queryResults2 = compareMinMax(queryResults)
    print4 = input('\nquery removes the PRE and POST columns from the input bodies query and changes the '
                   'column to roi_connectivity_weight, returning whichever has the higher value'
                   '\nWould you like to save the updated results? (y/n):   ')
    toCSV(print4, queryResults2)

    print('\nrunning statistics for threshold values...')
    statistics = findStatistics2(queryResults2)
    print('\n' + str(statistics))

    displayOptions2(queryResults2, statistics, ROI)

    return


def threeHopMain():
    print('\nUse the answers in parentheses to answer, otherwise will not run properly'
          '\nExample Circuit: x -> y -> z -> target\n')
    target = input('\nEnter the targeted body ID:   ')
    ROI = input('\nEnter the targeted ROI:   ')
    ROI = str(ROI)

    print("\nrunning three hop query...")
    # original results = queryResults
    queryResults = Target_ROI_ThreeHop(target, ROI)
    if queryResults.empty:
        print("\nEmpty data frame, try a different query")
        return
    print1 = input('\nWould you like to save query results? (y/n):   ')
    toCSV(print1, queryResults)

    print('\ngetting input bodies...')
    # original input bodies = inputBodies
    inputBodies = getInputBodies(queryResults, ROI)
    print2 = input('\nWould you like to save the input body query results? (y/n):   ')
    toCSV(print2, inputBodies)

    print('\nfinding mismatched bodies...'
          '\nquery removes bodies that are not annotated from original ROI two hop query')
    # queryResults2 is queryResults with mismatched bodies removed
    queryResults2, inputBodies2 = mismatchedBodies(queryResults, inputBodies)
    print3 = input('\nWould you like to save the mismatched body results? (y/n):   ')
    toCSV(print3, queryResults2)

    print('finding ROI synapse weight for input body query...')
    # minmax is inputBodies with the PRE/POST changed to roi_connectivity_weight
    minmax = compareMinMax(inputBodies2)
    print4 = input('\nquery removes the PRE and POST columns from the input bodies query and changes the '
                   'column to roi_connectivity_weight, returning whichever has the higher value'
                   '\nWould you like to save the updated results? (y/n):   ')
    toCSV(print4, minmax)

    print('\nrunning statistics for threshold values...')
    statistics = findStatistics(queryResults2, minmax)
    print('\n' + str(statistics))

    displayOptions(queryResults2, minmax, statistics, ROI)

    return


def oneHopMain():
    print('\nUse the answers in parentheses to answer, otherwise will not run properly'
          '\nExample Circuit: x -> y -> target\n')
    target = input('\nEnter the targeted body ID:   ')
    ROI = input('\nEnter the targeted ROI:   ')
    ROI = str(ROI)

    print("\nrunning one hop query...")
    # original results = queryResults
    queryResults = Target_ROI_OneHop(target, ROI)
    if queryResults.empty:
        print("\nEmpty data frame, try a different query")
        return
    print1 = input('\nWould you like to save query results? (y/n):   ')
    toCSV(print1, queryResults)

    print('finding ROI synapse weight for input body query...')
    # minmax is inputBodies with the PRE/POST changed to roi_connectivity_weight
    queryResults2 = compareMinMax(queryResults)
    print4 = input('\nquery removes the PRE and POST columns from the input bodies query and changes the '
                   'column to roi_connectivity_weight, returning whichever has the higher value'
                   '\nWould you like to save the updated results? (y/n):   ')
    toCSV(print4, queryResults2)

    print('\nrunning statistics for threshold values...')
    statistics = findStatistics2(queryResults2)
    print('\n' + str(statistics))

    displayOptions3(queryResults2, statistics, ROI)

    return



'''
Following functions help the main functions to run
Can be run individually to check for data breaks or errors
'''

# takes a bodyID and an ROI and returns a three body connection x->y->z
# the first body, x, receives input from a given ROI
# another query can be run to find out which bodies input to body x in the given ROI
# including it now would cause the query to break
# Hop Queries
def Target_ROI_ThreeHop(target, roi):
    target = str(target)
    query = (
            'MATCH (interneuron:`hemibrain_Neuron`)-[w2:ConnectsTo]->(TargetInput:`hemibrain_Neuron`)-[w3:ConnectsTo]->(Target:`hemibrain_Neuron`)'
            ' WHERE Target.bodyId = ' + target + ' AND NOT apoc.convert.fromJsonMap(interneuron.roiInfo)["' + roi + '"].post IS NULL'
                                                                                                                    ' RETURN interneuron.bodyId, interneuron.type, interneuron.instance, interneuron.status, w2.weight as '
                                                                                                                    'interneuron_weight, TargetInput.bodyId, TargetInput.type, TargetInput.instance, TargetInput.status, w3.weight as Target_weight, '
                                                                                                                    'Target.bodyId, Target.type, Target.instance, Target.status'
    )
    queryResults = client.fetch_custom(query)
    return queryResults


def Target_ROI_TwoHop(target, roi):
    target = str(target)
    query = (
            'MATCH (input:`hemibrain_Neuron`)-[w1:ConnectsTo]->(TargetInput:`hemibrain_Neuron`)-[w2:ConnectsTo]->(Target:`hemibrain_Neuron`)'
            ' WHERE Target.bodyId = ' + target + ' AND NOT apoc.convert.fromJsonMap(w1.roiInfo)["' + roi + '"] IS NULL'
                                                                                                           ' RETURN input.bodyId, input.type, input.instance, input.status, w1.weight as '
                                                                                                           'input_weight, apoc.convert.fromJsonMap(w1.roiInfo)["' + roi + '"].pre as PRE, '
                                                                                                                                                                          ' apoc.convert.fromJsonMap(w1.roiInfo)["' + roi + '"].post as POST, TargetInput.bodyId, TargetInput.type, '
                                                                                                                                                                                                                            'TargetInput.instance, TargetInput.status, w2.weight as Target_weight, '
                                                                                                                                                                                                                            'Target.bodyId, Target.type, Target.instance, Target.status'
    )
    queryResults = client.fetch_custom(query)
    return queryResults


def Target_ROI_OneHop(target, roi):
    target = str(target)
    query = (
            'MATCH (input:`hemibrain_Neuron`)-[w1:ConnectsTo]->(Target:`hemibrain_Neuron`)'
            ' WHERE Target.bodyId = ' + target + ' AND NOT apoc.convert.fromJsonMap(w1.roiInfo)["' + roi + '"] IS NULL'
                                                                                                           ' RETURN input.bodyId, input.type, input.instance, input.status, w1.weight as '
                                                                                                           'input_weight, apoc.convert.fromJsonMap(w1.roiInfo)["' + roi + '"].pre as PRE, '
                                                                                                                                                                          ' apoc.convert.fromJsonMap(w1.roiInfo)["' + roi + '"].post as POST, '
                                                                                                                                                                                                                            'Target.bodyId, Target.type, Target.instance, Target.status'
    )
    queryResults = client.fetch_custom(query)
    return queryResults


# Input body functions
def getInputBodies(queryResults, roi):
    bodies = list(queryResults['interneuron.bodyId'])
    query = (
            'WITH ' + str(bodies) + ' AS TARGETS'
                                    ' MATCH (input:`hemibrain_Neuron`)-[w:ConnectsTo]->(interneuron:`hemibrain_Neuron`)'
                                    ' WHERE interneuron.bodyId in TARGETS AND NOT apoc.convert.fromJsonMap(w.roiInfo)["' + roi + '"] IS NULL'
                                                                                                                                 ' RETURN input.bodyId, input.type, input.instance, input.status, apoc.convert.fromJsonMap(w.roiInfo)["' + roi + '"].pre as PRE, '
                                                                                                                                                                                                                                                 ' apoc.convert.fromJsonMap(w.roiInfo)["' + roi + '"].post as POST, w.weight as total_weight, interneuron.bodyId,'
                                                                                                                                                                                                                                                                                                  'interneuron.type, interneuron.instance, interneuron.status'
    )
    queryResults = client.fetch_custom(query)
    return queryResults


# query 1 pulls anything post synaptic in ROI - has to use interneuron.post because there is nothing in the query
# to signify the input of that neuron is in the ROI
# query 2 pulls any connection from the interneurons in query1 and pulls any input bodies in the given ROI.
# query2 uses the ROI of the connection because it is what makes sure that the synapse connections are in the ROI needed
# ROI weight and total weight can be different.
# This function takes away any mismatched bodies - has been deleting connections for bodies receiving input from
# bodies with no annotation  ex: 1251468324 -> 5813078603 & their subsequent connections

# also used after setting a threshold so that the cytoscape graph isn't broken
def mismatchedBodies(queryResults, inputBodies):
    qInter = list(queryResults['interneuron.bodyId'])
    inputInter = list(inputBodies['interneuron.bodyId'])
    diff = list(set(qInter).symmetric_difference(set(inputInter)))
    queryResults = queryResults[~queryResults['interneuron.bodyId'].isin(diff)]
    inputBodies = inputBodies[~inputBodies['interneuron.bodyId'].isin(diff)]
    print('Mismatched bodies removed: ' + str(diff))
    return queryResults, inputBodies


def compareMinMax(inputBodies):
    if 'PRE' not in inputBodies.columns:
        raise Exception("No column in DF called PRE; compare Min/Max already run")  # error if PRE doesn't exist
    for index, row in inputBodies.iterrows():
        preV = row["PRE"]
        postV = row["POST"]
        if preV is None:
            inputBodies.loc[index, 'POST'] = postV
        elif postV is None:
            inputBodies.loc[index, 'POST'] = preV
        elif postV < preV:
            inputBodies.loc[index, 'POST'] = preV  # replace post value with pre if pre is higher
            # replace post value with pre if pre is higher
    newDF = inputBodies  # create a new dataframe, remove pre column, rename post column
    newDF = newDF.drop("PRE", 1)
    newDF = newDF.rename({'POST': 'roi_connectivity_weight'}, axis=1)  # rename column name
    # save new dataframe as original filename
    if "Unnamed: 0" in newDF.columns:
        newDF = newDF.drop("Unnamed: 0", 1)  # drop unnecessary column
    return newDF


# splits based on the input type
def splitBasedOnInputType(inputBodies, type):
    withType = inputBodies[inputBodies['input.type'].str.contains(type, na=False)]
    withoutType = inputBodies[~inputBodies['input.type'].str.contains(type, na=False)]
    return withType, withoutType


# splits based on the interneuron type
def splitBasedOnInterneuronType(queryResults, type):
    withType = queryResults[queryResults['interneuron.type'].str.contains(type, na=False)]
    withoutType = queryResults[~queryResults['interneuron.type'].str.contains(type, na=False)]
    return withType, withoutType


# statistic functions
def findStatistics(queryResults, inputBodies):
    roiW = list(inputBodies['roi_connectivity_weight'])
    roiMean = statistics.mean(roiW)
    roiMedian = statistics.median(roiW)
    roiMedianGrouped = statistics.median_grouped(roiW)
    roiMode = statistics.mode(roiW)

    interW = list(queryResults['interneuron_weight'])
    interWMean = statistics.mean(interW)
    interWMedian = statistics.median(interW)
    interWMedianGrouped = statistics.median_grouped(interW)
    interWMode = statistics.mode(interW)

    statsDict = {"roiMean": roiMean, "roiMedian": roiMedian, "roiMedianGrouped": roiMedianGrouped, 'roiMode': roiMode,
                 'interMean': interWMean, 'interMedian': interWMedian, 'interMedianGrouped': interWMedianGrouped,
                 'interMode': interWMode}
    return statsDict


def findStatistics2(queryResults):
    interW = list(queryResults['roi_connectivity_weight'])
    interWMean = statistics.mean(interW)
    interWMedian = statistics.median(interW)
    interWMedianGrouped = statistics.median_grouped(interW)
    interWMode = statistics.mode(interW)
    print('\nStats for roi_connectivity_weight')
    statsDict = {'interMean': interWMean, 'interMedian': interWMedian, 'interMedianGrouped': interWMedianGrouped,
                 'interMode': interWMode}
    return statsDict


# threshold functions
def inputThresh(inputBodies, threshold):
    threshold = int(threshold)
    threshDF = inputBodies[inputBodies['roi_connectivity_weight'] >= threshold]
    return threshDF


def interThresh(queryResults, threshold):
    threshold = int(threshold)
    threshDF = queryResults[queryResults['interneuron_weight'] >= threshold]
    return threshDF


# reorganizing functions
def toCSV(answer, DF):
    if answer == 'y':
        filename = input('\nEnter a file name')
        if '.csv' in filename:
            DF.to_csv(filename, index=False)
        else:
            filename = filename + '.csv'
            DF.to_csv(filename, index=False)
    return


def reorgQuery(queryResults):
    columns = ['input.bodyId', 'input.type', 'input.instance', 'input.status', "Input",
               'weight', 'output.bodyId', 'output.type', 'output.instance',
               'output.status', 'Output']
    reorgDF = pd.DataFrame()
    row1 = []  # inter -> GFIN
    row2 = []  # GFIN -> GF

    for index, row in queryResults.iterrows():
        row1 = [row['interneuron.bodyId'], row['interneuron.type'], row['interneuron.instance'],
                row['interneuron.status'], None, row['interneuron_weight'], row['TargetInput.bodyId'],
                row['TargetInput.type'], row['TargetInput.instance'], row['TargetInput.status'], None]

        row2 = [row['TargetInput.bodyId'], row['TargetInput.type'], row['TargetInput.instance'],
                row['TargetInput.status'], None, row['Target_weight'], row['Target.bodyId'], row['Target.type'],
                row['Target.instance'], row['Target.status'], None]

        reorgDF = reorgDF.append([row1], ignore_index=True)
        reorgDF = reorgDF.append([row2], ignore_index=True)

    reorgDF.columns = columns

    reorgDF = reorgDF.where(reorgDF.notnull(), None)
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


def reorgQuery2(queryResults, ROI):
    columns = ['ROI', 'input.bodyId', 'input.type', 'input.instance', 'input.status', "Input",
               'weight', 'output.bodyId', 'output.type', 'output.instance',
               'output.status', 'Output']
    reorgDF = pd.DataFrame()
    row1 = []  # inter -> GFIN
    row2 = []  # GFIN -> GF

    for index, row in queryResults.iterrows():
        row1 = [ROI, row['input.bodyId'], row['input.type'], row['input.instance'],
                row['input.status'], None, row['input_weight'], row['TargetInput.bodyId'],
                row['TargetInput.type'], row['TargetInput.instance'], row['TargetInput.status'], None]

        row2 = [None, row['TargetInput.bodyId'], row['TargetInput.type'], row['TargetInput.instance'],
                row['TargetInput.status'], None, row['Target_weight'], row['Target.bodyId'], row['Target.type'],
                row['Target.instance'], row['Target.status'], None]

        reorgDF = reorgDF.append([row1], ignore_index=True)
        reorgDF = reorgDF.append([row2], ignore_index=True)

    reorgDF.columns = columns

    roispec = input('\nWould you like to make the input bodies ROI specific? (y/n)'
                    '\nThis will change the furthest body to the ROI name, making it a single node')

    if roispec == "y":
        for index, row in reorgDF.iterrows():
            if row['ROI'] is not None:
                reorgDF.loc[index, 'Input'] = row['ROI']
            elif row['input.type'] is not None:
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
    else:
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

    reorgDF = reorgDF.drop("ROI", 1)
    reorgDF = reorgDF.drop_duplicates()

    return reorgDF


def reorgQuery3(queryResults, ROI):
    columns = ['ROI', 'input.bodyId', 'input.type', 'input.instance', 'input.status', "Input",
               'weight', 'output.bodyId', 'output.type', 'output.instance',
               'output.status', 'Output']
    reorgDF = pd.DataFrame()
    row1 = []  # inter -> GFIN
    row2 = []  # GFIN -> GF

    for index, row in queryResults.iterrows():
        row1 = [ROI, row['input.bodyId'], row['input.type'], row['input.instance'],
                row['input.status'], None, row['input_weight'], row['Target.bodyId'],
                row['Target.type'], row['Target.instance'], row['Target.status'], None]

        reorgDF = reorgDF.append([row1], ignore_index=True)

    reorgDF.columns = columns

    roispec = input('\nWould you like to make the input bodies ROI specific? (y/n)'
                    '\nThis will change the furthest body to the ROI name, making it a single node')

    if roispec == "y":
        for index, row in reorgDF.iterrows():
            if row['ROI'] is not None:
                reorgDF.loc[index, 'Input'] = row['ROI']
            elif row['input.type'] is not None:
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
    else:
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

    reorgDF = reorgDF.drop("ROI", 1)
    reorgDF = reorgDF.drop_duplicates()

    return reorgDF


def reorganizeInputs(queryResults, ROI):
    columns = ['ROI', 'input.bodyId', 'input.type', 'input.instance', 'input.status', "Input", 'weight',
               'output.bodyId', 'output.type', 'output.instance', 'output.status', 'Output']

    row1 = []
    reorgDF = pd.DataFrame()

    for index, row in queryResults.iterrows():
        row1 = [ROI, row['input.bodyId'], row['input.type'], row['input.instance'], row['input.status'], None,
                row['roi_connectivity_weight'], row['interneuron.bodyId'], row['interneuron.type'],
                row['interneuron.instance'], row['interneuron.status'], None]

        reorgDF = reorgDF.append([row1], ignore_index=True)

    reorgDF.columns = columns

    roispec = input('\nWould you like to make the input bodies ROI specific? (y/n)'
                    '\nThis will change the furthest body to the ROI name, making it a single node')

    if roispec == "y":
        for index, row in reorgDF.iterrows():
            if row['ROI'] is not None:
                reorgDF.loc[index, 'Input'] = row['ROI']
            elif row['input.type'] is not None:
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
    else:
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

    reorgDF = reorgDF.drop("ROI", 1)
    reorgDF = reorgDF.drop_duplicates()
    return reorgDF


def addWeights(combinedDF):
    fileDF = combinedDF.groupby(['Input', 'Output'], as_index=False).agg(
        {'input.type': 'last', 'input.instance': 'last', 'weight': 'sum', 'output.type': 'last',
         'output.instance': 'last'})
    fileDF = fileDF[['input.type', 'input.instance', "Input", 'weight', 'output.type', 'output.instance', 'Output']]

    return fileDF


def addGFTypes(queryResults, filename2="FAFB_Hemibrain Comparison - Export_To_Python.csv"):
    gfins = pd.read_csv(filename2, sep=",")

    bodyIDDirect = list(gfins['Body ID'])
    bodyIDs = defaultdict(list)

    for index, row in gfins.iterrows():
        bodyIDs[row['GF input type']].append(row['Body ID'])

    inputGFlist = []
    outputGFlist = []

    reorgDF = queryResults.where(queryResults.notnull(), None)

    for index, row in reorgDF.iterrows():
        inputId = row['input.bodyId']
        outputId = row['output.bodyId']
        for k, v in bodyIDs.items():
            if inputId in v:
                inputGFlist.append(k)
            if outputId in v:
                outputGFlist.append(k)
        if inputId not in bodyIDDirect:
            inputGFlist.append(None)
        if outputId not in bodyIDDirect:
            outputGFlist.append(None)

    ins = np.asarray(inputGFlist)
    outs = np.asarray(outputGFlist)
    reorgDF['GFInput.Classification'] = ins
    reorgDF['GFInput.Classification2'] = outs

    for index, row in reorgDF.iterrows():
        if row['GFInput.Classification'] is not None:
            reorgDF.loc[index, 'Input'] = row['GFInput.Classification']
        if row['GFInput.Classification2'] is not None:
            reorgDF.loc[index, 'Output'] = row['GFInput.Classification2']

    return reorgDF


# display option functions
def displayOptions(queryResults, inputBodies, statistics, ROI):
    option = input('\n Pick an action  (x -> y -> z -> target):'
                   '\n a) View Statistics of weight columns'
                   '\n b) Add threshold to input weight (x -> y)'
                   '\n c) Add threshold to interneuron weight (y -> z)'
                   '\n d) extract types from input bodies (x)'
                   '\n e) extract types from interneuron bodies'
                   '\n f) add weights and end - option to add GF input types (last action)'
                   '\n g) more info     \n')

    if option == 'a':
        print(statistics)
        displayOptions(queryResults, inputBodies, statistics, ROI)

    if option == 'b':
        print('\nthreshold values are inclusive')
        print1 = input(
            '\nwould you like to set a threshold for the input body to the interneuron? (first hop) (y/n):   ')
        if print1 == 'y':
            input_threshold = input(
                '\nthis threshold is set with the roi_connectivity_column (roi specific connections)'
                '\nEnter a threshold value (number):')
            # inputBodiesThresh is the input bodies query with everything equal to or higher than the thresh value
            inputBodiesThresh = inputThresh(inputBodies, input_threshold)
            print2 = input('\nwould you like to save the input threshold results? (y/n):   ')
            toCSV(print2, inputBodiesThresh)

        change1 = input(
            '\nWould you like to keep these changes moving forward or revert to original files, '
            'removing the threshold values? (change/revert):   ')
        if change1 == "change":
            displayOptions(queryResults, inputBodiesThresh, statistics, ROI)
        else:
            displayOptions(queryResults, inputBodies, statistics, ROI)

    if option == 'c':
        print('\nthreshold values are inclusive')
        print3 = input(
            '\nwould you like to set a threshold for the interneuron to the target input neuron? (second hop) (y/n):   ')
        if print3 == 'y':
            interthresh = input('\nEnter a threshold value (number):   ')
            # queryResultsThresh is the queryResults query with everything equal to or higher than the thresh value
            queryResultsThresh = interThresh(queryResults, interthresh)
            print4 = input('\nwould you like to save the input threshold results? (y/n):   ')
            toCSV(print4, queryResultsThresh)

        change2 = input(
            '\nWould you like to keep these changes moving forward or revert to original files, '
            'removing the threshold values? (change/revert):   ')
        if change2 == "change":
            displayOptions(queryResultsThresh, inputBodies, statistics, ROI)
        elif change2 == "revert":
            displayOptions(queryResults, inputBodies, statistics, ROI)
        else:
            print("incorrect option")

    if option == 'd':
        type = input('\nWhich type would you like to extract from input type?\n')
        toKeep = input('\nWould you like to continue using the file with or without ' + type + ' (with/without)?\n')
        withInputType, withoutInputType = splitBasedOnInputType(inputBodies, type)

        print7 = input('\nWould you like to save the input type file? (y/n)\n')

        if toKeep == 'with':
            toCSV(print7, withInputType)
            displayOptions(queryResults, withInputType, statistics, ROI)
        else:
            toCSV(print7, withoutInputType)
            displayOptions(queryResults, withoutInputType, statistics, ROI)

    if option == 'e':
        type = input('\nWhich type would you like to extract from interneuron type?\n')
        toKeep = input('\nWould you like to continue using the file with or without ' + type + ' (with/without)?\n')
        withInputType, withoutInputType = splitBasedOnInterneuronType(queryResults, type)

        print6 = input('\nWould you like to save the interneuron type file? (y/n)\n')
        if toKeep == 'with':
            toCSV(print6, withInputType)
            displayOptions(withInputType, inputBodies, statistics, ROI)
        else:
            toCSV(print6, withoutInputType)
            displayOptions(withoutInputType, inputBodies, statistics, ROI)

    if option == 'f':
        print('\nreorganizing files for cytoscape input...'
              '\nreorganizing input bodies uses roi_connectivity_weight')

        queryResults, inputBodies = mismatchedBodies(queryResults, inputBodies)
        cyto1 = reorgQuery(queryResults)
        cyto2 = reorganizeInputs(inputBodies, ROI)

        combinedDF = cyto1.append(cyto2, ignore_index=True)
        combinedDF = combinedDF.drop_duplicates()

        print4 = input(
            '\nRunning GF input types will replace the current input/output type with the GF input type if exists'
            '\nwould you like to add Giant Fiber input types? (y/n):   ')
        if print4 == 'y':
            combinedDF = addGFTypes(combinedDF)

        print('\nadding weights and removing duplicate lines...')
        addedDF = addWeights(combinedDF)
        print5 = input('\nwould you like to save the cytoscape file? (added weights, reorganized file) (y/n):   ')
        toCSV(print5, addedDF)

    if option == 'g':
        print(
            '\na) Displays the statistic information for weight columns. Mean, median, weighted median, and mode.  Helpful for '
            '\ndetermining threshold values.'
            '\nb) Adds a threshold to input -> interneuron weights. This action will remove anything below the threshold weight'
            '\nc) Adds a threshold to interneuron -> targetInput body weights. This action will remove anything below the threshold weight'
            '\nd) Removes data based on input.type from original query, you can decide to keep and continue working on the'
            '\nfile that contains the given type or the file that removes the given type - useful to focus on or avoid certain neuron types'
            '\ne) Removes data based on interneuron.type from original query, you can decide to keep and continue working on the'
            '\nfile that contains the given type or the file that removes the given type - useful to focus on or avoid certain neuron types'
            '\nf) adds weights of similar types and condenses files into one for cytoscape use -- must be the last action as body IDs will be '
            '\nlost in the process;  gives option to add GF input types\n')
        displayOptions(queryResults, inputBodies, statistics, ROI)

    return


def displayOptions2(queryResults, statistics, ROI):
    option = input('\n Pick an action  (x -> y -> z -> target):'
                   '\n a) View Statistics of weight columns'
                   '\n b) Add threshold to input weight (x -> y)'
                   '\n c) extract types from input bodies (x)'
                   '\n d) add weights and end - option to add GF input types (last action)'
                   '\n e) more info     \n')

    if option == 'a':
        print(statistics)
        displayOptions2(queryResults, statistics, ROI)

    if option == 'b':
        print('\nthreshold values are inclusive')
        print1 = input(
            '\nwould you like to set a threshold for the input body to the interneuron? (first hop) (y/n):   ')
        if print1 == 'y':
            input_threshold = input(
                '\nthis threshold is set with the roi_connectivity_column (roi specific connections)'
                '\nEnter a threshold value (number):')
            # inputBodiesThresh is the input bodies query with everything equal to or higher than the thresh value
            inputBodiesThresh = inputThresh(queryResults, input_threshold)
            print2 = input('\nwould you like to save the input threshold results? (y/n):   ')
            toCSV(print2, inputBodiesThresh)

        change1 = input(
            '\nWould you like to keep these changes moving forward or revert to original files, '
            'removing the threshold values? (change/revert):   ')
        if change1 == "change":
            displayOptions2(inputBodiesThresh, statistics, ROI)
        else:
            displayOptions2(queryResults, statistics, ROI)

    if option == 'c':
        type = input('\nWhich type would you like to extract from input type?\n')
        toKeep = input('\nWould you like to continue using the file with or without ' + type + ' (with/without)?\n')
        withInputType, withoutInputType = splitBasedOnInputType(queryResults, type)

        print7 = input('\nWould you like to save the input type file? (y/n)\n')

        if toKeep == 'with':
            toCSV(print7, withInputType)
            displayOptions2(withInputType, statistics, ROI)
        else:
            toCSV(print7, withoutInputType)
            displayOptions2(withoutInputType, statistics, ROI)

    if option == 'd':
        print('\nreorganizing files for cytoscape input...'
              '\nreorganizing input bodies uses roi_connectivity_weight')
        reorgResults = reorgQuery2(queryResults, ROI)
        print4 = input(
            '\nRunning GF input types will replace the current input/output type with the GF input type if exists'
            '\nwould you like to add Giant Fiber input types? (y/n):   ')
        if print4 == 'y':
            reorgResults = addGFTypes(reorgResults)

        print('\nadding weights and removing duplicate lines...')
        addedDF = addWeights(reorgResults)
        print5 = input('\nwould you like to save the cytoscape file? (added weights, reorganized file) (y/n):   ')
        toCSV(print5, addedDF)

    if option == 'e':
        print(
            '\na) Displays the statistic information for weight columns. Mean, median, weighted median, and mode.  Helpful for '
            '\ndetermining threshold values.'
            '\nb) Adds a threshold to input -> interneuron weights. This action will remove anything below the threshold weight'
            '\nc) Removes data based on input.type from original query, you can decide to keep and continue working on the'
            '\nfile that contains the given type or the file that removes the given type - useful to focus on or avoid certain neuron types'
            '\nd) adds weights of similar types and condenses files into one for cytoscape use -- must be the last action as body IDs will be '
            '\nlost in the process;  gives option to add GF input types\n')
        displayOptions2(queryResults, statistics, ROI)

    return


def displayOptions3(queryResults, statistics, ROI):
    option = input('\n Pick an action  (x -> y -> z -> target):'
                   '\n a) View Statistics of weight columns'
                   '\n b) Add threshold to input weight (x -> y)'
                   '\n c) extract types from input bodies (x)'
                   '\n d) add weights and end - option to add GF input types (last action)'
                   '\n e) more info     \n')

    if option == 'a':
        print(statistics)
        displayOptions3(queryResults, statistics, ROI)

    if option == 'b':
        print('\nthreshold values are inclusive')
        print1 = input(
            '\nwould you like to set a threshold for the input body to the interneuron? (first hop) (y/n):   ')
        if print1 == 'y':
            input_threshold = input(
                '\nthis threshold is set with the roi_connectivity_column (roi specific connections)'
                '\nEnter a threshold value (number):')
            # inputBodiesThresh is the input bodies query with everything equal to or higher than the thresh value
            inputBodiesThresh = inputThresh(queryResults, input_threshold)
            print2 = input('\nwould you like to save the input threshold results? (y/n):   ')
            toCSV(print2, inputBodiesThresh)

        change1 = input(
            '\nWould you like to keep these changes moving forward or revert to original files, '
            'removing the threshold values? (change/revert):   ')
        if change1 == "change":
            displayOptions3(inputBodiesThresh, statistics, ROI)
        else:
            displayOptions3(queryResults, statistics, ROI)

    if option == 'c':
        type = input('\nWhich type would you like to extract from input type?\n')
        toKeep = input('\nWould you like to continue using the file with or without ' + type + ' (with/without)?\n')
        withInputType, withoutInputType = splitBasedOnInputType(queryResults, type)

        print7 = input('\nWould you like to save the input type file? (y/n)\n')

        if toKeep == 'with':
            toCSV(print7, withInputType)
            displayOptions3(withInputType, statistics, ROI)
        else:
            toCSV(print7, withoutInputType)
            displayOptions3(withoutInputType, statistics, ROI)

    if option == 'd':
        print('\nreorganizing files for cytoscape input...'
              '\nreorganizing input bodies uses roi_connectivity_weight')
        reorgResults = reorgQuery3(queryResults, ROI)
        print4 = input(
            '\nRunning GF input types will replace the current input/output type with the GF input type if exists'
            '\nwould you like to add Giant Fiber input types? (y/n):   ')
        if print4 == 'y':
            reorgResults = addGFTypes(reorgResults)

        print('\nadding weights and removing duplicate lines...')
        addedDF = addWeights(reorgResults)
        print5 = input('\nwould you like to save the cytoscape file? (added weights, reorganized file) (y/n):   ')
        toCSV(print5, addedDF)

    if option == 'e':
        print(
            '\na) Displays the statistic information for weight columns. Mean, median, weighted median, and mode.  Helpful for '
            '\ndetermining threshold values.'
            '\nb) Adds a threshold to input -> interneuron weights. This action will remove anything below the threshold weight'
            '\nc) Removes data based on input.type from original query, you can decide to keep and continue working on the'
            '\nfile that contains the given type or the file that removes the given type - useful to focus on or avoid certain neuron types'
            '\nd) adds weights of similar types and condenses files into one for cytoscape use -- must be the last action as body IDs will be '
            '\nlost in the process;  gives option to add GF input types\n')
        displayOptions3(queryResults, statistics, ROI)

    return


'''
DNs = [1405231475, 1072063538, 5813020347, 1262356170,  1281324958, 1566597156, 1655997973, 2307027729, 5813024015,5813026936,
       5813050455, 707116522, 1222928995, 887195902, 1229107423]

def main():
    target = input('\nEnter the targeted body ID (x -> y -> z -> target):   ')
    ROI = input('\nEnter the targeted ROI:   ')
    ROI = str(ROI)

    print("\nrunning two hop query...")
    #original results = queryResults
    queryResults = Target_ROI_TwoHop(target, ROI)
    print1 = input('\nWould you like to save query results? (y/n):   ')
    toCSV(print1, queryResults)

    print('\ngetting input bodies...')
    #original input bodies = inputBodies
    inputBodies = getInputBodies(queryResults, ROI)
    print2 = input('\nWould you like to save the input body query results? (y/n):   ')
    toCSV(print2, inputBodies)

    print('\nfinding mismatched bodies...'
          '\nquery removes bodies that are not annotated from original ROI two hop query')
    #queryResults2 is queryResults with mismatched bodies removed
    queryResults2 = mismatchedBodies(queryResults, inputBodies)
    print3 = input('\nWould you like to save the mismatched body results? (y/n):   ')
    toCSV(print3, queryResults2)

    print('finding ROI synapse weight for input body query...')
    #minmax is inputBodies with the PRE/POST changed to roi_connectivity_weight
    minmax = compareMinMax(inputBodies)
    print4 = input('\nquery removes the PRE and POST columns from the input bodies query and changes the '
                   'column to roi_connectivity_weight, returning whichever has the higher value' 
                   '\nWould you like to save the updated results? (y/n):   ')
    toCSV(print4, minmax)

    print('\nrunning statistics for threshold values...')
    statistics = findStatistics(queryResults2, minmax)
    print('\n' + str(statistics))

    print('\nthreshold values are inclusive')

    print5 = input('\nwould you like to set a threshold for the input body to the interneuron? (first hop) (y/n):   ')
    if print5 == 'y':
        input_threshold = input('\nthis threshold is set with the roi_connectivity_column (roi specific connections)'
                            '\nEnter a threshold value:')

        #inputBodiesThresh is the input bodies query with everything equal to or higher than the thresh value
        inputBodiesThresh = inputThresh(minmax, input_threshold)
        print7 = input('\nwould you like to save the input threshold results? (y/n):   ')
        toCSV(print7, inputBodiesThresh)

    else:
        inputBodiesThresh = minmax


    print6 = input('\nwould you like to set a threshold for the interneuron to the target input neuron? (second hop) (y/n):   ')
    if print6 == 'y':
        interthresh = input('\nEnter a threshold value:   ')

        #queryResultsThresh is the queryResults query with everything equal to or higher than the thresh value
        queryResultsThresh = interThresh(queryResults2, interthresh)
        print8 = input('\nwould you like to save the input threshold results? (y/n):   ')
        toCSV(print8, queryResultsThresh)
    else:
        queryResultsThresh = queryResults2


    print('\nreorganizing files for cytoscape input...'
          '\nreorganizing input bodies uses roi_connectivity_weight')

    cyto1 = reorgQuery(queryResultsThresh)
    cyto2 = reorganizeInputs(inputBodiesThresh, ROI)

    combinedDF = cyto1.append(cyto2, ignore_index=True)
    combinedDF = combinedDF.drop_duplicates()

    print10 = input('\nRunning GF input types will replace the current input/output type with the GF input type if exists'
                    '\nwould you like to add Giant Fiber input types? (y/n):   ')
    if print10 == 'y':
        combinedDF = addGFTypes(combinedDF)


    print('\nadding weights and removing duplicate lines...')
    addedDF = addWeights(combinedDF)
    print9 = input('\nwould you like to save the cytoscape file? (added weights, reorganized file) (y/n):   ')
    toCSV(print9, addedDF)

    return
'''

'''
option = input('\nPick an action  (x -> y -> z -> target):'
                  '\n a) View Statistics of weight columns'
                  '\n b) Add threshold to input weight (x -> y)'
                  '\n c) Add threshold to interneuron weight (y -> z)'
                  '\n d) Add GF input types'
                  '\n e) extract types from input bodies (x)'
                  '\n f) extract types from interneuron bodies'
                  '\n g) add weights and end (last action)'
                  '\n h) more info')

print('\na)Displays the statistic information for weight columns. Mean, median, weighted median, and mode.  Helpful for '
             '\ndetermining threshold values. 
             '\nb) Adds a threshold to input -> interneuron weights. This action will remove anything below the threshold weight'
             '\nc) Adds a threshold to interneuron -> targetInput body weights. This action will remove anything below the threshold weight'
             '\nd) Changes input types to Giant Fiber input types if they exist - types are identified from a separate CSV file'
             '\ne) Removes data based on input.type from original query, you can decide to keep and continue working on the'
             '\nfile that contains the given type or the file that removes the given type - useful to focus on or avoid certain neuron types'
             '\nf) Removes data based on interneuron.type from original query, you can decide to keep and continue working on the'
             '\nfile that contains the given type or the file that removes the given type - useful to focus on or avoid certain neuron types'
             '\ng) adds weights of similar types and condesnes file for cytoscape use -- must be the last action as body IDs will be '
             '\nlost in the process')
'''


def combineFiles(filename1, filename2):
    f1 = pd.read_csv(filename1)
    f2 = pd.read_csv(filename2)
    combinedDF = f1.append(f2, ignore_index=True)
    combinedDF = combinedDF.drop_duplicates()
    return combinedDF

##a query to return ALL bodies that receive x amount of input from cx???
