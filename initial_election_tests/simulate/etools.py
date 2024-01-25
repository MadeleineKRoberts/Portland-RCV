from votekit.elections import STV, fractional_transfer
from votekit import PlackettLuce, CambridgeSampler, AlternatingCrossover
from utils import BradleyTerry ## import BradleyTerry from here not votekit
import random
from votekit.graphs import PairwiseComparisonGraph
import numpy as np

ballot_generators = {
    "bt": BradleyTerry,
    "pl": PlackettLuce,
    "cs": CambridgeSampler,
    #"ac": AlternatingCrossover,
}

candidates = {
    "White": ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9", "W10"],
    "POC": ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10"],
}

direchlets = [
    {"W": {"C": 1, "W": 1}, "C": {"W": 1, "C": 1}},
]


def simulate_ensembles(
    #ensemble: list,
    #election: str,
    cohesion: dict,
    num_w: int,
    num_c: int,
    seats: int,
    num_elections: int,
    alphas: dict,
    num_ballots: int = 1000,
    low_turnout: bool = False,
    alternate_slate: callable = None,
    
):
    """
    Runs simulation of RCV elections of an ensemble of plans
    """

    
    plan_results = []

    # Portland blocks and coorsponding white VAP
    zone_shares = {1:0.568, 2:0.683, 3:0.744, 4:0.764}

    # Interate across the 4 Porland blocks
    for idx, share in enumerate(zone_shares):
        zone_data = {}
        zone_data["zone"] = idx
        zone_data["voter_share"] = share
        # build hyperparams base on share and other toggles
        blocs = {"W": share, "C": 1 - share}
        if low_turnout:
            blocs = {"W": (1 / 3), "C": (2 / 3)}
        # pick direchlets values
        # alphas = random.choice(direchlets)
        #alphas = {"W": {"C": 1, "W": 1}, "C": {"W": 1, "C": 1}}
        cand_slate = {
            # !! idk what this is
            "W": candidates["White"][:num_w],
            "C": candidates["POC"][:num_c],
        }

        # !! NOTE: Ask moon what this should be set to
        # crossover_rates = {"W": {"C": 0.4}, "C": {"W": 0.5}}

        # loop through number of simulated RCV elections
        for _ in range(num_elections):
            for model_name, model in ballot_generators.items():
                #print(model_name)

                """
                if model_name in ['cs', 'ac']:
                    generator = model.from_params(
                        slate_to_candidates=cand_slate,
                        bloc_voter_prop=blocs,
                        cohesion=cohesion,
                        alphas=alphas,
                        #bloc_crossover_rate=crossover_rates,
                    )
                else:
                    generator = model.from_params(
                        slate_to_candidates=cand_slate,
                        bloc_voter_prop=blocs,
                        cohesion=cohesion,
                        alphas=alphas,
                    )
                """
                #print(model_name)
                #print(cand_slate)
                #print(blocs)
                #print(cohesion)
                #print(alphas)
                generator = model.from_params(
                        slate_to_candidates=cand_slate,
                        bloc_voter_prop=blocs,
                        cohesion=cohesion,
                        alphas=alphas,
                    )

                ballots = generator.generate_profile(num_ballots)

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
            #print(zone_data)
            # condense the winners here and add to overall total list by model    
                

        plan_results.append(zone_data)

    return condense_results(plan_results) 


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


def slate_by_share(vote_share: float) -> dict:
    pass
