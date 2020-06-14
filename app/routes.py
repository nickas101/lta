from app import app
from flask import abort, redirect, url_for, render_template, Flask, request, flash, make_response, session, send_file, send_from_directory, Response
# from os import path
import os
import pandas as pd
from datetime import datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import scipy.ndimage as ndimage
import io
import json
import time

from celery import Celery

from multiprocessing import Process, Pipe, Value, Manager

from flask_bootstrap import Bootstrap

from .lib import overdue
from .lib import lta_script
from .lib import lta_results



folder = 'C:\Temp\dorsum'
#folder = '/Users/nickas/Documents/_to_upload/dorsum'
#folder = r'\\akl-file-02\Share\Harshad\dorsum_test'
#folder = ""
card1 = ""
card2 = ""
frequency = ""
result_test3_full = pd.DataFrame()


file = r'\\Akl-file-01\Departments\Engineering - Product R&D\Test Results\SuperFast Test Results\ADVA M6575 jump screen'
simple_folder = ""
part_number = ""
result = pd.DataFrame()
result_runs = pd.DataFrame()
plot_result = pd.DataFrame()
plot_result1 = pd.DataFrame()
# links = pd.DataFrame(columns=['pk_BatchId', 'fk_TestSystemId','link'])
links = pd.DataFrame(columns=['pk_BatchId', 'link'])
selected = 0
purposes = {}
locations = {}
plot_filename = ""
filename_plt = ""
base_directory = os.getcwd() + r"\app"
print("base_directory: " + str(base_directory))
norm = True
gauss = True
diff_fltr = True
diff_threshold = 0.2
sigm = 10
entered_search = ''
current = ''
progress = '2%'



@app.route('/')
def index():
    return redirect(url_for('lta'))


@app.route('/process')
def process():
    return render_template('process.html')


@app.route('/lta', methods=['post', 'get'])
def lta():
    return render_template('lta.html')


@app.route('/lta/overdue', methods=['post', 'get'])
def lta_overdue():
    global folder

    result = overdue.request()

    result.columns = ["Locations", "Nbr", "Board", "Freq", "Finish Date", "Run days", "Comment", "Crystal", "Packet", "SAP#","Jig","Owner", "Purpose"]
    result = result[["Board", "Locations", "Nbr", "Crystal", "Freq", "Jig", "Purpose", "Packet", "Owner", "Finish Date", "Run days", "SAP#", "Comment"]]

    finish_time = datetime.now()
    file_time = str(finish_time)
    file_time = file_time.replace(" ", "_")
    file_time = file_time.replace(":", "-")
    file_time = file_time.split(".")

    result_table = result.copy()

    result = result.set_index('Board')

    filename = 'overdue_cristals_' + str(file_time[0]) + '.csv'
    folder = base_directory + r'/temp_files/'
    filename_full = folder + filename
    result.to_csv(filename_full, encoding = 'utf-8')

    return render_template("lta_overdue.html",
                           column_names=result_table.columns.values,
                           filename = filename,
                           row_data=list(result_table.values.tolist()),
                           zip=zip)


@app.route('/lta/overdue/download/<path:filename>', methods=['GET', 'POST'])
def download_file(filename):
    global folder

    return send_from_directory(folder, filename=filename, as_attachment=True)






