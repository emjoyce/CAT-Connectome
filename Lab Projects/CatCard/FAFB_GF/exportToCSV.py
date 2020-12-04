'''
Emily Tenshaw & Jason Polsky
CAT-Card
Updated 11/30/2020

This file allows user to export GF input set data to a CSV.
It has examples of a few CSV formats. You can create different functions for the data you want to export.
'''

import datetime
import os
import csv

now = datetime.datetime.now()


# mySet should be the name of the set that you want to use, and formatType should be which info you want in your CSV
def makeCSV(mySet, formatType='saveGeneral'):
    formatTypeDict = {'saveGeneral': saveGeneral, 'saveClassSummary': saveClassSummary,
                      'saveWithAll': saveWithAll, 'saveWithAllAndAnnotations': saveWithAllAndAnnotations,
                      'saveWithNeuropils': saveWithNeuropils, 'saveWithDistributions': saveWithDistributions,
                      'saveWithModality': saveWithModality}
    copyNumber = 0
    if type(mySet) is list:
        nameVar = formatType
        nameVar += 'AllGF1inputNeurons'
        myFileName = str(nameVar)
    elif mySet.groupName is None:
        nameVar = formatType
        nameVar += 'AllGF1inputNeurons'
        myFileName = str(nameVar)
    elif mySet.groupName is 'None':
        nameVar = formatType
        nameVar += 'AllGF1inputNeurons'
        myFileName = str(nameVar)

    else:
        nameVar = ''
        myFileName = formatType
        myFileName += str(mySet.groupName)
    saveCount = 0
    pathVar = "C:/Users/etens/Desktop/pyCharmOutputs/CSV"
    myPath = "{}/{}/".format(pathVar, str(nameVar))
    myPath = os.path.normpath(myPath)

    if not os.path.isdir(myPath):
        os.makedirs(myPath)

    fileName = str(now.year) + str(now.month) + str(now.day)
    fileName += myFileName
    finalFileName = os.path.join(myPath, fileName)

    myFile = str(finalFileName)
    myFileCheck = myFile + ".csv"
    myBaseFile = myFile
    while os.path.isfile(myFileCheck) == True:
        copyNumber += 1
        myFileCheck = myFile + "_" + str(copyNumber)
        myBaseFile = myFileCheck
        myFileCheck += '.csv'
    myFile = myFileCheck
    args = [myFile, mySet]

    formatTypeDict[formatType](args)

    return

# a basic save function to transfer data to a CSV - doesn't include all info
def saveGeneral(args):
    myFile = args[0]
    mySet = args[1]
    with open(myFile, 'w', newline='') as outfile:
        myWriter = csv.writer(outfile)
        myWriter.writerow(['Neuron Name', 'skeletonID', 'GF1 Synapse Count', 'annotations'])
        for item in mySet:
            myWriter.writerow(
                [item.neuronName, item.skeletonID, item.GF1synapseCount, item.annotations])
    return


# used for exporting csv summary of GF input neurons broken down by class
def saveClassSummary(args):
    myFile = args[0]
    mySuperSet = args[1]
    with open(myFile, 'w', newline='') as outfile:
        myWriter = csv.writer(outfile)
        myWriter.writerow(
            ['Classification', 'Number of Neurons', 'Number of GF1 Synapses',
             'Minimum Synapses', 'Maximum Synapses', 'Median Synapses'])
        for i in mySuperSet:
            myWriter.writerow(
                [i.groupName, i.numNeurons, i.AllGF1Synapses, i.minSyn, i.maxSyn, i.medianSyn])
    return


# use this for exporting csv to be used in google sheet analysis of all GF input neurons
def saveWithAll(args):
    myFile = args[0]
    mySet = args[1]
    if 'JO_partners' not in mySet.varCheck:
        mySet.getJOPartnerNumbers()
    if 'synByBranch' not in mySet.varCheck:
        mySet.getAllGFINSynByBranch()
    if 'partners' not in mySet.varCheck:
        mySet.getNumPartnersBySkid()

    with open(myFile, 'w', newline='') as outfile:
        myWriter = csv.writer(outfile)
        myWriter.writerow(
            ['Neuron Name', 'skeletonID', 'GF1 Synapse Count', 'GF2 Synapse Count',
             'classification', 'hemisphere', 'cellBodyRind', 'somaHemisphere', 'commissure', 'numLC4Syn', 'numLPLC2Syn',
             'numLC6Syn', 'numLPLC1Syn', 'numLPC1Syn', 'numLC28Syn', 'numLLPC1Syn', 'numLPLC3Syn', 'lateral branch',
             'medial branch', 'anterior branch', 'soma tract', 'descending tract', 'classType', 'numJONSyn'])
        for item in mySet:
            myWriter.writerow(
                [item.neuronName, item.skeletonID, item.GF1synapseCount, item.GF2synapseCount,
                 item.classification, item.hemisphere, item.cellBodyRind, item.somaSide, item.commissure,
                 item.postsynapticToLC4, item.postsynapticToLPLC2, item.postsynapticToLC6, item.postsynapticToLPLC1,
                 item.postsynapticToLPC1, item.postsynapticToLC28, item.postsynapticToLLPC1, item.postsynapticToLPLC3,
                 item.synapsesByBranch['lateral'], item.synapsesByBranch['medial'], item.synapsesByBranch['anterior'],
                 item.synapsesByBranch['soma tract'], item.synapsesByBranch['descending tract'], item.classType,
                 item.postsynapticToJON])
    return


