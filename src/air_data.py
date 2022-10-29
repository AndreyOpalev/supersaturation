import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as pyplot
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

class AirData:
    """ Class to gather function to handle the air (humidity) data """

    def __init__(self, directory):
        self.directory = directory
        self.air_df = pd.DataFrame()

    def plot_loaded_data(self):
        fig, axes1 = pyplot.subplots(constrained_layout=True)

        # Humidity (left axis)
        axes1.xaxis.set_major_locator(mticker.MaxNLocator(nbins = 6))
        axes1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        axes1.set_xlabel('Time')
        axes1.set_ylabel('Humidity, %')
        l1, = axes1.plot(self.air_df.Time,
                         self.air_df.Humidity,
                         label = 'Humidity',
                         color='blue')

        axes2 = axes1.twinx()

        # Air and dew temperatures (right axis)
        axes2.set_ylabel('Temperature, deg')
        # axes2.tick_params(axis='y', labelcolor='orange') # does not work ok in jupyter
        l2, = axes2.plot(self.air_df.Time,
                         self.air_df.Temp,
                         label = 'Temperature',
                         color='orange')
        
        l3, = axes2.plot(self.air_df.Time,
                         self.air_df.DewTemp,
                         label = 'Dew temperature',
                         color='orange',
                         linestyle='dashed')

        axes2.legend([l1, l2, l3], ['Humidity', 'Temperature (right)', 'Dew temperature (right)'])

        axes1.grid(True, axis='x')
        pyplot.show()
       # pyplot.waitforbuttonpress()
        
        
    def load_data_file(self, date, sep=';', dateformat='%d.%m.%Y', timeformat='%H:%M:%S'):

        # Select the files to loaded based on date. It expects DDMMYY
        # format.
        csv_files = self.get_filenames()
        files_to_load = []
        for f in csv_files:
            if date in f:
                files_to_load.append(f)


        common_df = pd.DataFrame();
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
                             header = 0,
                             names = ['Date', 'Time', 'Humidity', 'Temp', 'DewTemp', 'PSYC'])
       
            # Convert Date string ('DD.MM.YYYY') to datetime object
            # df['Date'] = pd.Series(val.date() for val in pd.to_datetime(df['Date'], format= '%d.%m.%Y'))
            df['Date'] = pd.to_datetime(df['Date'], format= dateformat)
       
            # Convert 'Time' string to datetime object
            # dfDatime'] = pd.Series(val.date() for val in pd.to_datetime(df['Date'], format= '%d.%m.%Y'))
            # df['Time'] = pd.DatetimeIndex(pd.to_datetime(df['Time'], format= '%H:%M:%S')).time
            df['Time'] = pd.to_datetime(df['Time'], format= timeformat)

            common_df = pd.concat([common_df, df])

        # Save the read data    
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
        
    def plot(self):
        "Plots in a separete figure all air data"
