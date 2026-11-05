"""Tests for scoring/src/build_trial_table.py.

The normalized error walk is the part worth testing: answers are scalars, flat lists,
lists of pairs and dicts keyed by quantity name, and the tolerance mirrors each shape.

    python -m pytest tests/test_trial_table.py
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scoring" / "src"))

from build_trial_table import (  # noqa: E402
    count_leaves,
    normalized_error,
    read_usage,
    split_task_name,
    _value_from_json_text,
)


# --- task names -------------------------------------------------------------

@pytest.mark.parametrize("task_name,paper,task", [
    ("replicationbench/replicationbench__gw_cosmo__dark_energy", "gw_cosmo", "dark_energy"),
    # Paper ids and task ids both contain single underscores.
    ("replicationbench/replicationbench__trgb_std_candle__fit_aseq_bseq",
     "trgb_std_candle", "fit_aseq_bseq"),
    ("replicationbench/replicationbench__MUSE_outflows__dust_reddening",
     "MUSE_outflows", "dust_reddening"),
    ("replicationbench/replicationbench__hubble_trails__satellite_chance_post2020_acis",
     "hubble_trails", "satellite_chance_post2020_acis"),
])
def test_split_task_name(task_name, paper, task):
    assert split_task_name(task_name) == (paper, task)


def test_split_task_name_rejects_junk():
    assert split_task_name("not-a-harbor-task") == (None, None)
    assert split_task_name(None) == (None, None)


# --- normalized error, scalars ---------------------------------------------

def test_scalar_exact_match_is_zero():
    error, vector, note = normalized_error(0.05, 0.05, 0.01)
    assert (error, vector, note) == (0.0, [0.0], None)


def test_scalar_half_a_tolerance():
    error, _, note = normalized_error(0.055, 0.05, 0.01)
    assert note is None
    assert error == pytest.approx(0.5)


def test_scalar_at_the_tolerance_is_one():
    """The pass boundary: normalized_error <= 1 must mean the same as passing."""
    error, _, _ = normalized_error(0.06, 0.05, 0.01)
    assert error == pytest.approx(1.0)


def test_scalar_outside_tolerance_exceeds_one():
    error, _, _ = normalized_error(0.08, 0.05, 0.01)
    assert error > 1


def test_sign_does_not_matter():
    """Direction of the miss is irrelevant; only the distance counts.

    Compared with a tolerance because a ratio at the boundary carries float noise:
    see the boundary note in scoring/schema/trial-table.md.
    """
    low, _, _ = normalized_error(0.04, 0.05, 0.01)
    high, _, _ = normalized_error(0.06, 0.05, 0.01)
    assert low == pytest.approx(high)


# --- normalized error, lists ------------------------------------------------

def test_flat_list_takes_the_worst_element():
    """gw_nsbh-style [lower, median, upper] with a per-element tolerance."""
    error, vector, note = normalized_error([1.0, 2.0, 3.0], [1.0, 2.0, 3.6], [0.5, 0.5, 0.3])
    assert note is None
    assert vector == pytest.approx([0.0, 0.0, 2.0])
    assert error == pytest.approx(2.0)


def test_scalar_tolerance_broadcasts_over_a_list():
    error, vector, note = normalized_error([1.0, 2.0], [1.0, 2.2], 0.1)
    assert note is None
    assert vector == pytest.approx([0.0, 2.0])
    assert error == pytest.approx(2.0)


def test_nested_list_of_pairs():
    """eht_resolve returns [[value, uncertainty], ...] with a matching tolerance."""
    error, vector, note = normalized_error(
        [[44.1, 1.2], [44.0, 1.5]],
        [[44.1, 1.2], [44.0, 1.2]],
        [[2.0, 0.3], [2.0, 0.3]],
    )
    assert note is None
    assert vector == pytest.approx([0.0, 0.0, 0.0, 1.0])
    assert error == pytest.approx(1.0)


def test_list_length_mismatch_is_reported_not_scored():
    error, vector, note = normalized_error([1.0, 2.0], [1.0, 2.0, 3.0], [0.1, 0.1, 0.1])
    assert (error, vector) == (None, None)
    assert "length_mismatch" in note


# --- normalized error, dicts ------------------------------------------------

def test_dict_keyed_by_quantity_name():
    """astm3 and MUSE_outflows answers are dicts, not lists."""
    error, vector, note = normalized_error(
        {"photometry_only": 91.25, "all_modalities": 99.0},
        {"photometry_only": 91.25, "all_modalities": 100.0},
        {"photometry_only": 1, "all_modalities": 1},
    )
    assert note is None
    assert sorted(vector) == pytest.approx([0.0, 1.0])
    assert error == pytest.approx(1.0)


def test_dict_of_lists():
    error, _, note = normalized_error(
        {"ne_narrow": [300, 100]}, {"ne_narrow": [300, 150]}, {"ne_narrow": [50, 50]},
    )
    assert note is None
    assert error == pytest.approx(1.0)


def test_missing_dict_key_is_reported():
    error, _, note = normalized_error({"a": 1.0}, {"a": 1.0, "b": 2.0}, {"a": 0.1, "b": 0.1})
    assert error is None
    assert "missing_keys" in note


def test_wrong_shape_is_reported():
    error, _, note = normalized_error(1.0, [1.0, 2.0], [0.1, 0.1])
    assert error is None
    assert "shape_mismatch" in note


# --- zero tolerance ---------------------------------------------------------

def test_zero_tolerance_exact_match_is_zero():
    """ver_waves__gaia_rv_sample_size has tolerance 0: the count must match exactly."""
    error, vector, note = normalized_error(864268, 864268, 0)
    assert (error, vector, note) == (0.0, [0.0], None)


def test_zero_tolerance_any_miss_is_infinite():
    error, _, note = normalized_error(864269, 864268, 0)
    assert note is None
    assert error == float("inf")


def test_zero_tolerance_inside_a_list():
    """galaxy_soptics mixes real tolerances with exact-match integers."""
    error, vector, note = normalized_error(
        [1.8, 6, 0.8], [1.8, 5, 0.8], [0.2, 0, 0.1],
    )
    assert note is None
    assert vector[1] == float("inf")
    assert error == float("inf")


# --- missing inputs ---------------------------------------------------------

def test_missing_reported_value_is_not_scored_as_zero():
    """A trial whose answer was not retained must not look like a perfect answer."""
    assert normalized_error(None, 0.05, 0.01) == (None, None, "value_missing")


def test_missing_task_definition_is_not_scored():
    error, _, note = normalized_error(0.05, None, None)
    assert error is None
    assert note == "no_expected_or_tolerance"


def test_non_numeric_reported_value_is_reported():
    error, _, note = normalized_error("about 0.05", 0.05, 0.01)
    assert error is None
    assert "non_numeric" in note


# --- leaf counts ------------------------------------------------------------

@pytest.mark.parametrize("expected,leaves", [
    (0.05, 1),
    ([1.0, 2.0, 3.0], 3),
    ([[44.1, 1.2], [44.0, 1.2]], 4),
    ({"a": 1.0, "b": [1.0, 2.0]}, 3),
])
def test_count_leaves(expected, leaves):
    assert count_leaves(expected) == leaves


# --- reported value extraction ---------------------------------------------

def test_value_from_oracle_stdout():
    text = 'Oracle solution complete. Result written to /app/result.json\n{\n  "value": 0.05\n}\n'
    assert _value_from_json_text(text) == 0.05


def test_value_from_stdout_with_a_list():
    text = 'noise\n{\n  "value": [\n    -1.68,\n    0.71\n  ]\n}\n'
    assert _value_from_json_text(text) == [-1.68, 0.71]


def test_last_value_wins_when_an_agent_prints_twice():
    assert _value_from_json_text('{"value": 1}\nthinking\n{"value": 2}') == 2


def test_no_value_in_stdout():
    assert _value_from_json_text("I could not finish the task.") is None


def test_json_without_a_value_key_is_ignored():
    assert _value_from_json_text('{"status": "done"}') is None


# --- tokens and cost --------------------------------------------------------

def test_usage_from_agent_result():
    usage = read_usage({
        "n_input_tokens": 100, "n_cache_tokens": 20, "n_output_tokens": 5, "cost_usd": 0.01,
    })
    assert usage["n_total_tokens"] == 105
    assert usage["cost_usd"] == 0.01


def test_cache_is_not_counted_twice_in_the_total():
    """Harbor's n_input_tokens includes cache; n_cache_tokens is a subset of it."""
    usage = read_usage({
        "n_input_tokens": 1000, "n_cache_tokens": 900, "n_output_tokens": 50, "cost_usd": 0.1,
    })
    assert usage["n_total_tokens"] == 1050


