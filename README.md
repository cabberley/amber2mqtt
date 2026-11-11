<h1 align="center">
  <br>
  <i>Amber2MQTT Docker Container</i>
  <br>
  <h3 align="center">
    <i>Standalone Docker Container to Poll Amber for pricing updates then use MQTT to forward updates to your preferred workflow Engine</i>
    <br>
  </h3>
</h1>

<p align="center">
  <a><href="https://github.com/cabberley/amber2mqtt/releases"><img src="https://img.shields.io/github/v/release/cabberley/amber2mqtt?display_name=tag&include_prereleases&sort=semver" alt="Current version"></a> <img alt="GitHub Release Date" src="https://img.shields.io/github/release-date/cabberley/amber2mqtt">
  <img alt="GitHub" src="https://img.shields.io/github/license/cabberley/amber2mqtt"> <img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/cabberley/amber2mqtt/multi-publish.yml">
  <img alt="GitHub Issues or Pull Requests" src="https://img.shields.io/github/issues/cabberley/amber2mqtt"> <img alt="GitHub User's stars" src="https://img.shields.io/github/stars/cabberley"> <img alt="GitHub Downloads (all assets, all releases)" src="https://img.shields.io/github/downloads/cabberley/amber2mqtt/total">


</p>
<p align="center">
    <a href="https://github.com/hacs/integration"><img src="https://img.shields.io/badge/HACS-Custom-41BDF5.svg"></a>
</p>
<p align="center">
  <a href="https://www.buymeacoffee.com/cabberley" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
</p>

This Container will based on the timing schedules you setup:
1. Poll the Amber API using your account details
2. Poll the AEMO website to retrieve the latest actual price & data for the current interval

NOTE: New sensors that will generate 5min periods from the Amber 30minute forecasts, these new sensors for Extended General and feed in prices use the available 5min prices and then convert the 30min forecasts into 6 x 5min forecasts for the 30 minute period. Helpful for those that use EMHASS and wish to do 5 minute time resolution predictions/plans. To enable this read below to add a new config option called "forecast288".

**NOTE:** This Add-on does require a MQTT Broker, you can use the Home Assistant Mosquitto Add-on or an external Broker

## Installation
On your Docker Host:

- create a config directory for your container, i.e. "/configs/amber2mqtt"
- Create a "data" directory under that config directory
- Copy the options.json file from this repository and edit it with your Amber and MQTT Broker details.
- Optionally if your MQTT Broker requires a username and password in the mqtt section add a key value pair for:
   - username
   - password
  

Create a new docker container and pull the image.
- make sure to map the volume /data to your config folder storing the options.json file

If you prefer to use GitHub Container Registry:
`docker pull ghcr.io/cabberley/amber2mqtt:latest`

### Advanced Configuration

In the Amber and AEMO sections there are a pair of keys for seconds and minutes. These instruct the scheduling engine inside the Add-on what time periods to poll the Amber and AEMO sites respectively.
In the default config for example the Amber Site will be polled:
 - on each listed second "14,16,18,19,21,23,25,27,30,32,35,40,45,50,55"
 - When the Minute equals "0-1,5-6,10-11,15-16,20-21,25-26,30-31,35-36,40-41,45-46,50-51,55-56"
 - When the code gets a confirmed price for the current 5 minute interval it will then stop and not continue until the next 5 minute interval starts.

Updating 5min, 30min and Billing interval forecasts
New option to add to your options.json to followup the inital Amber data update and collect immediately the 5/30/user billing forecast data.
To enable this new feature add the folowing keys in the AMber section of your options.json file, if they have not been added the container will assume False and not create or collect the forecast data:
   - "forecast5min": "True"
   - "forecast30min": "True"
   - "forecastUser": "True"
   - "forecast288": "True"

Make sure you include "," at the end of the correct lines to align with JSON file format!!

Amber limits you currently to 50 requests per 5 minutes and if you exceed that you will be blocked until the next 5 minute period starts. So also take into considderation what other apps you have that are also hitting the Amber website as you will quickly run out of calls if there are delays in the price being published.

The AEMO minutes and seconds work the same way.

You can adjust these according to your needs, but in doing so consider the timing of when these prices are published and that they are not available immediately at the start of the 5min intervals!

### AEMO dashboard data

AEMO polling uses the public dashboard API at `dashboards.public.aemo.com.au`,
replacing the retired visualisations report endpoint. The dashboard API key is
loaded automatically from its public configuration, cached, and refreshed once
if authentication fails. No additional user configuration is required.

Existing MQTT topics, sensor names, price units and attributes are unchanged.
Settlement intervals are checked in fixed NEM market time (UTC+10), independent
of the container timezone or daylight saving, including hour and day boundaries.
Incomplete or invalid dashboard data raises an error rather than publishing
partial prices.

### Request failures and recovery

Both polling jobs retain immediate retries with bounded waits. AEMO requests use
a 30-second connect/read timeout and up to three retries; server `Retry-After`
delays are capped at five seconds. Amber uses a 30-second request timeout, three
attempts and five-second retry delays, with nested SDK retries disabled.
These are request/inactivity timeouts, not a hard deadline for a complete poll.

Failures are logged by the scheduler and retried at the next configured polling
time, without restarting the container. A cycle is marked complete only after
all enabled fetches and MQTT publishes have succeeded. Failed forecasts or MQTT
enqueue errors leave the cycle eligible for retry; previously published retained
messages may be sent again. MQTT remains QoS 0, so successful enqueueing does not
guarantee delivery to the broker.

Only one instance of each polling job runs at a time. Scheduled times that occur
while that job is still running are skipped; polling resumes on the next
configured time after it finishes. Completion is tracked per five-minute
interval, so a slow previous-interval poll cannot suppress the next interval.

Run the offline polling regression tests after installing the declared dependencies:
`python -m unittest discover -s tests`
