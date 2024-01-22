import matplotlib.pyplot as plt
import numpy as np
import os 
from etools import simulate_ensembles
import json
import random
import os

ballot_generators = {
    "bt": "Bradley Terry",
    "pl": "Plackett Luce",
    "cs": "Cambridge Sampler",
    #"ac": AlternatingCrossover,
}

# Parameters to change
alpha_cc = [0.5, 1, 2]
alpha = [1, 0.5, 2]
candidates = [(3,3),(3,5),(5,3),(2,6),(6,2)]

def simulate_1000():
    num_elections = 1000
    for c in candidates:
        for b in alpha:
            for a in alpha_cc:
                num_w = c[0][0]
                num_c = c[0][1]
                
                alphas = {"W": {"C": b, "W": b}, "C": {"W": b, "C": a}}
                cohesion={"W": 0.7, "C": 0.8}

                basic_start = simulate_ensembles(
                    cohesion=cohesion,
                    num_w=num_w,
                    num_c=num_c,
                    seats=3,
                    num_elections=num_elections,
                    alphas=alphas
                )
                
                params = (
                "White candidates: " + str(num_w) + ";\n"
                "POC candidates: " + str(num_c) + ";\n"
                "alpha_CC " +  str(a) + ";\n" #TODO update variable after allowing for different alphas
                "alpha_CW: " + str(b)  + ";\n" #TODO update variable after allowing for different alphas
                "alpha_CC " +  str(b) + ";\n" #TODO update variable after allowing for different alphas
                "alpha_CW: " + str(b) #TODO update variable after allowing for different alphas
                # + ";\n" "Number of Simulated Elections per Zone: " + str(num_elections)
                )

                # simulation type is for the file name - 
                #example: 1_3W_3C_0.5CC means alpha = 1 for alpha WW,WC,CW; 3 White candidates, 
                #3 POC Candidates, and 0.5 for alpha CW
                simulation_type = str(num_w) + "W_" + str(num_c) + "C_" + str(alphas["C"]["C"]) + "CC_" + str(alphas["C"]["W"]) + "CW_" + str(alphas["W"]["C"]) + "WC_" + str(alphas["W"]["W"]) + "WW_" + str(cohesion["C"]) + "cohesC" +  str(cohesion["W"]) + "cohesW"

                generate_histogram(basic_start['bt'], 'bt', simulation_type, params, num_elections)
                generate_histogram(basic_start['pl'], 'pl', simulation_type, params, num_elections)
                generate_histogram(basic_start['cs'], 'cs', simulation_type, params, num_elections)


def generate_histogram(data, election_type, simulation_type, params, num_elections):
    unique_values, counts = np.unique(data, return_counts=True)

    plt.bar(unique_values, counts, align='center', alpha=0.7, width=0.8)   

    # Set ranges for axes
    plt.xticks(np.arange(1, 9, 1))  # Set distinct whole numbers
    plt.ylim(0, num_elections) # Set to the number of simulated elections

    plt.xlabel('Number of Elected POC Candidates')
    plt.ylabel('Frequency')
    plt.title('Histogram for ' + ballot_generators[election_type] + ' model ')

    # Display the average
    average_value = np.mean(data)
    plt.text(0.5, -0.15, f'Average Number of Elected POC Candidates: {average_value:.2f}', transform=plt.gca().transAxes, fontsize=10, ha='center')

    plt.text(0.05, 0.95, params, transform=plt.gca().transAxes, fontsize=8, verticalalignment='top')
    plt.tight_layout()

    current_directory = os.getcwd()
    output_path = os.path.join(current_directory, 'Histograms', f'{election_type}_{simulation_type}_histogram.png')
    plt.savefig(output_path)
    plt.show()

if __name__ == "__main__":
    simulate_1000()
