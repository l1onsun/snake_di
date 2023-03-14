FROM l1onsun/snake_di_multipy:latest
WORKDIR /snake_di_qa

RUN apk add --no-cache libffi sqlite-dev git

COPY ./requirements ./requirements
RUN python -m pip install -r requirements/dev-requirements.txt

COPY .pre-commit-config.yaml .
RUN git init . && pre-commit install-hooks

COPY LICENSE .
COPY pyproject.toml .
COPY ./snake_di ./snake_di
COPY ./tests ./tests
COPY tasks.py .
COPY noxfile.py .
COPY Readme.md .

RUN git add snake_di tests tasks.py noxfile.py

CMD ["bash"]