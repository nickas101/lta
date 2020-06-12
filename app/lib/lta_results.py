import os
import sys
import glob
import pyodbc 
from pandas import DataFrame
import pandas as pd


import scipy.ndimage as ndimage
import numpy as np
import time

import animation
# from waitingspinnerwidget import QtWaitingSpinner

from mpl_toolkits.axes_grid1 import host_subplot
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtGui import QIcon

import matplotlib
matplotlib.use('QT5Agg')

import matplotlib.pylab as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure
from matplotlib import animation

import matplotlib._pylab_helpers

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# from PyQt4 import QtGui
#
# from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
# from matplotlib.figure import Figure


connection = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                        "Server=akl-longage3\LONGAGE3;"
                        "Database=LTMAL3;"
                        "UID=RAKON\nikolai;"
                        "Trusted_Connection=yes;")

df = pd.DataFrame()
df_plot = pd.DataFrame()

unit_name = 'test1'
# freq_nom = 26

# plt.ion()

plotted = False
# fig = None
# ax1 = None
plt.rcParams.update({'figure.autolayout': True})
fig, ax1 = plt.subplots()


def main(search_text = "Siward"):
    global connection
    global df
    # global freq_nom



    


    # register_matplotlib_converters()
    
    # if all_units:
    #     command = "select * from locData join brdData on locData.fk_brdID = brdData.pk_brdID join runData on runData.pk_runID = locData.fk_runID where runData.currentRun = 'True' and runData.finishDate < CURRENT_TIMESTAMP"
    # elif crystalType == '':
    #     if moustrap:
    #         command = "select * from locData join brdData on locData.fk_brdID = brdData.pk_brdID join runData on runData.pk_runID = locData.fk_runID where runData.currentRun = 'True' and runData.finishDate < CURRENT_TIMESTAMP and runData.oscillator = 'Mousetrap'"
    #     else:
    #         command = "select * from locData join brdData on locData.fk_brdID = brdData.pk_brdID join runData on runData.pk_runID = locData.fk_runID where runData.currentRun = 'True' and runData.finishDate < CURRENT_TIMESTAMP and runData.oscillator <> 'Mousetrap'"
    # else:
    #     if moustrap:
    #         command = "select * from locData join brdData on locData.fk_brdID = brdData.pk_brdID join runData on runData.pk_runID = locData.fk_runID where runData.currentRun = 'True' and runData.finishDate < CURRENT_TIMESTAMP and runData.oscillator = 'Mousetrap' and runData.crystalType = " + crystalType
    #     else:
    #         command = "select * from locData join brdData on locData.fk_brdID = brdData.pk_brdID join runData on runData.pk_runID = locData.fk_runID where runData.currentRun = 'True' and runData.finishDate < CURRENT_TIMESTAMP and runData.oscillator <> 'Mousetrap' and runData.crystalType = " + crystalType


    # command = "select * from measData where measData.fk_locID = '5A09D288-6325-431E-9664-ED7CA5A44FAE' and measData.frq <> '9999'"

    command = "select * from runData where runData.purpose like '%" + str(search_text) + "%' or runData.comment like '%" + str(search_text) + "%' or runData.packetNumber like '%" + str(search_text) + "%' or runData.crystalNumber like '%" + str(search_text) + "%'"


    df = pd.read_sql(command, connection)

    df['startDate'] = df['startDate'].dt.date
    df['finishDate'] = df['finishDate'].dt.date

    result = df



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

    return df


