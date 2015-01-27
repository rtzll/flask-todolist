# -*- coding: utf-8 -*-

import humanize

from . import filters_blueprint


@filters_blueprint.app_template_filter('humanize')
def humanize_time(datetime):
    return humanize.naturaltime(datetime)
