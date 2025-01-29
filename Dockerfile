# sarmhf,amd64,armv7,aarch64
ARG TARGETARCH
# armhf=raspbian, amd64,armv7,aarch64=debian
ARG os_version=python

FROM ghcr.io/home-assistant/$TARGETARCH-base-$os_version:latest AS base

# check if TARGETARCH was passed by build-arg
ARG TARGETARCH
ENV TARGETARCH=${TARGETARCH:?}

# FROM python:3.13.1-alpine3.20

WORKDIR /opt/amber

RUN apk add --no-cache supercronic \
    && mkdir -p data \
    && mkdir -p config \
    && apk --no-cache upgrade \
    && apk add --no-cache tzdata

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV TZ=australia\Brisbane 


VOLUME /opt/amber/data \
  /opt/amber/config

ENTRYPOINT ["python", "app.py"]

LABEL org.opencontainers.image.authors="cabberley <chris@abberley.com.au>"