def plot(index):
    global connection
    global df
    global df_plot


    # print("index = " + str(index))

    run_id = str(df['pk_runID'].iloc[index])

    # freq_nom = float(df['nomFrq'].iloc[index])

    # print("run_id = " + str(run_id))
    # print("freq_nom = " + str(freq_nom))


    command = "select * from measData where measData.fk_locID in (select pk_locID from locData where locData.fk_runID = '" + str(run_id) + "') and measData.frq <> '9999' and compFreq <> '9999'"

    # print(str(command))

    # command = "select * from runData where runData.purpose like '%" + str(search_text) + "%'"
    #
    df_plot = pd.read_sql(command, connection)

    # print(df_plot)


    locations = df_plot['fk_locID'].unique().tolist()

    # df[df.population > 10][['country', 'square']]

    # print(locations[1])

    # df_plot = df_plot.sort_values(by=['fk_locID', 'measDate'])

    result = df_plot

    # result = df_plot[df_plot['fk_locID'] == locations[1]]
    #
    # result = result.sort_values(by=['measDate'])

    # print(result)



    # # filename = filename.replace('.csv', '') + '_filtered.csv'
    path = r"\\rakdata2\Share\Nikolai\serial\sql_results\\"
    filename = path + 'result.csv'
    result.to_csv(filename, encoding = 'utf-8')
    #
    #
    #
    #
    #
    # figFvI = plt.figure(figsize = (16,10))
    #
    # fviHost = host_subplot(111)
    # plt.subplots_adjust(right = 1) # Was 0.5
    #
    # plotTitle = "\nAgeing data " + str(unit_name)
    # fviHost.set_title(plotTitle)
    # fviHost.set_xlabel('Time, ', color='r')
    # fviHost.set_ylabel('Frequency, ppm', color='b')
    #
    # fviHost.tick_params(axis = 'y', colors = 'b')
    # fviHost.tick_params(axis = 'x', colors = 'r')
    #
    # fviHost.plot(df['measDate'], df['frq_ppm'], color='b', alpha = 1, label = "Residual", linewidth=.5)
    # # fviHost.plot(df_raw['Offset Frequency (Hz)'], df_raw['PN_FLT'], color='b', alpha = 0.5, label = "Residual", linewidth=1)
    # # fviHost.set_xscale('log')
    #
    # # Show the major grid lines with dark grey lines
    # fviHost.grid(b=True, which='major', color='#666666', linestyle='-', alpha=0.5)
    #
    # # Show the minor grid lines with very faint and almost transparent grey lines
    # fviHost.minorticks_on()
    # fviHost.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    #
    #
    # # save_plot = path + r'\\results//' + str(unit_name) + '.png'
    # save_plot = path + r'//' + str(unit_name) + '.png'
    # figFvI.savefig(save_plot, bbox_inches = 'tight')
    #
    # plt.close(figFvI)
    #
    # spinner.stop()

    return result, locations





# **************************

# print(os.getcwd())
# sys.exit()

