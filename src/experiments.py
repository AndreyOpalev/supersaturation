import pandas as pd

class ExperimentNotes:
    """ Class to process experiment notes stored in the xml file"""

    "Read file"
    def __init__(self, filename):
        
        # Read from an excel file to DataFrame
        df = pd.read_excel(filename)

        # Reduce number of columns
        df = df[['date', 'start', 'end', 'sample', 'ts', 'S']]

        # Convert Date string ('DD/MM/YYYY') to date pbject
        df['date'] = pd.to_datetime(df['date'], format= '%d/%m/%Y')

        # Convert 'start' and 'end' times to datetime object
        df['start'] = pd.to_datetime(df['start'], format= '%H:%M:%S')
        df['end'] = pd.to_datetime(df['end'], format= '%H:%M:%S')
        
        # Keep as a data member                      
        self.notes = df
        self.filename = filename

    def get_experiment_list(self):
        notes = self.notes.copy()

        # Originally the used type is datetime, and it's shown for the
        # date field as "<date> 00:00:00.000" and for time as
        # "1970-01-01 <time>". Here the simplest way (and the only
        # one I know) how to make the print is more clear.
        notes['date'] = pd.to_datetime(notes['date'], format= '%d/%m/%Y').dt.date
        notes['start'] = pd.to_datetime(notes['start'], format= '%H:%M:%S').dt.time
        notes['end'] = pd.to_datetime(notes['end'], format= '%H:%M:%S').dt.time

        return notes

    def get_data(self, index):
        return self.notes.loc[index]#loc(index)
