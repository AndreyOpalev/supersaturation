import matplotlib.pyplot as pyplot
import matplotlib.ticker as mticker
import pandas as pd
import datetime
import vapor_pressure_over_water as vapor


class SupersaturationCalc:
    """ Class to keep results """

    def __init__(self):
       "Does nothing yet"

    def calc_supersaturation(self, humidity, air_pressure, sample_pressure):
        return (humidity / 100.0) * air_pressure * (1.0 / sample_pressure)

    def compute(self,
                start_time : datetime.time, 
                end_time : datetime.time,
                target_sample_temp : float,
                estimated_supersat : float,
                air_df : pd.DataFrame,
                cooling_speed : float):
    
        # 1. Do a slice of data in interval [start_time, end_time]
        cropped_air_data = air_df.loc[(air_df.Time >= start_time) & (air_df.Time < end_time)]
        cropped_air_data = cropped_air_data.reset_index(drop=True)

        # 2. Added a column "SampleTemperature" filled with target_sample_temp
        cropped_air_data.loc[:, 'SampleTemp'] = [target_sample_temp] * len(cropped_air_data.index)
        #     sampleTemperature = pd.DataFrame([target_sample_temp] * len(cropped_air_data.index), columns=['SampleTemp'])
        #     cropped_air_data = pd.concat([cropped_air_data, sampleTemperature])

        # 3. Modify SampleTemp considering cooling speed
        dew_temperature_at_start_time = cropped_air_data.DewTemp[cropped_air_data.Time > start_time].iloc[0]
 #       print("Dew temperature at the start time, deg: ", dew_temperature_at_start_time)

        cropped_air_data.loc[0, 'SampleTemp'] = dew_temperature_at_start_time
        
        for i in range(1, len(cropped_air_data.index)):
        
            dt = cropped_air_data['Time'].iloc[i] - cropped_air_data.Time.iloc[i - 1]
            
 #           print('Time interval elapsed, s: {.3f}'.format(dt.total_seconds()))
 #           print('Previous sample temperature, deg.: {.3f}'.format(cropped_air_data.loc[i-1, 'SampleTemp']))
 #           print("Sample temperature coolled down to, deg: {.3f}"
 #                 .format(cropped_air_data['SampleTemp'].iloc[i-1] - (cooling_speed / 60.0) * dt.total_seconds()))

            cropped_air_data.loc[i, 'SampleTemp'] = cropped_air_data['SampleTemp'].iloc[i-1] - (cooling_speed / 60.0) * dt.total_seconds()

            if cropped_air_data['SampleTemp'].iloc[i] <= target_sample_temp:
                cropped_air_data.loc[i, 'SampleTemp'] = target_sample_temp
                break
        
            cropped_air_data.loc[cropped_air_data['SampleTemp'].isnull(), 'SampleTemp'] = target_sample_temp

            supersaturation = self.calc_supersaturation(cropped_air_data['Humidity'], 
                                                        vapor.get_vapor_pressure_interpolated(cropped_air_data['Temp']),
                                                        vapor.get_vapor_pressure_interpolated(cropped_air_data['SampleTemp']))
    
            # 4. Add "Supersaturation"to the final data
            # TODO: Create a new DataFrame by concat.
            cropped_air_data.loc[:, 'Supersaturation'] = supersaturation
    
            # TODO: Move it out.
            # 5. Made relative time and put it as string
            # cropped_air_data.Time = cropped_air_data.Time - cropped_air_data.Time[0]
            # cropped_air_data.Time = cropped_air_data.Time.dt.strftime("%H:%M:%S")
            self.computed_supersaturation = cropped_air_data

    def get_results(self):
        return self.computed_supersaturation

    def plot(self, title=""):
        time = self.computed_supersaturation.Time
        supersaturation = self.computed_supersaturation.Supersaturation
    
        time_deltas = [(t - time.loc[0]).total_seconds() for t in time]    
    
        fig, axes = pyplot.subplots(constrained_layout=True)

        # Start time since 0
    
        axes.xaxis.set_major_locator(mticker.MaxNLocator(nbins = 6))
        # axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        axes.set_xlabel('Time, s')
        axes.set_ylabel('Supersaturation')
        axes.plot(time_deltas, supersaturation)
        axes.set_title(title)
        axes.grid()
        axes.set_title("Supersaturation")
        pyplot.show()


