FROM python:3

WORKDIR /usr/src/app

RUN pip install --no-cache-dir flask google-api-python-client google-auth-oauthlib

RUN apt update
RUN apt-get -qq install vim clang-6.0

COPY *.py ./
COPY static static/
COPY templates templates/
COPY data data/

ENTRYPOINT [ "python", "./main.py" ]
