DogApi
======

A Python client for the DataDog API.

- Library Documentation: http://pydoc.datadoghq.com
- HTTP API Documentation: http://docs.datadoghq.com/api/
- DataDogHQ: http://datadoghq.com
- Code: https://github.com/DataDog/dogapi ([![Build Status](https://travis-ci.org/DataDog/dogapi.png?branch=fabric)](https://travis-ci.org/DataDog/dogapi))

Change Log
----------

- 1.9.0
  - Release date: 2014.11.17
  - Add Monitors API [#115](https://github.com/DataDog/dogapi/pull/115)
  - Allow override of host from statsd [#116](https://github.com/DataDog/dogapi/pull/116)
  - Fix ImportError when `ssl` module is missing [#114](https://github.com/DataDog/dogapi/pull/114)
  - Change `repo_name` logic for bare git repos [#97](https://github.com/DataDog/dogapi/pull/97)
  - Fixes for Python 3 [#105](https://github.com/DataDog/dogapi/pull/105)

- 1.8.5
  - Release date: 2014.09.24
  - Improve dashboard API Validation [#25](https://github.com/DataDog/dogapi/issues/25) and [#26] (https://github.com/DataDog/dogapi/issues/26)
  - Add version command [#65] (https://github.com/DataDog/dogapi/issues/65)
  - Correct typos in search docstring [#100] (https://github.com/DataDog/dogapi/issues/100)
  - A new method to get snapshots using a graph definition [#78] (https://github.com/DataDog/dogapi/issues/78)
  - A new method to check if a snapshot is ready.
  - Fix bug in snapshot API [#99](https://github.com/DataDog/dogapi/issues/99)
  - Add silenced_timeout_ts to alert API [#96](https://github.com/DataDog/dogapi/pull/96)

- 1.8.0
  - Release date: 2014.05.22
  - Update dogshell dashboard post, push, and update to accept new template variable format [#89](https://github.com/DataDog/dogapi/pull/89)
  - Fix bug preventing Fabric events from getting written
  - Update Fabric integration to capture stdout and stderr in event [#94](https://github.com/DataDog/dogapi/pull/95)

- 1.7.0
  - Release date: 2014.05.07
  - When setting up dogapi for fabric, optionally accept an application key as well as an api key. Thanks @zupo. [#60](https://github.com/DataDog/dogapi/pull/60)
  - Remove logging.basicConfig() from module scope. Thanks @micktwomey. [#67](https://github.com/DataDog/dogapi/pull/67)
  - Fix post-receive hook to support bare repositories. Thanks @mattbailey [#84](https://github.com/DataDog/dogapi/pull/84)
  - Minor documentation updates for gauge/increment. Thanks @robbyt [#85](https://github.com/DataDog/dogapi/pull/85)
  - Update dogshell post event with source type and aggregation key arguments. [#87](https://github.com/DataDog/dogapi/pull/87)

- 1.6.5
  - Release date: 2014.02.24
  - Fix typo in fabric task, #82

- 1.6.4
  - Release date: 2014.02.19
  - Prevent exceptions due to misnamed variable, #79 @smartkiwi

- 1.6.3
  - Release date: 2014.02.07
  - Allow further customizations of fabric task, fix typos, @alq666

- 1.6.2
    - Release date: 2014.01.16
    - Don't catch KeyboardInterrupt when sending to StatsD

- 1.6.1
    - Release date: 2013.11.19
    - Add notifications to `dogwrap` command

- 1.6.0
    - Release date: 2013.10.09
    - Update Fabric integration to support @roles and @hosts decorators.
    - Add timeout and notify_no_data to alert API.

- 1.5.0
    - Release date: 2013.9.17
    - Add dogwrap command for calling scripts and generating events from their results

- 1.4.2
    - Release date: 2013.08.22
    - Add template variables to dashboard API.

- 1.4.1
    - Release date: 2013.08.15
    - Add a `--counter` option to `dog metric post` to submit unsigned 64-bit counters to Datadog.

- 1.4.0
    - Release date: 2013.07.16
    - Add an API for creating/updating/deleting/sharing Screenboards.

- 1.3.0
    - Release date: 2013.06.27
    - Add an API for inviting users
    - Add an API for taking graph snapshots

- 1.2.3
    - Release date: 2013.05.13
    - Add a timeout paramter to HTTP connections

- 1.2.2
    - Release date: 2013.04.24
    - Add tags argument to metric post
    - Add arguments to fabric notify

- 1.2.1
    - Release date: 2013.03.06
    - Fixed backwards compatability issues in the tagging api introduced in 1.2.0

- 1.2.0
    - Release date: 2013.02.19
    - Context manager for capturing histogram of code execution time (thanks @cpennington)
    - Support for setting `source` type when submitting host tags

- 1.1.2
    - Release date: 2012.12.19
    - fabric: Allow custom task event naming

- 1.1.1
    - Release date: 2012.11.27
    - Better handling of API errors

- 1.1.0
    - Release date: 2012.11.06
    - Support for the metric alert API.

- 1.0.14
    - Release date: 2012.10.16
    - Ensure the `timed` decorator preserves function attributes.

- 1.0.13
    - Release date: 2012.09.21
    - Added missing `dashboards` endpoint, which fetches all of an org's dashes

- 1.0.11
    - Release date: 2012.08.13
    - Fixes Fabric support when mixing old- and new-style tasks.

- 1.0.10
    - Release date: 2012.08.03
    - Extra command-line arguments: --api-key and --application-key

- 1.0.9
    - Release date: 2012.06.22
    - Fabric support

- 1.0.7, 1.0.8
    - never published

- 1.0.6
    - Release date: 2012.06.05
    - Bug fix in dogshell on python 3

- 1.0.5
    - Release date: 2012.05.29
    - Compatible with python 3.2

- 1.0.4
    - Release date: 2012.04.16
    - A rash of performance improvements to DogStatsApi's stats collection
      methods.
    - DogStatsApi's metrics collection and flushing can now be disabled with
      a configuration change.
    - Removed locking from DogStatsApi's metrics collection, trading some
      accuracy when many threads are writing to the same instance in exchange
      for performance.

- 1.0.0
    - Release date: 2012.03.21
    - This release is a backwards incompatible rewrite of the library.
    - The API wrapper was renamed from SimpleClient to DogHttpApi. It's
      interface was also updated. Check the docs for changes.
    - Added DogStatsApi, a tool for collecting metrics with little application
      overhead.
