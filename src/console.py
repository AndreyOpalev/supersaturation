import sys
import os
from experiments import ExperimentNotes
from air_data import AirData
from supersaturation import Supersaturation

class Console:

    def __init__(self, path_to_experiments, path_to_air_data):
        print(path_to_experiments)
        print(path_to_air_data)

        self.experiments = ExperimentNotes(path_to_experiments)
        self.air_data = AirData(path_to_air_data)

    def print_help(self):
        print("Command list:")
        print("   - help - print this help message.")
        print("   - notes - prints all experiments notes.")
        print("   - quit / exit - stops the program.")
        print("   - air - prints list of air data files.")
        print("   - air load DDMMYY - loads a particular data set.")
        print("   - air plot - creates a plot for the loaded data set.")
        print("   - saturation <index> - calculates saturation and saves in a csv file.")

    def print_experiments(self):
        print("The list of experiments:")
        all_notes = self.experiments.get_experiment_list()
        print(all_notes.to_string())

    def print_air_data_files(self):
        print("The list of air data files:")
        filenames = self.air_data.get_filenames()
        for f in filenames:
            print(f)

    def compute_saturation(self, experiment_index):
        print("Computing supersaturation for {}".format(experiment_index))

        # Get the experiment note
        experiment = self.experiments.get_data(experiment_index)
        print(experiment)

        # Load air data correspondig to the date
        date_str = experiment.date.strftime("%d%m%y")
        self.air_data.load_data_file(date_str);

        #XSprint("Type of time:", type(experiment.start.values[0]))
        # Convert Pandas Series type to 
        
        # Compute saturation
        saturation = Supersaturation()
        saturation.compute(experiment.start,         # start time
                           experiment.end,           # end time
                           experiment.ts,            # target sample temperature
                           experiment.S,             # computed saturation?
                           self.air_data.get_data(), # Air data
                           5.0)                      # Cooling speed, deg / min
        
        # Save and plot
        if not os.path.exists('output'):
            os.makedirs('output')
            
        saturation.save_to_csv("output")
        saturation.plot()
        
    def run(self):
        is_run = True
        while (is_run):
            command = input("> ")

            if "notes" == command:
                self.print_experiments()
            elif "air" == command:
                self.print_air_data_files()
            elif "air load" in command:
                date = command.split(" ")[2]
                self.air_data.load_data_file(date)
            elif "air plot" == command:
                self.air_data.plot_loaded_data()
            elif "saturation" in command:
                experiment_index = int(command.split(" ")[1])
                self.compute_saturation(experiment_index)
            elif "quit" == command or "exit" == command:
                is_run = False
            elif "help" in command:
                self.print_help()
            else:
                print("{} is unknown command\n".format(command))


if __name__ == '__main__':
    print(sys.argv)

    path_to_experiments = sys.argv[1]
    path_to_air_data = sys.argv[2]

    console = Console(path_to_experiments, path_to_air_data)
    console.print_help()
    sys.exit(console.run())
