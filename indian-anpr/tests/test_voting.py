from services.result_voting import TemporalVotingManager


def test_temporal_voting_majority():
    voter = TemporalVotingManager(required_votes=3, timeout_seconds=5.0)
    track_id = 101

    voter.add_observation(track_id, "MH47BP8265", 0.90)
    plate, _ = voter.get_confirmed_plate(track_id)
    assert plate is None

    voter.add_observation(track_id, "MH47BP8265", 0.92)
    plate, _ = voter.get_confirmed_plate(track_id)
    assert plate is None

    voter.add_observation(track_id, "MH47BP8268", 0.70)
    plate, _ = voter.get_confirmed_plate(track_id)
    assert plate is None

    voter.add_observation(track_id, "MH47BP8265", 0.95)
    plate, conf = voter.get_confirmed_plate(track_id)
    assert plate == "MH47BP8265"
    assert conf > 0.90
