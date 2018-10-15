FROM python:3.7-alpine

ADD . /opt/mokapi
WORKDIR /opt/mokapi

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "mokapi"]
