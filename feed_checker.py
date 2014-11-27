"""
Usage:
    feed_checker.py CALENDAR_PATH CREDENTIALS_PATH EVENTS_OUTPUT

Arguments:
    CALENDAR_PATH       path to ical file
    CREDENTIALS_PATH    path to file with google user credentials
    EVENTS_OUTPUT       path to file to save upcoming events for hangout runner

"""
from icalendar import Calendar
import arrow
from yaml import dump
from docopt import docopt


def get_upcomming_events_from_google_ical_file(ical_path):
    gcal = Calendar.from_ical(open(ical_path, 'rb').read())
    now = arrow.utcnow()
    events = (item for item in gcal.subcomponents if item.name == "VEVENT")
    upcomming_events = (e for e in events if arrow.get(e['DTSTART'].dt) > now)
    return [
        dict(event_url=str(event.get('URL', '')),
             start_time=event['DTSTART'].dt.isoformat(),
             end_time=event['DTEND'].dt.isoformat(),
             last_modified=event['LAST-MODIFIED'].dt.isoformat(),
             created=event['CREATED'].dt.isoformat(),
             uid=str(event['UID']),
             # XXX: can't find a way to get event attendees list
             attendees=[str(email)[7:] for email in event['ATTENDEE']]
                       if isinstance(event['ATTENDEE'], list) else
                       [str(event['ATTENDEE'])[7:]],
             description=str(event['DESCRIPTION']),
             location=str(event['LOCATION']),
             summary=str(event['SUMMARY']),)
        for event in upcomming_events]


def main(calendar_path, credentials_path, events_output):
    # get all upcoming events from feed
    events = get_upcomming_events_from_google_ical_file(calendar_path)

    # save events to yaml file for internal use
    with open(events_output, 'w') as events_output_file:
        events_output_file.write(
            dump({'upcoming_events': events}, default_flow_style=False))


if __name__ == "__main__":
    arguments = docopt(__doc__)
    main(calendar_path=arguments['CALENDAR_PATH'],
         credentials_path=arguments['CREDENTIALS_PATH'],
         events_output=arguments['EVENTS_OUTPUT'])