'''
Examples of other formats
Might not have everything able to run these -- guidelines 
'''

def saveWithAllAndAnnotations(args):
    myFile = args[0]
    mySet = args[1]
    if 'synByBranch' not in mySet.varCheck:
        mySet.getAllGFINSynByBranch()
    if 'partners' not in mySet.varCheck:
        mySet.getNumPartnersBySkid()
    with open(myFile, 'w', newline='') as outfile:
        myWriter = csv.writer(outfile)
        myRows0 = ['Neuron Name', 'skeletonID', 'GF1 Synapse Count', 'GF2 Synapse Count',
                   'classification', 'hemisphere', 'cellBodyRind', 'somaHemisphere', 'commissure', 'numLC4Syn',
                   'numLPLC2Syn', 'numLC6Syn', 'numLPLC1Syn', 'numLPC1Syn', 'numLC28Syn', 'numLLPC1Syn', 'numLPLC3Syn',
                   'lateral branch', 'medial branch', 'anterior branch', 'soma tract', 'descending tract']
        myRows = myRows0 + mySet.allAnnotations
        myWriter.writerow(myRows)
        for item in mySet:
            theseAnnotations = []
            for annotation in mySet.allAnnotations:
                if annotation in item.annotations:
                    theseAnnotations.append(1)
                else:
                    theseAnnotations.append(0)
            curRow = [item.neuronName, item.skeletonID, item.GF1synapseCount, item.GF2synapseCount,
                      item.classification, item.hemisphere, item.cellBodyRind, item.somaSide,
                      item.commissure, item.postsynapticToLC4, item.postsynapticToLPLC2, item.postsynapticToLC6,
                      item.postsynapticToLPLC1, item.postsynapticToLPC1, item.postsynapticToLC28,
                      item.postsynapticToLLPC1, item.postsynapticToLPLC3, item.synapsesByBranch['lateral'],
                      item.synapsesByBranch['medial'], item.synapsesByBranch['anterior'],
                      item.synapsesByBranch['soma tract'], item.synapsesByBranch['descending tract']]
            fullRow = curRow + theseAnnotations
            myWriter.writerow(fullRow)
    return

