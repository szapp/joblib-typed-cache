alias setup := install
alias sync := install
alias update := install

# List all commands by default when typing only `just``
@_default:
    just --list

#########
# CHECK #
#########

# Lint and format
[group('check')]
lint:
    uv run ruff check --fix
    uv run ruff format

# Check types
[group('check')]
typing:
    uv run ty check src

# Check coverage (pytest)
[group('check')]
cov *args:
    uv run pytest {{ args }}

# Run all tests on all dependency combinations (nox)
[group('check')]
test *args:
    uv run nox {{ args }}

# Check docstrings on tests
[group('check')]
check-testdocs:
    uv run interrogate tests

# Check cognitive complexity
[group('check')]
check-complexity:
    uv run complexipy

# Run linting, formatting, tests and type-checking
[group('check')]
check-all: lint cov test typing check-testdocs check-complexity

##############
# LIFE CYCLE #
##############

# Bring environment up-to-date
[group('lifecycle')]
install:
    uv sync
    uv run prek install --install-hooks --overwrite --no-progress

# Reset environment and all cache files
[group('lifecycle')]
clean:
    uvx pyclean . -d all
    uvx prek uninstall --no-progress
    -rm -rf .venv

# Setup environment from scratch
[group('lifecycle')]
fresh: clean install

# Upgrade python and all dependencies
[group('lifecycle')]
upgrade:
    uv sync --upgrade
    uv run prek auto-update --no-progress
