*************************************
Automated managing of Google Hangouts
*************************************

This is a couple of script to automate hangouts On Airs.

Use case looks like this:
    1. User creates OnAir event on Hangouts page (and it automatically appears at Google Calendar)
    2. Cron runs calendar checking script. Checking script reads ical feed and overrides  'output.rss'
    3. Cron runs hangout runner script, which reads 'output.rss' and in case if there is need to start a OnAir:
         1. At 30 minus before event:
               1. Goes on event  page and gets guests list
               2. Starts Hangout and invites guests
         2. At 5 minutes before event starts broadcasting
         3. At 1 hour after each event shut downs the hangout

Configuration
=============

Before installation you need to set feed url in buildout.cfg:

.. code-block:: ini

    iCal_URL = https://www.google.com/calendar/ical/doejohnbot%40gmail.com/private-fd989039a68d46b8f239184ec84319f5/basic.ics

also you may change some other parameters (like path to file with credential of feed output config) there:

.. code-block:: ini

    calendar_file_path = ${buildout:directory}/events.ical
    credentials_file = ${buildout:directory}/credentials.yaml
    events_file = ${buildout:directory}/events.yaml
    rss_config_path = ${buildout:directory}/output_feed_config.yaml

Don't forger to rebuild buildout after editing buildout.cfg.

Set credentials you want to use for google authentication into credentials.yaml:

.. code-block:: yaml

    email: you_email@gmail.com
    password: password

How to install
==============

.. code-block:: bash

    python3 bootstrap.py
    bin/buildout

How to use
==========

On installation step adds 2 cronjobs:
    * feed checker
    * hangouts runner
