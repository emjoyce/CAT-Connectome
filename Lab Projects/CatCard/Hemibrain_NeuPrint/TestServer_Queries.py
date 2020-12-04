"""
Emily Tenshaw
CAT-Card
12/2/2020

**Always check which server is connected and up to date
Queries that the Card Lab ran using the test server
Some might be random, some similar to other files
"""

import neuprint as neu
import csv
import pandas as pd
import numpy as np
import ast
import os
from collections import defaultdict

# client = neu.Client('emdata1.int.janelia.org:13000', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtaWx5dGVuc2hhd0BnbWFpbC5jb20iLCJsZXZlbCI6InJlYWR3cml0ZSIsImltYWdlLXVybCI6Imh0dHBzOi8vbGg0Lmdvb2dsZXVzZXJjb250ZW50LmNvbS8tdmhYaGxhYjFxcFEvQUFBQUFBQUFBQUkvQUFBQUFBQUFBQUEvQUNIaTNyZWcwN21uZHVkQ2RpWVRkeFJGWGdONmlnMENOZy9waG90by5qcGc_c3o9NTA_c3o9NTAiLCJleHAiOjE3NTc5NzcyMTR9.uoMuun4AQ82VI7qUjO7f0G5CKOUX4KqAIF89CkQN4do')
client = neu.Client('neuprint-test.janelia.org', dataset='hemibrain',
                    token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtaWx5dGVuc2hhd0BnbWFpbC5jb20iLCJsZXZlbCI6InJlYWR3cml0ZSIsImltYWdlLXVybCI6Imh0dHBzOi8vbGg0Lmdvb2dsZXVzZXJjb250ZW50LmNvbS8tdmhYaGxhYjFxcFEvQUFBQUFBQUFBQUkvQUFBQUFBQUFBQUEvQUtGMDVuRFRUOHBhUHFCT3dMNk5nblZHVENIR2xGWEp0QS9waG90by5qcGc_c3o9NTA_c3o9NTAiLCJleHAiOjE3NjQ5ODIyODh9.UjUHbKZQpReYOShvtKMzZWxJE-saJ4FWN6iD9hAcZaQ')


# files saved will be located in the folder "TestingServerCSV"


# ---- Two Hop Queries -------------------------------------------------------------------------------------------
# Main funciton to run a two hop query - uses other functions below to run
# Similar to queries in other files but uses test server specifically
def run_TwoHop(roi):
    # get query
    queryResults = ROITwoHopQuery(roi)
    # get Inputs in ROI
    inputBodies = getInputBodies(queryResults, roi)
    queryResults = mismatchedBodies(queryResults, inputBodies)
    gfTypes = addGFTypes(queryResults)
    reorgDF = reorganizeCSV(gfTypes)

    # input Commands
    # compare min/max
    inputBodiesCompare = compareMinMax(inputBodies)
    # add ROI Column
    inputROI = addROIColumn(inputBodiesCompare, roi)
    # input GFTypes
    inputTypes = addInputGFTypes(inputROI)
    # reorg Inputs
    reorgIns = reorganizeInputs(inputTypes)
    combinedDF = combineQueries(reorgDF, reorgIns)

    added = addWeights(combinedDF, roi)

    return


def ROITwoHopQuery(roi):
    query = (
            'MATCH (interneuron:hemibrain_Neuron)-[w2:ConnectsTo]->(GFInput:hemibrain_Neuron)-[w3:ConnectsTo]->(GF:hemibrain_Neuron)'
            ' WHERE GF.bodyId = 2307027729 AND NOT apoc.convert.fromJsonMap(interneuron.roiInfo)["' + roi + '"].post IS NULL'
                                                                                                            ' RETURN interneuron.bodyId, interneuron.type, interneuron.instance, interneuron.status, '
                                                                                                            'w2.weight as interneuron_weight, GFInput.bodyId, GFInput.type, GFInput.instance, GFInput.status, w3.weight as GF_weight, GF.bodyId, GF.type, GF.instance, GF.status'
    ).format(dataset='hemibrain:v1.0')
    queryResults = client.fetch_custom(query)
    file = "TestServerCSV/" + roi + "TwoHop.csv"
    queryResults.to_csv(file, sep='\t', index=False)
    return queryResults


def addGFTypes(queryResults, filename2="FAFB_Hemibrain Comparison - Export_To_Python.csv"):
    # fileDF = pd.read_csv(filename, sep='\t')
    reorgDF = queryResults
    gfins = pd.read_csv(filename2, sep=",")

    bodyIDDirect = list(gfins['Body ID'])
    bodyIDs = defaultdict(list)

    for index, row in gfins.iterrows():
        bodyIDs[row['GF input type']].append(row['Body ID'])

    inputGFlist = []
    outputGFlist = []

    reorgDF = reorgDF.where(reorgDF.notnull(), None)

    for index, row in reorgDF.iterrows():
        inputId = row['interneuron.bodyId']
        outputId = row['GFInput.bodyId']
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

    # filename = filename.replace('TestServerCSV/', "")
    reorgDF = reorgDF[['interneuron.bodyId', 'interneuron.type', 'interneuron.instance',
                       'interneuron.status', 'GFInput.Classification', 'interneuron_weight',
                       'GFInput.bodyId', 'GFInput.type', 'GFInput.instance', 'GFInput.status',
                       'GFInput.Classification2',
                       'GF_weight', 'GF.bodyId', 'GF.type', 'GF.instance', 'GF.status']]
    # reorgDF.to_csv(filename, sep="\t", index=False)
    return reorgDF


# saves with different filename
def reorganizeCSV(gfTypes):
    # fileDF = pd.read_csv(filename, sep='\t')
    columns = ['input.bodyId', 'input.type', 'input.instance', 'input.status', 'GFInput.Classification', "Input",
               'roi_connectivity_weight', 'total_weight', 'weight', 'output.bodyId', 'output.type', 'output.instance',
               'output.status', 'GFInput.Classification2', 'Output']
    fileDF = gfTypes
    reorgDF = pd.DataFrame()
    row1 = []  # inter -> GFIN
    row2 = []  # GFIN -> GF

    for index, row in fileDF.iterrows():
        row1 = [row['interneuron.bodyId'], row['interneuron.type'], row['interneuron.instance'],
                row['interneuron.status'], row['GFInput.Classification'], None,
                None, row['interneuron_weight'], row['interneuron_weight'], row['GFInput.bodyId'], row['GFInput.type'],
                row['GFInput.instance'], row['GFInput.status'], row['GFInput.Classification2'], None]

        row2 = [row['GFInput.bodyId'], row['GFInput.type'], row['GFInput.instance'], row['GFInput.status'],
                row['GFInput.Classification2'], None,
                None, row['GF_weight'], row['GF_weight'], row['GF.bodyId'], row['GF.type'], row['GF.instance'],
                'Traced', 'GF', "GF"]

        reorgDF = reorgDF.append([row1], ignore_index=True)
        reorgDF = reorgDF.append([row2], ignore_index=True)

    reorgDF.columns = columns

    reorgDF = reorgDF.where(reorgDF.notnull(), None)
    for index, row in reorgDF.iterrows():
        if row['GFInput.Classification'] is not None:
            reorgDF.loc[index, 'Input'] = row['GFInput.Classification']
        elif row['input.type'] is not None:
            reorgDF.loc[index, 'Input'] = row['input.type']
        elif row['input.instance'] is not None:
            reorgDF.loc[index, 'Input'] = row['input.instance']
        else:
            reorgDF.loc[index, 'Input'] = row['input.bodyId']

        if row['GFInput.Classification2'] is not None:
            reorgDF.loc[index, 'Output'] = row['GFInput.Classification2']
        elif row['output.type'] is not None:
            reorgDF.loc[index, 'Output'] = row['output.type']
        elif row['output.instance'] is not None:
            reorgDF.loc[index, 'Output'] = row['output.instance']
        else:
            reorgDF.loc[index, 'Output'] = row['output.bodyId']

    # filename = filename.replace('TestServerCSV/', "")
    reorgDF = reorgDF.drop_duplicates()
    # reorgDF.to_csv(filename, sep="\t", index=False)
    return reorgDF


# Input body functions
def getInputBodies(queryResults, roi):
    bodies = list(queryResults['interneuron.bodyId'])
    query = (
            'WITH ' + str(bodies) + ' AS TARGETS'
                                    ' MATCH (input:hemibrain_Neuron)-[w:ConnectsTo]->(interneuron:hemibrain_Neuron)'
                                    ' WHERE interneuron.bodyId in TARGETS AND NOT apoc.convert.fromJsonMap(w.roiInfo)["' + roi + '"] IS NULL'
                                                                                                                                 ' RETURN input.bodyId, input.type, input.instance, input.status, apoc.convert.fromJsonMap(w.roiInfo)["' + roi + '"].pre as PRE, '
                                                                                                                                                                                                                                                 ' apoc.convert.fromJsonMap(w.roiInfo)["' + roi + '"].post as POST, w.weight as total_weight, interneuron.bodyId,'
                                                                                                                                                                                                                                                                                                  'interneuron.type, interneuron.instance, interneuron.status'
    ).format(dataset='hemibrain:v1.0')
    queryResults = client.fetch_custom(query)
    file = "TestServerCSV/" + roi + "TwoHop_Inputs.csv"
    queryResults.to_csv(file, sep='\t', index=False)
    return queryResults


def compareMinMax(queryResults):
    if 'PRE' not in queryResults.columns:
        raise Exception("No column in DF called PRE; compare Min/Max already run")  # error if PRE doesn't exist
    for index, row in queryResults.iterrows():
        preV = row["PRE"]
        postV = row["POST"]
        if postV < preV:
            queryResults.loc[index, 'POST'] = preV  # replace post value with pre if pre is higher
    newDF = queryResults  # create a new dataframe, remove pre column, rename post column
    newDF = newDF.drop("PRE", 1)
    newDF = newDF.rename({'POST': 'roi_connectivity_weight'}, axis=1)  # rename column name
    # save new dataframe as original filename
    if "Unnamed: 0" in newDF.columns:
        newDF = newDF.drop("Unnamed: 0", 1)  # drop unnecessary column
    # file = "TestServerCSV/" + roi + "TwoHop_Inputs2.csv"
    # newDF.to_csv(file, sep="\t", index=False)       #save to csv
    return newDF


# saves with same filename
def addROIColumn(queryResults, roi):
    roicol = []
    for index, row in queryResults.iterrows():
        roicol.append(roi)
    queryResults['ROI'] = roicol
    queryResults = queryResults[['ROI', 'input.bodyId', 'input.type', 'input.instance',
                                 'input.status', 'roi_connectivity_weight', 'total_weight',
                                 'interneuron.bodyId', 'interneuron.type', 'interneuron.instance',
                                 'interneuron.status']]
    # file = "TestServerCSV/" + roi + "TwoHop_Inputs2.csv"
    # queryResults.to_csv(filename, sep='\t', index=False)
    return queryResults


def addInputGFTypes(queryResults, filename2="FAFB_Hemibrain Comparison - Export_To_Python.csv"):
    reorgDF = queryResults
    gfins = pd.read_csv(filename2, sep=",")

    bodyIDDirect = list(gfins['Body ID'])
    bodyIDs = defaultdict(list)

    for index, row in gfins.iterrows():
        bodyIDs[row['GF input type']].append(row['Body ID'])

    inputGFlist = []
    outputGFlist = []

    reorgDF = reorgDF.where(reorgDF.notnull(), None)

    for index, row in reorgDF.iterrows():
        inputId = row['input.bodyId']
        outputId = row['interneuron.bodyId']
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

    # filename = filename.replace('TestServerCSV/', "")
    reorgDF = reorgDF[['ROI', 'input.bodyId', 'input.type', 'input.instance',
                       'input.status', 'GFInput.Classification', 'roi_connectivity_weight', 'total_weight',
                       'interneuron.bodyId', 'interneuron.type', 'interneuron.instance', 'interneuron.status',
                       'GFInput.Classification2']]
    # reorgDF.to_csv(filename, sep="\t", index=False)
    return reorgDF


def reorganizeInputs(queryResults):
    columns = ['ROI', 'input.bodyId', 'input.type', 'input.instance', 'input.status', 'GFInput.Classification', "Input",
               'roi_connectivity_weight',
               'total_weight', 'weight', 'output.bodyId', 'output.type', 'output.instance', 'output.status',
               'GFInput.Classification2',
               'Output']

    row1 = []
    reorgDF = pd.DataFrame()

    for index, row in queryResults.iterrows():
        row1 = [row['ROI'], row['input.bodyId'], row['input.type'], row['input.instance'], row['input.status'],
                row['GFInput.Classification'], None,
                row['roi_connectivity_weight'], row['total_weight'], row['roi_connectivity_weight'],
                row['interneuron.bodyId'],
                row['interneuron.type'], row['interneuron.instance'], row['interneuron.status'],
                row['GFInput.Classification2'], None]

        reorgDF = reorgDF.append([row1], ignore_index=True)

    reorgDF.columns = columns

    for index, row in reorgDF.iterrows():
        if row['ROI'] is not None:
            reorgDF.loc[index, 'Input'] = row['ROI']
        elif row['GFInput.Classification'] is not None:
            reorgDF.loc[index, 'Input'] = row['GFInput.Classification']
        elif row['input.type'] is not None:
            reorgDF.loc[index, 'Input'] = row['input.type']
        elif row['input.instance'] is not None:
            reorgDF.loc[index, 'Input'] = row['input.instance']
        else:
            reorgDF.loc[index, 'Input'] = row['input.bodyId']

        if row['GFInput.Classification2'] is not None:
            reorgDF.loc[index, 'Output'] = row['GFInput.Classification2']
        elif row['output.type'] is not None:
            reorgDF.loc[index, 'Output'] = row['output.type']
        elif row['output.instance'] is not None:
            reorgDF.loc[index, 'Output'] = row['output.instance']
        else:
            reorgDF.loc[index, 'Output'] = row['output.bodyId']

    reorgDF = reorgDF.drop("ROI", 1)
    reorgDF = reorgDF.drop_duplicates()
    return reorgDF


def combineQueries(reorgDF, reorgIns):
    combinedDF = reorgDF.append(reorgIns, ignore_index=True)
    combinedDF = combinedDF.drop_duplicates()
    return combinedDF


# adds together weights when input/output is the same #needs to be done after creating input/output columns
def addWeights(combinedDF, roi):
    # fileDF = pd.read_csv(filename, sep="\t")
    # if 'Input' not in fileDF.columns:
    #   fileDF = pd.read_csv(filename, sep=',')

    fileDF = combinedDF.groupby(['Input', 'Output'], as_index=False).agg(
        {'input.type': 'last', 'input.instance': 'last', 'GFInput.Classification': 'last',
         'roi_connectivity_weight': 'sum', 'total_weight': 'sum', 'weight': 'sum', 'output.type': 'last',
         'output.instance': 'last',
         'GFInput.Classification2': 'last'})
    fileDF = fileDF[
        ['input.type', 'input.instance', 'GFInput.Classification', "Input", 'roi_connectivity_weight', 'total_weight',
         'weight', 'output.type', 'output.instance', 'GFInput.Classification2', 'Output']]

    # filename = filename.replace("TestServerCSV/", "")
    fileDF.to_csv("TestServerCSV/Added_" + roi + "TwoHop.csv", sep="\t", index=False)
    return


def mismatchedBodies(queryResults, inputBodies):
    qInter = list(queryResults['interneuron.bodyId'])
    inputInter = list(inputBodies['interneuron.bodyId'])
    diff = list(set(qInter).difference(inputInter))
    count = 0
    for index, row in queryResults.iterrows():
        for body in diff:
            if row['interneuron.bodyId'] == body:
                queryResults = queryResults.drop([index])
                count = count + 1
    return queryResults



'''
to run a two hop query:
if you want to run the query, add ROI column, add GF types, and reorganize:
*enter the ROI you want in place of "PB"

    import TestServer_Queries as TS
    TS.run_TwoHop("PB")     

This will create three files - the original query, the second query, and a reorganized file.  
The resulting file that can be used in cytoscape is "Added_PBTwoHop.csv" inside the TestServerCSV folder
'''


# ----- type -> GF -----------------------------------------------------------------------------------

# can both be used for LC6 query using type "LC6"
# uses contains - can be exact like "PB12a" or can be less specific like "PB12"
def typeToGFInput(type):
    query = (
            'MATCH (type:hemibrain_Neuron)-[w1:ConnectsTo]->(GFInput:hemibrain_Neuron)-[w2:ConnectsTo]->(GF:hemibrain_Neuron)'
            ' WHERE type.type CONTAINS "' + type + '" AND GF.bodyId = 2307027729'
                                                   ' RETURN type.bodyId, type.type, type.instance, w1.weight as weight1, GFInput.bodyId, GFInput.type,'
                                                   'GFInput.instance, w2.weight as weight2, GF.bodyId, GF.type, GF.instance'
    ).format(dataset='hemibrain:v1.0')
    queryResults = client.fetch_custom(query)
    file = "TestServerCSV/" + type + "_ToGF.csv"
    queryResults.to_csv(file, sep='\t', index=False)
    return


def typeToGFInput2Hop(type):
    query = (
            'MATCH (type:hemibrain_Neuron)-[w1:ConnectsTo]->(interneuron:hemibrain_Neuron)-[w2:ConnectsTo]->(GFInput:hemibrain_Neuron)-[w3:ConnectsTo]->(GF:hemibrain_Neuron)'
            ' WHERE type.type CONTAINS "' + type + '" AND GF.bodyId = 2307027729'
                                                   ' RETURN type.bodyId, type.type, type.instance, w1.weight as weight1, interneuron.bodyId, interneuron.type,'
                                                   ' interneuron.instance, w2.weight as weight2, GFInput.bodyId, GFInput.type,'
                                                   'GFInput.instance, w3.weight as weight3, GF.bodyId, GF.type, GF.instance'
    ).format(dataset='hemibrain:v1.0')
    queryResults = client.fetch_custom(query)
    file = "TestServerCSV/" + type + "_ToGF_TwoHop.csv"
    queryResults.to_csv(file, sep='\t', index=False)
    return


def addGFTypes_TypeQuery(filename, filename2="FAFB_Hemibrain Comparison - Export_To_Python.csv"):
    fileDF = pd.read_csv(filename, sep='\t')
    reorgDF = fileDF
    gfins = pd.read_csv(filename2, sep=",")

    bodyIDDirect = list(gfins['Body ID'])
    bodyIDs = defaultdict(list)

    for index, row in gfins.iterrows():
        bodyIDs[row['GF input type']].append(row['Body ID'])

    inputGFlist = []
    outputGFlist = []

    reorgDF = reorgDF.where(reorgDF.notnull(), None)

    for index, row in reorgDF.iterrows():
        inputId = row['type.bodyId']
        outputId = row['GFInput.bodyId']
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

    reorgDF = reorgDF[['type.bodyId', 'type.type', 'type.instance',
                       'GFInput.Classification', 'weight1', 'GFInput.bodyId', 'GFInput.type',
                       'GFInput.instance', 'GFInput.Classification2', 'weight2', 'GF.bodyId',
                       'GF.type', 'GF.instance']]
    reorgDF.to_csv(filename, sep="\t", index=False)
    return


# one hop
def reorganizeCSV_TypeQuery(filename):
    fileDF = pd.read_csv(filename, sep='\t')
    columns = ['input.bodyId', 'input.type', 'input.instance', 'GFInput.Classification', "Input",
               'weight', 'output.bodyId', 'output.type', 'output.instance', 'GFInput.Classification2',
               'Output']

    reorgDF = pd.DataFrame()
    row1 = []  # inter -> GFIN
    row2 = []  # GFIN -> GF

    for index, row in fileDF.iterrows():
        row1 = [row['type.bodyId'], row['type.type'], row['type.instance'], row['GFInput.Classification'], None,
                row['weight1'], row['GFInput.bodyId'], row['GFInput.type'], row['GFInput.instance'],
                row['GFInput.Classification2'], None]

        row2 = [row['GFInput.bodyId'], row['GFInput.type'], row['GFInput.instance'], row['GFInput.Classification2'],
                None,
                row['weight2'], row['GF.bodyId'], row['GF.type'], row['GF.instance'], 'GF', "GF"]

        reorgDF = reorgDF.append([row1], ignore_index=True)
        reorgDF = reorgDF.append([row2], ignore_index=True)

    reorgDF.columns = columns

    reorgDF = reorgDF.where(reorgDF.notnull(), None)
    for index, row in reorgDF.iterrows():
        if row['GFInput.Classification'] is not None:
            reorgDF.loc[index, 'Input'] = row['GFInput.Classification']
        elif row['input.type'] is not None:
            reorgDF.loc[index, 'Input'] = row['input.type']
        elif row['input.instance'] is not None:
            reorgDF.loc[index, 'Input'] = row['input.instance']
        else:
            reorgDF.loc[index, 'Input'] = row['input.bodyId']

        if row['GFInput.Classification2'] is not None:
            reorgDF.loc[index, 'Output'] = row['GFInput.Classification2']
        elif row['output.type'] is not None:
            reorgDF.loc[index, 'Output'] = row['output.type']
        elif row['output.instance'] is not None:
            reorgDF.loc[index, 'Output'] = row['output.instance']
        else:
            reorgDF.loc[index, 'Output'] = row['output.bodyId']

    reorgDF = reorgDF.drop_duplicates()
    reorgDF.to_csv(filename, sep="\t", index=False)
    return


# adds together weights when input/output is the same #needs to be done after creating input/output columns
def addWeight_TypeQuery(filename):
    fileDF = pd.read_csv(filename, sep="\t")
    if 'Input' not in fileDF.columns:
        fileDF = pd.read_csv(filename, sep=',')

    fileDF = fileDF.groupby(['Input', 'Output'], as_index=False).agg(
        {'input.type': 'last', 'input.instance': 'last', 'GFInput.Classification': 'last',
         'weight': 'sum', 'output.type': 'last', 'output.instance': 'last',
         'GFInput.Classification2': 'last'})

    fileDF = fileDF[['input.type', 'input.instance', 'GFInput.Classification', "Input", 'weight',
                     'output.type', 'output.instance', 'GFInput.Classification2', 'Output']]

    filename = filename.replace("TestServerCSV/", "")
    fileDF.to_csv("TestServerCSV/Added_" + filename, sep="\t", index=False)

    return


def typeQuery_OneHop(type):
    typeToGFInput(type)
    filename = "TestServerCSV/" + type + "_ToGF.csv"
    addGFTypes_TypeQuery(filename)
    reorganizeCSV_TypeQuery(filename)
    addWeight_TypeQuery(filename)
    return


def typeQuery_TwoHop(type):
    typeToGFInput(type)
    filename = "TestServerCSV/" + type + "_ToGF_TwoHop.csv"


# twoHop
def addGFTypes_TypeQuery2(filename, filename2="FAFB_Hemibrain Comparison - Export_To_Python.csv"):
    fileDF = pd.read_csv(filename, sep='\t')
    reorgDF = fileDF
    gfins = pd.read_csv(filename2, sep=",")

    bodyIDDirect = list(gfins['Body ID'])
    bodyIDs = defaultdict(list)

    for index, row in gfins.iterrows():
        bodyIDs[row['GF input type']].append(row['Body ID'])

    inputGFlist = []
    interGFlist = []
    outputGFlist = []

    reorgDF = reorgDF.where(reorgDF.notnull(), None)

    for index, row in reorgDF.iterrows():
        inputId = row['type.bodyId']
        interId = row['interneuron.bodyId']
        outputId = row['GFInput.bodyId']
        for k, v in bodyIDs.items():
            if inputId in v:
                inputGFlist.append(k)
            if interId in v:
                interGFlist.append(k)
            if outputId in v:
                outputGFlist.append(k)
        if inputId not in bodyIDDirect:
            inputGFlist.append(None)
        if outputId not in bodyIDDirect:
            outputGFlist.append(None)

    ins = np.asarray(inputGFlist)
    inter = np.asarray(interGFlist)
    outs = np.asarray(outputGFlist)
    reorgDF['GFInput.Classification'] = ins
    reorgDF['GFInput.Classification2'] = inter
    reorgDF['GFInput.Classification3'] = outs

    reorgDF = reorgDF[['type.bodyId', 'type.type', 'type.instance',
                       'GFInput.Classification', 'weight1', 'interneuron.bodyId', 'interneuron.type',
                       'interneuron.instance',
                       'GFInput.Classification2', 'weight2', 'GFInput.bodyId', 'GFInput.type',
                       'GFInput.instance', 'GFInput.Classification3', 'weight3', 'GF.bodyId',
                       'GF.type', 'GF.instance']]
    reorgDF.to_csv(filename, sep="\t", index=False)
    return


# twoHop ---- NOT FINISHED
def reorganizeCSV_TypeQuery2(filename):
    fileDF = pd.read_csv(filename, sep='\t')
    columns = ['input.bodyId', 'input.type', 'input.instance', 'GFInput.Classification', "Input",
               'weight', 'output.bodyId', 'output.type', 'output.instance', 'GFInput.Classification2',
               'Output']

    reorgDF = pd.DataFrame()
    row1 = []  # input -> inter
    row2 = []  # inter -> GFInput
    row3 = []  # GFInput -> GF

    for index, row in fileDF.iterrows():
        row1 = [row['type.bodyId'], row['type.type'], row['type.instance'], row['GFInput.Classification'], None,
                row['weight1'],
                row['interneuron.bodyId'], row['interneuron.type'], row['interneuron.instance'],
                row['GFInput.Classification2'], None]

        row2 = [row['interneuron.bodyId'], row['interneuron.type'], row['interneuron.instance'],
                row['GFInput.Classification2'],
                None, row['weight2'], row['GFInput.bodyId'], row['GFInput.type'], row['GFInput.instance'],
                row['GFInput.Classification3'], None]

        row3 = [row['GFInput.bodyId'], row['GFInput.type'], row['GFInput.instance'], row['GFInput.Classification3'],
                None,
                row['weight3'], row['GF.bodyId'], row['GF.type'], row['GF.instance'], 'GF', "GF"]

        reorgDF = reorgDF.append([row1], ignore_index=True)
        reorgDF = reorgDF.append([row2], ignore_index=True)

    reorgDF.columns = columns

    reorgDF = reorgDF.where(reorgDF.notnull(), None)
    for index, row in reorgDF.iterrows():
        if row['GFInput.Classification'] is not None:
            reorgDF.loc[index, 'Input'] = row['GFInput.Classification']
        elif row['input.type'] is not None:
            reorgDF.loc[index, 'Input'] = row['input.type']
        elif row['input.instance'] is not None:
            reorgDF.loc[index, 'Input'] = row['input.instance']
        else:
            reorgDF.loc[index, 'Input'] = row['input.bodyId']

        if row['GFInput.Classification2'] is not None:
            reorgDF.loc[index, 'Output'] = row['GFInput.Classification2']
        elif row['output.type'] is not None:
            reorgDF.loc[index, 'Output'] = row['output.type']
        elif row['output.instance'] is not None:
            reorgDF.loc[index, 'Output'] = row['output.instance']
        else:
            reorgDF.loc[index, 'Output'] = row['output.bodyId']

    reorgDF = reorgDF.drop_duplicates()
    reorgDF.to_csv(filename, sep="\t", index=False)
    return


'''
saves to "TestServerCSV"
example:

    Use single command:
    
    TS.typeQuery_OneHop("LC6)  
    - final is "Added_LC6_ToGF.csv"

OR run each command individually:

    TS.typeToGFInput("LC6")
    TS.addGFTypes_TypeQuery("TestServerCSV/LC6_ToGF.csv")
    TS.reorganizeCSV_TypeQuery("TestServerCSV/LC6_ToGF.csv")
    TS.addWeight_TypeQuery("TestServerCSV/LC6_ToGF.csv")
    - final is "Added_LC6_ToGF.csv"
'''


# ----- All LCs ------------------------------------------------------------------------------------
'''
Queries created for data Nathan needed in lab
'''

'''
LC types:
LC4,LC6,LC9,LC10,LC11,LC12,LC13,LC14,LC15,LC16,LC17,LC18,LC20,LC21,LC22,LC24,LC25,LC26,LC27,LC28a,LC28b,LC28c,LC28d,LC29,LC31,LC32

LC4
LC6
LC9
LC10
LC11
LC12
LC13
LC14
LC15
LC16
LC17
LC18
LC20
LC21
LC22
LC24
LC25
LC26
LC27
LC28a
LC28b
LC28c
LC28d
LC29
LC31
LC32
--------------
LPLC1
LPLC2
LPLC4

'''


def NathanLCQuery():
    NathanLC = ['LC18', 'LC21', 'LC11', 'LC25', 'LC15', 'LPLC2', 'LC4', 'LPLC1', 'LC17', 'LC12']
    allResults = pd.DataFrame()
    allResults2 = pd.DataFrame()
    allResults3 = pd.DataFrame()
    allResults4 = pd.DataFrame()
    for NathanLCs in NathanLC:
        query = (
                ' MATCH (LC:hemibrain_Neuron)-[c:ConnectsTo]->(output:hemibrain_Neuron)'
                ' WHERE LC.type = "' + str(NathanLCs) + '" AND output.status = "Traced"'
                                                        ' RETURN COUNT(LC.type), LC.type, SUM(c.weight), AVG(c.weight), output.bodyId, output.type, output.instance, output.status, output.statusLabel'
        ).format(dataset='hemibrain:v1.0')
        queryResults = client.fetch_custom(query)
        queryResults.to_csv("TestServerCSV/NathanLC/" + str(NathanLCs) + "_Summed_Query_WithOL.csv", index=False)
        allResults = allResults.append(queryResults)

    for NathanLCs2 in NathanLC:
        query2 = (
                ' MATCH (LC:hemibrain_Neuron)-[c:ConnectsTo]->(output:hemibrain_Neuron)'
                ' WHERE LC.type = "' + str(NathanLCs2) + '" AND output.status = "Traced"'
                                                         ' RETURN LC.bodyId, LC.type, c.weight, c.roiInfo, output.bodyId, output.type, output.instance, output.status, output.statusLabel'
        ).format(dataset='hemibrain:v1.0')
        queryResults2 = client.fetch_custom(query2)
        queryResults2.to_csv("TestServerCSV/NathanLC/" + str(NathanLCs2) + "_Query_WithOL.csv", index=False)
        allResults2 = allResults2.append(queryResults2)

    allResults.to_csv("TestServerCSV/NathanLC/Summed_WithOL.csv", index=False)
    allResults2.to_csv("TestServerCSV/NathanLC/Expanded_WithOL.csv", index=False)

    for NathanLCs3 in NathanLC:
        query3 = (
                ' MATCH (LC:hemibrain_Neuron)-[c:ConnectsTo]->(output:hemibrain_Neuron)'
                ' WHERE LC.type = "' + str(NathanLCs3) + '" AND output.status = "Traced" '
                                                         'AND apoc.convert.fromJsonMap(c.roiInfo)["OL(R)"] IS NULL'
                                                         ' RETURN COUNT(LC.type), LC.type, SUM(c.weight), AVG(c.weight), output.bodyId, output.type, output.instance, output.status, output.statusLabel'
        ).format(dataset='hemibrain:v1.0')
        queryResults3 = client.fetch_custom(query3)
        queryResults3.to_csv("TestServerCSV/NathanLC/" + str(NathanLCs3) + "_Summed_Query_WithoutOL.csv", index=False)
        allResults3 = allResults3.append(queryResults3)

    for NathanLCs4 in NathanLC:
        query4 = (
                ' MATCH (LC:hemibrain_Neuron)-[c:ConnectsTo]->(output:hemibrain_Neuron)'
                ' WHERE LC.type = "' + str(NathanLCs4) + '" AND output.status = "Traced"'
                                                         ' AND apoc.convert.fromJsonMap(c.roiInfo)["OL(R)"] IS NULL'
                                                         ' RETURN LC.bodyId, LC.type, c.weight, c.roiInfo, output.bodyId, output.type, output.instance, output.status, output.statusLabel'
        ).format(dataset='hemibrain:v1.0')
        queryResults4 = client.fetch_custom(query4)
        queryResults4.to_csv("TestServerCSV/NathanLC/" + str(NathanLCs4) + "_Query_WithoutOL.csv", index=False)
        allResults4 = allResults4.append(queryResults4)

    allResults3.to_csv("TestServerCSV/NathanLC/Summed_WithoutOL.csv", index=False)
    allResults4.to_csv("TestServerCSV/NathanLC/Expanded_WithoutOL.csv", index=False)
    return


def allLCQuery():
    LCs = ['LC4', 'LC6', 'LC9', 'LC10', 'LC11', 'LC12', 'LC13', 'LC14', 'LC15', 'LC16', 'LC17', 'LC18', 'LC20', 'LC21',
           'LC22', 'LC24',
           'LC25', 'LC26', 'LC27', 'LC28a', 'LC28b', 'LC28c', 'LC28d', 'LC29', 'LC31', 'LC32', 'LPLC1', 'LPLC2',
           'LPLC4']

    allResults = pd.DataFrame()
    allResults2 = pd.DataFrame()
    allResults3 = pd.DataFrame()
    allResults4 = pd.DataFrame()
    for LC in LCs:
        query = (
                ' MATCH (LC:hemibrain_Neuron)-[c:ConnectsTo]->(output:hemibrain_Neuron)'
                ' WHERE LC.type = "' + str(LC) + '" AND output.status = "Traced"'
                                                 ' RETURN COUNT(LC.type), LC.type, SUM(c.weight), AVG(c.weight), output.bodyId, output.type, output.instance, output.status, output.statusLabel'
        ).format(dataset='hemibrain:v1.0')
        queryResults = client.fetch_custom(query)
        queryResults.to_csv("TestServerCSV/AllLC/" + str(LC) + "_Summed_Query_WithOL.csv", index=False)
        allResults = allResults.append(queryResults)

    for LC2 in LCs:
        query2 = (
                ' MATCH (LC:hemibrain_Neuron)-[c:ConnectsTo]->(output:hemibrain_Neuron)'
                ' WHERE LC.type = "' + str(LC2) + '" AND output.status = "Traced"'
                                                  ' RETURN LC.bodyId, LC.type, c.weight, c.roiInfo, output.bodyId, output.type, output.instance, output.status, output.statusLabel'
        ).format(dataset='hemibrain:v1.0')
        queryResults2 = client.fetch_custom(query2)
        queryResults2.to_csv("TestServerCSV/AllLC/" + str(LC2) + "_Query_WithOL.csv", index=False)
        allResults2 = allResults2.append(queryResults2)

    allResults.to_csv("TestServerCSV/AllLC/Summed_WithOL.csv", index=False)
    allResults2.to_csv("TestServerCSV/AllLC/Expanded_WithOL.csv", index=False)

    for LC3 in LCs:
        query3 = (
                ' MATCH (LC:hemibrain_Neuron)-[c:ConnectsTo]->(output:hemibrain_Neuron)'
                ' WHERE LC.type = "' + str(LC3) + '" AND output.status = "Traced" '
                                                  'AND apoc.convert.fromJsonMap(c.roiInfo)["OL(R)"] IS NULL'
                                                  ' RETURN COUNT(LC.type), LC.type, SUM(c.weight), AVG(c.weight), output.bodyId, output.type, output.instance, output.status, output.statusLabel'
        ).format(dataset='hemibrain:v1.0')
        queryResults3 = client.fetch_custom(query3)
        queryResults3.to_csv("TestServerCSV/AllLC/" + str(LC3) + "_Summed_Query_WithoutOL.csv", index=False)
        allResults3 = allResults3.append(queryResults3)

    for LC4 in LCs:
        query4 = (
                ' MATCH (LC:hemibrain_Neuron)-[c:ConnectsTo]->(output:hemibrain_Neuron)'
                ' WHERE LC.type = "' + str(LC4) + '" AND output.status = "Traced"'
                                                  ' AND apoc.convert.fromJsonMap(c.roiInfo)["OL(R)"] IS NULL'
                                                  ' RETURN LC.bodyId, LC.type, c.weight, c.roiInfo, output.bodyId, output.type, output.instance, output.status, output.statusLabel'
        ).format(dataset='hemibrain:v1.0')
        queryResults4 = client.fetch_custom(query4)
        queryResults4.to_csv("TestServerCSV/AllLC/" + str(LC4) + "_Query_WithoutOL.csv", index=False)
        allResults4 = allResults4.append(queryResults4)

    allResults3.to_csv("TestServerCSV/AllLC/Summed_WithoutOL.csv", index=False)
    allResults4.to_csv("TestServerCSV/AllLC/Expanded_WithoutOL.csv", index=False)
    return


'''
def LCDict(allResults):
    for index, row in allResults.iterrows():
        LCDict[row['output.bodyId']].append({row["LC.type"]: row['SUM(c.weight)']})


for k, v in LCDict.items():
    if len(v) >= 5:
        LargerThan5[k].append(v)
        
        
   LargerThan5[1838257401][0][0]  
   
for index, row in allResults.iterrows():

bodyIds = [1838257401, 1809264255, 1191273014, 1873086710, 1907510214, 703106626, 1688505620, 1314052933, 1222985895, 5813038197, 1220270134, 5812987890, 1435791739, 1251287671, 1190926889, 1877217777, 1251032454, 1839288696, 1466861327, 1284027922, 2121711447, 1715459859, 1284377842, 1312061760, 1374063129, 5813061197, 1320290839, 1781268241, 1350626363, 5813039148, 5813023322, 1014344148, 1417768398, 1476868405, 1405780725, 1252665371, 1377845289, 1189559257, 1539508448, 1749258134, 5813022959, 1628523730, 1070950293, 1907584319, 1874035952, 5812988820, 1438524573, 1936848448, 1590979045, 1281303666, 915179102, 1416796844, 5813021112, 5813057178, 1318991216, 1068885266, 1354394414, 1281324958, 5813038299, 1343736290, 1907574944, 1189912345, 1498574596, 1220257051, 1810956698, 1937875810, 1998922583, 1342372169, 1224560577, 1158528396, 1283354429, 1218901359, 1219246255, 1221289185, 5813075607, 1342717266, 1188885915, 1040004619, 5813054141, 1435835226, 1072059176, 1158191887, 1157850005, 1406911688, 1375845363, 947573616, 1621357756, 1539193374, 1009984360, 1322263019, 1283708500, 1906159299, 5812998136, 1540518369, 575063620, 1469931842, 1529596392, 5813056453, 1221285128, 1159555822, 1376149163, 1562366881, 1589982128, 1403392477, 1311677904, 1374413370, 5901205169, 1281998821, 1405784237, 5812988098, 1312015204, 1343749602, 1474424990, 1434798830, 5812989593, 1435822283, 1435822158, 1504437450, 1249932198, 956082289, 1281316775, 1779221851, 1255405703, 1343749180, 5812988723, 5813045346, 5812992348, 1590650826, 1558605806, 1443040649, 1261229600, 5813078095, 1404109050, 1220257145, 5813050145, 5813081448, 1652043674, 5813023480, 1527553417, 1435489086, 1749275570, 1469947367, 1250277991, 1373398705, 1352684733, 5813038319, 5813033742, 1382308349, 1503733177, 1591701396, 1160070135, 1719643238, 1409540932, 5812990470, 5813037812, 1469663014, 1344064626, 1468207771, 1220260858, 5813038198, 544366430, 1591683365, 1622350949, 1529583573, 1404446113, 5812991035, 1312369036, 1352357010, 1560652549, 1013291042, 1128676181, 1343395439, 1017802759, 1404778340, 1817458164, 1747181914, 5813056423, 950561202, 1658990108, 1469905436, 1406966879, 1263668331, 1439889795, 1480222035, 5813033705, 1531323523, 1469227143, 1290209390, 1623378159, 1374767239, 1007256476, 1499912869, 1222332850, 1378251040, 1437224617, 1377841477, 1282676872, 1528573372, 1559284412, 1079872487, 1497200791, 5813070050, 1776536574, 5813060840, 1407148900, 1405789352, 1381277138, 2027238554, 1312346567, 1232603386, 1654076802, 5812988099, 1263663953, 1532060598, 1654405904, 1560988839, 1624074309, 1352335144, 1529923621, 981583545, 5812988128, 1779231120, 1567482594, 1232607449, 1189230639, 5812993250, 6400000641, 1776536597, 1559284164, 1807917290, 1589636158, 1284373356, 1558605812, 5812991538, 5813000369, 1311669538, 5812996611, 1497542425, 1809592670, 1466516076, 1684451749, 1566528972, 5812994445, 1319919698, 5812994347, 1685142429, 1716168586, 730709173, 1500020535, 1435140135, 1653752968, 5813038118, 1686169952, 5813047489, 5813061112, 1507139129, 5812990678, 5813023353, 1625412457, 1468630778, 5813058376, 5813022591, 1474446666, 5813037804, 1343403608, 1750946622, 1690011290, 1718179755, 1414694799, 1656792632, 1047784113, 2349505897, 1532410248, 5813053860, 1687525648, 1654754488, 2279285729, 5813069020, 5813054443, 5812992769, 912601209, 1232262105, 1777871882, 1715814552, 1467858252, 1747177906, 1686839045, 1779934954, 1533036404, 1655458719, 861242399, 1624747496, 1294362092, 5813000476, 5813077803, 1962409606, 1597493900, 1746849335, 1870655814, 5813038816, 1684434364, 1375769049, 5813025000, 1232603375, 1407179534, 1746858454, 1965117110, 1962754727, 5813077633, 1813399871, 5901213153, 1500020379, 1777542293, 2117929003, 2124762952, 1783362106, 1593417998, 2337582623, 1783051753, 1446061566, 1903746235, 1376485417, 1902364719, 1781328716, 1965125069, 1563095398, 1905784006, 1469918192, 2154417368, 1777918421, 1838615654, 1875460978, 2149663918, 1782364786, 5813047992, 2336572685, 1781333405, 1745157026, 1342371499, 5812996992, 1998250011, 1962759336, 1932730059, 2055859601, 1189912812, 5812994896, 1620671365, 2120010436, 1783068831, 5813056582, 2181048794, 2242759530, 1807572051, 1781674298, 1566519741, 1869649833, 1900335666, 1404101175, 2029624973, 2431693514, 2183777296, 1653428683, 5812989163, 2307207910, 2027912072, 1508118556, 2275491917, 1849179266, 2368604927, 2213438953, 5813062759, 1497205225, 5901215009, 5813062668, 1480525262, 1535086505, 2430359628, 1346560069, 1221457679, 1005149651, 5813062698, 1137085385, 2126426316, 974771466, 2063691268, 5813031440, 1476824820, 1164131530, 1876125353, 2061265627, 1595106149, 985369220, 2000226559, 1746507975, 2244810862, 1903046343, 1532699404, 5812993245, 5813049193, 1188889654, 2058950925, 1849507321, 2369995763, 1813352159, 1998176218, 5901204314, 5813057579, 1262654129, 5813024217, 1849178917, 1717899720, 1656494014, 1717899399, 1261561493, 986763451, 5813027276, 2120982517, 1005857944, 5812991924, 1346896720, 1848151877, 2245501457, 1595084420, 1346900360, 1407873674, 2278599819, 2275832690, 2244802974, 1903073323, 2026862112, 1288888967, 1504342382, 2249538551, 1996160234, 1684127680, 5813103030, 1407874177, 1563099587, 1049169888, 1080200419, 1262990404, 1938536260, 884477487, 2060297104, 5813049443, 1018472039, 1198132041, 1532060472, 1935813134, 1873353948, 5813079288, 1188599723, 1375504297, 1289242975, 1319583458, 5813041360, 1232594718, 1375504403, 670547617, 1259851971, 1229849059, 5812989550, 5813038177, 5813021583, 1007550646, 5813070572, 2158120721, 1232249325, 701201945, 1192744779, 1351667174, 1352331062, 974027716, 769263962, 1535087168, 1251684081, 1748222538, 1102407288, 1632016438, 2251593112, 1226831477, 1375504427, 1002360103, 1289920105, 5813026724, 5813068559, 1201568417, 1344810921, 5813048443, 1315084914, 858838262, 1498720407, 676479217, 1073691439, 1351312482, 708208811, 1317886409, 1231955849, 1965155742, 5813056020, 1231955819, 768806088, 1442708190, 1232634093, 1406147470, 1259852010, 1563389824, 1627509034, 1321564092, 1199855170, 1200195625, 1230190149, 5812987690, 5813044940, 1289574568, 644001906, 912290165, 581599704, 1231619255, 1654107502, 1381311623, 1658199518, 5812986572, 1232249314, 1201568464, 1320622829, 1352335943, 1167438283, 1200541193, 1200541130, 1259230618, 1777227052, 5813054053, 1232288020, 1625446695, 1198818609, 1287645091, 5813060834, 1198132028, 638148241, 1199159635, 5813057854, 5813109987, 1263327185, 1167438189, 977222655, 732600113, 1343407759, 792040520, 1167438288, 5813064410, 1690897627, 1386780502, 857793013, 486410031, 1232262131, 1135458373, 612634432, 821344462, 1230531237, 702760942, 1500373828, 1229507863, 1720950695, 5812981242, 1099981052, 1282348408, 1748929680, 5812989707, 1261565726, 1468230494, 1251978693, 5813075410, 797424771, 1345778226, 1747228863, 5813044470, 1192723421, 1043066007, 1074493547, 1722310842, 1038938989, 917527702, 1407260897, 1446762036, 974839706, 1167438034, 2342029025, 5813078261, 1006146837, 1196816048, 826062651, 1353031856, 5813053863, 1290227332, 1190591244, 1138855577, 1044701474, 5813053966, 1535791554, 950928506, 5812991476, 1230531125, 5812983094, 1902066682, 1418186940, 1439203192, 1719549300, 1624756312, 5813038196, 5812988854, 1531988112, 1314747047, 1314069729, 1564374638, 1007576087, 1593784995, 985036637, 1347147045, 5813054032, 1232266414, 2122047447, 1502342255, 671574812, 2063346008, 1189601546, 1937879935, 5813010405, 1259856448, 5813015781, 1351623779, 1222104921, 1319591678, 854093627, 1967844926, 1291573712, 543369332, 676504624, 577123102, 5813041581, 1049839301, 1379187792, 1718202035, 1657263405, 770249286, 1261902687, 544383511, 1134107162, 1080541803, 1288530238, 1442314421, 5813057077, 5812988577, 1597157083, 1848143184, 1222769755, 5813038770, 1686190133, 1533723752, 1811997861, 5812991001, 1595745569, 1319583082, 737093754, 1528926565, 1350937208, 1808936407, 5812988573, 919513165, 1808949598, 5812990956, 1110562345, 1935126292, 821345327, 1875469390, 1438550573, 7112579856, 1344810847, 1352664363, 738155917, 1232607542, 1222778569, 418607079, 1872046345, 1374438280, 1499248377, 1198123389, 1288897930, 2089648712, 2058954777, 2088285029, 1502001218, 2181730644, 1933426240, 1996872082, 1501665145, 1351644908, 945058110, 485037749, 1346788757, 760306167, 1079859469, 1749944256, 1810645950, 1747884974, 1562689878, 1561977675, 5813060340, 1232607453, 2246175600, 1500953002, 885810757, 1566169568, 1498582584, 733649312, 1628230708, 915105429, 1532358825, 1933429987, 5901207927, 1654110835, 1017781118, 1414776601, 986059699, 1874749571, 5812994094, 5813038911, 1875435759, 1438304554, 1604440343, 770585045, 1499226615, 1285750483, 5813056280, 1283031294, 1468877324, 1380979698, 1285849782, 2247525717, 2341317296, 1969222604, 5813016981, 1872358035, 1938830923, 2032301858, 1873738899, 2000265159, 2092343673, 2060285444, 1874782886, 1968877434, 1564097484, 1874063177, 2092684587, 2030605509, 1016758041, 543702551, 1503413234, 1501640127, 5812993665, 889523223, 1382023849, 2249261885, 5813054748, 2309272340, 1935821486, 1470950640, 1936507376, 2278906805, 2089977802, 857456902, 1469269528, 1110906913, 1294362035, 1563782253, 1872396010, 1872046798, 5813054785, 1994139218, 1263327135, 5812988063, 1289213295, 1414405144, 791527493, 1627561374, 5812990492, 2184437237, 1936128170, 1319246910, 1232607205, 1874395413, 1378168833, 1252116913, 987104744, 1017802884, 852738675, 5812988825, 5813022024, 5813077658, 1199496144, 1198818551, 5813067929, 1625800608, 5812989167, 1466511550, 1294021030, 5812988514, 1079527389, 1468350445, 1437527210, 1343732093, 1501664753, 1781324410, 1079867909, 5813048932, 1563393904, 1017797863, 5813017541, 1439577670, 1532342546, 1469214664, 5812992345, 1747518018, 1813403953, 1294362042, 544379269, 1560661080, 1745847773, 1404783051, 1714466923, 1529630300, 1405111246, 5812992219, 1901008788, 1280971174, 1589972966, 1250282268, 1501660164, 2462110671, 1745510607, 5813077655, 1621008677, 5812996956, 1530704811, 1808267138, 1251654856, 1622740353, 5812991952, 1466848532, 1622360309, 1590309572, 1653770546, 1684443103, 1435136061, 1559948889, 5812994314, 5813044569, 5813013339, 5812993994, 1498246331, 5812988077, 1110903013, 1376827225, 5812989161, 892609630, 1469589825, 1625804774, 1161688286, 1128274593, 5812979017, 1136744598, 1315770230, 1561351296, 1810659099, 1110894595, 1167092919, 1110557531, 1251995567, 5812988532, 1499830503, 1159206228, 1158877783, 1534798033, 517086196, 1158191562, 797442049, 1745830360, 1745852140, 1808241116, 1776865370, 1530606252, 1313702895, 5813014491, 986758977, 1471600919, 1408880450, 986767293, 1191315642, 914130079, 448342846, 854106922, 2371001151, 2059295981, 2184096375, 5813068748, 1017793356, 2308935125, 955029299, 1849166071, 1817453065, 1782982915, 5813133355, 1813382259, 1935088341, 1687184361, 1685781176, 1500029052, 1817785661, 5813039410, 1844421716, 1291569166, 1567482299, 5901215488, 1563364112, 1748187330, 5813075792, 1779567374, 1749258463, 5813045792, 1565496703, 1780953910, 1529933124, 5813062096, 1379183233, 1534721340, 1500603847, 1594730879, 1110903093, 1995861983, 1405788552, 1189566974, 1467859487, 1343744386, 1343045604, 1199496243, 1169492931, 5813016381, 574736017, 1906111185, 1906789614, 1783000305, 1719591388, 1138807924, 1566519520, 1686229077, 1262602271, 5813034544, 5812989421, 669325882, 1561309135, 1345455479, 1376134899, 1531323131, 1261220527, 1593730160, 1346645554, 1406155403, 1718896883, 666847851, 1440252127, 1906499952, 2153407415, 2026866677, 5813068239, 2369619281, 1110535962, 1110566383, 1842051749, 2122713426, 2121685030, 1912600163, 1653070984, 1412989088, 1532401727, 1344733447, 5813038679, 1561304414, 1561301125, 1158532993, 1110186452, 1751666374, 2340298769, 1469240274, 5813060163, 1528253194, 1747215795, 1714791446, 5813016380, 1528244653, 1533338992, 1904755969, 1875090567, 1875409918, 1438300285, 2155393090, 1817444670, 1016749259, 884450920, 388280381, 1597494148, 5812990925, 1466844031, 1280634257, 1404083795, 5812990472, 1500288728, 1655474822, 1562707421, 1375798493, 892964102, 1876761314, 5813002401, 5812999429, 1934768198, 1563126068, 1905092617, 2028559316, 1818473569, 1746884134, 1564157830, 1290961410, 1284338822, 1220948264, 1172627154, 1499277688, 5901215834, 2026896672, 2213452322, 1159715613, 1532699530, 2028261424, 2090681039, 5813007604, 5813031567, 1849503142, 2121707030, 1848156241, 2148964632, 1906159372, 1995516734, 2119665568, 1374442368, 1405106221, 1533040625, 1319919610, 5812997245, 1719237849, 5812994939, 861574640, 1282806123, 1221280490, 1188889837, 1221285175, 1135441187, 5812990060, 543692985, 1565833050, 1439590350, 1935813192, 2151334747, 1814410124, 1813732543, 1280980178, 5813061218, 1444351896, 1193448112, 5812992408, 1319923967, 1474087416, 1778920327, 1809259484, 1500024261, 1686156878, 1468196413, 1848496662, 2371337394, 1374784418, 1408207343, 1435140170, 1561646261, 5812990478, 1219592090, 1564123481, 1965492600, 2213789483, 5813000452, 1937193993, 2119324105, 1842005270, 2149987166, 1818122205, 1813391435, 1749270652, 1817448921, 1812363713, 1817449236, 1655496596, 1345442381, 5812987880, 1252337419, 1561688563, 1434798670, 862265699, 1621012598, 1620667669, 1379530114, 1316086414, 1658855991, 1597456370, 1100900138, 1753385655, 1847806275, 1281649467, 1281985562, 1250959964, 1189567690, 1652725444, 574058475, 1685828529, 1507445759, 5813054575, 5813002984, 1257245650, 1559961497, 1592382424, 1809260021, 1594126040, 1903413800, 5813038918, 1438304646, 1319579391, 2026880372, 1139153136, 696863848, 1818136404, 1809273516, 1313038188, 5813033955, 1777210876, 1747569967, 1685147024, 1933433614, 1251292628, 1528577476, 1405111071, 822393878, 516055524, 883121695, 1745165001, 1779239531, 852738302, 1467987587, 5813078658, 1440652320, 1940545072, 1159262177, 1815385988, 1655497024, 1789933168, 1356772884, 1280958033, 1249940263, 1188885499, 1252337098, 1342687063, 1343745534, 1312369181, 1595853024, 1658885859, 1325405571, 1940557189, 1969537024, 5812995535, 1412014916, 1934737876, 5813025002, 5812998725, 2059282786, 1748925835, 1904420313, 5812994062, 5812990157, 1379644459, 1534038921, 1133109676, 544046671, 1441283637, 5813031775, 1437302815, 2337569638, 2121690154, 701923413, 5813040744, 1285167873, 1130152528, 792369310, 945238486, 1128572709, 1627030775, 2398292746, 1498582292, 1810986443, 5812989300, 5813078174, 1875124235, 1172623224, 1684438377, 2120303900, 2026854120, 1873086684, 1807226822, 2181035795, 1963450199, 5813048268, 892600621, 918529614, 1128576728, 757880474, 5812980456, 860910626, 1689201166, 1285849916, 1657258136, 2094708038, 1566799785, 1751982133, 5812996568, 1938175243, 1970565478, 5813022538, 1260197431, 1503331732, 731736853, 1563122080, 893642012, 541697718, 2031308992, 1502364155, 1072063538, 1660241426, 1406583670, 5813001173, 2094381099, 1255138222, 5813023434, 1659904546, 821703262, 955365826, 1537466874, 955715991, 956043578, 1411250251, 1629168807, 2063013720, 974839708, 883514695, 1659866988, 1567107667, 1691937933, 1659235557, 956060773, 1876105544, 1018462968, 1876449448, 1347125913, 1503042472, 1468342128, 955383233, 1691933852, 1536434011, 852392901, 481035392, 824470535, 730398229, 419907780, 511685969, 1562703917, 1159944202, 1407866051, 1595431209, 1190737748, 2064683443, 5813054096, 1441590157, 1376791612, 1378182447, 1500369887, 1283030884, 1284386082, 1048125065, 1690902029, 1261220600, 2095374163, 1221768103, 1659184557, 1378604678, 1533040839, 1623422292, 1167434000, 1110885663, 1139498661, 1080212848, 1049502699, 1657516638, 1312368829, 1260192984, 5813021943, 1069632261, 1378587904, 1968548221, 1017094185, 1659522043, 1533063011, 1907824988, 1049510640, 1445445434, 1505753240, 1938489987, 1690220122, 1690283476, 1690910458, 1048120973, 1658502349, 1750605638, 5813041801, 5813126319, 1535718264, 1378860414, 2248587492, 1317457971, 1037328706, 1436188322, 5812986560, 1405145183, 5812991470, 1596811105, 1752980788, 5813046513, 2064040742, 1782309935, 1437276654, 5813002534, 1968531068, 1817449059, 1111580845, 1342704830, 1344086667, 913835893, 5813022826, 1877446436, 1595473051, 5812998950, 2030622534, 884464419, 5812998963, 2094043383, 2125414881, 789636635, 1904117126, 1467797424, 2156808568, 5813047655, 5813064415, 544038123, 1716487667, 5812989312, 915148745, 2214803693, 1966455276, 5813046323, 1289233847, 1717157246, 1439927802, 5813058236, 1409882329, 1877152860, 1439574161, 1561655196, 5901200775, 1069607310, 1657949330, 5901217539, 1374554946, 1533355907, 1346460600, 5812990726, 1939543295, 1449225711, 5901196898, 2061303987, 1843714465, 1999587615, 1629206279, 793815358, 1375482740, 2029587298, 1687874335, 1289574643, 1750273378, 1936482367, 1750595497, 5813069528, 1751986317, 5813002657, 852738570, 5813025540, 1376140131, 1561325878, 5813069702, 1251996302, 1376809072, 1438563366, 1320263998, 1377512967, 758296423, 1595409504, 1690228471, 697882667, 852724544, 1937501015, 1504092028, 1504700834, 1009919653, 1316431876, 1782987343, 1719250390, 976187276, 1468872910, 1319928209, 1628869271, 1407853195, 1688194895, 1531063618, 1437863703, 1468238571, 2215813235, 2372342652, 5813047685, 5901225239, 5813033675, 2032664066, 1779611494, 1718551623, 1905114003, 1936482106, 1563467433, 2059926799, 1935113207, 2341653659, 1873065775, 2186146614, 852051464, 2372718728, 1967866061, 1379541865, 1284054234, 1718227906, 1996522484, 1252121060, 1965825035, 1566511014, 1375924140, 1968215498, 573414975, 1967508592, 1723325346, 1005857954, 1716842091, 544038294, 1560311044, 1687844304, 1533015284, 1192434435, 1595062898, 5813002071, 1750269273, 1289229674, 1749919261, 1286083010, 1593388964, 2059275182, 1283371992, 1623391753, 1439903052, 1313392097, 1560328753, 1313733623, 1313388284, 1344055093, 1592728245, 1562712175, 1651710340, 2058932928, 1688535040, 1561347849, 1714462594, 5813054101, 1435817223, 1374097180, 1285076268, 1529635236, 1716522421, 1778220673, 1350277508, 1843023572, 5813001134, 2276540626, 1906104050, 5813002519, 1501074253, 1715158302, 1684127778, 1282844980, 1252151253, 1319587003, 5813015345, 1377002848, 915157442, 1591704108, 2339650329, 2183427685, 1847452619, 1684472544, 1997196747, 2246874503, 2058955063, 2152729460, 1470996844, 1813728233, 1222701117, 1750937412, 1905093495, 2091669751, 1996190954, 1719237770, 1437868812, 2186837387, 2033010036, 1904433415, 884463495, 1782321284, 1748550345, 1685149833, 5901200176, 5901197700, 1903397125, 2092019182, 5813031566, 1965142604, 2027880999, 1288893672, 1905114943, 1714816347, 1717562249, 5812993996, 1905093552, 2121340624, 2152371061, 1839975232, 1343749689, 1652747834, 1622394511, 735004751, 1686147462, 1562352871, 1559979355, 1436961485, 1227135350, 1384017738, 1563441250, 947923543, 1128200628, 1563436471, 1344811248, 1158903092, 1562054982, 1497875250, 1344469603, 1322626125, 1313849969, 1158873783, 1654818612, 1570896561, 1321305370, 1407947423, 1319927827, 1315758373, 1448794542, 1189606310, 1190409318, 1437186918, 1285068138, 5813045027, 5813038167, 1599872317, 1539496112, 1446062404, 5813063087, 1623081361, 1745147720, 1471337627, 1222302866, 1346115608, 1468993852, 1477434062, 1375462484, 943809606, 1505412068, 1714795031, 1714821040, 1683756677, 1715499249, 2088950218, 1683440362, 5813045024, 1624418395, 1344469589, 5812989784, 1499683287, 1189606166, 1529599641, 1993789617, 1776886049, 1841019896, 1652405664, 1652030642, 1500949679, 5813068801, 5813022753, 2187130567, 1450875637, 1750251452, 1779598492, 447228814, 1504428248, 5813049966, 1966174797, 1500369943, 1932747064, 1344469477, 2122704413, 1535808539, 1476782322, 2338956347, 2184463562, 944836835, 2244823763, 1350613510, 1873725935, 1749236368, 1074484603, 823395525, 2308585856, 2120342655, 1905429029, 1502701269, 1406928592, 1504096339, 5813002456, 1289238841, 1810978852, 1967537971, 1438304464, 1537456949, 1414712300, 1653395872, 1997498177, 1442699865, 1841663352, 5813107445, 1476778177, 1528914548, 1810944084, 5813018754, 1870993614, 1414073219, 1808927915, 5813022794, 1624083046, 5812989160, 1099333424, 1375504361, 1510855070, 2001633881, 2247535548, 1289229700, 5812989983, 5813031888, 5812985952, 1449486007, 1465824781, 1037237333, 1506120610, 5813034441, 1500063929, 1283039493, 1314075070, 7112613460, 1161399526, 977218524, 5813021911, 575073147, 790741191, 1344090837, 1130714433, 1288202406, 1538476539, 976190756, 1970219420, 1877792679, 1037895459, 1350273443, 2217488515, 1876112808, 1783682503, 2031266973, 2244482994, 5813054169, 2211737961, 881596353, 1285155206, 5812983356, 1006560977, 977913894, 1812005485, 1718883440, 1751601967, 2061316365, 1872720467, 2372697700, 1965483574, 1282007450, 1316194019, 674423996, 757530901, 666843764, 1969230358, 2000903820, 1723658004, 1538471582, 884122973, 1385015126, 1511593574, 1870655688, 1935118166, 1443026992, 1904083110, 1345860891, 1038926500, 1382002299, 1189605993, 5812995785, 2091997530, 2278224718, 1597835331, 1319919814, 858458268, 1256494044, 759960572, 853726809, 644757911, 945161760, 1225455907, 665169278, 5812983383, 1813727537, 821003563, 884446447, 1688855750, 1719569268, 5813075754, 200326126, 541723677, 479925776, 5813115583, 665820084, 672598344, 541723810, 758938220, 5813040731, 5813078595, 357224041, 821007911, 885132185, 357515217, 5813078062, 449250041, 944802835, 516857964, 727889637, 1314729915, 853097199, 1344431292, 603068370, 1076742501, 696859758, 452971138, 1563755856, 5813034789, 1408535544, 1005110376, 915503330, 1847115656, 358847551, 5813062635, 512308235, 574740549, 544037996, 515092013]
 
   

bodyIds = [1838257401, 1809264255, 1191273014, 1873086710, 1907510214, 703106626, 1688505620, 1314052933, 1222985895, 5813038197, 1220270134, 5812987890, 1435791739, 1251287671, 1190926889, 1877217777, 1251032454, 1839288696, 1466861327, 1284027922, 2121711447, 1715459859, 1284377842, 1312061760, 1374063129, 5813061197, 1320290839, 1781268241, 1350626363, 5813039148, 5813023322, 1014344148, 1417768398, 1476868405, 1405780725, 1252665371, 1377845289, 1189559257, 1539508448, 1749258134, 5813022959, 1628523730, 1070950293, 1907584319, 1874035952, 5812988820, 1438524573, 1936848448, 1590979045, 1281303666, 915179102, 1416796844, 5813021112, 5813057178, 1318991216, 1068885266, 1354394414, 1281324958, 5813038299, 1343736290, 1907574944, 1189912345, 1498574596, 1220257051, 1810956698, 1937875810, 1998922583, 1342372169, 1224560577, 1158528396, 1283354429, 1218901359, 1219246255, 1221289185, 5813075607, 1342717266, 1188885915, 1040004619, 5813054141, 1435835226, 1072059176, 1158191887, 1157850005, 1406911688, 1375845363, 947573616, 1621357756, 1539193374, 1009984360, 1322263019, 1283708500, 1906159299, 5812998136, 1540518369, 575063620, 1469931842, 1529596392, 5813056453, 1221285128, 1159555822, 1376149163, 1562366881, 1589982128, 1403392477, 1311677904, 1374413370, 5901205169, 1281998821, 1405784237, 5812988098, 1312015204, 1343749602, 1474424990, 1434798830, 5812989593, 1435822283, 1435822158, 1504437450, 1249932198, 956082289, 1281316775, 1779221851, 1255405703, 1343749180, 5812988723, 5813045346, 5812992348, 1590650826, 1558605806, 1443040649, 1261229600, 5813078095, 1404109050, 1220257145, 5813050145, 5813081448, 1652043674, 5813023480, 1527553417, 1435489086, 1749275570, 1469947367, 1250277991, 1373398705, 1352684733, 5813038319, 5813033742, 1382308349, 1503733177, 1591701396, 1160070135, 1719643238, 1409540932, 5812990470, 5813037812, 1469663014, 1344064626, 1468207771, 1220260858, 5813038198, 544366430, 1591683365, 1622350949, 1529583573, 1404446113, 5812991035, 1312369036, 1352357010, 1560652549, 1013291042, 1128676181, 1343395439, 1017802759, 1404778340, 1817458164, 1747181914, 5813056423, 950561202, 1658990108, 1469905436, 1406966879, 1263668331, 1439889795, 1480222035, 5813033705, 1531323523, 1469227143, 1290209390, 1623378159, 1374767239, 1007256476, 1499912869, 1222332850, 1378251040, 1437224617, 1377841477, 1282676872, 1528573372, 1559284412, 1079872487, 1497200791, 5813070050, 1776536574, 5813060840, 1407148900, 1405789352, 1381277138, 2027238554, 1312346567, 1232603386, 1654076802, 5812988099, 1263663953, 1532060598, 1654405904, 1560988839, 1624074309, 1352335144, 1529923621, 981583545, 5812988128, 1779231120, 1567482594, 1232607449, 1189230639, 5812993250, 6400000641, 1776536597, 1559284164, 1807917290, 1589636158, 1284373356, 1558605812, 5812991538, 5813000369, 1311669538, 5812996611, 1497542425, 1809592670, 1466516076, 1684451749, 1566528972, 5812994445, 1319919698, 5812994347, 1685142429, 1716168586, 730709173, 1500020535, 1435140135, 1653752968, 5813038118, 1686169952, 5813047489, 5813061112, 1507139129, 5812990678, 5813023353, 1625412457, 1468630778, 5813058376, 5813022591, 1474446666, 5813037804, 1343403608, 1750946622, 1690011290, 1718179755, 1414694799, 1656792632, 1047784113, 2349505897, 1532410248, 5813053860, 1687525648, 1654754488, 2279285729, 5813069020, 5813054443, 5812992769, 912601209, 1232262105, 1777871882, 1715814552, 1467858252, 1747177906, 1686839045, 1779934954, 1533036404, 1655458719, 861242399, 1624747496, 1294362092, 5813000476, 5813077803, 1962409606, 1597493900, 1746849335, 1870655814, 5813038816, 1684434364, 1375769049, 5813025000, 1232603375, 1407179534, 1746858454, 1965117110, 1962754727, 5813077633, 1813399871, 5901213153, 1500020379, 1777542293, 2117929003, 2124762952, 1783362106, 1593417998, 2337582623, 1783051753, 1446061566, 1903746235, 1376485417, 1902364719, 1781328716, 1965125069, 1563095398, 1905784006, 1469918192, 2154417368, 1777918421, 1838615654, 1875460978, 2149663918, 1782364786, 5813047992, 2336572685, 1781333405, 1745157026, 1342371499, 5812996992, 1998250011, 1962759336, 1932730059, 2055859601, 1189912812, 5812994896, 1620671365, 2120010436, 1783068831, 5813056582, 2181048794, 2242759530, 1807572051, 1781674298, 1566519741, 1869649833, 1900335666, 1404101175, 2029624973, 2431693514, 2183777296, 1653428683, 5812989163, 2307207910, 2027912072, 1508118556, 2275491917, 1849179266, 2368604927, 2213438953, 5813062759, 1497205225, 5901215009, 5813062668, 1480525262, 1535086505, 2430359628, 1346560069, 1221457679, 1005149651, 5813062698, 1137085385, 2126426316, 974771466, 2063691268, 5813031440, 1476824820, 1164131530, 1876125353, 2061265627, 1595106149, 985369220, 2000226559, 1746507975, 2244810862, 1903046343, 1532699404, 5812993245, 5813049193, 1188889654, 2058950925, 1849507321, 2369995763, 1813352159, 1998176218, 5901204314, 5813057579, 1262654129, 5813024217, 1849178917, 1717899720, 1656494014, 1717899399, 1261561493, 986763451, 5813027276, 2120982517, 1005857944, 5812991924, 1346896720, 1848151877, 2245501457, 1595084420, 1346900360, 1407873674, 2278599819, 2275832690, 2244802974, 1903073323, 2026862112, 1288888967, 1504342382, 2249538551, 1996160234, 1684127680, 5813103030, 1407874177, 1563099587, 1049169888, 1080200419, 1262990404, 1938536260, 884477487, 2060297104, 5813049443, 1018472039, 1198132041, 1532060472, 1935813134, 1873353948, 5813079288, 1188599723, 1375504297, 1289242975, 1319583458, 5813041360, 1232594718, 1375504403, 670547617, 1259851971, 1229849059, 5812989550, 5813038177, 5813021583, 1007550646, 5813070572, 2158120721, 1232249325, 701201945, 1192744779, 1351667174, 1352331062, 974027716, 769263962, 1535087168, 1251684081, 1748222538, 1102407288, 1632016438, 2251593112, 1226831477, 1375504427, 1002360103, 1289920105, 5813026724, 5813068559, 1201568417, 1344810921, 5813048443, 1315084914, 858838262, 1498720407, 676479217, 1073691439, 1351312482, 708208811, 1317886409, 1231955849, 1965155742, 5813056020, 1231955819, 768806088, 1442708190, 1232634093, 1406147470, 1259852010, 1563389824, 1627509034, 1321564092, 1199855170, 1200195625, 1230190149, 5812987690, 5813044940, 1289574568, 644001906, 912290165, 581599704, 1231619255, 1654107502, 1381311623, 1658199518, 5812986572, 1232249314, 1201568464, 1320622829, 1352335943, 1167438283, 1200541193, 1200541130, 1259230618, 1777227052, 5813054053, 1232288020, 1625446695, 1198818609, 1287645091, 5813060834, 1198132028, 638148241, 1199159635, 5813057854, 5813109987, 1263327185, 1167438189, 977222655, 732600113, 1343407759, 792040520, 1167438288, 5813064410, 1690897627, 1386780502, 857793013, 486410031, 1232262131, 1135458373, 612634432, 821344462, 1230531237, 702760942, 1500373828, 1229507863, 1720950695, 5812981242, 1099981052, 1282348408, 1748929680, 5812989707, 1261565726, 1468230494, 1251978693, 5813075410, 797424771, 1345778226, 1747228863, 5813044470, 1192723421, 1043066007, 1074493547, 1722310842, 1038938989, 917527702, 1407260897, 1446762036, 974839706, 1167438034, 2342029025, 5813078261, 1006146837, 1196816048, 826062651, 1353031856, 5813053863, 1290227332, 1190591244, 1138855577, 1044701474, 5813053966, 1535791554, 950928506, 5812991476, 1230531125, 5812983094, 1902066682, 1418186940, 1439203192, 1719549300, 1624756312, 5813038196, 5812988854, 1531988112, 1314747047, 1314069729, 1564374638, 1007576087, 1593784995, 985036637, 1347147045, 5813054032, 1232266414, 2122047447, 1502342255, 671574812, 2063346008, 1189601546, 1937879935, 5813010405, 1259856448, 5813015781, 1351623779, 1222104921, 1319591678, 854093627, 1967844926, 1291573712, 543369332, 676504624, 577123102, 5813041581, 1049839301, 1379187792, 1718202035, 1657263405, 770249286, 1261902687, 544383511, 1134107162, 1080541803, 1288530238, 1442314421, 5813057077, 5812988577, 1597157083, 1848143184, 1222769755, 5813038770, 1686190133, 1533723752, 1811997861, 5812991001, 1595745569, 1319583082, 737093754, 1528926565, 1350937208, 1808936407, 5812988573, 919513165, 1808949598, 5812990956, 1110562345, 1935126292, 821345327, 1875469390, 1438550573, 7112579856, 1344810847, 1352664363, 738155917, 1232607542, 1222778569, 418607079, 1872046345, 1374438280, 1499248377, 1198123389, 1288897930, 2089648712, 2058954777, 2088285029, 1502001218, 2181730644, 1933426240, 1996872082, 1501665145, 1351644908, 945058110, 485037749, 1346788757, 760306167, 1079859469, 1749944256, 1810645950, 1747884974, 1562689878, 1561977675, 5813060340, 1232607453, 2246175600, 1500953002, 885810757, 1566169568, 1498582584, 733649312, 1628230708, 915105429, 1532358825, 1933429987, 5901207927, 1654110835, 1017781118, 1414776601, 986059699, 1874749571, 5812994094, 5813038911, 1875435759, 1438304554, 1604440343, 770585045, 1499226615, 1285750483, 5813056280, 1283031294, 1468877324, 1380979698, 1285849782, 2247525717, 2341317296, 1969222604, 5813016981, 1872358035, 1938830923, 2032301858, 1873738899, 2000265159, 2092343673, 2060285444, 1874782886, 1968877434, 1564097484, 1874063177, 2092684587, 2030605509, 1016758041, 543702551, 1503413234, 1501640127, 5812993665, 889523223, 1382023849, 2249261885, 5813054748, 2309272340, 1935821486, 1470950640, 1936507376, 2278906805, 2089977802, 857456902, 1469269528, 1110906913, 1294362035, 1563782253, 1872396010, 1872046798, 5813054785, 1994139218, 1263327135, 5812988063, 1289213295, 1414405144, 791527493, 1627561374, 5812990492, 2184437237, 1936128170, 1319246910, 1232607205, 1874395413, 1378168833, 1252116913, 987104744, 1017802884, 852738675, 5812988825, 5813022024, 5813077658, 1199496144, 1198818551, 5813067929, 1625800608, 5812989167, 1466511550, 1294021030, 5812988514, 1079527389, 1468350445, 1437527210, 1343732093, 1501664753, 1781324410, 1079867909, 5813048932, 1563393904, 1017797863, 5813017541, 1439577670, 1532342546, 1469214664, 5812992345, 1747518018, 1813403953, 1294362042, 544379269, 1560661080, 1745847773, 1404783051, 1714466923, 1529630300, 1405111246, 5812992219, 1901008788, 1280971174, 1589972966, 1250282268, 1501660164, 2462110671, 1745510607, 5813077655, 1621008677, 5812996956, 1530704811, 1808267138, 1251654856, 1622740353, 5812991952, 1466848532, 1622360309, 1590309572, 1653770546, 1684443103, 1435136061, 1559948889, 5812994314, 5813044569, 5813013339, 5812993994, 1498246331, 5812988077, 1110903013, 1376827225, 5812989161, 892609630, 1469589825, 1625804774, 1161688286, 1128274593, 5812979017, 1136744598, 1315770230, 1561351296, 1810659099, 1110894595, 1167092919, 1110557531, 1251995567, 5812988532, 1499830503, 1159206228, 1158877783, 1534798033, 517086196, 1158191562, 797442049, 1745830360, 1745852140, 1808241116, 1776865370, 1530606252, 1313702895, 5813014491, 986758977, 1471600919, 1408880450, 986767293, 1191315642, 914130079, 448342846, 854106922, 2371001151, 2059295981, 2184096375, 5813068748, 1017793356, 2308935125, 955029299, 1849166071, 1817453065, 1782982915, 5813133355, 1813382259, 1935088341, 1687184361, 1685781176, 1500029052, 1817785661, 5813039410, 1844421716, 1291569166, 1567482299, 5901215488, 1563364112, 1748187330, 5813075792, 1779567374, 1749258463, 5813045792, 1565496703, 1780953910, 1529933124, 5813062096, 1379183233, 1534721340, 1500603847, 1594730879, 1110903093, 1995861983, 1405788552, 1189566974, 1467859487, 1343744386, 1343045604, 1199496243, 1169492931, 5813016381, 574736017, 1906111185, 1906789614, 1783000305, 1719591388, 1138807924, 1566519520, 1686229077, 1262602271, 5813034544, 5812989421, 669325882, 1561309135, 1345455479, 1376134899, 1531323131, 1261220527, 1593730160, 1346645554, 1406155403, 1718896883, 666847851, 1440252127, 1906499952, 2153407415, 2026866677, 5813068239, 2369619281, 1110535962, 1110566383, 1842051749, 2122713426, 2121685030, 1912600163, 1653070984, 1412989088, 1532401727, 1344733447, 5813038679, 1561304414, 1561301125, 1158532993, 1110186452, 1751666374, 2340298769, 1469240274, 5813060163, 1528253194, 1747215795, 1714791446, 5813016380, 1528244653, 1533338992, 1904755969, 1875090567, 1875409918, 1438300285, 2155393090, 1817444670, 1016749259, 884450920, 388280381, 1597494148, 5812990925, 1466844031, 1280634257, 1404083795, 5812990472, 1500288728, 1655474822, 1562707421, 1375798493, 892964102, 1876761314, 5813002401, 5812999429, 1934768198, 1563126068, 1905092617, 2028559316, 1818473569, 1746884134, 1564157830, 1290961410, 1284338822, 1220948264, 1172627154, 1499277688, 5901215834, 2026896672, 2213452322, 1159715613, 1532699530, 2028261424, 2090681039, 5813007604, 5813031567, 1849503142, 2121707030, 1848156241, 2148964632, 1906159372, 1995516734, 2119665568, 1374442368, 1405106221, 1533040625, 1319919610, 5812997245, 1719237849, 5812994939, 861574640, 1282806123, 1221280490, 1188889837, 1221285175, 1135441187, 5812990060, 543692985, 1565833050, 1439590350, 1935813192, 2151334747, 1814410124, 1813732543, 1280980178, 5813061218, 1444351896, 1193448112, 5812992408, 1319923967, 1474087416, 1778920327, 1809259484, 1500024261, 1686156878, 1468196413, 1848496662, 2371337394, 1374784418, 1408207343, 1435140170, 1561646261, 5812990478, 1219592090, 1564123481, 1965492600, 2213789483, 5813000452, 1937193993, 2119324105, 1842005270, 2149987166, 1818122205, 1813391435, 1749270652, 1817448921, 1812363713, 1817449236, 1655496596, 1345442381, 5812987880, 1252337419, 1561688563, 1434798670, 862265699, 1621012598, 1620667669, 1379530114, 1316086414, 1658855991, 1597456370, 1100900138, 1753385655, 1847806275, 1281649467, 1281985562, 1250959964, 1189567690, 1652725444, 574058475, 1685828529, 1507445759, 5813054575, 5813002984, 1257245650, 1559961497, 1592382424, 1809260021, 1594126040, 1903413800, 5813038918, 1438304646, 1319579391, 2026880372, 1139153136, 696863848, 1818136404, 1809273516, 1313038188, 5813033955, 1777210876, 1747569967, 1685147024, 1933433614, 1251292628, 1528577476, 1405111071, 822393878, 516055524, 883121695, 1745165001, 1779239531, 852738302, 1467987587, 5813078658, 1440652320, 1940545072, 1159262177, 1815385988, 1655497024, 1789933168, 1356772884, 1280958033, 1249940263, 1188885499, 1252337098, 1342687063, 1343745534, 1312369181, 1595853024, 1658885859, 1325405571, 1940557189, 1969537024, 5812995535, 1412014916, 1934737876, 5813025002, 5812998725, 2059282786, 1748925835, 1904420313, 5812994062, 5812990157, 1379644459, 1534038921, 1133109676, 544046671, 1441283637, 5813031775, 1437302815, 2337569638, 2121690154, 701923413, 5813040744, 1285167873, 1130152528, 792369310, 945238486, 1128572709, 1627030775, 2398292746, 1498582292, 1810986443, 5812989300, 5813078174, 1875124235, 1172623224, 1684438377, 2120303900, 2026854120, 1873086684, 1807226822, 2181035795, 1963450199, 5813048268, 892600621, 918529614, 1128576728, 757880474, 5812980456, 860910626, 1689201166, 1285849916, 1657258136, 2094708038, 1566799785, 1751982133, 5812996568, 1938175243, 1970565478, 5813022538, 1260197431, 1503331732, 731736853, 1563122080, 893642012, 541697718, 2031308992, 1502364155, 1072063538, 1660241426, 1406583670, 5813001173, 2094381099, 1255138222, 5813023434, 1659904546, 821703262, 955365826, 1537466874, 955715991, 956043578, 1411250251, 1629168807, 2063013720, 974839708, 883514695, 1659866988, 1567107667, 1691937933, 1659235557, 956060773, 1876105544, 1018462968, 1876449448, 1347125913, 1503042472, 1468342128, 955383233, 1691933852, 1536434011, 852392901, 481035392, 824470535, 730398229, 419907780, 511685969, 1562703917, 1159944202, 1407866051, 1595431209, 1190737748, 2064683443, 5813054096, 1441590157, 1376791612, 1378182447, 1500369887, 1283030884, 1284386082, 1048125065, 1690902029, 1261220600, 2095374163, 1221768103, 1659184557, 1378604678, 1533040839, 1623422292, 1167434000, 1110885663, 1139498661, 1080212848, 1049502699, 1657516638, 1312368829, 1260192984, 5813021943, 1069632261, 1378587904, 1968548221, 1017094185, 1659522043, 1533063011, 1907824988, 1049510640, 1445445434, 1505753240, 1938489987, 1690220122, 1690283476, 1690910458, 1048120973, 1658502349, 1750605638, 5813041801, 5813126319, 1535718264, 1378860414, 2248587492, 1317457971, 1037328706, 1436188322, 5812986560, 1405145183, 5812991470, 1596811105, 1752980788, 5813046513, 2064040742, 1782309935, 1437276654, 5813002534, 1968531068, 1817449059, 1111580845, 1342704830, 1344086667, 913835893, 5813022826, 1877446436, 1595473051, 5812998950, 2030622534, 884464419, 5812998963, 2094043383, 2125414881, 789636635, 1904117126, 1467797424, 2156808568, 5813047655, 5813064415, 544038123, 1716487667, 5812989312, 915148745, 2214803693, 1966455276, 5813046323, 1289233847, 1717157246, 1439927802, 5813058236, 1409882329, 1877152860, 1439574161, 1561655196, 5901200775, 1069607310, 1657949330, 5901217539, 1374554946, 1533355907, 1346460600, 5812990726, 1939543295, 1449225711, 5901196898, 2061303987, 1843714465, 1999587615, 1629206279, 793815358, 1375482740, 2029587298, 1687874335, 1289574643, 1750273378, 1936482367, 1750595497, 5813069528, 1751986317, 5813002657, 852738570, 5813025540, 1376140131, 1561325878, 5813069702, 1251996302, 1376809072, 1438563366, 1320263998, 1377512967, 758296423, 1595409504, 1690228471, 697882667, 852724544, 1937501015, 1504092028, 1504700834, 1009919653, 1316431876, 1782987343, 1719250390, 976187276, 1468872910, 1319928209, 1628869271, 1407853195, 1688194895, 1531063618, 1437863703, 1468238571, 2215813235, 2372342652, 5813047685, 5901225239, 5813033675, 2032664066, 1779611494, 1718551623, 1905114003, 1936482106, 1563467433, 2059926799, 1935113207, 2341653659, 1873065775, 2186146614, 852051464, 2372718728, 1967866061, 1379541865, 1284054234, 1718227906, 1996522484, 1252121060, 1965825035, 1566511014, 1375924140, 1968215498, 573414975, 1967508592, 1723325346, 1005857954, 1716842091, 544038294, 1560311044, 1687844304, 1533015284, 1192434435, 1595062898, 5813002071, 1750269273, 1289229674, 1749919261, 1286083010, 1593388964, 2059275182, 1283371992, 1623391753, 1439903052, 1313392097, 1560328753, 1313733623, 1313388284, 1344055093, 1592728245, 1562712175, 1651710340, 2058932928, 1688535040, 1561347849, 1714462594, 5813054101, 1435817223, 1374097180, 1285076268, 1529635236, 1716522421, 1778220673, 1350277508, 1843023572, 5813001134, 2276540626, 1906104050, 5813002519, 1501074253, 1715158302, 1684127778, 1282844980, 1252151253, 1319587003, 5813015345, 1377002848, 915157442, 1591704108, 2339650329, 2183427685, 1847452619, 1684472544, 1997196747, 2246874503, 2058955063, 2152729460, 1470996844, 1813728233, 1222701117, 1750937412, 1905093495, 2091669751, 1996190954, 1719237770, 1437868812, 2186837387, 2033010036, 1904433415, 884463495, 1782321284, 1748550345, 1685149833, 5901200176, 5901197700, 1903397125, 2092019182, 5813031566, 1965142604, 2027880999, 1288893672, 1905114943, 1714816347, 1717562249, 5812993996, 1905093552, 2121340624, 2152371061, 1839975232, 1343749689, 1652747834, 1622394511, 735004751, 1686147462, 1562352871, 1559979355, 1436961485, 1227135350, 1384017738, 1563441250, 947923543, 1128200628, 1563436471, 1344811248, 1158903092, 1562054982, 1497875250, 1344469603, 1322626125, 1313849969, 1158873783, 1654818612, 1570896561, 1321305370, 1407947423, 1319927827, 1315758373, 1448794542, 1189606310, 1190409318, 1437186918, 1285068138, 5813045027, 5813038167, 1599872317, 1539496112, 1446062404, 5813063087, 1623081361, 1745147720, 1471337627, 1222302866, 1346115608, 1468993852, 1477434062, 1375462484, 943809606, 1505412068, 1714795031, 1714821040, 1683756677, 1715499249, 2088950218, 1683440362, 5813045024, 1624418395, 1344469589, 5812989784, 1499683287, 1189606166, 1529599641, 1993789617, 1776886049, 1841019896, 1652405664, 1652030642, 1500949679, 5813068801, 5813022753, 2187130567, 1450875637, 1750251452, 1779598492, 447228814, 1504428248, 5813049966, 1966174797, 1500369943, 1932747064, 1344469477, 2122704413, 1535808539, 1476782322, 2338956347, 2184463562, 944836835, 2244823763, 1350613510, 1873725935, 1749236368, 1074484603, 823395525, 2308585856, 2120342655, 1905429029, 1502701269, 1406928592, 1504096339, 5813002456, 1289238841, 1810978852, 1967537971, 1438304464, 1537456949, 1414712300, 1653395872, 1997498177, 1442699865, 1841663352, 5813107445, 1476778177, 1528914548, 1810944084, 5813018754, 1870993614, 1414073219, 1808927915, 5813022794, 1624083046, 5812989160, 1099333424, 1375504361, 1510855070, 2001633881, 2247535548, 1289229700, 5812989983, 5813031888, 5812985952, 1449486007, 1465824781, 1037237333, 1506120610, 5813034441, 1500063929, 1283039493, 1314075070, 7112613460, 1161399526, 977218524, 5813021911, 575073147, 790741191, 1344090837, 1130714433, 1288202406, 1538476539, 976190756, 1970219420, 1877792679, 1037895459, 1350273443, 2217488515, 1876112808, 1783682503, 2031266973, 2244482994, 5813054169, 2211737961, 881596353, 1285155206, 5812983356, 1006560977, 977913894, 1812005485, 1718883440, 1751601967, 2061316365, 1872720467, 2372697700, 1965483574, 1282007450, 1316194019, 674423996, 757530901, 666843764, 1969230358, 2000903820, 1723658004, 1538471582, 884122973, 1385015126, 1511593574, 1870655688, 1935118166, 1443026992, 1904083110, 1345860891, 1038926500, 1382002299, 1189605993, 5812995785, 2091997530, 2278224718, 1597835331, 1319919814, 858458268, 1256494044, 759960572, 853726809, 644757911, 945161760, 1225455907, 665169278, 5812983383, 1813727537, 821003563, 884446447, 1688855750, 1719569268, 5813075754, 200326126, 541723677, 479925776, 5813115583, 665820084, 672598344, 541723810, 758938220, 5813040731, 5813078595, 357224041, 821007911, 885132185, 357515217, 5813078062, 449250041, 944802835, 516857964, 727889637, 1314729915, 853097199, 1344431292, 603068370, 1076742501, 696859758, 452971138, 1563755856, 5813034789, 1408535544, 1005110376, 915503330, 1847115656, 358847551, 5813062635, 512308235, 574740549, 544037996, 515092013]

for index, row in allResults.iterrows():
    for body in bodyIds:
        if row['output.bodyId'] == body:
            L5[index].append[row]



LCs = ['LC4','LC6','LC9','LC10','LC11','LC12','LC13','LC14','LC15','LC16','LC17','LC18','LC20','LC21','LC22','LC24',
       'LC25','LC26','LC27','LC28a','LC28b','LC28c','LC28d','LC29','LC31','LC32']

bodyIds = [1838257401, 1809264255, 1191273014, 1873086710, 1907510214, 703106626, 1688505620, 1314052933, 1222985895, 5813038197, 1220270134, 5812987890, 1435791739, 1251287671, 1190926889, 1877217777, 1251032454, 1839288696, 1466861327, 1284027922, 2121711447, 1715459859, 1284377842, 1312061760, 1374063129, 5813061197, 1320290839, 1781268241, 1350626363, 5813039148, 5813023322, 1014344148, 1417768398, 1476868405, 1405780725, 1252665371, 1377845289, 1189559257, 1539508448, 1749258134, 5813022959, 1628523730, 1070950293, 1907584319, 1874035952, 5812988820, 1438524573, 1936848448, 1590979045, 1281303666, 915179102, 1416796844, 5813021112, 5813057178, 1318991216, 1068885266, 1354394414, 1281324958, 5813038299, 1343736290, 1907574944, 1189912345, 1498574596, 1220257051, 1810956698, 1937875810, 1998922583, 1342372169, 1224560577, 1158528396, 1283354429, 1218901359, 1219246255, 1221289185, 5813075607, 1342717266, 1188885915, 1040004619, 5813054141, 1435835226, 1072059176, 1158191887, 1157850005, 1406911688, 1375845363, 947573616, 1621357756, 1539193374, 1009984360, 1322263019, 1283708500, 1906159299, 5812998136, 1540518369, 575063620, 1469931842, 1529596392, 5813056453, 1221285128, 1159555822, 1376149163, 1562366881, 1589982128, 1403392477, 1311677904, 1374413370, 5901205169, 1281998821, 1405784237, 5812988098, 1312015204, 1343749602, 1474424990, 1434798830, 5812989593, 1435822283, 1435822158, 1504437450, 1249932198, 956082289, 1281316775, 1779221851, 1255405703, 1343749180, 5812988723, 5813045346, 5812992348, 1590650826, 1558605806, 1443040649, 1261229600, 5813078095, 1404109050, 1220257145, 5813050145, 5813081448, 1652043674, 5813023480, 1527553417, 1435489086, 1749275570, 1469947367, 1250277991, 1373398705, 1352684733, 5813038319, 5813033742, 1382308349, 1503733177, 1591701396, 1160070135, 1719643238, 1409540932, 5812990470, 5813037812, 1469663014, 1344064626, 1468207771, 1220260858, 5813038198, 544366430, 1591683365, 1622350949, 1529583573, 1404446113, 5812991035, 1312369036, 1352357010, 1560652549, 1013291042, 1128676181, 1343395439, 1017802759, 1404778340, 1817458164, 1747181914, 5813056423, 950561202, 1658990108, 1469905436, 1406966879, 1263668331, 1439889795, 1480222035, 5813033705, 1531323523, 1469227143, 1290209390, 1623378159, 1374767239, 1007256476, 1499912869, 1222332850, 1378251040, 1437224617, 1377841477, 1282676872, 1528573372, 1559284412, 1079872487, 1497200791, 5813070050, 1776536574, 5813060840, 1407148900, 1405789352, 1381277138, 2027238554, 1312346567, 1232603386, 1654076802, 5812988099, 1263663953, 1532060598, 1654405904, 1560988839, 1624074309, 1352335144, 1529923621, 981583545, 5812988128, 1779231120, 1567482594, 1232607449, 1189230639, 5812993250, 6400000641, 1776536597, 1559284164, 1807917290, 1589636158, 1284373356, 1558605812, 5812991538, 5813000369, 1311669538, 5812996611, 1497542425, 1809592670, 1466516076, 1684451749, 1566528972, 5812994445, 1319919698, 5812994347, 1685142429, 1716168586, 730709173, 1500020535, 1435140135, 1653752968, 5813038118, 1686169952, 5813047489, 5813061112, 1507139129, 5812990678, 5813023353, 1625412457, 1468630778, 5813058376, 5813022591, 1474446666, 5813037804, 1343403608, 1750946622, 1690011290, 1718179755, 1414694799, 1656792632, 1047784113, 2349505897, 1532410248, 5813053860, 1687525648, 1654754488, 2279285729, 5813069020, 5813054443, 5812992769, 912601209, 1232262105, 1777871882, 1715814552, 1467858252, 1747177906, 1686839045, 1779934954, 1533036404, 1655458719, 861242399, 1624747496, 1294362092, 5813000476, 5813077803, 1962409606, 1597493900, 1746849335, 1870655814, 5813038816, 1684434364, 1375769049, 5813025000, 1232603375, 1407179534, 1746858454, 1965117110, 1962754727, 5813077633, 1813399871, 5901213153, 1500020379, 1777542293, 2117929003, 2124762952, 1783362106, 1593417998, 2337582623, 1783051753, 1446061566, 1903746235, 1376485417, 1902364719, 1781328716, 1965125069, 1563095398, 1905784006, 1469918192, 2154417368, 1777918421, 1838615654, 1875460978, 2149663918, 1782364786, 5813047992, 2336572685, 1781333405, 1745157026, 1342371499, 5812996992, 1998250011, 1962759336, 1932730059, 2055859601, 1189912812, 5812994896, 1620671365, 2120010436, 1783068831, 5813056582, 2181048794, 2242759530, 1807572051, 1781674298, 1566519741, 1869649833, 1900335666, 1404101175, 2029624973, 2431693514, 2183777296, 1653428683, 5812989163, 2307207910, 2027912072, 1508118556, 2275491917, 1849179266, 2368604927, 2213438953, 5813062759, 1497205225, 5901215009, 5813062668, 1480525262, 1535086505, 2430359628, 1346560069, 1221457679, 1005149651, 5813062698, 1137085385, 2126426316, 974771466, 2063691268, 5813031440, 1476824820, 1164131530, 1876125353, 2061265627, 1595106149, 985369220, 2000226559, 1746507975, 2244810862, 1903046343, 1532699404, 5812993245, 5813049193, 1188889654, 2058950925, 1849507321, 2369995763, 1813352159, 1998176218, 5901204314, 5813057579, 1262654129, 5813024217, 1849178917, 1717899720, 1656494014, 1717899399, 1261561493, 986763451, 5813027276, 2120982517, 1005857944, 5812991924, 1346896720, 1848151877, 2245501457, 1595084420, 1346900360, 1407873674, 2278599819, 2275832690, 2244802974, 1903073323, 2026862112, 1288888967, 1504342382, 2249538551, 1996160234, 1684127680, 5813103030, 1407874177, 1563099587, 1049169888, 1080200419, 1262990404, 1938536260, 884477487, 2060297104, 5813049443, 1018472039, 1198132041, 1532060472, 1935813134, 1873353948, 5813079288, 1188599723, 1375504297, 1289242975, 1319583458, 5813041360, 1232594718, 1375504403, 670547617, 1259851971, 1229849059, 5812989550, 5813038177, 5813021583, 1007550646, 5813070572, 2158120721, 1232249325, 701201945, 1192744779, 1351667174, 1352331062, 974027716, 769263962, 1535087168, 1251684081, 1748222538, 1102407288, 1632016438, 2251593112, 1226831477, 1375504427, 1002360103, 1289920105, 5813026724, 5813068559, 1201568417, 1344810921, 5813048443, 1315084914, 858838262, 1498720407, 676479217, 1073691439, 1351312482, 708208811, 1317886409, 1231955849, 1965155742, 5813056020, 1231955819, 768806088, 1442708190, 1232634093, 1406147470, 1259852010, 1563389824, 1627509034, 1321564092, 1199855170, 1200195625, 1230190149, 5812987690, 5813044940, 1289574568, 644001906, 912290165, 581599704, 1231619255, 1654107502, 1381311623, 1658199518, 5812986572, 1232249314, 1201568464, 1320622829, 1352335943, 1167438283, 1200541193, 1200541130, 1259230618, 1777227052, 5813054053, 1232288020, 1625446695, 1198818609, 1287645091, 5813060834, 1198132028, 638148241, 1199159635, 5813057854, 5813109987, 1263327185, 1167438189, 977222655, 732600113, 1343407759, 792040520, 1167438288, 5813064410, 1690897627, 1386780502, 857793013, 486410031, 1232262131, 1135458373, 612634432, 821344462, 1230531237, 702760942, 1500373828, 1229507863, 1720950695, 5812981242, 1099981052, 1282348408, 1748929680, 5812989707, 1261565726, 1468230494, 1251978693, 5813075410, 797424771, 1345778226, 1747228863, 5813044470, 1192723421, 1043066007, 1074493547, 1722310842, 1038938989, 917527702, 1407260897, 1446762036, 974839706, 1167438034, 2342029025, 5813078261, 1006146837, 1196816048, 826062651, 1353031856, 5813053863, 1290227332, 1190591244, 1138855577, 1044701474, 5813053966, 1535791554, 950928506, 5812991476, 1230531125, 5812983094, 1902066682, 1418186940, 1439203192, 1719549300, 1624756312, 5813038196, 5812988854, 1531988112, 1314747047, 1314069729, 1564374638, 1007576087, 1593784995, 985036637, 1347147045, 5813054032, 1232266414, 2122047447, 1502342255, 671574812, 2063346008, 1189601546, 1937879935, 5813010405, 1259856448, 5813015781, 1351623779, 1222104921, 1319591678, 854093627, 1967844926, 1291573712, 543369332, 676504624, 577123102, 5813041581, 1049839301, 1379187792, 1718202035, 1657263405, 770249286, 1261902687, 544383511, 1134107162, 1080541803, 1288530238, 1442314421, 5813057077, 5812988577, 1597157083, 1848143184, 1222769755, 5813038770, 1686190133, 1533723752, 1811997861, 5812991001, 1595745569, 1319583082, 737093754, 1528926565, 1350937208, 1808936407, 5812988573, 919513165, 1808949598, 5812990956, 1110562345, 1935126292, 821345327, 1875469390, 1438550573, 7112579856, 1344810847, 1352664363, 738155917, 1232607542, 1222778569, 418607079, 1872046345, 1374438280, 1499248377, 1198123389, 1288897930, 2089648712, 2058954777, 2088285029, 1502001218, 2181730644, 1933426240, 1996872082, 1501665145, 1351644908, 945058110, 485037749, 1346788757, 760306167, 1079859469, 1749944256, 1810645950, 1747884974, 1562689878, 1561977675, 5813060340, 1232607453, 2246175600, 1500953002, 885810757, 1566169568, 1498582584, 733649312, 1628230708, 915105429, 1532358825, 1933429987, 5901207927, 1654110835, 1017781118, 1414776601, 986059699, 1874749571, 5812994094, 5813038911, 1875435759, 1438304554, 1604440343, 770585045, 1499226615, 1285750483, 5813056280, 1283031294, 1468877324, 1380979698, 1285849782, 2247525717, 2341317296, 1969222604, 5813016981, 1872358035, 1938830923, 2032301858, 1873738899, 2000265159, 2092343673, 2060285444, 1874782886, 1968877434, 1564097484, 1874063177, 2092684587, 2030605509, 1016758041, 543702551, 1503413234, 1501640127, 5812993665, 889523223, 1382023849, 2249261885, 5813054748, 2309272340, 1935821486, 1470950640, 1936507376, 2278906805, 2089977802, 857456902, 1469269528, 1110906913, 1294362035, 1563782253, 1872396010, 1872046798, 5813054785, 1994139218, 1263327135, 5812988063, 1289213295, 1414405144, 791527493, 1627561374, 5812990492, 2184437237, 1936128170, 1319246910, 1232607205, 1874395413, 1378168833, 1252116913, 987104744, 1017802884, 852738675, 5812988825, 5813022024, 5813077658, 1199496144, 1198818551, 5813067929, 1625800608, 5812989167, 1466511550, 1294021030, 5812988514, 1079527389, 1468350445, 1437527210, 1343732093, 1501664753, 1781324410, 1079867909, 5813048932, 1563393904, 1017797863, 5813017541, 1439577670, 1532342546, 1469214664, 5812992345, 1747518018, 1813403953, 1294362042, 544379269, 1560661080, 1745847773, 1404783051, 1714466923, 1529630300, 1405111246, 5812992219, 1901008788, 1280971174, 1589972966, 1250282268, 1501660164, 2462110671, 1745510607, 5813077655, 1621008677, 5812996956, 1530704811, 1808267138, 1251654856, 1622740353, 5812991952, 1466848532, 1622360309, 1590309572, 1653770546, 1684443103, 1435136061, 1559948889, 5812994314, 5813044569, 5813013339, 5812993994, 1498246331, 5812988077, 1110903013, 1376827225, 5812989161, 892609630, 1469589825, 1625804774, 1161688286, 1128274593, 5812979017, 1136744598, 1315770230, 1561351296, 1810659099, 1110894595, 1167092919, 1110557531, 1251995567, 5812988532, 1499830503, 1159206228, 1158877783, 1534798033, 517086196, 1158191562, 797442049, 1745830360, 1745852140, 1808241116, 1776865370, 1530606252, 1313702895, 5813014491, 986758977, 1471600919, 1408880450, 986767293, 1191315642, 914130079, 448342846, 854106922, 2371001151, 2059295981, 2184096375, 5813068748, 1017793356, 2308935125, 955029299, 1849166071, 1817453065, 1782982915, 5813133355, 1813382259, 1935088341, 1687184361, 1685781176, 1500029052, 1817785661, 5813039410, 1844421716, 1291569166, 1567482299, 5901215488, 1563364112, 1748187330, 5813075792, 1779567374, 1749258463, 5813045792, 1565496703, 1780953910, 1529933124, 5813062096, 1379183233, 1534721340, 1500603847, 1594730879, 1110903093, 1995861983, 1405788552, 1189566974, 1467859487, 1343744386, 1343045604, 1199496243, 1169492931, 5813016381, 574736017, 1906111185, 1906789614, 1783000305, 1719591388, 1138807924, 1566519520, 1686229077, 1262602271, 5813034544, 5812989421, 669325882, 1561309135, 1345455479, 1376134899, 1531323131, 1261220527, 1593730160, 1346645554, 1406155403, 1718896883, 666847851, 1440252127, 1906499952, 2153407415, 2026866677, 5813068239, 2369619281, 1110535962, 1110566383, 1842051749, 2122713426, 2121685030, 1912600163, 1653070984, 1412989088, 1532401727, 1344733447, 5813038679, 1561304414, 1561301125, 1158532993, 1110186452, 1751666374, 2340298769, 1469240274, 5813060163, 1528253194, 1747215795, 1714791446, 5813016380, 1528244653, 1533338992, 1904755969, 1875090567, 1875409918, 1438300285, 2155393090, 1817444670, 1016749259, 884450920, 388280381, 1597494148, 5812990925, 1466844031, 1280634257, 1404083795, 5812990472, 1500288728, 1655474822, 1562707421, 1375798493, 892964102, 1876761314, 5813002401, 5812999429, 1934768198, 1563126068, 1905092617, 2028559316, 1818473569, 1746884134, 1564157830, 1290961410, 1284338822, 1220948264, 1172627154, 1499277688, 5901215834, 2026896672, 2213452322, 1159715613, 1532699530, 2028261424, 2090681039, 5813007604, 5813031567, 1849503142, 2121707030, 1848156241, 2148964632, 1906159372, 1995516734, 2119665568, 1374442368, 1405106221, 1533040625, 1319919610, 5812997245, 1719237849, 5812994939, 861574640, 1282806123, 1221280490, 1188889837, 1221285175, 1135441187, 5812990060, 543692985, 1565833050, 1439590350, 1935813192, 2151334747, 1814410124, 1813732543, 1280980178, 5813061218, 1444351896, 1193448112, 5812992408, 1319923967, 1474087416, 1778920327, 1809259484, 1500024261, 1686156878, 1468196413, 1848496662, 2371337394, 1374784418, 1408207343, 1435140170, 1561646261, 5812990478, 1219592090, 1564123481, 1965492600, 2213789483, 5813000452, 1937193993, 2119324105, 1842005270, 2149987166, 1818122205, 1813391435, 1749270652, 1817448921, 1812363713, 1817449236, 1655496596, 1345442381, 5812987880, 1252337419, 1561688563, 1434798670, 862265699, 1621012598, 1620667669, 1379530114, 1316086414, 1658855991, 1597456370, 1100900138, 1753385655, 1847806275, 1281649467, 1281985562, 1250959964, 1189567690, 1652725444, 574058475, 1685828529, 1507445759, 5813054575, 5813002984, 1257245650, 1559961497, 1592382424, 1809260021, 1594126040, 1903413800, 5813038918, 1438304646, 1319579391, 2026880372, 1139153136, 696863848, 1818136404, 1809273516, 1313038188, 5813033955, 1777210876, 1747569967, 1685147024, 1933433614, 1251292628, 1528577476, 1405111071, 822393878, 516055524, 883121695, 1745165001, 1779239531, 852738302, 1467987587, 5813078658, 1440652320, 1940545072, 1159262177, 1815385988, 1655497024, 1789933168, 1356772884, 1280958033, 1249940263, 1188885499, 1252337098, 1342687063, 1343745534, 1312369181, 1595853024, 1658885859, 1325405571, 1940557189, 1969537024, 5812995535, 1412014916, 1934737876, 5813025002, 5812998725, 2059282786, 1748925835, 1904420313, 5812994062, 5812990157, 1379644459, 1534038921, 1133109676, 544046671, 1441283637, 5813031775, 1437302815, 2337569638, 2121690154, 701923413, 5813040744, 1285167873, 1130152528, 792369310, 945238486, 1128572709, 1627030775, 2398292746, 1498582292, 1810986443, 5812989300, 5813078174, 1875124235, 1172623224, 1684438377, 2120303900, 2026854120, 1873086684, 1807226822, 2181035795, 1963450199, 5813048268, 892600621, 918529614, 1128576728, 757880474, 5812980456, 860910626, 1689201166, 1285849916, 1657258136, 2094708038, 1566799785, 1751982133, 5812996568, 1938175243, 1970565478, 5813022538, 1260197431, 1503331732, 731736853, 1563122080, 893642012, 541697718, 2031308992, 1502364155, 1072063538, 1660241426, 1406583670, 5813001173, 2094381099, 1255138222, 5813023434, 1659904546, 821703262, 955365826, 1537466874, 955715991, 956043578, 1411250251, 1629168807, 2063013720, 974839708, 883514695, 1659866988, 1567107667, 1691937933, 1659235557, 956060773, 1876105544, 1018462968, 1876449448, 1347125913, 1503042472, 1468342128, 955383233, 1691933852, 1536434011, 852392901, 481035392, 824470535, 730398229, 419907780, 511685969, 1562703917, 1159944202, 1407866051, 1595431209, 1190737748, 2064683443, 5813054096, 1441590157, 1376791612, 1378182447, 1500369887, 1283030884, 1284386082, 1048125065, 1690902029, 1261220600, 2095374163, 1221768103, 1659184557, 1378604678, 1533040839, 1623422292, 1167434000, 1110885663, 1139498661, 1080212848, 1049502699, 1657516638, 1312368829, 1260192984, 5813021943, 1069632261, 1378587904, 1968548221, 1017094185, 1659522043, 1533063011, 1907824988, 1049510640, 1445445434, 1505753240, 1938489987, 1690220122, 1690283476, 1690910458, 1048120973, 1658502349, 1750605638, 5813041801, 5813126319, 1535718264, 1378860414, 2248587492, 1317457971, 1037328706, 1436188322, 5812986560, 1405145183, 5812991470, 1596811105, 1752980788, 5813046513, 2064040742, 1782309935, 1437276654, 5813002534, 1968531068, 1817449059, 1111580845, 1342704830, 1344086667, 913835893, 5813022826, 1877446436, 1595473051, 5812998950, 2030622534, 884464419, 5812998963, 2094043383, 2125414881, 789636635, 1904117126, 1467797424, 2156808568, 5813047655, 5813064415, 544038123, 1716487667, 5812989312, 915148745, 2214803693, 1966455276, 5813046323, 1289233847, 1717157246, 1439927802, 5813058236, 1409882329, 1877152860, 1439574161, 1561655196, 5901200775, 1069607310, 1657949330, 5901217539, 1374554946, 1533355907, 1346460600, 5812990726, 1939543295, 1449225711, 5901196898, 2061303987, 1843714465, 1999587615, 1629206279, 793815358, 1375482740, 2029587298, 1687874335, 1289574643, 1750273378, 1936482367, 1750595497, 5813069528, 1751986317, 5813002657, 852738570, 5813025540, 1376140131, 1561325878, 5813069702, 1251996302, 1376809072, 1438563366, 1320263998, 1377512967, 758296423, 1595409504, 1690228471, 697882667, 852724544, 1937501015, 1504092028, 1504700834, 1009919653, 1316431876, 1782987343, 1719250390, 976187276, 1468872910, 1319928209, 1628869271, 1407853195, 1688194895, 1531063618, 1437863703, 1468238571, 2215813235, 2372342652, 5813047685, 5901225239, 5813033675, 2032664066, 1779611494, 1718551623, 1905114003, 1936482106, 1563467433, 2059926799, 1935113207, 2341653659, 1873065775, 2186146614, 852051464, 2372718728, 1967866061, 1379541865, 1284054234, 1718227906, 1996522484, 1252121060, 1965825035, 1566511014, 1375924140, 1968215498, 573414975, 1967508592, 1723325346, 1005857954, 1716842091, 544038294, 1560311044, 1687844304, 1533015284, 1192434435, 1595062898, 5813002071, 1750269273, 1289229674, 1749919261, 1286083010, 1593388964, 2059275182, 1283371992, 1623391753, 1439903052, 1313392097, 1560328753, 1313733623, 1313388284, 1344055093, 1592728245, 1562712175, 1651710340, 2058932928, 1688535040, 1561347849, 1714462594, 5813054101, 1435817223, 1374097180, 1285076268, 1529635236, 1716522421, 1778220673, 1350277508, 1843023572, 5813001134, 2276540626, 1906104050, 5813002519, 1501074253, 1715158302, 1684127778, 1282844980, 1252151253, 1319587003, 5813015345, 1377002848, 915157442, 1591704108, 2339650329, 2183427685, 1847452619, 1684472544, 1997196747, 2246874503, 2058955063, 2152729460, 1470996844, 1813728233, 1222701117, 1750937412, 1905093495, 2091669751, 1996190954, 1719237770, 1437868812, 2186837387, 2033010036, 1904433415, 884463495, 1782321284, 1748550345, 1685149833, 5901200176, 5901197700, 1903397125, 2092019182, 5813031566, 1965142604, 2027880999, 1288893672, 1905114943, 1714816347, 1717562249, 5812993996, 1905093552, 2121340624, 2152371061, 1839975232, 1343749689, 1652747834, 1622394511, 735004751, 1686147462, 1562352871, 1559979355, 1436961485, 1227135350, 1384017738, 1563441250, 947923543, 1128200628, 1563436471, 1344811248, 1158903092, 1562054982, 1497875250, 1344469603, 1322626125, 1313849969, 1158873783, 1654818612, 1570896561, 1321305370, 1407947423, 1319927827, 1315758373, 1448794542, 1189606310, 1190409318, 1437186918, 1285068138, 5813045027, 5813038167, 1599872317, 1539496112, 1446062404, 5813063087, 1623081361, 1745147720, 1471337627, 1222302866, 1346115608, 1468993852, 1477434062, 1375462484, 943809606, 1505412068, 1714795031, 1714821040, 1683756677, 1715499249, 2088950218, 1683440362, 5813045024, 1624418395, 1344469589, 5812989784, 1499683287, 1189606166, 1529599641, 1993789617, 1776886049, 1841019896, 1652405664, 1652030642, 1500949679, 5813068801, 5813022753, 2187130567, 1450875637, 1750251452, 1779598492, 447228814, 1504428248, 5813049966, 1966174797, 1500369943, 1932747064, 1344469477, 2122704413, 1535808539, 1476782322, 2338956347, 2184463562, 944836835, 2244823763, 1350613510, 1873725935, 1749236368, 1074484603, 823395525, 2308585856, 2120342655, 1905429029, 1502701269, 1406928592, 1504096339, 5813002456, 1289238841, 1810978852, 1967537971, 1438304464, 1537456949, 1414712300, 1653395872, 1997498177, 1442699865, 1841663352, 5813107445, 1476778177, 1528914548, 1810944084, 5813018754, 1870993614, 1414073219, 1808927915, 5813022794, 1624083046, 5812989160, 1099333424, 1375504361, 1510855070, 2001633881, 2247535548, 1289229700, 5812989983, 5813031888, 5812985952, 1449486007, 1465824781, 1037237333, 1506120610, 5813034441, 1500063929, 1283039493, 1314075070, 7112613460, 1161399526, 977218524, 5813021911, 575073147, 790741191, 1344090837, 1130714433, 1288202406, 1538476539, 976190756, 1970219420, 1877792679, 1037895459, 1350273443, 2217488515, 1876112808, 1783682503, 2031266973, 2244482994, 5813054169, 2211737961, 881596353, 1285155206, 5812983356, 1006560977, 977913894, 1812005485, 1718883440, 1751601967, 2061316365, 1872720467, 2372697700, 1965483574, 1282007450, 1316194019, 674423996, 757530901, 666843764, 1969230358, 2000903820, 1723658004, 1538471582, 884122973, 1385015126, 1511593574, 1870655688, 1935118166, 1443026992, 1904083110, 1345860891, 1038926500, 1382002299, 1189605993, 5812995785, 2091997530, 2278224718, 1597835331, 1319919814, 858458268, 1256494044, 759960572, 853726809, 644757911, 945161760, 1225455907, 665169278, 5812983383, 1813727537, 821003563, 884446447, 1688855750, 1719569268, 5813075754, 200326126, 541723677, 479925776, 5813115583, 665820084, 672598344, 541723810, 758938220, 5813040731, 5813078595, 357224041, 821007911, 885132185, 357515217, 5813078062, 449250041, 944802835, 516857964, 727889637, 1314729915, 853097199, 1344431292, 603068370, 1076742501, 696859758, 452971138, 1563755856, 5813034789, 1408535544, 1005110376, 915503330, 1847115656, 358847551, 5813062635, 512308235, 574740549, 544037996, 515092013]

bods = [1873086710, 1628523730, 1435835226, 1809592670, 730709173, 1343403608, 2124762952, 1005857944]


allResults2 = pd.DataFrame()
for LCType in LCs:
    for bodyId in bods:
        query = (
                                        ' MATCH (LC:hemibrain_Neuron)-[c:ConnectsTo]->(output:hemibrain_Neuron)'
                                        ' WHERE output.bodyId = '+str(bodyId)+' AND LC.type = "'+str(LCType)+'"'
                                                                                                             ' RETURN COUNT(LC.type), LC.type, SUM(c.weight), output.bodyId, output.type, output.instance'
        ).format(dataset='hemibrain:v1.0')
        queryResults = client.fetch_custom(query)
        allResults2 = allResults2.append(queryResults)

'''
