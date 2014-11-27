"""
Usage:
    feed_checker.py EVENTS OUTPUT_FEED_CONFIG

Arguments:
    EVENTS              path to yaml file with upcoming events
    OUTPUT_FEED_CONFIG  path to output rss feed config

"""

from PyRSS2Gen import RSS2, RSSItem
import datetime
from yaml import load
from docopt import docopt


def mapfileds(mapping, event):
    kwargs = {}
    for to_key, from_key in mapping.items():
        if isinstance(from_key, list):
            kwargs[to_key] = '\n\n'.join([event.get(k, '') for k in from_key])
        else:
            kwargs[to_key] = event.get(from_key, '')
    return kwargs


def yaml_to_rss(events, feed_config):
    items = [RSSItem(**mapfileds(feed_config['item_fileds_mapping'], event))
             for event in events]
    return RSS2(
        lastBuildDate=datetime.datetime.now(),
        items=items,
        **feed_config['feed_info'])


if __name__ == "__main__":
    arguments = docopt(__doc__)
    feed_config = load(open(arguments['OUTPUT_FEED_CONFIG'], 'r').read())
    events = load(open(arguments['EVENTS'], 'r').read())['upcoming_events']
    rss = yaml_to_rss(events=events, feed_config=feed_config)
    with open(feed_config['feed_output_file'], "w") as feed_output_file:
        rss.write_xml(feed_output_file)