@app.route('/lta/search', methods=['post', 'get'])
def lta_search():
    global result
    global selected
    global purposes
    global entered_search
    global plot_result1
    global current
    global progress

    current = ''
    progress = '2%'

    freq = ''
    purp = ''
    crystal_type = ''
    owner = ''
    sap = ''
    start_date = ''
    finish_date = ''
    jig = ''
    packet = ''

    if request.method == 'POST':
        selected = int(request.form.get('purpose'))
        print("Selected from list: " + str(selected))

        freq = str(result['nomFrq'].iloc[selected] / 1000000) + "MHz"
        purp = str(result['purpose'].iloc[selected])
        crystal_type = str(result['crystalType'].iloc[selected])
        owner = str(result['owner'].iloc[selected])
        sap = str(result['crystalNumber'].iloc[selected])
        start = str(result['startDate'].iloc[selected])
        finish = str(result['finishDate'].iloc[selected])
        start_date = start.split(" ")[0]
        finish_date = finish.split(" ")[0]
        jig = str(result['oscillator'].iloc[selected])
        packet = str(result['packetNumber'].iloc[selected])

        #plot_result1 = lta_script.select(selected, result)

    elif request.method == 'GET' and request.args.get('search'):
        entered_search = request.args.get('search')
        print("Selected search: " + str(entered_search))

        result, purposes = lta_script.search(entered_search)

        if purposes:
            selected = 0
            print("Selected from list: " + str(selected))

            freq = str(result['nomFrq'].iloc[selected] / 1000000) + "MHz"
            purp = str(result['purpose'].iloc[selected])
            crystal_type = str(result['crystalType'].iloc[selected])
            owner = str(result['owner'].iloc[selected])
            sap = str(result['crystalNumber'].iloc[selected])
            start = str(result['startDate'].iloc[selected])
            finish = str(result['finishDate'].iloc[selected])
            start_date = start.split(" ")[0]
            finish_date = finish.split(" ")[0]
            jig = str(result['oscillator'].iloc[selected])
            packet = str(result['packetNumber'].iloc[selected])

    else:
        purposes = {}
        entered_search = ''

    return render_template('lta_search.html',
                           purposes=purposes,
                           entered_purpose=selected,
                           freq=freq,
                           purp=purp,
                           crystal_type=crystal_type,
                           owner=owner,
                           sap=sap,
                           start=start_date,
                           finish=finish_date,
                           jig=jig,
                           packet=packet,
                           entered_search=entered_search,
                           progress=50,
                           total_units=10,
                           i=5
                           )


@app.route('/lta/plot', methods=['post', 'get'])
def lta_plot():
    global result
    global selected
    global purposes
    global plot_result
    global plot_result1
    global locations
    global plot_filename
    global filename_plt
    global norm
    global diff_fltr
    global gauss
    global current
    global progress

    threshold = 50
    diff_threshold = .5
    current = ''
    progress = '2%'

    plot_result1 = lta_script.select(selected, result)
    plot_result2, locations = lta_script.plot(plot_result1)

    plot_result = pd.DataFrame()

    total = len(locations)

    print(total)
    i = 1


    for location in locations:

        current = str(i) + '/' + str(total)
        progr = int(round(100*(i/total), 0))
        if progr > 100:
            progr = 100
        progress = str(progr) + '%'

        df_single = lta_script.filter(plot_result2, location, threshold, diff_threshold)

        plot_result = pd.concat([plot_result, df_single], ignore_index=True, sort=False)

        i = i + 1



    return render_template('plot_result.html', filename = filename_plt, normal = norm, diff = diff_fltr, gs = gauss)


@app.route('/lta/data')
def data():

    def prepare_data():
        global current
        global progress


        json_data = json.dumps(
            {'progress': progress,
             'current': progress,
             # 'current': current,
             })

        yield f"data:{json_data}\n\n"

        time.sleep(.1)

    return Response(prepare_data(), mimetype='text/event-stream')


@app.route('/lta/replot', methods=['post', 'get'])
def lta_replot():
    global result
    global selected
    global purposes
    global plot_result
    global locations
    global plot_filename
    global filename_plt
    global norm
    global diff_fltr
    global gauss

    if request.form.getlist('norm'):
        norm = True
    else:
        norm = False

    if request.form.getlist('diff_fltr'):
        diff_fltr = True
    else:
        diff_fltr = False

    if request.form.getlist('gauss'):
        gauss = True
    else:
        gauss = False

    # plot_result, locations = lta_script.plot(selected, result)

    return render_template('plot_result.html', filename = filename_plt, normal = norm, diff = diff_fltr, gs = gauss)



