FROM ubuntu:18.04

RUN apt-get update -y && apt-get install -y python3-pip python3-dev git gcc g++

WORKDIR /myapp

COPY ./requirements.txt /myapp/requirements.txt

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . /myapp

ENTRYPOINT ["python3","run.py"]
