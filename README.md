# StromGedachtApiMqttConnector

get the data from the and publish to mqtt broker

This Python scripts grabs content of the StromGedacht API and publishes the data to an MQTT-Broker.

**Why MQTT?**

There are plenty of solutions available to directly record the data of a inverter with e.g. InfluxDB or a SQL Database.

MQTT was chosen, because it is (from my point of view) the most flexible solution to process the data further on.
In my use case, there is a telegraf instance running, that forwards all MQTT data to InfluxDB, thus no additional Interface from "field level" to the monitoring instance. A nice benefit is the possibility to integrate the MQTT stream into Node-Red or any other automation system such as OpenHAB etc.

## Setup

** CAUTION**
From IT_Security Point-of-View, the whole script might be a nightmare!
Feel free to enhance and contribute!

### Add credentials to the *config.ini*-file

copy the file with the cmd `cp config_template.ini config.ini`
and adjust all the required configuration settings to your *config.ini*-file

### create docker container

building the container
`docker build -t stromgedacht2mqtt:latest .`

`docker run stromgedacht2mqtt:latest stromgedacht2mqtt:latest`

building the container with docker-compose
`docker-compose up`

* Run `python3 sgamc.py`

There's also a Docker Image available on [Docker Hub](https://hub.docker.com/repository/docker/wolfi82/stromgedacht2mqtt).
Note: The Docker-Container runs pretty stable on a amd64 acrchitecture. For arm architectures such as Raspberry Pi, the container is not yet running.
in the *Dockerfile* you might ùncomment `FROM arm32v7/python:3.8-slim-buster` and give it a try.

## Description or the runtime sequence

- get data
- convert to json
- create mqtt message
- publish message

## Missing features:

- exception handling  **implemented only rudimentary, enhancements are on my todo-list**
  - connection errors
    - route to API
    - route to MQTT Broker
  - data inconsistency
  - etc. etc.
- interface to docker logging console

## Problems to be solved:

- Docker container environment ==>
- how to make sure that the latest lib is used?
- runtime monitoring shall provide (detailed) information on the issue causing the container to break.

## use cases for data consumption

### Grafana

By logging the data with this script it's easily possible to create a nice
Grafana Dashboard to display some of the interesting data.

### NODE-RED

**... to be developped**