@app.route('/lta/plot/plot1.png', methods=['post', 'get'])
def plot1_png():
    global result
    global selected
    global purposes
    global plot_result
    global locations
    global plot_filename
    global filename_plt
    global norm
    global diff_fltr
    global gauss


    freq_nom = float(result['nomFrq'].iloc[selected])
    freq_nom_str = str(freq_nom / 1000000) + "MHz"
    crystal_type = result['crystalType'].iloc[selected]
    crystal_number = result['crystalNumber'].iloc[selected]
    packet_number = result['packetNumber'].iloc[selected]

    fig = Figure(figsize=(12, 6), dpi=110)
    # figFvT = plt.figure(figsize=(12, 10))
    axis = fig.add_subplot(1, 1, 1)

    # axis.plot(xs, ys)

    # plotTitle = "Ageing data for " + str(freq_nom_str) + ", " + str(crystal_type) + ", SAP number " + str(crystal_number) + ", packet #" + str(packet_number)
    # axis.set_title(plotTitle)
    axis.set_xlabel('Days')

    if norm:
        axis.set_ylabel('Frequency, ppb')
        norm_str = " (normalized)"
    else:
        axis.set_ylabel('Frequency, ppm')
        norm_str = ""

    # # ax1.tick_params(axis = 'y', colors = 'b')
    #
    # locations = locations.sort()

    for location in locations:
        print(location)
        result_single = plot_result[plot_result['fk_locID'] == location]
        result_single = result_single.sort_values(by=['measDate'])

        # result_single['DIFF'] = diff(result_single['compFreq'])
        # df_selected = result_single.copy()
        # indes2 = df_selected[((df_selected['DIFF'] > diff_threshold) | (df_selected['DIFF'] < -diff_threshold))].index
        # df_selected.drop(indes2, inplace=True)



        # result_single['freq_savgol'] = signal.savgol_filter(result_single['compFreq'], 31, 0)
        #
        # freq_raw = df_output['compFreq']
        # # freq_raw = df_output['freq_savgol']
        # freq_ftr = ndimage.gaussian_filter(freq_raw, sigma=sigm, order=0)
        #
        # if gauss:
        #     df_output['freq_fltr'] = freq_ftr
        # else:
        #     df_output['freq_fltr'] = freq_raw
        #
        # freq_initial = df_output['freq_fltr'].iloc[0]
        # freq_ppm = 1000000 * (df_output['freq_fltr'] - freq_nom) / freq_nom
        # freq_ppb = 1000000000 * (df_output['freq_fltr'] - freq_initial) / freq_initial



        # bins = result_single['measDate']
        bins = result_single['Days']
        loc = result_single['loc'].iloc[0]
        brd = result_single['brd'].iloc[0]
        label = "loc#" + str(loc)

        #if diff_fltr:
        data = result_single['freq_ppb_fltr_cut']
        # else:
        #     data = result_single['freq_ppb']

        if result_single['Days'].max() < 25:
            sigma = 3
        elif result_single['Days'].max() < 50:
            sigma = 5
        elif result_single['Days'].max() < 80:
            sigma = 10
        else:
            sigma = 50

        #if gauss:
        data_plot = result_single['freq_ppb_fltr_cut_smo']
        # else:
        #     data_plot = data

        # if norm:
        #     data = freq_ppb
        # else:
        #     data = freq_ppm

        #if location == '12925A25-0672-4705-ADAC-F1A290BC4A34':
        axis.plot(bins, data_plot, alpha=1, label=label, linewidth= .75)
            #ax2 = axis.twinx()
            # ax2.plot(bins, df_output['DIFF'], alpha=1, label=label, color = 'tab:orange', linewidth=.75)

    plotTitle = "Ageing data" + norm_str + " for " + str(freq_nom_str) + ", " + str(crystal_type) + ", SAP number " + str(
        crystal_number) + ", packet #" + str(packet_number) + ", board #" + str(brd)
    axis.set_title(plotTitle)

    #
    #     ax1.plot(bins, data, alpha=1, label="LTA", linewidth=1)
    #
    # Show the major grid lines with dark grey lines
    axis.grid(b=True, which='major', color='#666666', linestyle='-', alpha=0.5)

    # Show the minor grid lines with very faint and almost transparent grey lines
    axis.minorticks_on()
    axis.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    axis.legend()
    #
    # labels = axis.get_xticklabels()
    # axis.setp(labels, rotation=45, horizontalalignment='right')
    #

    # fig.canvas.manager.toolbar.add_tool('zoom', 'foo')
    # fig.canvas.draw()
    #
    # # add toolbar
    # toolbar = self.addToolBar(QtCore.Qt.BottomToolBarArea, NavigationToolbar(self.plotWidget, self))

    finish_time = datetime.now()
    file_time = str(finish_time)
    file_time = file_time.replace(" ", "_")
    file_time = file_time.replace(":", "-")
    file_time = file_time.split(".")

    filename_plt = 'plot_' + str(file_time[0]) + '.png'
    # folder = r'C:/Temp/downloads/'
    folder = base_directory + r'/temp_files/'
    plot_filename = folder + filename_plt
    fig.savefig(plot_filename, bbox_inches='tight')

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route('/lta/plot/plot2.png', methods=['post', 'get'])
def plot2_png():
    global result
    global selected
    global purposes
    global plot_result
    global locations
    global plot_filename
    global filename_plt
    global norm
    global diff_fltr
    global gauss


    freq_nom = float(result['nomFrq'].iloc[selected])
    freq_nom_str = str(freq_nom / 1000000) + "MHz"
    crystal_type = result['crystalType'].iloc[selected]
    crystal_number = result['crystalNumber'].iloc[selected]
    packet_number = result['packetNumber'].iloc[selected]

    fig = Figure(figsize=(12, 6), dpi=110)
    # figFvT = plt.figure(figsize=(12, 10))
    axis = fig.add_subplot(1, 1, 1)

    # axis.plot(xs, ys)

    # plotTitle = "Ageing data for " + str(freq_nom_str) + ", " + str(crystal_type) + ", SAP number " + str(crystal_number) + ", packet #" + str(packet_number)
    # axis.set_title(plotTitle)
    axis.set_xlabel('Days')

    if norm:
        axis.set_ylabel('Frequency, ppb')
        norm_str = " (normalized)"
    else:
        axis.set_ylabel('Frequency, ppm')
        norm_str = ""

    # # ax1.tick_params(axis = 'y', colors = 'b')
    #
    # locations = locations.sort()

    for location in locations:
        print(location)
        result_single = plot_result[plot_result['fk_locID'] == location]
        result_single = result_single.sort_values(by=['measDate'])

        # result_single['DIFF'] = diff(result_single['compFreq'])
        # df_selected = result_single.copy()
        # indes2 = df_selected[((df_selected['DIFF'] > diff_threshold) | (df_selected['DIFF'] < -diff_threshold))].index
        # df_selected.drop(indes2, inplace=True)



        # result_single['freq_savgol'] = signal.savgol_filter(result_single['compFreq'], 31, 0)
        #
        # freq_raw = df_output['compFreq']
        # # freq_raw = df_output['freq_savgol']
        # freq_ftr = ndimage.gaussian_filter(freq_raw, sigma=sigm, order=0)
        #
        # if gauss:
        #     df_output['freq_fltr'] = freq_ftr
        # else:
        #     df_output['freq_fltr'] = freq_raw
        #
        # freq_initial = df_output['freq_fltr'].iloc[0]
        # freq_ppm = 1000000 * (df_output['freq_fltr'] - freq_nom) / freq_nom
        # freq_ppb = 1000000000 * (df_output['freq_fltr'] - freq_initial) / freq_initial



        # bins = result_single['measDate']
        bins = result_single['Days']
        loc = result_single['loc'].iloc[0]
        brd = result_single['brd'].iloc[0]
        label = "loc#" + str(loc)

        #if diff_fltr:
        #data = result_single['freq_ppb_fltr_cut']
        # else:
        data = result_single['freq_ppb']

        if result_single['Days'].max() < 25:
            sigma = 3
        elif result_single['Days'].max() < 50:
            sigma = 5
        elif result_single['Days'].max() < 80:
            sigma = 10
        else:
            sigma = 50

        #if gauss:
        data_plot = result_single['freq_ppb_smo']
        #else:
        #    data_plot = data

        # if norm:
        #     data = freq_ppb
        # else:
        #     data = freq_ppm

        #if location == '12925A25-0672-4705-ADAC-F1A290BC4A34':
        axis.plot(bins, data_plot, alpha=1, label=label, linewidth= .75)
            #ax2 = axis.twinx()
            # ax2.plot(bins, df_output['DIFF'], alpha=1, label=label, color = 'tab:orange', linewidth=.75)

    plotTitle = "Ageing data" + norm_str + " for " + str(freq_nom_str) + ", " + str(crystal_type) + ", SAP number " + str(
        crystal_number) + ", packet #" + str(packet_number) + ", board #" + str(brd)
    axis.set_title(plotTitle)

    #
    #     ax1.plot(bins, data, alpha=1, label="LTA", linewidth=1)
    #
    # Show the major grid lines with dark grey lines
    axis.grid(b=True, which='major', color='#666666', linestyle='-', alpha=0.5)

    # Show the minor grid lines with very faint and almost transparent grey lines
    axis.minorticks_on()
    axis.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    axis.legend()
    #
    # labels = axis.get_xticklabels()
    # axis.setp(labels, rotation=45, horizontalalignment='right')
    #

    # fig.canvas.manager.toolbar.add_tool('zoom', 'foo')
    # fig.canvas.draw()
    #
    # # add toolbar
    # toolbar = self.addToolBar(QtCore.Qt.BottomToolBarArea, NavigationToolbar(self.plotWidget, self))

    finish_time = datetime.now()
    file_time = str(finish_time)
    file_time = file_time.replace(" ", "_")
    file_time = file_time.replace(":", "-")
    file_time = file_time.split(".")

    filename_plt = 'plot_' + str(file_time[0]) + '.png'
    # folder = r'C:/Temp/downloads/'
    folder = base_directory + r'/temp_files/'
    plot_filename = folder + filename_plt
    fig.savefig(plot_filename, bbox_inches='tight')

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')




