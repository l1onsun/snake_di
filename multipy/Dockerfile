FROM alpine:latest as build
WORKDIR /snake_di_multipy

RUN apk add --no-cache --virtual .build-deps \
    curl \
    git \
    bash \
    build-base \
    libffi-dev \
    openssl-dev \
    bzip2-dev \
    zlib-dev \
    xz-dev \
    readline-dev \
    sqlite-dev \
    tk-dev
RUN curl https://pyenv.run | bash
ENV PATH=/root/.pyenv/bin:${PATH}

ENV PYTHON_CONFIGURE_OPTS="--without-doc-strings"
RUN pyenv install 3.8 3.9 3.10 3.11
COPY _alpine_clean_up_pyenv.bash .
RUN bash _alpine_clean_up_pyenv.bash 3.8 3.9 3.10 3.11

FROM alpine:latest
WORKDIR /snake_di_multipy

RUN apk add --no-cache bash

COPY --from=build /root/.pyenv /root/.pyenv
ENV PATH=/root/.pyenv/bin:${PATH}
COPY _alpine_symlink_pyenv_pythons.bash .
RUN bash ./_alpine_symlink_pyenv_pythons.bash 3.8 3.9 3.10 3.11
ENV PATH=/snake_di_multipy/python_bin:${PATH}

CMD ["bash"]