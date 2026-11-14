
from backend.clustering import detect_swarms


def test_detects_swarm_with_all_three_signals():
    text_matches = [
        {
            "account_1": "user1",
            "account_2": "user2",
            "similarity": 0.95
        },
        {
            "account_1": "user2",
            "account_2": "user3",
            "similarity": 0.95
        }
    ]

    timing_bursts = [
        {
            "accounts": ["user1", "user2", "user3"]
        }
    ]

    account_matches = [
        {
            "account_1": "user1",
            "account_2": "user2",
            "similarity": 0.95
        },
        {
            "account_1": "user2",
            "account_2": "user3",
            "similarity": 0.95
        }
    ]

    swarms = detect_swarms(
        text_matches,
        timing_bursts,
        account_matches,
        min_signals=2,
        min_accounts=3
    )

    assert len(swarms) == 1
    assert swarms[0]["accounts"] == ["user1", "user2", "user3"]


def test_does_not_detect_swarm_with_only_text_and_timing():
    text_matches = [
        {
            "account_1": "user1",
            "account_2": "user2",
            "similarity": 1.0
        },
        {
            "account_1": "user2",
            "account_2": "user3",
            "similarity": 1.0
        }
    ]

    timing_bursts = [
        {
            "accounts": ["user1", "user2", "user3"]
        }
    ]

    swarms = detect_swarms(
        text_matches,
        timing_bursts,
        [],
        min_signals=2,
        min_accounts=3
    )

    assert swarms == []


def test_does_not_detect_swarm_with_only_one_signal():
    text_matches = [
        {
            "account_1": "user1",
            "account_2": "user2",
            "similarity": 0.95
        },
        {
            "account_1": "user2",
            "account_2": "user3",
            "similarity": 0.95
        }
    ]

    swarms = detect_swarms(
        text_matches,
        [],
        [],
        min_signals=2,
        min_accounts=3
    )

    assert swarms == []

def test_does_not_detect_swarm_from_one_timing_burst_and_account_similarity():
    timing_bursts = [
        {
            "accounts": ["user1", "user2", "user3"]
        }
    ]

    account_matches = [
        {
            "account_1": "user1",
            "account_2": "user2",
            "similarity": 0.95
        },
        {
            "account_1": "user2",
            "account_2": "user3",
            "similarity": 0.95
        }
    ]

    swarms = detect_swarms(
        [],
        timing_bursts,
        account_matches,
        min_signals=2,
        min_accounts=3
    )

    assert swarms == []

def test_detects_swarm_with_text_and_account_similarity():
    text_matches = [
        {
            "account_1": "user1",
            "account_2": "user2",
            "similarity": 0.95
        },
        {
            "account_1": "user2",
            "account_2": "user3",
            "similarity": 0.95
        }
    ]

    account_matches = [
        {
            "account_1": "user1",
            "account_2": "user2",
            "similarity": 0.95
        },
        {
            "account_1": "user2",
            "account_2": "user3",
            "similarity": 0.95
        }
    ]

    swarms = detect_swarms(
        text_matches,
        [],
        account_matches,
        min_signals=2,
        min_accounts=3
    )

    assert len(swarms) == 1
    assert swarms[0]["accounts"] == ["user1", "user2", "user3"]
