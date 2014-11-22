"""
Usage:
    check_ical_file_and_create_cron_jobs.py CALENDAR_PATH HANGOUT_RUNNER_SHEDULE_EVENTS_PATH EVENTS_CONFIG_LOCATION CREDENTIALS_PATH RUN_CMD

Arguments:
    CALENDAR_PATH                        path to ical file
    HANGOUT_RUNNER_SHEDULE_EVENTS_PATH   path to file with list of events uids which is added to cron scheduler
    EVENTS_CONFIG_LOCATION               path to directory where events configs for hangout runner are saved
    CREDENTIALS_PATH                     path to file with google user credentials
    RUN_CMD                              path hangout runner to script

"""
import os
from tempfile import TemporaryFile
import subprocess as sp
from icalendar import Calendar
import arrow
from yaml import dump
from docopt import docopt


def add_entry_to_at(time, command):
    at_date = arrow.get(time).to('local').strftime("%H:%M %m/%d/%Y")
    with TemporaryFile() as tmpfile:
        tmpfile.write(bytes(command, 'UTF-8'))
        tmpfile.seek(0)
        (_, std_err) = sp.Popen(
            ('at', at_date), stdin=tmpfile).communicate(timeout=1)
    if std_err:
        raise IOError(std_err)


def get_upcomming_events_from_google_ical_file(ical_path):
    gcal = Calendar.from_ical(open(ical_path, 'rb').read())
    now = arrow.utcnow()
    events = (item for item in gcal.subcomponents if item.name == "VEVENT")
    upcomming_events = (e for e in events if arrow.get(e['DTSTART'].dt) > now)
    return [
        dict(event_url=str(event['URL']),
             start_time=event['DTSTART'].dt.isoformat(),
             end_time=event['DTEND'].dt.isoformat(),
             modification_time=event['LAST-MODIFIED'].dt.isoformat(),
             uid=str(event['UID']),
             attendees=['loremimpusbot@gmail.com', ])  # XXX: can't find a way to get event attendees list
        for event in upcomming_events]


def main(calendar_path, hangout_runner_shedule_events_path,
         events_config_location, credentials_path, run_cmd):
    events = get_upcomming_events_from_google_ical_file(calendar_path)
    hangout_runner_shedule_events = open(
        hangout_runner_shedule_events_path, 'r').readlines()
    events_to_add_to_schedule = (
        e for e in events if e['uid'] not in hangout_runner_shedule_events)
    for event in events_to_add_to_schedule:
        event_config_path = os.path.join(events_config_location, event['uid'])
        with open(event_config_path, 'w') as event_config_file:
            event_config_file.write(dump(event, default_flow_style=False))
        hangout_runner_shedule_events.append(event['uid'])
        add_entry_to_at(
            arrow.get(event['start_time']).replace(minutes=-30).isoformat(),
            "%s %s %s" % (run_cmd, credentials_path, event_config_path))
    with open(hangout_runner_shedule_events_path, 'w') as shedule_file:
        shedule_file.write('\n'.join(hangout_runner_shedule_events))

if __name__ == "__main__":
    arguments = docopt(__doc__)
    main(calendar_path=arguments['CALENDAR_PATH'],
         credentials_path=arguments['CREDENTIALS_PATH'],
         events_config_location=arguments['EVENTS_CONFIG_LOCATION'],
         hangout_runner_shedule_events_path=arguments['HANGOUT_RUNNER_SHEDULE_EVENTS_PATH'],
         run_cmd=arguments['RUN_CMD'])
