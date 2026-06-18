"""Pipeline + curation tests. The LLM is stood in for by a deterministic fake,
so the parse/stamp/promote machinery is exercised without any API key — which is
exactly the QC-over-unreliable-output story, made testable."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from argkit.curate import CurationDecision, apply_decisions, review_queue
from argkit.pipeline import (
    expand_candidates,
    parse_json_candidates,
    reconcile_cross_check,
)
from argkit.schema import CurationStatus
from _builders import make_arg, make_graph

_TS = datetime(2026, 6, 18, tzinfo=timezone.utc)


class FakeClient:
    model_name = "fake-model"

    def __init__(self, response: str) -> None:
        self._response = response

    def complete(self, prompt: str) -> str:  # noqa: ARG002 - prompt unused by the fake
        return self._response


def test_parse_json_candidates_extracts_array():
    raw = 'Here you go:\n[{"title": "X"}, {"title": "Y"}]\nThanks!'
    assert parse_json_candidates(raw) == [{"title": "X"}, {"title": "Y"}]


def test_parse_json_candidates_raises_on_garbage():
    with pytest.raises(ValueError):
        parse_json_candidates("no array here")


def test_expand_candidates_stamps_candidate_provenance():
    client = FakeClient('[{"title": "A1", "stance": "pro", "confidence": 0.6}]')
    out = expand_candidates(client, "root claim", now=_TS)
    assert len(out) == 1
    prov = out[0]["provenance"]
    assert prov["generator_model"] == "fake-model"
    assert prov["status"] == CurationStatus.CANDIDATE.value
    assert prov["prompt_sha256"]  # fingerprint present


def test_reconcile_cross_check_only_agreement_promotes():
    assert reconcile_cross_check(True, True) == CurationStatus.CROSS_CHECKED
    assert reconcile_cross_check(True, False) == CurationStatus.CANDIDATE
    assert reconcile_cross_check(False, True) == CurationStatus.CANDIDATE
    assert reconcile_cross_check(False, False) == CurationStatus.CANDIDATE


def test_review_queue_lists_uncurated_arguments():
    graph = make_graph(
        arguments=[
            make_arg("A", status=CurationStatus.CURATED_ACCEPTED),
            make_arg("B", status=CurationStatus.CANDIDATE),
            make_arg("C", status=CurationStatus.CROSS_CHECKED),
        ],
        conflicts=[],
    )
    assert set(review_queue(graph)) == {"B", "C"}


def test_apply_decisions_writes_terminal_status_and_note():
    graph = make_graph(
        arguments=[make_arg("B", status=CurationStatus.CROSS_CHECKED)],
        conflicts=[],
    )
    decided = apply_decisions(graph, [CurationDecision(argument_id="B", accept=False,
                                                       note="hallucinated citation")])
    arg = decided.argument("B")
    assert arg.provenance.status == CurationStatus.CURATED_REJECTED
    assert arg.provenance.curator_note == "hallucinated citation"
    assert review_queue(decided) == []
