"""
Various scripts for the files in this package
"""

'''
# making the DN files 

import DnAutosegClassSet as DNCS
import checkV14
DNSet = DNCS.builder()
checkV14.checkV14SKID(DNSet)
DNCS.makeCSV(DNSet)


# making the AN files

import checkV14
import AscendingNeuronClassSet as ANCS
ANSet = ANCS.builder()
checkV14.checkV14SKID(ANSet)
ANCS.makeCSV(ANSet)

# making plots

import makePlots as MP
DN_DF = MP.openDN_CSV()
MP.makeSunburstCharts(DN_DF)
MP.onlyFindSoma(DN_DF)
MP.identifiedDNs(DN_DF)
'''