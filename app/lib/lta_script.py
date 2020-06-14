import os
import sys
import glob
import pyodbc
import pandas as pd
from datetime import datetime
from sympy import diff
import scipy.signal as signal
from math import fabs


import scipy.ndimage as ndimage
import numpy as np
import time



df = pd.DataFrame()
df_plot = pd.DataFrame()

unit_name = 'test1'
diff_threshold = 0.1

base_directory = os.getcwd() + r"/app"

plotted = False



def search(search_text = "Siward"):
    if search_text == 'Brian' or search_text == 'Bryan' or search_text == 'brian' or search_text == 'bryan':
        search_text = "Ryan"
    connection = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                        "Server=akl-longage3\LONGAGE3;"
                        "Database=LTMAL3;"
                        "UID=RAKON\nikolai;"
                        "Trusted_Connection=yes;")

    command = "select * from runData where runData.purpose like '%" + str(search_text) \
              + "%' or runData.comment like '%" + str(search_text) \
              + "%' or runData.owner like '%" + str(search_text) \
              + "%' or runData.packetNumber like '%" + str(search_text) \
              + "%' or runData.crystalNumber like '%" + str(search_text) + "%'"

    df = pd.read_sql(command, connection)



    # Examples

    # df['startDate'] = df['startDate'].dt.date
    # df['finishDate'] = df['finishDate'].dt.date
    # # df.replace(to_replace='oven320', value='')
    # df = df.set_index('runNumber')
    # df['nomFrq'] = round(df['nomFrq'],2)
    # df.sort_values(['runNumber', 'brd', 'loc'], ascending=[True, True, True], inplace=True)
    # # df['amount'] = df.groupby(['runNumber'])['brd'].count()
    # # df['locs'] = df.groupby(['runNumber'])['brd'].prod()
    # df['locs'] = df['loc'].astype(str)
    # df1 = df.groupby(['runNumber'])['locs'].apply(','.join).reset_index()
    # df1 = df1.set_index('runNumber')
    # df = df.drop(columns=['loc', 'locs'])
    # result = pd.concat([df1, df], axis=1, join='inner')
    # result = result.drop_duplicates()
    # # gaussian filter
    # df_filtered = ndimage.gaussian_filter(df_freq, sigma=25, order=0)

    i = 0
    purposes = {}
    for item in df['purpose']:
        purposes[i] = item
        i = i + 1

    return df, purposes



def select(index_external, df_external):

    connection = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                        "Server=akl-longage3\LONGAGE3;"
                        "Database=LTMAL3;"
                        "UID=RAKON\nikolai;"
                        "Trusted_Connection=yes;")


    run_id = str(df_external['pk_runID'].iloc[index_external])

    command = "select measDate, compFreq, loc, brd, fk_locID from measData " \
              "join locData on measData.fk_locID = locData.pk_locID " \
              "join brdData on brdData.pk_brdID = locData.fk_brdID " \
              "where measData.fk_locID in (select pk_locID from locData where locData.fk_runID = '" + str(run_id) + "') " \
                "and measData.frq <> '9999' and compFreq <> '9999'"


    plot_result = pd.read_sql(command, connection)

    return plot_result


def plot(plot_result):

    plot_result.sort_values(['measDate'], ascending=[True], inplace=True)
    initial_time = plot_result['measDate'].iloc[0]
    plot_result['Days'] = (plot_result['measDate'] - initial_time).dt.total_seconds() / 86400

    plot_result.sort_values(['brd', 'loc'], ascending=[True, True], inplace=True)
    plot_result['DIFF'] = diff(plot_result['compFreq'])

    locations = plot_result['fk_locID'].unique().tolist()

    # ****************************************************************

    #df_result = pd.DataFrame()

    # threshold = 50
    # diff_threshold = .5
    # delta = 0
    # counter = 0
    # delta_local_previous = 0

    # for location in locations:
    #
    #
    #     df_single = filter(plot_result, location, threshold, diff_threshold)
    #
    #
    #     df_result = pd.concat([df_result, df_single], ignore_index=True, sort=False)

    # ****************************************************************

    # finish_time = datetime.now()
    # file_time = str(finish_time)
    # file_time = file_time.replace(" ", "_")
    # file_time = file_time.replace(":", "-")
    # file_time = file_time.split(".")
    #
    #
    # # # filename = filename.replace('.csv', '') + '_filtered.csv'
    # # path = r"C:\\Temp\downloads"
    # path = base_directory + r'/temp_files/'
    # filename = path +  'lta_result_' + str(file_time[0]) + '.csv'
    # # filename = path + r'result.csv'
    # df_result.to_csv(filename, encoding = 'utf-8')


    return plot_result, locations




