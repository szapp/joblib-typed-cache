import nox
from packaging.version import Version

PYPROJECT = nox.project.load_toml("pyproject.toml")
PYTHON_VERSIONS = nox.project.python_versions(PYPROJECT)


@nox.session(python=PYTHON_VERSIONS)
@nox.parametrize("pydantic", ["1.10.14", "2.14.0"])
def tests(session, pydantic):
    if pydantic == "1.10.14" and Version(session.python) >= Version("3.15"):
        session.skip("Unsupported pydantic version")
    session.install(".", "--group", "tests", f"pydantic=={pydantic}")
    session.run("pytest", "--no-cov", "--inline-snapshot=disable")
