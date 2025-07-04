# Docker Container for Amber2MQTT

# Beta Testing atm

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

