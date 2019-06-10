FROM python:3.7-slim

# RUN apt-get update -y && apt-get install libglib2.0 -y && apt-get clean

WORKDIR /server

ADD ./requirements.txt requirements.txt

RUN pip install -r requirements.txt

ADD server.py .
ADD lib lib/
ADD data data/
ADD templates templates/
ADD static static/
ADD settings.py .

CMD ["python", "server.py"]