def filter(plot_result, location, threshold, diff_threshold):
    delta = 0
    counter = 0

    df_single = plot_result[plot_result['fk_locID'] == location]

    loc = df_single['loc'].iloc[0]
    print(loc)

    df_single.sort_values(['Days'], ascending=[True], inplace=True)

    # print(df_single)

    freq_initial = df_single['compFreq'].iloc[0]

    freq_ppb = 1000000000 * (df_single['compFreq'] - freq_initial) / freq_initial

    df_single['freq_ppb'] = freq_ppb

    df_single = df_single.reset_index()

    count_row = df_single.shape[0]

    # print(count_row)

    for index, row in df_single.iterrows():
        if index < count_row - 9:

            previous = df_single['freq_ppb'].iloc[index:(index + 5)].mean()
            current = df_single['freq_ppb'].iloc[(index + 5)]
            next = df_single['freq_ppb'].iloc[(index + 5):(index + 10)].mean()

            delta_local = next - previous
            df_single.at[index + 5, 'DELTA_LOC'] = delta_local

            if delta_local > threshold or delta_local < -threshold:

                delta_local_loc_max = delta_local

                for i in range(10):
                    previous_loc = df_single['freq_ppb'].iloc[(index + i):(index + 5 + i)].mean()
                    next_loc = df_single['freq_ppb'].iloc[(index + 5 + i):(index + 10 + i)].mean()
                    delta_local_loc = next_loc - previous_loc
                    if fabs(delta_local_loc) > fabs(delta_local_loc_max):
                        delta_local_loc_max = delta_local_loc

                df_single.at[index + 5, 'DELTA_MAX'] = delta_local_loc_max

                if counter > 10:
                    delta = delta - delta_local_loc_max
                    counter = 0

            df_single.at[index + 5, 'freq_ppb_fltr'] = df_single['freq_ppb'].iloc[(index + 7)] + delta  # +5
            df_single.at[index + 5, 'DELTA'] = delta

            counter = counter + 1

    df_single['DIFF2'] = diff(df_single['freq_ppb_fltr'])

    for index, row in df_single.iterrows():
        if (index > 7 and index < (count_row - 7)):
            if (df_single['DIFF2'].iloc[index] > diff_threshold or df_single['DIFF2'].iloc[
                index] < -diff_threshold):
                previous = df_single['freq_ppb_fltr'].iloc[index - 6:(index - 2)].mean()
                next = df_single['freq_ppb_fltr'].iloc[(index + 2):(index + 6)].mean()

                df_single.at[index, 'freq_ppb_fltr'] = (previous + next) / 2
                df_single.at[index - 1, 'freq_ppb_fltr'] = (previous + next) / 2
                df_single.at[index + 1, 'freq_ppb_fltr'] = (previous + next) / 2

    df_single['DIFF3'] = diff(df_single['freq_ppb_fltr'])

    for index, row in df_single.iterrows():
        if (index > 7 and index < (count_row - 7)):
            if (df_single['DIFF3'].iloc[index] > diff_threshold or df_single['DIFF3'].iloc[
                index] < -diff_threshold):
                previous = df_single['freq_ppb_fltr'].iloc[index - 6:(index - 2)].mean()
                next = df_single['freq_ppb_fltr'].iloc[(index + 2):(index + 6)].mean()

                df_single.at[index, 'freq_ppb_fltr'] = (previous + next) / 2
                df_single.at[index - 1, 'freq_ppb_fltr'] = (previous + next) / 2
                df_single.at[index + 1, 'freq_ppb_fltr'] = (previous + next) / 2

    df_single.dropna(subset=['freq_ppb_fltr'], inplace=True)

    df_single.sort_values(['Days'], ascending=[True], inplace=True)

    freq_initial_2 = df_single['freq_ppb_fltr'].iloc[0]

    df_single['freq_ppb_fltr_cut'] = df_single['freq_ppb_fltr'] - freq_initial_2

    df_single = df_single.drop(df_single.columns[[0]], axis=1)

    if df_single['Days'].max() < 25:
        sigma = 2
    elif df_single['Days'].max() < 50:
        sigma = 4
    elif df_single['Days'].max() < 80:
        sigma = 7
    else:
        sigma = 20

    df_single['freq_ppb_fltr_cut_smo_temp'] = ndimage.gaussian_filter(df_single['freq_ppb_fltr_cut'], sigma=sigma, order=0)
    df_single['freq_ppb_smo_temp'] = ndimage.gaussian_filter(df_single['freq_ppb'], sigma=sigma, order=0)

    df_single['freq_ppb_fltr_cut_smo'] = df_single['freq_ppb_fltr_cut_smo_temp'] - df_single['freq_ppb_fltr_cut_smo_temp'].iloc[0]
    df_single['freq_ppb_smo'] = df_single['freq_ppb_smo_temp'] - df_single['freq_ppb_smo_temp'].iloc[0]

    return df_single
