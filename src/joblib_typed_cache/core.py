import logging
from collections.abc import Callable, Sequence
from functools import partial, wraps
from typing import Any, Literal, Protocol, Self, cast, overload

import joblib

logger = logging.getLogger(__name__)


class CachedFunc[**P, R](Protocol):
    @property
    def cache(self) -> joblib.memory.MemorizedFunc: ...
    def uncached(self, *args: P.args, **kwargs: P.kwargs) -> R: ...
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...
    def clear(self) -> None: ...


class CacheMethod(Protocol):
    @overload
    def __call__[**P, R](
        self,
        func: Callable[P, R],
        ignore: Sequence[str] | None = None,
        verbose: int | None = None,
        mmap_mode: Literal["r+", "r", "w+", "c", False] | None = False,
        cache_validation_callback: Callable[[dict[str, Any]], bool] | None = None,
    ) -> CachedFunc[P, R]: ...

    @overload
    def __call__[**P, R](
        self,
        ignore: Sequence[str] | None = None,
        verbose: int | None = None,
        mmap_mode: Literal["r+", "r", "w+", "c", False] | None = False,
        cache_validation_callback: Callable[[dict[str, Any]], bool] | None = None,
    ) -> Self: ...

    def __call__[**P, R](
        self,
        func: Callable[P, R] | None = None,
        ignore: Sequence[str] | None = None,
        verbose: int | None = None,
        mmap_mode: Literal["r+", "r", "w+", "c", False] | None = False,
        cache_validation_callback: Callable[[dict[str, Any]], bool] | None = None,
    ) -> CachedFunc[P, R] | Self: ...


class Memory(joblib.Memory):
    @overload
    def cache[**P, R](self, func: Callable[P, R]) -> CachedFunc[P, R]: ...

    @overload
    def cache[**P, R](
        self,
        func: Callable[P, R],
        ignore: Sequence[str] | None = None,
        verbose: int | None = None,
        mmap_mode: Literal["r+", "r", "w+", "c", False] | None = False,
        cache_validation_callback: Callable[[dict[str, Any]], bool] | None = None,
    ) -> CachedFunc[P, R]: ...

    @overload
    def cache(
        self,
        ignore: Sequence[str] | None = None,
        verbose: int | None = None,
        mmap_mode: Literal["r+", "r", "w+", "c", False] | None = False,
        cache_validation_callback: Callable[[dict[str, Any]], bool] | None = None,
    ) -> CacheMethod: ...

    def cache[**P, R](  # type: ignore
        self,
        func: Callable[P, R] | None = None,
        ignore: Sequence[str] | None = None,
        verbose: int | None = None,
        mmap_mode: Literal["r+", "r", "w+", "c", False] | None = False,
        cache_validation_callback: Callable[[dict[str, Any]], bool] | None = None,
    ) -> CachedFunc[P, R] | CacheMethod:
        # Allow partial initialization and mimic joblib.
        if func is None:
            part = partial(
                self.cache,
                ignore=ignore,
                verbose=verbose,
                mmap_mode=mmap_mode,
                cache_validation_callback=cache_validation_callback,
            )
            return cast(CacheMethod, part)

        # Create the original cache, i.e. the MemorizedFunc object
        cached_func = super().cache(
            func=func,
            ignore=ignore,
            verbose=verbose,
            mmap_mode=mmap_mode,
            cache_validation_callback=cache_validation_callback,
        )

        func_module = getattr(func, "__module__", "")
        func_name = getattr(func, "__qualname__", str(func))
        func_fullname = f"{func_module}.{func_name}".lstrip(".")

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            """Pydantic neither supports objects nor methods, so wrap in function."""
            logger.debug("Attempt to retrieve cache for %s", func_fullname)
            return cached_func(*args, **kwargs)

        # Keep references accessible
        setattr(wrapper, "cache", cached_func)
        setattr(wrapper, "uncached", cached_func.func)
        setattr(wrapper, "clear", cached_func.clear)

        # As a CachedFunc type-checkers should allow `cached_func.clear()`.
        return cast(CachedFunc[P, R], wrapper)
