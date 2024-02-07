import matplotlib.pyplot as plt
import numpy as np
import os 
ballot_generators = {
    "bt": "Bradley Terry",
    "pl": "Plackett Luce",
    "cs": "Cambridge Sampler",
    #"ac": AlternatingCrossover,
}

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
