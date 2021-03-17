import nox

PACKAGE_NAME = "a_and_a"

# The default sessions that are run
nox.options.sessions = [
    "blacken",
    "test",
]


@nox.session(venv_backend="conda", reuse_venv=True)
def test(session):
    """Run test suite."""

    session.install("pytest")
    session.install(".")
    session.run("pytest")


@nox.session(python=3.8, venv_backend="conda", reuse_venv=True)
def blacken(session):
    """Run black formatter on the library, tests, and source."""
    session.install("black")
    session.run(*["black", "a_and_a", "tests", "noxfile.py", "setup.py"])
