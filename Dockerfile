FROM                        python:3.6.7-slim
MAINTAINER                  tech@ashe.kr

WORKDIR                     /srv

ADD                        ./nginx /srv/nginx/
ADD                        ./gunicorn /srv/gunicorn/

RUN                         pip install --upgrade pip
RUN                         pip install pipenv

ADD                        ./sources/Pipfile /srv/Pipfile
ADD                        ./sources/Pipfile.lock /srv/Pipfile.lock
RUN                         pipenv lock --requirements > requirements.txt
RUN                         pip install -r requirements.txt
RUN                         pip install gunicorn

ADD                        ./sources/app/ /srv/app/
