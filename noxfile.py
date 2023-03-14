import nox


@nox.session(python=["3.8", "3.9", "3.10", "3.11"])
def tests(session: nox.Session):
    session.install(".")
    session.install("-r", "requirements/nox-requirements.txt")
    session.run("pytest")
