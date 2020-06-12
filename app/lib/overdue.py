import os
import sys
import pyodbc 
import pandas as pd


def request():

    connection = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                        "Server=akl-longage3\LONGAGE3;"
                        "Database=LTMAL3;"
                        "UID=RAKON\nikolai;"
                        "Trusted_Connection=yes;")

    command = "select * from locData join brdData on locData.fk_brdID = brdData.pk_brdID join runData on runData.pk_runID = locData.fk_runID where runData.currentRun = 'True' and runData.finishDate < CURRENT_TIMESTAMP"

    df = pd.read_sql(command, connection)

    df = df.drop(columns=[
        'pk_locID', 
        'fk_runID', 
        'fk_brdID', 
        'fk_ovenID', 
        'pk_brdID', 
        'status', 
        'vchar',
        'pk_runID',
        'ppmStartDate',
        'operator',
        'limUpper',
        'limLower',
        'email',
        'emailSent',
        'emailNoteTime',
        'opemail',
        'sendemail',
        'sendopemail',
        'prodMonitoring',
        'standardProduction',
        'limUpper1',
        'limLower1',
        'hotStore',
        'processExperiment',
        'designExperiment',
        'returnUnits',
        'freqDivider',
        'rma',
        'currentRun',
        'sealingMethod',
        'glue',
        'startDate'
        ]) 

    # df['startDate'] = df['startDate'].dt.date
    df['finishDate'] = df['finishDate'].dt.date

    df = df.set_index('runNumber')

    df['nomFrq'] = df['nomFrq']/1000000
    df['nomFrq'] = round(df['nomFrq'],2)

    df.sort_values(['runNumber', 'brd', 'loc'], ascending=[True, True, True], inplace=True)

    df['locs'] = df['loc'].astype(str)

    df1 = df.groupby(['runNumber'])['locs'].apply(','.join).reset_index()
    df1 = df1.set_index('runNumber')
    df = df.drop(columns=['loc', 'locs'])
    df1['nbr'] = df.groupby(['runNumber'])['brd'].count()
    result = pd.concat([df1, df], axis=1, join='inner')
    result = result.drop_duplicates() 
    # result.sort_values(['brd', 'runNumber'], ascending=[True, True], inplace=True)
    result.sort_values(['owner', 'brd'], ascending=[True, True], inplace=True)
    # result = result.set_index('brd')


    return result
