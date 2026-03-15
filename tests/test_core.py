import logging
from pathlib import Path

import pydantic
import pytest
from inline_snapshot import snapshot

from joblib_typed_cache import Memory

if pydantic.__version__ >= "2.0":  # pragma: no cover
    validate_call = pydantic.validate_call()
else:  # pragma: no cover
    validate_call = pydantic.validate_arguments(config={"validate_return": False})


@pytest.fixture(scope="function", name="memory")
def _memory(tmp_path: Path) -> Memory:
    """Typed Joblib Memory object with valid file system backend."""
    return Memory(location=str(tmp_path / ".cache"), verbose=0)


def dummy(a: int = 1, note: str = "") -> bool:
    """Dummy function to cache."""
    logging.info(note)
    return True


class TestMemory:
    def test_cache_is_recomputed_on_force(
        self, memory: Memory, caplog: pytest.LogCaptureFixture
    ):
        """The original cache functionality is not impacted."""

        my_cache = memory.cache(ignore=["note"])  # Two steps to cover all branches
        cached_func = my_cache(dummy)

        with caplog.at_level(logging.INFO):
            cached_func(note="1")  # Start
            cached_func(note="2")
            cached_func.clear()  # Reset
            cached_func(note="3")
            cached_func.uncached(note="4")  # No reset
            cached_func(note="5")
            cached_func(2, note="6")  # Add cache
            cached_func(note="7")
            cached_func(2, note="8")
            cached_func(note="9")

        assert caplog.messages == snapshot(["1", "3", "4", "6"])

    def test_cache_passes_pydantic_validation_on_valid_input(
        self, memory: Memory, caplog: pytest.LogCaptureFixture
    ):
        """Regression test of the main idea."""

        cached_func = memory.cache(dummy, ignore=["note"])
        validated_cached_func = validate_call(cached_func)

        with caplog.at_level(logging.INFO):
            validated_cached_func(note="1")
            validated_cached_func(note="2")

        assert caplog.messages == snapshot(["1"])

    def test_cache_fails_pydantic_validation_on_invalid_input(self, memory: Memory):
        """Make sure that proper validation occurs."""

        cached_func = memory.cache(dummy, ignore=["note"])
        validated_cached_func = validate_call(cached_func)

        with pytest.raises(pydantic.ValidationError):
            validated_cached_func("wrong type")  # type: ignore

    def test_cache_preservers_docstring(self, memory: Memory):
        """The wrapping-operation should preserve the docstring."""

        non_decorated_func = memory.cache(dummy)

        @memory.cache
        def decorated_func() -> None:  # pragma: no cover
            """Docstring of decorated_func."""
            pass

        assert non_decorated_func.__doc__ == snapshot("Dummy function to cache.")
        assert decorated_func.__doc__ == snapshot("Docstring of decorated_func.")

    def test_cache_handles_partial_initialization(self, memory: Memory):
        """The cache can be initialized partially repeatedly."""

        partial_cache_0 = memory.cache(ignore=["arg_0"])
        partial_cache_1 = partial_cache_0(ignore=["arg_1"])
        partial_cache_2 = partial_cache_1()
        partial_cache_3 = partial_cache_2(ignore=[])

        func_0 = partial_cache_0(dummy)
        func_1 = partial_cache_1(dummy)
        func_2 = partial_cache_2(dummy)
        func_3 = partial_cache_3(dummy)

        @partial_cache_0
        def decorated_func_0(arg_0: int) -> None:  # pragma: no cover
            pass

        @partial_cache_1(ignore=["arg"])
        def decorated_func_1(arg: int) -> None:  # pragma: no cover
            pass

        assert func_0.cache.ignore == snapshot(["arg_0"])
        assert func_1.cache.ignore == snapshot(["arg_1"])
        assert func_2.cache.ignore == snapshot(["arg_1"])
        assert func_3.cache.ignore == snapshot([])
        assert decorated_func_0.cache.ignore == snapshot(["arg_0"])
        assert decorated_func_1.cache.ignore == snapshot(["arg"])
