"""
Emily Tenshaw
CAT-Card
12/2/2020

Creates various plots to easily view the DN data & features.
The csv this file uses has the putative_ascending neurons removed and the "duplicate - auto" neurons removed.
This removes double counted neurons.
#12/02/2020 @ 2:25PM
filename = 'C:/Users/etens/Desktop/pyCharmOutputs/DescendingNeuron_Complete_Status.csv'
"""

import chart_studio
import chart_studio.plotly as py
import plotly.express as px
import pandas as pd
chart_studio.tools.set_credentials_file(username='etenshaw', api_key='1ZfRttbxiCZ95A7eBz0f')


def openDN_CSV(filename='C:/Users/etens/Desktop/pyCharmOutputs/DescendingNeuron_Complete_Status.csv'):
    DN_DF = pd.read_csv(filename)
    return DN_DF


# sunburst charts of DN data
def makeSunburstCharts(DN_DF):
    # DN_DF = DN_DF[DN_DF['DT Hemisphere'] != "check DT"]
    DN_DF_FindSoma_Filter = DN_DF[DN_DF['Soma Hemisphere'] != "FindSoma"]
    DN_DF_RightDT = DN_DF_FindSoma_Filter[DN_DF_FindSoma_Filter['DT Hemisphere'] == "Right"]

    fig = px.sunburst(DN_DF_FindSoma_Filter, path=['DT Hemisphere', 'Soma Hemisphere', 'DN Type'],
                      title="Both DT - Soma Hem - DN Type")
    py.plot(fig, filename="Both DT - Soma Hem - DN Type")

    DN_DF_RightDT.Classification = DN_DF_RightDT['Classification'].fillna('No Classification')
    fig = px.sunburst(DN_DF_RightDT, path=['Soma Hemisphere', 'DN Type', 'Classification'],
                      title="Right DT - Soma Hem - DN Type - Classification")
    py.plot(fig, filename="Right DT - Soma Hem - DN Type - Classification")

    return


# sunburst chart of DNs that don't have a soma - checks soma status & counts
def onlyFindSoma(DN_DF):
    FindSoma_DF = DN_DF[DN_DF['Soma Hemisphere'] == "FindSoma"]
    fig = px.sunburst(FindSoma_DF, path=['DT Hemisphere', 'Status'],
                      title="Find Soma: DN Tract - Status")
    py.plot(fig, filename="Find Soma: DN Tract - Status")
    return


# sunburst chart of only identified DNs - easy to see which are found
def identifiedDNs(DN_DF):
    typed = DN_DF[DN_DF['ID'] == 'Typed DN']
    identified = DN_DF[DN_DF['ID'] == 'Identified DN']

    ID_DN = typed.append(identified, ignore_index=True)

    fig = px.sunburst(ID_DN, path=['ID', 'DN Type', 'Classification'], title="Identified - Type - Classification")
    py.plot(fig, filename="Identified - Type - Classification")

    return


# separation of DN types - DNa, DNb, etc.
def separateDNType(DN_DF):
    DNa = DN_DF[DN_DF['DN Type'] == 'DNa']
    DNb = DN_DF[DN_DF['DN Type'] == 'DNb']
    DNc = DN_DF[DN_DF['DN Type'] == 'DNc']
    DNd = DN_DF[DN_DF['DN Type'] == 'DNd']
    DNg = DN_DF[DN_DF['DN Type'] == 'DNg']
    DNp = DN_DF[DN_DF['DN Type'] == 'DNp']

    return DNa, DNb, DNc, DNd, DNg, DNp
