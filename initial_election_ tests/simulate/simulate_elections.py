import matplotlib.pyplot as plt
import numpy as np
import os 
from etools import simulate_ensembles
import json
import random
import os
import argparse

ballot_generators = {
    "bt": "Bradley Terry",
    "pl": "Plackett Luce",
    "cs": "Cambridge Sampler",
    #"ac": AlternatingCrossover,
}



def simulate_elections(candidates, alpha, alpha_cc, num_elections):
    for c in candidates:
        for b in alpha:
            for a in alpha_cc:
                num_w = c[0]
                num_c = c[1]
                params = (
                        "White candidates: " + str(num_w) + ";\n"
                        "POC candidates: " + str(num_c) + ";\n"
                        "alpha_CW: " + str(a)
                    )
                alphas = {"W": {"C": b, "W": b}, "C": {"W": b, "C": a}}
                basic_start = simulate_ensembles(
                    cohesion={"W": 0.7, "C": 0.8},
                    num_w=num_w,
                    num_c=num_c,
                    seats=3,
                    num_elections=num_elections,
                    alphas=alphas
                )
                # simulation type is for the file name - 
                #example: 1_3W_3C_0.5CC means alpha = 1 for alpha WW,WC,CW; 3 White candidates, 
                #3 POC Candidates, and 0.5 for alpha CW
                simulation_type = str(b) + "_" + str(num_w) + "W_" + str(num_c) + "C_" + str(a) + "CC"
                generate_histogram(basic_start['bt'], 'bt', simulation_type, params)
                generate_histogram(basic_start['pl'], 'pl', simulation_type, params)
                generate_histogram(basic_start['cs'], 'cs', simulation_type, params)


def generate_histogram(data, election_type, simulation_type, params, show_fig=False):
    unique_values, counts = np.unique(data, return_counts=True)

    plt.bar(unique_values, counts, align='center', alpha=0.7, width=0.8)

    plt.xticks(np.arange(min(unique_values), max(unique_values)+1, 1))  # Set x-axis ticks at distinct whole numbers
    plt.xlabel('Number of Elected POC Candidates')
    plt.ylabel('Frequency')
    plt.title('Histogram for ' + ballot_generators[election_type] + ' model ')
    current_directory = os.getcwd()
    output_path = os.path.join(current_directory, 'Histograms', f'{election_type}_{simulation_type}_histogram.png')
    plt.text(0.05, 0.95, params, transform=plt.gca().transAxes, fontsize=8, verticalalignment='top')
    plt.savefig(output_path)
    if show_fig:
        plt.show()

if __name__ == "__main__":
    # Parameters to change
    # alpha_cc = [0.5, 1, 2]
    # alpha = [1, 0.5, 2]
    # candidates = [(3,3),(3,5),(5,3),(2,6),(6,2)]
    parser = argparse.ArgumentParser(description='Run election simulations.')
    parser.add_argument("--candidates", type=int, nargs='+')
    parser.add_argument("--alpha", type=float, nargs='+')
    parser.add_argument("--alpha_cc", type=float, nargs='+')
    
    args = parser.parse_args()

    alpha_cc = args.alpha_cc
    alpha = args.alpha
    candidates_long_list = args.candidates
    candidates_len = len(candidates_long_list)
    candidates = []
    for i in range(0,candidates_len,2):
        candidates.append((candidates_long_list[i], candidates_long_list[i+1]))

    simulate_elections(candidates=candidates, alpha=alpha, alpha_cc=alpha_cc, num_elections=1000)

