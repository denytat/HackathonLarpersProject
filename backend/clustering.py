
import networkx as nx
from itertools import combinations


def build_swarm_graph(
    text_matches,
    timing_bursts,
    account_matches,
    min_signals=2
):
    """
    Build a graph connecting accounts using three detection signals.

    An edge is created only when at least min_signals
    independent signals support the account pair.
    """

    graph = nx.Graph()

    # Store evidence for each account pair
    pair_evidence = {}

    def get_pair(account_a, account_b):
        return tuple(sorted((account_a, account_b)))

    def add_evidence(account_a, account_b, signal, score):
        if account_a == account_b:
            return

        pair = get_pair(account_a, account_b)

        if pair not in pair_evidence:
            pair_evidence[pair] = {}

        # Keep the strongest score for each signal
        previous = pair_evidence[pair].get(signal, 0)

        pair_evidence[pair][signal] = max(previous, score)

    # 1. Text similarity evidence
    for match in text_matches:
        add_evidence(
            match["account_1"],
            match["account_2"],
            "text_similarity",
            float(match["similarity"])
        )

    # 2. Timing burst evidence
    for burst in timing_bursts:
        accounts = sorted(set(burst["accounts"]))

        for account_a, account_b in combinations(accounts, 2):
            add_evidence(
                account_a,
                account_b,
                "timing_burst",
                1.0
            )

    # 3. Account behaviour evidence
    for match in account_matches:
        add_evidence(
            match["account_1"],
            match["account_2"],
            "account_similarity",
            float(match["similarity"])
        )

    # Add only pairs supported by enough independent signals
    weights = {
        "text_similarity": 0.40,
        "timing_burst": 0.30,
        "account_similarity": 0.30
    }

    for (account_a, account_b), evidence in pair_evidence.items():

        if len(evidence) < min_signals:
            continue

        score = sum(
            evidence[signal] * weights[signal]
            for signal in evidence
        )

        graph.add_edge(
            account_a,
            account_b,
            score=round(score, 3),
            evidence=evidence
        )

    return graph


def find_swarms(graph, min_accounts=3):
    """
    Find connected groups of accounts and calculate
    an average connection score for each group.
    """

    swarms = []

    components = sorted(
        nx.connected_components(graph),
        key=lambda component: (-len(component), sorted(component))
    )

    for component in components:

        if len(component) < min_accounts:
            continue

        subgraph = graph.subgraph(component)

        edge_scores = [
            data["score"]
            for _, _, data in subgraph.edges(data=True)
        ]

        average_score = (
            sum(edge_scores) / len(edge_scores)
            if edge_scores else 0
        )

        evidence = []

        for account_a, account_b, data in subgraph.edges(data=True):
            evidence.append({
                "account_1": account_a,
                "account_2": account_b,
                "score": data["score"],
                "signals": data["evidence"]
            })

        swarms.append({
            "id": f"swarm_{len(swarms) + 1}",
            "accounts": sorted(component),
            "score": round(average_score, 3),
            "evidence": evidence
        })

    return swarms


def detect_swarms(
    text_matches,
    timing_bursts,
    account_matches,
    min_signals=2,
    min_accounts=3
):
    """Complete graph clustering process."""

    graph = build_swarm_graph(
        text_matches,
        timing_bursts,
        account_matches,
        min_signals=min_signals
    )

    return find_swarms(
        graph,
        min_accounts=min_accounts
    )
