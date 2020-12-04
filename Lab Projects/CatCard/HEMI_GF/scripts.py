"""
#scripts

import branchBoundingBox as BB
import GFInputNeuronClass as GFN
import GFInputFunctions as GFF
import GFInputSetClass as GFS
GFInputNeurons = GFF.readCSV()

#pulls relevant body IDs and GF input type
bodyDict, classDict, somaHemisphere = GFF.getInputBodiesAndType(GFInputNeurons)

#puts body IDs into query
queryResults = GFF.gfInputQuery(bodyDict)

#add GF types to data
queryResults = GFF.addInputType(bodyDict, queryResults, somaHemisphere)


queryArray = GFF.queryDataFrameToArray(queryResults)
inputList = GFF.queryArrayToNeuronList(queryArray)
inputSet = GFS.builder(inputList)

for body in inputSet:
    body.getSynapsesByBranch()
inputSet.getSynapsesByBranch()



"""

'''
ex: how to find specific dataframe entry
queryResults.loc[queryResults['input.bodyId'] == 2063767972]
'''

''' 
GF LC4 connectivity 
To Run:
LC4 -> GF synapes example:
import GF_LC4_Syns as GLC

queryResults = GLC.getTypeCoords("LC4", 2307027729)
GLC.getPostsynPartners(queryResults, "LC4Syns.csv")
queryResults2 = GLC.getTypeCoords2("LC4", 2307027729)
GLC.getPostsynPartners2(queryResults2, "LC4Syns2.csv")
'''