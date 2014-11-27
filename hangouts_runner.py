"""
What it does:
    * About ~30 minutes before each event starts, start up the Hangout and
      invite the people requested.
    * At ~5 minutes before each event starts broadcasting the event.
    * At ~1 hour after each event shut downs the hangout.

Usage:
    hangouts_runner.py <credentials_path> <events_list_path>

"""

from time import sleep
from docopt import docopt
from yaml import load
from hangout_api import Hangouts
import arrow
from operator import itemgetter

import os.path
here = os.path.abspath(os.path.dirname(__file__))

import logging
import logging.handlers
logger = logging.getLogger('hangout_runner')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
fh = logging.handlers.RotatingFileHandler(
    os.path.join(here, 'hangout_runner.log'), maxBytes=52428800, backupCount=5)
formatter = logging.Formatter(
    '%(asctime)s (%(process)d) - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)


def wait_until_time(time, minutes_delta=0):
    stop_waiting_time = arrow.get(time).replace(minutes=minutes_delta)
    while (stop_waiting_time - arrow.utcnow()).total_seconds() > 0:
        sleep(10)


def handle_hangout(
        email, password, event_url, start_time, end_time, attendees=None):
    logger.info('Initializing hangout handler for %s HoA event' % event_url)
    hangout = Hangouts()

    logger.info('Logging in as %s' % email)
    hangout.login(email, password)
    logger.info('Logged in')

    if attendees is None:
        # getting attendees list from event page
        logger.info('Getting attendees list from event page')
        hangout.browser.get(event_url)
        users_nodes = hangout.browser.css(
            'a[href^="./"]', eager=True, timeout=60)
        users = (i.text for i in users_nodes if i.text)
        attendees = tuple(set(users))
        logger.info('Got %s attendees' % len(attendees))

    # staring and inviting the people
    logger.info('Starting Hangout On Air')
    hangout.start(on_air=event_url)
    logger.info('Started')
    logger.info('Inviting  people')
    hangout.invite(attendees)
    logger.info('Invited')

    # ~5 minutes before event starting broadcasting
    wait_until_time(start_time, minutes_delta=-5)
    logger.info('Starting Broadcast (event starts at %s by UTC)' % start_time)
    hangout.broadcast.start()
    logger.info('Broadcasting')

    # waiting until event ends
    wait_until_time(end_time)
    logger.info('Event time is ended (event ends at %s by UTC)' % end_time)

    # waiting one more hour and shutting down the hangout
    wait_until_time(end_time, minutes_delta=60)
    logger.info('Shutting down the hangout')
    hangout.broadcast.stop()
    logger.info('Exiting')


def get_event_to_start(events):
    events = events['upcoming_events']
    events.sort(key=itemgetter('start_time'))
    if arrow.get(events[0]['start_time']).replace(minutes=-30) <= arrow.utcnow():
        return events[0]


def main():
    arguments = docopt(__doc__)
    credentials = load(open(arguments['<credentials_path>'], 'r').read())
    events = load(open(arguments['<events_list_path>'], 'r').read())
    on_air_options = get_event_to_start(events)
    if on_air_options is None:
        logger.info('No events to start')
        return
    handle_hangout(
        email=credentials['email'],
        password=credentials['password'],
        event_url=on_air_options['event_url'],
        start_time=on_air_options['start_time'],
        end_time=on_air_options['end_time'],
        attendees=on_air_options['attendees'],
    )


if __name__ == '__main__':
    try:
        main()
    except Exception as exp:
        logger.exception(exp)
        raise exp
