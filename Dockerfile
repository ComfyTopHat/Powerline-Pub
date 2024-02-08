# syntax=docker/dockerfile:1

FROM python:3.10.11-slim-buster

RUN useradd -m docker && echo "docker:docker" | chpasswd && adduser docker sudo
RUN apt-get update && apt-get install -y gnupg2
RUN apt-get update; apt-get install curl -y
RUN apt-get install -y unixodbc-dev
RUN apt-get install -y libgssapi-krb5-2


RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt update 
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17

WORKDIR /api


COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .


CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "80"]