def saveWithNeuropils(args):
    myFile = args[0]
    mySet = args[1]

    myNeuropils = ['AL_L', 'AL_R', 'AME_L', 'AME_R', 'AMMC_L', 'AMMC_R', 'AOTU_L', 'AOTU_R', 'ATL_L', 'ATL_R', 'AVLP_L',
                   'AVLP_R',
                   'BU_L', 'BU_R', 'CAN_L', 'CAN_R', 'CRE_L', 'CRE_R', 'EB', 'EPA_L', 'EPA_R', 'FB', 'FLA_L', 'FLA_R',
                   'GA_L', 'GA_R', 'GNG', 'GOR_L', 'GOR_R', 'IB_L', 'IB_R', 'ICL_L', 'ICL_R', 'IPS_L', 'IPS_R',
                   'LAL_L', 'LAL_R', 'LH_L', 'LH_R', 'LO_L', 'LO_R', 'LOP_L', 'LOP_R', 'MB_CA_L', 'MB_CA_R', 'MB_LAC_L',
                   'MB_LAC_R', 'MB_ML_L', 'MB_ML_R', 'MB_PED_L', 'MB_PED_R', 'MB_VL_L', 'MB_VL_R', 'MB_whole_L',
                   'MB_whole_R', 'ME_L', 'ME_R', 'NO', 'PB', 'PLP_L', 'PLP_R', 'PRW', 'PVLP_L', 'PVLP_R', 'SAD',
                   'SCL_L', 'SCL_R', 'SIP_L', 'SIP_R',
                   'SLP_L', 'SLP_R', 'SMP_L', 'SMP_R', 'SPS_L', 'SPS_R', 'VES_L', 'VES_R', 'WED_L', 'WED_R']

    with open(myFile, 'w', newline='') as outfile:
        myWriter = csv.writer(outfile)
        rows1 = ['Neuron Name', 'Classification']
        allRows = rows1 + myNeuropils
        myWriter.writerow(allRows)
        for item in mySet:
            myWriter.writerow([item.neuronName, item.classification, item.neuropils['AL_L'], item.neuropils['AL_R'],
                               item.neuropils['AME_L'], item.neuropils['AME_R'], item.neuropils['AMMC_L'],
                               item.neuropils['AMMC_R'],
                               item.neuropils['AOTU_L'], item.neuropils['AOTU_R'], item.neuropils['ATL_L'],
                               item.neuropils['ATL_R'],
                               item.neuropils['AVLP_L'], item.neuropils['AVLP_R'], item.neuropils['BU_L'],
                               item.neuropils['BU_R'],
                               item.neuropils['CAN_L'], item.neuropils['CAN_R'], item.neuropils['CRE_L'],
                               item.neuropils['CRE_R'],
                               item.neuropils['EB'], item.neuropils['EPA_L'], item.neuropils['EPA_R'],
                               item.neuropils['FB'],
                               item.neuropils['FLA_L'], item.neuropils['FLA_R'], item.neuropils['GA_L'],
                               item.neuropils['GA_R'],
                               item.neuropils['GNG'], item.neuropils['GOR_L'], item.neuropils['GOR_R'],
                               item.neuropils['IB_L'],
                               item.neuropils['IB_R'], item.neuropils['ICL_L'], item.neuropils['ICL_R'],
                               item.neuropils['IPS_L'],
                               item.neuropils['IPS_R'], item.neuropils['LAL_L'], item.neuropils['LAL_R'],
                               item.neuropils['LH_L'],
                               item.neuropils['LH_R'], item.neuropils['LO_L'], item.neuropils['LO_R'],
                               item.neuropils['LOP_L'],
                               item.neuropils['LOP_R'], item.neuropils['MB_CA_L'], item.neuropils['MB_CA_R'],
                               item.neuropils['MB_LAC_L'],
                               item.neuropils['MB_LAC_R'], item.neuropils['MB_ML_L'], item.neuropils['MB_ML_R'],
                               item.neuropils['MB_PED_L'],
                               item.neuropils['MB_PED_R'], item.neuropils['MB_VL_L'], item.neuropils['MB_VL_R'],
                               item.neuropils['MB_whole_L'],
                               item.neuropils['MB_whole_R'], item.neuropils['ME_L'], item.neuropils['ME_R'],
                               item.neuropils['NO'],
                               item.neuropils['PB'], item.neuropils['PLP_L'], item.neuropils['PLP_R'],
                               item.neuropils['PRW'], item.neuropils['PVLP_L'],
                               item.neuropils['PVLP_R'], item.neuropils['SAD'], item.neuropils['SCL_L'],
                               item.neuropils['SCL_R'],
                               item.neuropils['SIP_L'], item.neuropils['SIP_R'], item.neuropils['SLP_L'],
                               item.neuropils['SLP_R'],
                               item.neuropils['SMP_L'], item.neuropils['SMP_R'], item.neuropils['SPS_L'],
                               item.neuropils['SPS_R'],
                               item.neuropils['VES_L'], item.neuropils['VES_R'], item.neuropils['WED_L'],
                               item.neuropils['WED_R']])
    return


def saveWithDistributions(args):
    myFile = args[0]
    mySet = args[1]

    distributions = ['Anterior', 'Medial', 'Lateral', 'Descending', 'Soma', 'AnteriorMedial', 'AnteriorLateral',
                     'AnteriorSoma', 'AnteriorDescending', 'MedialLateral', 'MedialSoma', 'MedialDescending',
                     'LateralSoma', 'LateralDescending', 'SomaDescending',

                     'AnteriorMedialLateral', 'AnteriorMedialSoma', 'AnteriorMedialDescending',
                     'AnteriorLateralSoma', 'AnteriorLateralDescending', 'AnteriorSomaDescending',
                     'MedialLateralSoma', 'MedialLateralDescending', 'MedialSomaDescending',
                     'LateralSomaDescending',

                     'AnteriorMedialLateralSoma', 'AnteriorMedialLateralDescending', 'AnteriorMedialSomaDescending',
                     'AnteriorLateralSomaDescending', 'MedialLateralSomaDescending', 'AllBranches']

    with open(myFile, 'w', newline='') as outfile:
        myWriter = csv.writer(outfile)
        rows1 = ['Neuron Name', 'Classification', 'Distribution']
        myWriter.writerow(rows1)
        for item in mySet:
            myWriter.writerow([item.neuronName, item.classification, item.distribution])
    return

def saveWithModality(args):
    myFile = args[0]
    mySet = args[1]
    index = list(range(695))
    num = 0
    with open(myFile, 'w', newline='') as outfile:
        myWriter = csv.writer(outfile)
        myWriter.writerow(
            ['Neuron Name', 'modality', 'classification', 'lateral branch', 'medial branch',
             'anterior branch', 'descending tract', 'soma tract', 'target', 'GF1 Synapse', 'Group Number'])
        for item in mySet:
            myWriter.writerow(
                [item.neuronName, item.classification, item.modality, item.synapsesByBranch['lateral'],
                 item.synapsesByBranch['medial'], item.synapsesByBranch['anterior'],
                 item.synapsesByBranch['descending tract'],
                 item.synapsesByBranch['soma tract'], 'Giant Fiber', item.GF1synapseCount, item.groupNumber])
            num = num + 1
    return
