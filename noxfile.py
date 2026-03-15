import nox

PYPROJECT = nox.project.load_toml("pyproject.toml")
PYTHON_VERSIONS = nox.project.python_versions(PYPROJECT, max_version="3.14")


@nox.session(python=PYTHON_VERSIONS)
@nox.parametrize("pydantic", ["1.10.14", "2.12.5"])
def tests(session, pydantic):
    session.install(".", "--group", "tests", f"pydantic=={pydantic}")
    session.run("pytest", "--no-cov", "--inline-snapshot=disable")
