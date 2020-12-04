"""
#how to build a basic GF input set
import CustomNeuronClassSet as CS
import subsetCreator as SC
mySet = CS.builder()

#add more data - don't have to run all, can run others
mySet = SC.sortBySynL2H(mySet)
mySet.getConnectors()
mySet.getNumPartnersBySkid()
mySet.getAllGFINSynByBranch()
mySet.findNeuropils()
mySet.findBranchDistributions()
mySet.combineAllSynLocations()


import plotBuilder as PB
allInfo = PB.getSynInfo(mySet)


"""