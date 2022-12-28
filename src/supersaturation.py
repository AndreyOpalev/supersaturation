from experiments import ExperimentNotes
from air_data import AirData
from supersaturation_calc import SupersaturationCalc
import matplotlib.dates as mdates
import matplotlib.units as munits
import matplotlib.dates as md
import pandas as pd
import os
import datetime as datetime
import numpy as np
import matplotlib.pyplot as pyplot


class Supersaturation:

    def __init__(self,
                 path_to_experiments,
                 path_to_air_data,
                 path_to_output,
                 cooling_speed,
                 air_data_date_format):
        self.experiments = ExperimentNotes(path_to_experiments)
        self.air_data = AirData(path_to_air_data)
        self.path_to_output = path_to_output
        self.cooling_speed = cooling_speed
        self.air_data_date_format = air_data_date_format

    def print_experiments(self):
        all_notes = self.experiments.get_experiment_list()
        print(all_notes.to_string())

    def print_air_data_files(self):
        filenames = self.air_data.get_filenames()
        for f in filenames:
            print(f)

    def compute_saturation(self, experiment_index):
        # Get the experiment note
        experiment = self.experiments.get_data(experiment_index)
        print(experiment)

        # Load air data correspondig to the date
        date_str = experiment.date.strftime("%d%m%y")
        self.air_data.load_data_file(date_str,
                                     sep=";",
                                     dateformat=self.air_data_date_format)

        # print("Type of time:", type(experiment.start.values[0]))
        # Convert Pandas Series type to

        # Compute saturation
        saturation_calc = SupersaturationCalc()
        saturation_calc.compute(experiment.start,          # start time
                                experiment.end,            # end time
                                experiment.ts,             # target sample temperature
                                experiment.S,              # computed saturation?
                                self.air_data.get_data(),  # Air data
                                self.cooling_speed)        # Cooling speed, deg / min

        # Save
        output_path = self.save_to_csv(saturation_calc)

        return output_path
        
    def save_to_csv(self, supersaturation_calc):

        # Create folder if does not exist
        if not os.path.exists(self.path_to_output):
           os.makedirs(self.path_to_output)

        # Make the printed date and time values without extra info
        # and don't change the computed data itself.
        data = supersaturation_calc.get_results().copy()
        data["Date"] = pd.to_datetime(data['Date'], format='%d/%m/%Y').dt.date

        # Create a filename
        full_path = "{}/supersaturation_{}_{}_{}.csv".format(
            self.path_to_output,
            data["Date"].iloc[0],
            data["Time"].iloc[0].strftime('%H:%M:%S'),
            data["Time"].iloc[-1].strftime('%H:%M:%S'))

        # Make timestamp relative and we did it after, since
        # the start and end time is used to generate filename
        data["Time"] = (data["Time"] - data["Time"].iloc[0])
        data["Time"] = pd.to_datetime(data['Time'].astype(str), format='0 days %H:%M:%S').dt.time

        data.to_csv(full_path, sep=';')

        print("The computed results are saved in the {}.".format(full_path))

        return full_path

    def plot_results(self, output_file):
        df = pd.read_csv(output_file,
                         sep=';',
                         encoding='cp1251',
                         index_col=0,
                         header=0,
                         names=['Date', 'Time', 'Humidity', 'Temp', 'DewTemp', 'PSYC', 'SampleTemp', 'Supersaturation'])

        t = pd.to_datetime(df['Date'] + ' ' + df['Time'],
                           format="%Y-%m-%d %H:%M:%S")

        # Dateformatter
        t_fmt = md.DateFormatter('%H:%M:%S')
    
        # Time is always a problem
        converter = mdates.ConciseDateConverter()
        munits.registry[np.datetime64] = converter
        munits.registry[datetime.date] = converter
        munits.registry[datetime.datetime] = converter

        fig = pyplot.figure(figsize=(10, 10))

        # Plot Humidity
        ax1 = fig.add_subplot(411)
        ax1.set_ylabel('Humidity, %')
        ax1.grid(True)
        ax1.plot(t, df.Humidity, color='blue')

        # Plot Temperature
        ax2 = fig.add_subplot(412, sharex=ax1)
        ax2.set_ylabel('Temperature, deg')
        ax2.grid(True)
        ax2.plot(t, df.Temp, color='orange')

        # Plot Dew temperature
        ax3 = fig.add_subplot(413, sharex=ax1, sharey=ax2)
        ax3.set_ylabel('Dew temperature, deg')
        ax3.grid(True)
        ax3.plot(t, df.DewTemp, color='orange')

        # Plot Supersaturation
        ax4 = fig.add_subplot(414)
        ax4.set_ylabel('Supersaturation')
        ax4.grid(True)
        ax4.plot(t, df.Supersaturation, color='red')

        # Configure X axis
        ax4.set_xlabel("Time")
        ax4.xaxis.set_major_formatter(t_fmt)
        
        # Plot
        ax1.set_title("Output data")
        pyplot.setp(ax1.get_xticklabels(), visible=False)
        pyplot.setp(ax2.get_xticklabels(), visible=False)
        pyplot.setp(ax3.get_xticklabels(), visible=False)
        pyplot.show()
