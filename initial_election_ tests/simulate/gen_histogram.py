import matplotlib.pyplot as plt
import numpy as np

ballot_generators = {
    "bt": "Bradley Terry",
    "pl": "Plackett Luce",
    "cs": "Cambridge Sampler",
    #"ac": AlternatingCrossover,
}

def generate_histogram(data, election_type):
    unique_values, counts = np.unique(data, return_counts=True)

    plt.bar(unique_values, counts, align='center', alpha=0.7, width=0.8)

    plt.xticks(np.arange(min(unique_values), max(unique_values)+1, 1))  # Set x-axis ticks at distinct whole numbers
    plt.xlabel('Number of Elected POC Candidates')
    plt.ylabel('Frequency')
    plt.title('Histogram for ' + ballot_generators[election_type] + ' model ')
    plt.show()