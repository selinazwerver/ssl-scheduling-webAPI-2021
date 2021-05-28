FROM python:3

WORKDIR /usr/src/app

RUN pip install --no-cache-dir flask google-api-python-client google-auth-oauthlib

COPY . .

ENTRYPOINT [ "python", "./main.py" ]