from votekit.elections import STV, fractional_transfer
from votekit import CambridgeSampler
#from utils import BradleyTerry ## import BradleyTerry from here not votekit
import random
from votekit.graphs import PairwiseComparisonGraph
import numpy as np
import votekit.ballot_generator as bg
from votekit.ballot_generator import SlatePreference
import json
import os

ballot_generators = {
    #"bt": BradleyTerry,
    #"pl": PlackettLuce,
    #"cs": CambridgeSampler,
    "sp": SlatePreference
}

candidates_to_select = {
    "WP": ["WP1", "WP2", "WP3", "WP4", "WP5", "WP6", "WP7", "WP8", "WP9", "WP10"],
    "WC": ["WC1", "WC2", "WC3", "WC4", "WC5", "WC6", "WC7", "WC8", "WC9", "WC10"],
    "C": ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10"],
}

def simulate_ensembles(
    #ensemble: list,
    #election: str,
    cohesion: dict,
    seats: int,
    num_elections: int,
    alphas: dict,
    candidates: list,
    num_ballots: int = 1000,
    low_turnout: bool = False,
    alternate_slate: callable = None,
    
):
    """
    Runs simulation of RCV elections of an ensemble of plans
    """
    
    plan_results = []
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)

    # Portland blocks and coorsponding white VAP
    zone_shares = {1:0.568, 2:0.683, 3:0.744, 4:0.764}

    # Interate across the 4 Portland blocks
    for idx, share in enumerate(zone_shares):
        zone_data = {}
        zone_data["zone"] = idx
        zone_data["voter_share"] = share
        # build hyperparams base on share and other toggles
        # based on the voter file
        blocs = {"C": 0.15, "WP": 0.79, "WC": 0.06}
        cand_slate = {
            "WP": candidates_to_select["WP"][:candidates[1]],  
            "WC": candidates_to_select["WC"][:candidates[2]],  
            "C": candidates_to_select["C"][:candidates[0]],   
        }
        # loop through number of simulated RCV elections
        for _ in range(num_elections):
            for model_name, model in ballot_generators.items():
                data = {
                    'bloc_voter_prop': blocs,
                    'cohesion_parameters': cohesion,
                    'alphas': alphas,
                    'slate_to_candidates':cand_slate
                }

                generator = model.from_params(**data)
                #print("Preference Intervals:", generator.pref_intervals_by_bloc)

                ballots = generator.generate_profile(num_ballots)

                #ballots.to_csv(current_dir + '/ballots.csv')

                results = STV(
                    ballots,
                    transfer=fractional_transfer,
                    seats=seats,
                    quota = "droop", # Added from chris' code
                    ballot_ties=False,
                    tiebreak = "random", # Added from chris' code
                ).run_election()

                num_winners = count_winners(results.winners(), "C")

                if model_name not in zone_data:
                    zone_data[model_name] = []
                zone_data[model_name].append(num_winners)
        plan_results.append(zone_data)

    #print(f"Plan Results {idx + 1}", plan_results)
    #print("Results across zones", condense_results(plan_results))
    #print(plan_results)

    return(plan_results), condense_results(plan_results)

def condense_results (plan_results):
    election_results = {}
    
    for election_type in ballot_generators:
        summed_zone_results = []
        for item in plan_results:
            zone = item['zone']
            win_list = item[election_type]

            if len(summed_zone_results) == 0:
                summed_zone_results = win_list
            else: 
                summed_zone_results = np.add(summed_zone_results, win_list)
        election_results[election_type] = summed_zone_results

    return election_results


def count_winners(elected: list[set], party: str) -> int:
    """
    Counts number of elected candidates from the inputted party.
    """
    winner_count = 0

    for winner_set in elected:
        for cand in winner_set:
            if cand[0] == party:
                winner_count += 1

    return winner_count

def convert_tuples_in_keys(obj):
    """Recursively convert tuples in dictionary keys to strings."""
    if isinstance(obj, dict):
        return {str(key): convert_tuples_in_keys(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_tuples_in_keys(element) for element in obj]
    elif isinstance(obj, tuple):
        return str(obj) 
    else:
        return obj 


def slate_by_share(vote_share: float) -> dict:
    pass