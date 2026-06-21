import pytest

from modules.neuro_symbolic import (
    ParameterSampler,
    ParameterSamplingError,
    SolverExecutor,
)


def test_integer_range_is_respected() -> None:
    sampler = ParameterSampler()
    schema = {
        "type": "object",
        "properties": {
            "n": {"type": "integer", "min": 2, "max": 4},
        },
        "required": ["n"],
    }

    values = [
        sampler.sample_from_schema(schema, seed=seed)["n"]
        for seed in range(20)
    ]

    assert all(2 <= value <= 4 for value in values)


def test_exclude_is_respected() -> None:
    sampler = ParameterSampler()
    schema = {
        "type": "object",
        "properties": {
            "a": {"type": "integer", "minimum": -1, "maximum": 1, "exclude": [0]},
            "b": {"type": "integer", "minimum": -1, "maximum": 1, "not": 0},
        },
        "required": ["a", "b"],
    }

    values = [
        sampler.sample_from_schema(schema, seed=seed)
        for seed in range(20)
    ]

    assert all(params["a"] != 0 for params in values)
    assert all(params["b"] != 0 for params in values)


def test_choice_is_sampled_from_choices() -> None:
    sampler = ParameterSampler()
    schema = {
        "type": "object",
        "properties": {
            "numer_type": {
                "type": "choice",
                "choices": ["sin_x", "exp_minus_1"],
            },
        },
        "required": ["numer_type"],
    }

    params = sampler.sample_from_schema(schema, seed=4)

    assert params["numer_type"] in {"sin_x", "exp_minus_1"}


def test_default_is_used_when_fixed_range_or_schema_requires_it() -> None:
    sampler = ParameterSampler()
    schema = {
        "type": "object",
        "properties": {
            "fixed": {"type": "integer", "min": 3, "max": 3},
            "coefficient": {"type": "integer", "default": 7},
        },
        "required": ["fixed", "coefficient"],
    }

    params = sampler.sample_from_schema(schema, seed=99)

    assert params == {
        "fixed": 3,
        "coefficient": 7,
    }


def test_seed_makes_sampling_deterministic() -> None:
    sampler = ParameterSampler()
    schema = {
        "type": "object",
        "properties": {
            "n": {"type": "integer", "minimum": 1, "maximum": 10},
            "kind": {"choices": ["alpha", "beta", "gamma"]},
        },
        "required": ["n", "kind"],
    }

    assert sampler.sample_from_schema(schema, seed=123) == sampler.sample_from_schema(
        schema,
        seed=123,
    )


def test_sampled_params_execute_builtin_solver_without_error() -> None:
    sampler = ParameterSampler(seed=12)
    executor = SolverExecutor()

    params = sampler.sample_for_solver("INT_XN_EXP")
    result = executor.execute("INT_XN_EXP", params)

    assert params["a"] != 0
    assert result.success is True
    assert result.output is not None


def test_sample_result_reports_attempt_count() -> None:
    sampler = ParameterSampler(seed=3)

    result = sampler.sample_result_for_solver("DET_2X2")

    assert result.solver_code == "DET_2X2"
    assert result.attempts == 1
    assert set(result.params) == {"a11", "a12", "a21", "a22"}


def test_exhausted_exclude_rules_raise_clear_error() -> None:
    sampler = ParameterSampler()
    schema = {
        "type": "object",
        "properties": {
            "n": {
                "type": "integer",
                "minimum": 1,
                "maximum": 2,
                "exclude": [1, 2],
            },
        },
    }

    with pytest.raises(ParameterSamplingError, match="no values"):
        sampler.sample_from_schema(schema)
