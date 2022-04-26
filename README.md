# Satellite Data pipeline

We want to create a lookup table in bigquery that contains the position (x,y,z) of every orbcomm and spire satellite for every second of every day.

For achieving this goal we want to get on a daily basis the TLE (Two Line Element) of all the satellites from Orbcomm and Spire and store them in BQ. Then we want to process the TLE per day per satellite and create one record with the position of the satellite per second. We will end up having a table with the following schema:
`norad_id, timestamp, lat, lon, altitude`

# Running

## Dependencies

You just need [docker](https://www.docker.com/) and
[docker-compose](https://docs.docker.com/compose/) in your machine to run the
pipeline. No other dependency is required.

## Setup

The pipeline reads it's input from BigQuery, so you need to first authenticate
with your google cloud account inside the docker images. To do that, you need
to run this command and follow the instructions:

```
docker-compose run gcloud auth login
```

## CLI

The pipeline includes a CLI.
Just run `docker-compose run --rm pipe_satellite_data` and follow the
instructions there.

# License

Copyright 2022 Global Fishing Watch

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