def test_value_scan_is_fast_on_a_large_log():
    import time
    text = ('{"type": "assistant", "message": {"content": "x"}}\n' * 20000) + '{"value": 3.5}\n'
    began = time.time()
    assert _value_from_json_text(text) == 3.5
    assert time.time() - began < 5


def test_nested_value_object_returns_the_outer_value():
    assert _value_from_json_text('log {"value": {"a": 1}} end') == {"a": 1}


def test_usage_is_null_for_the_oracle():
    """Every agent_result field is null in the oracle job; nothing may become 0."""
    usage = read_usage({
        "n_input_tokens": None, "n_cache_tokens": None,
        "n_output_tokens": None, "cost_usd": None, "model_usage": None,
    })
    assert usage["n_total_tokens"] is None
    assert usage["cost_usd"] is None


def test_usage_falls_back_to_model_usage():
    """Some agents report per model totals instead of the top-level fields."""
    usage = read_usage({
        "n_input_tokens": None, "n_cache_tokens": None, "n_output_tokens": None,
        "cost_usd": None,
        "model_usage": {
            "model-a": {"input_tokens": 10, "output_tokens": 2, "cost": 0.001},
            "model-b": {"input_tokens": 5, "output_tokens": 1, "cost": 0.002},
        },
    })
    assert usage["n_input_tokens"] == 15
    assert usage["n_output_tokens"] == 3
    assert usage["cost_usd"] == pytest.approx(0.003)
    assert usage["n_total_tokens"] == 18