# project_path = r"\\Akl-file-01\Departments\Engineering - Product R&D\Stored Files\Nikolai\scripts\LTA_results\\"

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        uic.loadUi('2.ui', self)

        self.setWindowIcon(QIcon('banana.png'))
        self.setWindowTitle("LTA results")

        self.pushButton_2.clicked.connect(self.buttonClicked)
        self.pushButton_plot.clicked.connect(self.listItemDoubleClicked)


    def listItemClicked(self, item):
        # QMessageBox.information(self, "ListWidget", "You clicked: " + item.text())
        # print(item)
        index = self.listWidget.currentRow()

        freq = str(df['nomFrq'].iloc[index] / 1000000) + "MHz"
        purpose = str(df['purpose'].iloc[index])
        crystal_type = str(df['crystalType'].iloc[index])
        owner = str(df['owner'].iloc[index])
        sap = str(df['crystalNumber'].iloc[index])

        df['startDate'] = df['startDate'].dt.date
        df['finishDate'] = df['finishDate'].dt.date
        start = str(df['startDate'].iloc[index])
        finish = str(df['finishDate'].iloc[index])
        jig = str(df['oscillator'].iloc[index])
        packet = str(df['packetNumber'].iloc[index])

        self.label12.setText(str(freq))
        self.label101.setText(purpose)
        self.label_7.setText(crystal_type)
        self.label_15.setText(owner)
        self.label_17.setText(sap)
        self.label_13.setText(start)
        self.label_21.setText(finish)
        self.label_25.setText(jig)
        self.label_27.setText(packet)

        return self.listWidget.currentRow()


    def itemSelectionChanged (self):
        # QMessageBox.information(self, "ListWidget", "You clicked: " + item.text())
        # print(item)
        index = self.listWidget.currentRow()

        freq = str(df['nomFrq'].iloc[index] / 1000000) + "MHz"
        purpose = str(df['purpose'].iloc[index])
        crystal_type = str(df['crystalType'].iloc[index])
        owner = str(df['owner'].iloc[index])
        sap = str(df['crystalNumber'].iloc[index])
        start = str(df['startDate'].iloc[index])
        finish = str(df['finishDate'].iloc[index])
        jig = str(df['oscillator'].iloc[index])
        packet = str(df['packetNumber'].iloc[index])

        self.label12.setText(str(freq))
        self.label101.setText(purpose)
        self.label_7.setText(crystal_type)
        self.label_15.setText(owner)
        self.label_17.setText(sap)
        self.label_13.setText(start)
        self.label_21.setText(finish)
        self.label_25.setText(jig)
        self.label_27.setText(packet)

        return self.listWidget.currentRow()


    def listItemDoubleClicked(self, item):
        global plotted

        print(" \n************************************************************ ")

        # Buttons are blocked while plotting
        self.pushButton_plot.setText("Wait...")
        self.pushButton_2.setText("Wait...")
        self.pushButton_2.setEnabled(False)
        self.pushButton_plot.setEnabled(False)
        QtWidgets.qApp.processEvents()

        print('plotted = ' + str(plotted))
        print("Fig -> " + str(fig))

        if plotted:
            ax1.clear()
            fig.canvas.draw()
            # fig.canvas.flush_events()

        index = self.listWidget.currentRow()
        result, locations = plot(index)

        freq_nom = float(df['nomFrq'].iloc[index])
        freq_nom_str = str(float(df['nomFrq'].iloc[index]) / 1000000) + "MHz"
        crystal_type = df['crystalType'].iloc[index]
        crystal_number = df['crystalNumber'].iloc[index]
        packet_number = df['packetNumber'].iloc[index]


        # if plotted:
        #     ax1.remove()
        # else:

        # plt.ion()
        # if plotted == False:
        #     print("Creating fig and ax1 objects...")
            # fig, ax1 = plt.subplots()

        plotTitle = "Ageing data for " + str(freq_nom_str) + ", " + str(crystal_type) + ", SAP number " + str(crystal_number) + ", packet #" + str(packet_number)
        ax1.set_title(plotTitle)
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Frequency, ppm')
        # ax1.tick_params(axis = 'y', colors = 'b')

        for location in locations:
            result_single = df_plot[df_plot['fk_locID'] == location]
            result_single = result_single.sort_values(by=['measDate'])
            freq_ppm = 1000000 * (result_single['compFreq'] - freq_nom) / freq_nom
            data = freq_ppm
            bins = result_single['measDate']

            ax1.plot(bins, data, alpha=1, label="LTA", linewidth=1)


        # Show the major grid lines with dark grey lines
        ax1.grid(b=True, which='major', color='#666666', linestyle='-', alpha=0.5)

        # Show the minor grid lines with very faint and almost transparent grey lines
        ax1.minorticks_on()
        ax1.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

        labels = ax1.get_xticklabels()
        plt.setp(labels, rotation=45, horizontalalignment='right')

        fig.canvas.draw()
        # fig.canvas.flush_events()

        print("Axes -> " + str(ax1))
        # if plotted == False:
        #     fig.canvas.draw()

        # print(plt.style.available)
        # plt.style.use('fivethirtyeight')



        # fig.tight_layout()


        #clear the previous graph from the frame
        # for graph in self.frame_graph.winfo_children():
        # for graph in self.plot1.winfo_children():
        #     graph.destroy()

        # for tb in self.toolbar.winfo_children():
        #     tb.destroy()




        # plot
        self.plotWidget = FigureCanvas(fig)
        lay = QtWidgets.QVBoxLayout(self.plot1)
        # lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.plotWidget)

        # add toolbar
        toolbar = self.addToolBar(QtCore.Qt.BottomToolBarArea, NavigationToolbar(self.plotWidget, self))
        # toolbar.update()

        # fig.canvas.draw_idle()

        plotted = True

        # Buttons are released after plotting
        self.pushButton_plot.setText("Plot")
        self.pushButton_2.setText("Search")
        self.pushButton_2.setDisabled(False)
        self.pushButton_plot.setDisabled(False)
        QtWidgets.qApp.processEvents()

        print("Fig numbers -> " + str(plt.get_fignums()))

        # print("Fig -> " + str(plt.getp(fig)))
        # print("Fig -> " + str(plt.gcf()))
        print("Axes -> " + str(plt.getp(fig, 'axes')))
        print("Children -> " + str(plt.getp(fig, 'children')))
        # print(ax1.get_figure())

        # figures = [manager.canvas.figure
        #            for manager in matplotlib._pylab_helpers.Gcf.get_all_fig_managers()]
        # print("print figures")
        # print(figures)

        # [<matplotlib.figure.Figure object at 0xb788ac6c>, <matplotlib.figure.Figure object at 0xa143d0c>]
        #
        # for i, figure in enumerate(figures):
        #     print(i)
            # figure.savefig('figure%d.png' % i)




    def buttonClicked(self):

        search_text = self.lineEdit.text()

        # df = main(search_text)
        main(search_text)
        self.listWidget.clear()

        self.label12.clear()
        self.label101.clear()
        self.label_7.clear()
        self.label_15.clear()
        self.label_17.clear()

        # print(df['purpose'])

        self.listWidget.addItems(df['purpose'])

        # self.listWidget.itemClicked.connect(self.listItemClicked)
        self.listWidget.itemSelectionChanged.connect(self.itemSelectionChanged)
        self.listWidget.itemDoubleClicked.connect(self.listItemDoubleClicked)


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())


# plt.ioff()
# plt.close()