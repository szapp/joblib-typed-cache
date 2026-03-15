# Joblib Typed Cache

[![CI](https://github.com/szapp/joblib-typed-cache/actions/workflows/ci.yml/badge.svg)](https://github.com/szapp/joblib-typed-cache/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/joblib-typed-cache.svg)](https://pypi.python.org/pypi/joblib-typed-cache)
[![Python Versions](https://img.shields.io/pypi/pyversions/joblib-typed-cache.svg)](https://github.com/szapp/joblib-typed-cache)
[![Support on Ko-fi](https://img.shields.io/badge/ko--fi-support-ff586e?logo=kofi&logoColor=white)](https://ko-fi.com/szapp)

Joblib's cache functionality in `joblib.Memory` does not preserve type annotations of the underlying function.
That poses obstacles for pydantic validation and for modern type checkers and autocompletion in IDEs.

This package simply defines an incomplete adapter for the cache functionality.

## Installation

```shell
uv add joblib-typed-cache
```

## Usage

The package offers a drop-in replacement for `joblib.Memory.cache`.

```python
from typed_joblib_cache import Memory

cache = Memory(location="~/.cache", verbose=0)


@cache(ignore=["db_connection"])
def get_user(user_id: str, db_connection: str) -> dict[str, str]:
    # Simulate data retrieval
    return {"user_id": user_id, "email": "john@example.com", "transaction_id": 42}
```

In this example, the function `get_user` will retain helpful tooltips in IDE and can also be used in conjunction with pydantic type validation.

```python
import pydantic

get_user_validated = validate_call(get_user)
```