def test_top_level_usage_wins_over_model_usage():
    usage = read_usage({
        "n_input_tokens": 100, "n_cache_tokens": None, "n_output_tokens": None,
        "cost_usd": None, "model_usage": {"m": {"input_tokens": 1, "output_tokens": 7}},
    })
    assert usage["n_input_tokens"] == 100
    assert usage["n_output_tokens"] == 7


# --- caps -------------------------------------------------------------------

from build_trial_table import _confidence_from_markdown, apply_caps


def test_under_the_token_cap_passes_within_cap():
    caps = apply_caps({"n_total_tokens": 4_999_999}, None, True)
    assert (caps["capped_tokens"], caps["capped"], caps["passed_within_cap"]) == (False, False, True)


def test_over_the_token_cap_cannot_pass_within_cap():
    caps = apply_caps({"n_total_tokens": 5_000_001}, None, True)
    assert (caps["capped_tokens"], caps["capped"], caps["passed_within_cap"]) == (True, True, False)


def test_exactly_at_the_cap_is_not_capped():
    assert apply_caps({"n_total_tokens": 5_000_000}, None, True)["capped_tokens"] is False


def test_time_limit_marks_capped():
    caps = apply_caps({"n_total_tokens": 10}, "AgentTimeoutError", False)
    assert (caps["capped_time"], caps["capped"], caps["passed_within_cap"]) == (True, True, False)


def test_unknown_tokens_leave_a_pass_unscored():
    caps = apply_caps({"n_total_tokens": None}, None, True)
    assert caps["capped_tokens"] is None
    assert caps["passed_within_cap"] is None


def test_a_failure_is_false_within_cap_even_without_tokens():
    assert apply_caps({"n_total_tokens": None}, None, False)["passed_within_cap"] is False


def test_custom_cap():
    assert apply_caps({"n_total_tokens": 200}, None, True, token_cap=100)["capped_tokens"] is True


# --- confidence from report.md ----------------------------------------------

@pytest.mark.parametrize("text, value", [
    ("3. Confidence: 0.8\n", 0.8),
    ("**Confidence:** 0.65 (the fit converged)", 0.65),
    ("## Confidence\n\n0.9\n", 0.9),
    ("Confidence: 75%", 0.75),
    ("3. Confidence: .4", 0.4),
    ("Method: 3 steps\nConfidence: 1", 1.0),
    ("3. Confidence (0 to 1): 0.7", 0.7),
    ("Confidence, a number from 0 to 1: 0.35", 0.35),
    ("Confidence [0-1]: 0.2", 0.2),
])
def test_confidence_from_markdown(text, value):
    assert _confidence_from_markdown(text) == (pytest.approx(value), None)


def test_confidence_above_one_is_rejected():
    assert _confidence_from_markdown("Confidence: 8") == (None, "confidence_out_of_range")


def test_confidence_without_a_number():
    assert _confidence_from_markdown("Confidence: high") == (None, "confidence_not_numeric")


def test_report_without_confidence():
    assert _confidence_from_markdown("Method: fit\nResult: 70") == (None, "confidence_missing")