@app.route('/lta/plot/plot3.png', methods=['post', 'get'])
def plot3_png():
    global result
    global selected
    global purposes
    global plot_result
    global locations
    global plot_filename
    global filename_plt
    global norm
    global diff_fltr
    global gauss


    freq_nom = float(result['nomFrq'].iloc[selected])
    freq_nom_str = str(freq_nom / 1000000) + "MHz"
    crystal_type = result['crystalType'].iloc[selected]
    crystal_number = result['crystalNumber'].iloc[selected]
    packet_number = result['packetNumber'].iloc[selected]

    fig = Figure(figsize=(12, 6), dpi=110)
    # figFvT = plt.figure(figsize=(12, 10))
    axis = fig.add_subplot(1, 1, 1)

    # axis.plot(xs, ys)

    # plotTitle = "Ageing data for " + str(freq_nom_str) + ", " + str(crystal_type) + ", SAP number " + str(crystal_number) + ", packet #" + str(packet_number)
    # axis.set_title(plotTitle)
    axis.set_xlabel('Days')

    if norm:
        axis.set_ylabel('Frequency, ppb')
        norm_str = " (normalized)"
    else:
        axis.set_ylabel('Frequency, ppm')
        norm_str = ""

    # # ax1.tick_params(axis = 'y', colors = 'b')
    #
    # locations = locations.sort()

    for location in locations:
        print(location)
        result_single = plot_result[plot_result['fk_locID'] == location]
        result_single = result_single.sort_values(by=['measDate'])

        # result_single['DIFF'] = diff(result_single['compFreq'])
        # df_selected = result_single.copy()
        # indes2 = df_selected[((df_selected['DIFF'] > diff_threshold) | (df_selected['DIFF'] < -diff_threshold))].index
        # df_selected.drop(indes2, inplace=True)



        # result_single['freq_savgol'] = signal.savgol_filter(result_single['compFreq'], 31, 0)
        #
        # freq_raw = df_output['compFreq']
        # # freq_raw = df_output['freq_savgol']
        # freq_ftr = ndimage.gaussian_filter(freq_raw, sigma=sigm, order=0)
        #
        # if gauss:
        #     df_output['freq_fltr'] = freq_ftr
        # else:
        #     df_output['freq_fltr'] = freq_raw
        #
        # freq_initial = df_output['freq_fltr'].iloc[0]
        # freq_ppm = 1000000 * (df_output['freq_fltr'] - freq_nom) / freq_nom
        # freq_ppb = 1000000000 * (df_output['freq_fltr'] - freq_initial) / freq_initial



        # bins = result_single['measDate']
        bins = result_single['Days']
        loc = result_single['loc'].iloc[0]
        brd = result_single['brd'].iloc[0]
        label = "loc#" + str(loc)

        #if diff_fltr:
        data = result_single['freq_ppb_fltr_cut']
        # else:
        #     data = result_single['freq_ppb']

        if result_single['Days'].max() < 25:
            sigma = 3
        elif result_single['Days'].max() < 50:
            sigma = 5
        elif result_single['Days'].max() < 80:
            sigma = 10
        else:
            sigma = 50

        #if gauss:
        #data_plot = ndimage.gaussian_filter(data, sigma=sigma, order=0)
        #else:
        data_plot = data

        # if norm:
        #     data = freq_ppb
        # else:
        #     data = freq_ppm

        #if location == '12925A25-0672-4705-ADAC-F1A290BC4A34':
        axis.plot(bins, data_plot, alpha=1, label=label, linewidth= .75)
            #ax2 = axis.twinx()
            # ax2.plot(bins, df_output['DIFF'], alpha=1, label=label, color = 'tab:orange', linewidth=.75)

    plotTitle = "Ageing data" + norm_str + " for " + str(freq_nom_str) + ", " + str(crystal_type) + ", SAP number " + str(
        crystal_number) + ", packet #" + str(packet_number) + ", board #" + str(brd)
    axis.set_title(plotTitle)

    #
    #     ax1.plot(bins, data, alpha=1, label="LTA", linewidth=1)
    #
    # Show the major grid lines with dark grey lines
    axis.grid(b=True, which='major', color='#666666', linestyle='-', alpha=0.5)

    # Show the minor grid lines with very faint and almost transparent grey lines
    axis.minorticks_on()
    axis.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    axis.legend()
    #
    # labels = axis.get_xticklabels()
    # axis.setp(labels, rotation=45, horizontalalignment='right')
    #

    # fig.canvas.manager.toolbar.add_tool('zoom', 'foo')
    # fig.canvas.draw()
    #
    # # add toolbar
    # toolbar = self.addToolBar(QtCore.Qt.BottomToolBarArea, NavigationToolbar(self.plotWidget, self))

    finish_time = datetime.now()
    file_time = str(finish_time)
    file_time = file_time.replace(" ", "_")
    file_time = file_time.replace(":", "-")
    file_time = file_time.split(".")

    filename_plt = 'plot_' + str(file_time[0]) + '.png'
    # folder = r'C:/Temp/downloads/'
    folder = base_directory + r'/temp_files/'
    plot_filename = folder + filename_plt
    fig.savefig(plot_filename, bbox_inches='tight')

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route('/lta/plot/plot4.png', methods=['post', 'get'])
def plot4_png():
    global result
    global selected
    global purposes
    global plot_result
    global locations
    global plot_filename
    global filename_plt
    global norm
    global diff_fltr
    global gauss


    freq_nom = float(result['nomFrq'].iloc[selected])
    freq_nom_str = str(freq_nom / 1000000) + "MHz"
    crystal_type = result['crystalType'].iloc[selected]
    crystal_number = result['crystalNumber'].iloc[selected]
    packet_number = result['packetNumber'].iloc[selected]

    fig = Figure(figsize=(12, 6), dpi=110)
    # figFvT = plt.figure(figsize=(12, 10))
    axis = fig.add_subplot(1, 1, 1)

    # axis.plot(xs, ys)

    # plotTitle = "Ageing data for " + str(freq_nom_str) + ", " + str(crystal_type) + ", SAP number " + str(crystal_number) + ", packet #" + str(packet_number)
    # axis.set_title(plotTitle)
    axis.set_xlabel('Days')

    if norm:
        axis.set_ylabel('Frequency, ppb')
        norm_str = " (normalized)"
    else:
        axis.set_ylabel('Frequency, ppm')
        norm_str = ""

    # # ax1.tick_params(axis = 'y', colors = 'b')
    #
    # locations = locations.sort()

    for location in locations:
        print(location)
        result_single = plot_result[plot_result['fk_locID'] == location]
        result_single = result_single.sort_values(by=['measDate'])

        # result_single['DIFF'] = diff(result_single['compFreq'])
        # df_selected = result_single.copy()
        # indes2 = df_selected[((df_selected['DIFF'] > diff_threshold) | (df_selected['DIFF'] < -diff_threshold))].index
        # df_selected.drop(indes2, inplace=True)



        # result_single['freq_savgol'] = signal.savgol_filter(result_single['compFreq'], 31, 0)
        #
        # freq_raw = df_output['compFreq']
        # # freq_raw = df_output['freq_savgol']
        # freq_ftr = ndimage.gaussian_filter(freq_raw, sigma=sigm, order=0)
        #
        # if gauss:
        #     df_output['freq_fltr'] = freq_ftr
        # else:
        #     df_output['freq_fltr'] = freq_raw
        #
        # freq_initial = df_output['freq_fltr'].iloc[0]
        # freq_ppm = 1000000 * (df_output['freq_fltr'] - freq_nom) / freq_nom
        # freq_ppb = 1000000000 * (df_output['freq_fltr'] - freq_initial) / freq_initial



        # bins = result_single['measDate']
        bins = result_single['Days']
        loc = result_single['loc'].iloc[0]
        brd = result_single['brd'].iloc[0]
        label = "loc#" + str(loc)

        #if diff_fltr:
        #data = result_single['freq_ppb_fltr_cut']
        # else:
        data = result_single['freq_ppb']

        if result_single['Days'].max() < 25:
            sigma = 3
        elif result_single['Days'].max() < 50:
            sigma = 5
        elif result_single['Days'].max() < 80:
            sigma = 10
        else:
            sigma = 50

        # if gauss:
        #     data_plot = ndimage.gaussian_filter(data, sigma=sigma, order=0)
        # else:
        data_plot = data

        # if norm:
        #     data = freq_ppb
        # else:
        #     data = freq_ppm

        #if location == '12925A25-0672-4705-ADAC-F1A290BC4A34':
        axis.plot(bins, data_plot, alpha=1, label=label, linewidth= .75)
            #ax2 = axis.twinx()
            # ax2.plot(bins, df_output['DIFF'], alpha=1, label=label, color = 'tab:orange', linewidth=.75)

    plotTitle = "Ageing data" + norm_str + " for " + str(freq_nom_str) + ", " + str(crystal_type) + ", SAP number " + str(
        crystal_number) + ", packet #" + str(packet_number) + ", board #" + str(brd)
    axis.set_title(plotTitle)

    #
    #     ax1.plot(bins, data, alpha=1, label="LTA", linewidth=1)
    #
    # Show the major grid lines with dark grey lines
    axis.grid(b=True, which='major', color='#666666', linestyle='-', alpha=0.5)

    # Show the minor grid lines with very faint and almost transparent grey lines
    axis.minorticks_on()
    axis.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    axis.legend()
    #
    # labels = axis.get_xticklabels()
    # axis.setp(labels, rotation=45, horizontalalignment='right')
    #

    # fig.canvas.manager.toolbar.add_tool('zoom', 'foo')
    # fig.canvas.draw()
    #
    # # add toolbar
    # toolbar = self.addToolBar(QtCore.Qt.BottomToolBarArea, NavigationToolbar(self.plotWidget, self))

    finish_time = datetime.now()
    file_time = str(finish_time)
    file_time = file_time.replace(" ", "_")
    file_time = file_time.replace(":", "-")
    file_time = file_time.split(".")

    filename_plt = 'plot_' + str(file_time[0]) + '.png'
    # folder = r'C:/Temp/downloads/'
    folder = base_directory + r'/temp_files/'
    plot_filename = folder + filename_plt
    fig.savefig(plot_filename, bbox_inches='tight')

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')



@app.route('/lta/plot/download', methods=['GET', 'POST'])
def download_plot():
    # global folder
    global plot_filename
    global filename_plt

    # folder = r'C:/Temp/downloads/'
    folder = base_directory + r'/temp_files/'

    return send_from_directory(folder, filename=filename_plt, as_attachment=True)