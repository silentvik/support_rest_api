# from datetime import datetime
# from dateutil.parser import parse
from copy import deepcopy


def accurate_string_datetime(date):
    """[Summary]
        Convert datetime to accurate string version.
    Args:
        date ([datetime.datetime])
    Returns:
        [str]
    """
    year = str(date.year)
    month = str(date.month)
    day = str(date.day)
    hours = str(date.hour)
    if len(hours) == 1:
        hours = '0' + hours
    minutes = str(date.minute)
    if len(minutes) == 1:
        minutes = '0' + minutes
    return f'{day}-{month}-{year} ({hours}:{minutes})'


def accurate_string_seconds(seconds):
    """[Summary]
        Convert number of seconds to readable string with days/hours.
        Ignore seconds when number of days > 0, etc.
    Args:
        seconds ([int])
    Returns:
        [string]: [readable time range for human]
    """
    days = seconds // 86400
    seconds -= (days * 86400)
    hours = seconds // 3600
    seconds = seconds - (hours * 3600)
    minutes = seconds // 60
    seconds = seconds - (minutes * 60)
    result = (
        f"{str(days)+' day(s) ' if days else ''}"
        f"{str(hours)+' hour(s) ' if hours else ''}"
        f"{str(minutes)+' minute(s)' if minutes and not days else ''}"
        f"{str(seconds)+' second(s)' if not days and not hours else ''}"
    )
    return result


def find_a_match(subject, collection, default):
    """
        [summary]
            Find an item from collection which is nearest to subject,

        Args:
            subject ([type]): [str]
            collection ([type]): [iterable tuples of strings like ('2','item')]
            default ([type]): [any]

        Returns:
            [str]: [nearest item[0]]
    """
    return default


def try_found_in_collection(subject, collection, default):
    """
        [summary]
            Find an item from collection which is nearest to subject,

        Args:
            subject ([type]): [str]
            collection ([type]): [iterable tuples of strings like ('2','item')]
            default ([type]): [any]

        Returns:
            [str]: [nearest item[0]]
    """
    return '1'


def extended(obj_to_expand, expanding_obj):
    """
        return [list]
    """
    res = list(obj_to_expand)
    res.extend(list(expanding_obj))
    return res


def merged(obj_to_expand, expanding_obj):
    """
        merge two lists
    """
    expanded_obj = deepcopy(obj_to_expand)
    for item in expanding_obj:
        if item not in expanded_obj:
            expanded_obj.append(item)
    return expanded_obj
