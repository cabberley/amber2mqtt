# sarmhf,amd64,armv7,aarch64
ARG TARGETARCH
# armhf=raspbian, amd64,armv7,aarch64=debian
ARG os_version=python

FROM ghcr.io/home-assistant/$TARGETARCH-base-$os_version:latest AS base

# check if TARGETARCH was passed by build-arg
ARG TARGETARCH
ENV TARGETARCH=${TARGETARCH:?}

# FROM python:3.13.1-alpine3.20

WORKDIR /app

RUN apk add --no-cache supercronic \
    && mkdir -p data \
    #&& mkdir -p config \
    && apk --no-cache upgrade \
    && apk add --no-cache tzdata

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

#ENV TZ=australia\Brisbane 

VOLUME /app/data
LABEL \
    io.hass.name="Amber2MQTT" \
    io.hass.description="Amber2MQTT: Amber 5min price polling for Home Assistant" \
    io.hass.version=${BUILD_VERSION} \
    io.hass.type="addon" \
    io.hass.arch="aarch64|amd64|armhf|armv7" \
    org.opencontainers.image.authors="Chris Abberley <chris@abberley.com.au>" \
    org.opencontainers.image.source="https://github.com/cabberley/amber2mqtt" \
    org.opencontainers.image.description="Amber and AEMO solution to poll prices quickly from their source."
  #/opt/amber/config

ENTRYPOINT ["python", "app.py"]
# Docker Labels for hass

