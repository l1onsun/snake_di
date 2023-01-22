from invoke import task


@task
def coverage_test(c):
    c.run("pytest --cov=pure_di/ tests")


@task
def coverage_report(c):
    c.run("coverage report -m")
