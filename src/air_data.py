import pandas as pd
import os
import matplotlib.pyplot as pyplot
import matplotlib.dates as mdates
import matplotlib.units as munits
import numpy as np
import datetime as datetime


class AirData:
    """ Class to gather function to handle the air (humidity) data """

    def __init__(self, directory):
        self.directory = directory
        self.air_df = pd.DataFrame()

    def plot_loaded_data(self):

        # Time is always a problem
        converter = mdates.ConciseDateConverter()
        munits.registry[np.datetime64] = converter
        munits.registry[datetime.date] = converter
        munits.registry[datetime.datetime] = converter

        fig = pyplot.figure(figsize=(10, 10))

        # Plot Humidity
        ax1 = fig.add_subplot(311)
        ax1.set_ylabel('Humidity, %')
        ax1.grid(True)
        ax1.plot(self.air_df.Time, self.air_df.Humidity, color='blue')

        # Plot Temperature
        ax2 = fig.add_subplot(312, sharex=ax1)
        ax2.set_ylabel('Temperature, deg')
        ax2.grid(True)
        ax2.plot(self.air_df.Time, self.air_df.Temp, color='orange')

        # Plot Dew temperature
        ax3 = fig.add_subplot(313, sharex=ax1, sharey=ax2)
        ax3.set_ylabel('Dew temperature, deg')
        ax3.grid(True)
        ax3.plot(self.air_df.Time, self.air_df.DewTemp, color='orange')
        
        # Plot
        ax1.set_title("Loaded air data")
        pyplot.setp(ax1.get_xticklabels(), visible=False)
        pyplot.setp(ax2.get_xticklabels(), visible=False)
        pyplot.show()

    def load_data_file(self,
                       date,
                       sep=';',
                       dateformat='%d.%m.%Y',
                       timeformat='%H:%M:%S'):

        # Select the files to loaded based on date. It expects DDMMYY
        # format.
        csv_files = self.get_filenames()
        files_to_load = []
        for f in csv_files:
            if date in f:
                files_to_load.append(f)

        common_df = pd.DataFrame()
        for f in files_to_load:
            f = self.directory + "/" + f
            print("Loading {}.".format(f))

            # catch, if possible, "UnicodeDecodeError: 'utf-8' codec can't
            # decode byte 0xb0 in position 38: invalid start byte".
            # There is argument "encoding_errorsstr"= {ignore, string, replace, etc}
            df = pd.read_csv(f,
                             sep=sep,
                             encoding='cp1251',
                             index_col=0,
                             header=0,
                             names=['Date', 'Time', 'Humidity', 'Temp', 'DewTemp', 'PSYC'])

            # Convert Date string ('DD.MM.YYYY') to datetime object
            df['Date'] = pd.to_datetime(df['Date'], format=dateformat)

            # dateformat 'Time' string to datetime object
            df['Time'] = pd.to_datetime(df['Time'], format=timeformat)

            # replace float's decimal separator (use always .)
            df['Humidity'] = (df['Humidity'].str.replace(',', '.')).astype(float)
            df['Temp'] = (df['Temp'].str.replace(',', '.')).astype(float)
            df['DewTemp'] = (df['DewTemp'].str.replace(',', '.')).astype(float)
            df['PSYC'] = (df['PSYC'].str.replace(',', '.')).astype(float)

            common_df = pd.concat([common_df, df])

        # Sort and save the read data
        common_df = common_df.sort_values(by=['Time'])
        common_df = common_df.reset_index(drop=True)
        self.air_df = common_df

    def get_data(self):
        return self.air_df

    def get_filenames(self):
        all_files = os.listdir(self.directory)
        csv_files = []
        for file in all_files:
            if file.endswith(".csv"):
                csv_files.append(file)
 
        return csv_files
