import numpy as np
import itertools
import random
from votekit import Ballot, PreferenceProfile
from fractions import Fraction


W = "W"  # Majority bloc - Republicans
POC = "C"  # Minority bloc - Democrats


class BradleyTerry:

    @classmethod
    def from_params(
        cls, slate_to_candidates=dict, bloc_voter_prop=dict, cohesion=dict, alphas=dict
    ):
        cls.minority_share = bloc_voter_prop[POC]
        cls.poc_for_poc = cohesion[POC]
        cls.poc_for_w = 1 - cohesion[POC]
        cls.w_for_w = cohesion[W]
        cls.w_for_poc = 1 - cohesion[W]
        cls.alphas = [alphas[POC][POC], alphas[POC][W], alphas[W][POC], alphas[W][W]]
        cls.num_poc = len(slate_to_candidates[POC])
        cls.num_w = len(slate_to_candidates[W])

        return cls

    @classmethod
    def generate_profile(cls, num_ballots):
        ballot_lst = []
        weights = {}
        for ranking in bradley_terry_dirichlet(
            poc_share=cls.minority_share,
            poc_support_for_poc_candidates=cls.poc_for_poc,
            poc_support_for_white_candidates=cls.poc_for_w,
            white_support_for_white_candidates=cls.w_for_w,
            white_support_for_poc_candidates=cls.w_for_poc,
            num_ballots=num_ballots,
            num_poc_candidates=cls.num_poc,
            num_white_candidates=cls.num_w,
            concentrations=cls.alphas,
            max_ballot_length=None,
        ):
            if tuple(ranking) not in weights:
                weights[tuple(ranking)] = 0
            weights[tuple(ranking)] += 1

        for ballot, weight in weights.items():
            ballot_lst.append(make_ballot(ballot, weight=weight))

        return PreferenceProfile(ballots=ballot_lst)


def make_ballot(ranking, weight):
    ballot_rank = []
    for cand in ranking:
        ballot_rank.append({cand})

    return Ballot(ranking=ballot_rank, weight=Fraction(weight))


def bradley_terry_dirichlet(
    poc_share=0.33,
    poc_support_for_poc_candidates=0.7,
    poc_support_for_white_candidates=0.3,
    white_support_for_white_candidates=0.8,
    white_support_for_poc_candidates=0.2,
    num_ballots=1000,
    num_poc_candidates=2,
    num_white_candidates=3,
    concentrations=[1.0, 1.0, 1.0, 1.0],  # poc_for_poc, poc_for_w, w_for_poc, w_for_w
    max_ballot_length=None,
):
    if max_ballot_length == None:
        max_ballot_length = num_poc_candidates + num_white_candidates
    num_candidates = [num_poc_candidates, num_white_candidates]
    alphas = concentrations
    candidates = ["D" + str(x) for x in range(num_poc_candidates)] + [
        "R" + str(x) for x in range(num_white_candidates)
    ]
    race_of_candidate = {x: x[0] for x in candidates}

    # simulate
    poc_elected = []
    poc_elected_atlarge = []
    # for n in range(num_simulations):
    # get support vectors
    noise0 = list(np.random.dirichlet([alphas[0]] * num_candidates[0])) + list(
        np.random.dirichlet([alphas[1]] * num_candidates[1])
    )
    noise1 = list(np.random.dirichlet([alphas[2]] * num_candidates[0])) + list(
        np.random.dirichlet([alphas[3]] * num_candidates[1])
    )
    white_support_vector = []
    poc_support_vector = []
    for i, (c, r) in enumerate(race_of_candidate.items()):
        if r == "D":
            white_support_vector.append((white_support_for_poc_candidates * noise1[i]))
            poc_support_vector.append((poc_support_for_poc_candidates * noise0[i]))
        elif r == "R":
            white_support_vector.append(
                (white_support_for_white_candidates * noise1[i])
            )
            poc_support_vector.append((poc_support_for_white_candidates * noise0[i]))

    ballots = []
    numballots = num_ballots
    ballots = paired_comparison_mcmc(
        num_ballots,
        {
            0: {x: poc_support_vector[i] for i, x in enumerate(candidates)},
            1: {x: white_support_vector[i] for i, x in enumerate(candidates)},
        },
        None,
        candidates,
        {0: poc_share, 1: 1 - poc_share},
        [0, 1],
        sample_interval=10,
        verbose=False,
    )
    # winners
    ballots = [b[:max_ballot_length] for b in ballots]
    # winners = cw.rcv_run(ballots.copy(), candidates, seats_open, cincinnati_transfer)
    # poc_elected.append(len([w for w in winners if w[0]=='A']))
    # atlargewinners = cw.at_large_run(ballots.copy(),candidates,seats_open)
    # poc_elected_atlarge.append(len([x for x in atlargewinners if x[0] == 'A']))

    return ballots


def paired_comparison_mcmc(
    num_ballots,
    mean_support_by_race,
    std_support_by_race,
    cand_list,
    vote_portion_by_race,
    race_list,
    seeds=None,
    sample_interval=10,
    verbose=True,
):
    # Sample from probability distribution for each race using MCMC - don't explicitly
    # compute probability of each ballot in advance
    # Draw from each race's prob distribution (number of ballots per race dtmd by cvap share)
    ordered_cand_pairs = list(itertools.permutations(cand_list, 2))
    ballots_list = []

    for race in race_list:
        # make dictionairy of paired comparisons: i.e. prob i>j for all ordered pairs of candidates
        # keys are ordered pair of candidates, values are prob i>j in pair of candidates
        paired_compare_dict = {
            k: mean_support_by_race[race][k[0]]
            / (mean_support_by_race[race][k[0]] + mean_support_by_race[race][k[1]])
            for k in ordered_cand_pairs
        }
        # starting ballot for mcmc
        start_ballot = list(np.random.permutation(cand_list))
        # function for evaluating single ballot in MCMC
        # don't need normalization term here! Exact probability of a particular ballot would be
        # output of this fnction divided by normalization term that MCMC allows us to avoid
        track_ballot_prob = []

        def ballot_prob(ballot):
            pairs_list_ballot = list(itertools.combinations(ballot, 2))
            paired_compare_trunc = {
                k: paired_compare_dict[k] for k in pairs_list_ballot
            }
            ballot_prob = np.product(list(paired_compare_trunc.values()))
            return ballot_prob

        # start MCMC with 'start_ballot'
        num_ballots_race = int(num_ballots * vote_portion_by_race[race])
        race_ballot_list = []
        step = 0
        accept = 0
        while len(race_ballot_list) < num_ballots_race:  # range(num_ballots_race):
            # proposed new ballot is a random switch of two elements in ballot before
            proposed_ballot = start_ballot.copy()
            j1, j2 = random.sample(range(len(start_ballot)), 2)
            proposed_ballot[j1], proposed_ballot[j2] = (
                proposed_ballot[j2],
                proposed_ballot[j1],
            )

            # acceptance ratio: (note - symmetric proposal function!)
            accept_ratio = min(
                ballot_prob(proposed_ballot) / ballot_prob(start_ballot), 1
            )
            # accept or reject proposal
            if random.random() < accept_ratio:
                start_ballot = proposed_ballot
                if step % sample_interval == 0:
                    race_ballot_list.append(start_ballot)
                accept += 1
            else:
                if step % sample_interval == 0:
                    race_ballot_list.append(start_ballot)
            step += 1
        ballots_list = ballots_list + race_ballot_list
        if verbose:
            if step > 0:
                print("Acceptance ratio for {} voters: ".format(race), accept / step)
    # plt.plot(track_ballot_prob)
    return ballots_list
