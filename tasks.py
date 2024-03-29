import tomllib

from invoke import task

# ToDo: find cleaner way to work with secrets
try:
    with open("local/config.toml", "rb") as f:
        config = tomllib.load(f)
except FileNotFoundError:
    config = {}


@task
def coverage_test(c):
    c.run("pytest --cov=snake_di/ tests")


@task
def coverage_report(c):
    c.run("coverage report -m --fail-under=100")


@task
def compile_requirements(c):
    env = 'CUSTOM_COMPILE_COMMAND="invoke compile-requirements"'
    for req in ["requirements/dev-requirements", "requirements/nox-requirements"]:
        c.run(f"{env} pip-compile {req}.in -o {req}.txt")


@task
def docker_login(c):
    username: str = config["docker"]["username"]
    password: str = config["docker"]["password"]
    c.run(f"echo {password} | docker login -u {username} --password-stdin")


@task
def build_multipy(c):
    c.run("docker buildx build multipy/ -t l1onsun/snake_di_multipy")


@task
def push_multipy(c):
    c.run("docker push l1onsun/snake_di_multipy")


@task
def build_qa(c):
    c.run("docker buildx build . -t l1onsun/snake_di_qa")


@task
def pypi_check(_):
    import requests

    from snake_di import __version__

    result = requests.get("https://pypi.python.org/pypi/snake_di/json")
    assert (
        __version__ not in result.json()["releases"].keys()
    ), "Version already published. Version dump required!"


@task(pre=[pypi_check])
def pypi_publish(c):
    username = config["flit"]["username"]
    password = config["flit"]["password"]
    env = f"FLIT_USERNAME={username} FLIT_PASSWORD={password}"
    c.run(f"{env} flit publish")
