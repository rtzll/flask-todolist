# -*- coding: utf-8 -*-

from datetime import datetime
import time

from . import utils


# Thanks to Dan Jacob and Sean Vieira for making the following snippet
# available at http://flask.pocoo.org/snippets/33/
@utils.app_template_filter('humanize')
def humanize_time(dt, past_='ago', future_='from now', default='just now'):
    """
    Returns string representing 'time since'
    or 'time until' e.g.
    3 days ago, 5 hours from now etc.
    """

    now = datetime.utcnow()
    # remove tzinfo
    dt = dt.replace(tzinfo=None)
    if now > dt:
        diff = now - dt
        dt_is_past = True
    else:
        diff = dt - now
        dt_is_past = False

    periods = (
        (diff.days // 365, 'year', 'years'),
        (diff.days // 30, 'month', 'months'),
        (diff.days // 7, 'week', 'weeks'),
        (diff.days, 'day', 'days'),
        (diff.seconds // 3600, 'hour', 'hours'),
        (diff.seconds // 60, 'minute', 'minutes'),
        (diff.seconds, 'second', 'seconds'),
    )

    for period, singular, plural in periods:

        if period:
            return '%d %s %s' % (
                period,
                singular if period == 1 else plural,
                past_ if dt_is_past else future_
            )

    return default


@utils.app_template_filter('in_seconds')
def in_seconds(dt):
    # return int((dt - datetime(1970, 1, 1)).total_seconds())
    return int(time.mktime(dt.timetuple()))
