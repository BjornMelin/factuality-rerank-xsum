from factuality_rerank_xsum.scorers.entity_support import score_entity_support


def test_entity_support_penalizes_number_distortion() -> None:
    source = "Alice won 3 awards in London on 12 May 2025."
    faithful = "Alice won 3 awards in London on 12 May 2025."
    distorted = "Alice won 5 awards in Paris on 12 May 2025."

    faithful_score = score_entity_support(source, faithful)
    distorted_score = score_entity_support(source, distorted)

    assert faithful_score["entity_support_score"] > distorted_score["entity_support_score"]
    assert len(distorted_score["unsupported_numbers"]) == 1
    assert len(distorted_score["unsupported_entities"]) >= 1
