# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.7-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN apt-get update
RUN apt-get install -y vim
RUN apt-get install -y gcc
RUN apt-get install -y g++
RUN apt-get install -y cmake
RUN python -m pip install -r requirements.txt

WORKDIR /content
COPY . /content


