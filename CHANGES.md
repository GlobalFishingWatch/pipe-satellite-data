# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a
Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## v3.0.0 - 2022-04-26

### Added

* [PIPELINE-756](https://globalfishingwatch.atlassian.net/browse/PIPELINE-756): Adds
  cloudbuild and tests.
  Drops pipe-tool dependencies.
  Drops bash scripting, uses python instead
  Drops Travis dependency.
  Uses new base image.

## v2.0.1 - 2020-03-04

### Added

* [GlobalFishingWatch/gfw-eng-tasks#20](https://github.com/GlobalFishingWatch/gfw-eng-tasks/issues/20): Adds
  fix to store only one TLE, instead of all the server returns, by norad_id by day.

## v2.0.0 - 2020-02-11

### Added

* [GlobalFishingWatch/GFW-Tasks#1181](https://github.com/GlobalFishingWatch/GFW-Tasks/issues/1181): Adds
  replace flag for tables in BigQuery.
  support for norad_id's when on some days the server SpaceTrack API doesn't give us data. Limits this feature for a maximum of 7 days.
  support for python3.7 and pipe-tools:v3.1.0.


### Changed

* [GlobalFishingWatch/GFW-Tasks#1181](https://github.com/GlobalFishingWatch/GFW-Tasks/issues/1181): Changes
  the CLOUD_SDK_VERSION to 268.0.0
  The pipe-tools version to v3.1.0
  The python version to 3.7
  The way of calling the flexible_operator.
  Updates the TLE schema wuth DECAYED field

## v1.0.0 - 2019-03-27

### Added

* [GlobalFishingWatch/GFW-Tasks#991](https://github.com/GlobalFishingWatch/GFW-Tasks/issues/991)
  * Updates the code to support [airflow-gfw](https://github.com/GlobalFishingWatch/airflow-gfw) library and also supports the pipe-tools [v2.0.0](https://github.com/GlobalFishingWatch/pipe-tools/releases/tag/v2.0.0)

## v0.0.1 - 2019-02-27

### Added

* [GlobalFishingWatch/GFW-Tasks#929](https://github.com/GlobalFishingWatch/GFW-Tasks/issues/929)
  Create distance to satellite lookup table
