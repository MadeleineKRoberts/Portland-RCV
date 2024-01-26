import matplotlib.pyplot as plt
import numpy as np
import os 
from etools_zbz import simulate_ensembles
import json
import random
import os
import argparse


# Terminal Command: 
# python simulate_elections_zbz.py --candidates 3 3 5 3 --alpha_params 1 1 1 1 --cohesion_params 0.7 0.8 --num_elections 1
# Will run the following:
    # 3W 3C candidates and 5W, 3C candidates
    # alphas = {"W": {"C": 1, "W": 1}, "C": {"W": 1, "C": 1}}
    # cohesion={"W": 0.7, "C": 0.8}
    # 10 elections

ballot_generators = {
    #"bt": "Bradley Terry",
    #"pl": "Plackett Luce",
    "cs": "Cambridge Sampler",
    #"ac": AlternatingCrossover,
    "sp": "Slate Preference"
}

def simulate_elections(candidates, alpha_params, cohesion_params, num_elections):
    for cand in candidates:
       for a in alpha_params:
            for coh in cohesion_params:

                num_w = cand[0]
                num_c = cand[1]

                wc = a[0]
                ww = a[1]
                cw = a[2]
                cc = a[3]

                coh_w = coh[0]
                coh_c = coh[1]
                
                alphas = {"W": {"C": wc, "W": ww}, "C": {"W": cw, "C": cc}}
                cohesion={"W": coh_w, "C": coh_c}

                basic_start = simulate_ensembles(
                    cohesion=cohesion,
                    num_w=num_w,
                    num_c=num_c,
                    seats=3,
                    num_elections=num_elections,
                    alphas=alphas
                )
                
                # iterate across each zones
                for zone_data in basic_start:
                    curr_zone = zone_data['zone'] + 1

                    params = (
                    "Zone: " + str(curr_zone) + ";\n"
                    "White candidates: " + str(num_w) + ";\n"
                    "POC candidates: " + str(num_c) + ";\n"
                    "alpha_WC " +  str(wc) + ";\n" 
                    "alpha_WW: " + str(ww)  + ";\n" 
                    "alpha_CW " +  str(cw) + ";\n" 
                    "alpha_CC: " + str(cc)
                    + ";\n" "Number of Simulated Elections per Zone: " + str(num_elections)
                    )

                    converted_results = {key: value for key, value in zone_data.items() if key not in ['zone', 'voter_share']}

                    election_results = {
                        "params": {
                            "zone" : curr_zone,
                            "num_white_candidates": num_w,
                            "num_poc_candidates": num_c,
                            "alphas": alphas,
                            "cohesion": cohesion
                        },
                        "results": converted_results
                    }

                    # Define the filename for JSON output
                    json_filename = f'zone_{curr_zone}_{num_elections}_elections_results.json'
                    output_directory = os.path.join(os.getcwd(), 'Results')
                    if not os.path.exists(output_directory):
                        os.makedirs(output_directory)
                    json_output_path = os.path.join(output_directory, json_filename)

                    with open(json_output_path, 'w') as json_file:
                        json.dump(election_results, json_file, indent=4)

                    # simulation type is for the file name - 
                    #example: 1_3W_3C_0.5CC means alpha = 1 for alpha WW,WC,CW; 3 White candidates, 
                    #3 POC Candidates, and 0.5 for alpha CW
                    simulation_type = str(curr_zone) + "Z_" + str(num_w) + "W_" + str(num_c) + "C_" + str(alphas["C"]["C"]) + "CC_" + str(alphas["C"]["W"]) + "CW_" + str(alphas["W"]["C"]) + "WC_" + str(alphas["W"]["W"]) + "WW_" + str(cohesion["C"]) + "cohC_" +  str(cohesion["W"]) + "cohW_ " + str(num_elections) + '_Simulations'
                    
                    generate_histogram(zone_data['cs'], 'cs', simulation_type, params, num_elections, curr_zone, num_w, num_c)
                    generate_histogram(zone_data['sp'], 'sp', simulation_type, params, num_elections, curr_zone, num_w, num_c)


import os
import matplotlib.pyplot as plt
import numpy as np

def generate_histogram(data, election_type, simulation_type, params, num_elections, curr_zone, num_w, num_c, show_plot=False):
    unique_values, counts = np.unique(data, return_counts=True)

    # Ensure that the bins on the x-axis include 0, 1, 2, and 3
    bin_edges = np.arange(-0.5, max(unique_values) + 1.5, 1)
    plt.hist(data, bins=bin_edges, align='mid', alpha=0.7, edgecolor='black')

    # Set ranges for axes
    plt.xticks([0, 1, 2, 3])

    plt.ylim(0, num_elections)  # Set to the number of simulated elections

    plt.xlabel('Number of Elected POC Candidates')
    plt.ylabel('Frequency')
    plt.title('Histogram for ' + ballot_generators[election_type] + ' model ')

    # Display the average
    average_value = np.mean(data)
    plt.text(0.5, -0.15, f'Average Number of Elected POC Candidates: {average_value:.2f}', transform=plt.gca().transAxes, fontsize=10, ha='center')

    plt.text(0.05, 0.95, params, transform=plt.gca().transAxes, fontsize=8, verticalalignment='top')
    plt.tight_layout()

    folder_name = str(election_type) + '_Zone_' + str(curr_zone) + '_' + str(num_w) + 'W_' + str(num_c) + 'C_Histograms'
    output_directory = os.path.join(os.getcwd(), 'Histograms', folder_name)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    output_path = os.path.join(output_directory, f'zone_{curr_zone}_{election_type}_{simulation_type}_histogram.png')
    plt.savefig(output_path)
    if show_plot:
        plt.show()
    plt.clf()

if __name__ == "__main__":
    # Parameters to change
    # alpha_cc = [0.5, 1, 2]
    # alpha = [1, 0.5, 2]
    # candidates = [(3,3),(3,5),(5,3),(2,6),(6,2)]
    parser = argparse.ArgumentParser(description='Run election simulations.')
    parser.add_argument("--candidates", type=int, nargs='+')
    parser.add_argument("--alpha_params", type=float, nargs='+')
    parser.add_argument("--cohesion_params", type=float, nargs='+')
    parser.add_argument("--num_elections", type=int)
    
    args = parser.parse_args()

    candidates_long_list = args.candidates
    candidates_len = len(candidates_long_list)
    candidates = []
    for i in range(0,candidates_len,2):
        candidates.append((candidates_long_list[i], candidates_long_list[i+1]))

    alpha_params_long_list = args.alpha_params
    alpha_params_len = len(alpha_params_long_list)
    alpha_params = []
    for i in range(0,alpha_params_len,4):
        alpha_params.append([alpha_params_long_list[i], alpha_params_long_list[i+1], alpha_params_long_list[i+2], alpha_params_long_list[i+3]])

    cohesion_params_long_list = args.cohesion_params
    cohesion_params_len = len(cohesion_params_long_list)
    cohesion_params = []
    for i in range(0,cohesion_params_len,2):
        cohesion_params.append((cohesion_params_long_list[i], cohesion_params_long_list[i+1]))

    num_elections = args.num_elections

    simulate_elections(candidates=candidates, alpha_params=alpha_params, cohesion_params=cohesion_params, num_elections=num_elections)

