from copy import deepcopy


def accurate_string_datetime(date):
    """[Summary]
        Converts datetime to accurate readable string version.
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
        Converts number of seconds to a readable string with days/hours or hours/minutes etc.
        Ignore seconds when number of days > 0.
        Args:
            seconds ([int])
        Returns:
            [str]: readable time range for human
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
        f"{str(minutes)+' minute(s) ' if minutes and not days else ''}"
        f"{str(seconds)+' second(s)' if not days and not hours else ''}"
    )
    if result[-1] == ' ':
        result = result[:-1]
    return result


def merged(obj_to_expand, expanding_obj):
    """
        merge two lists, returns a new list obj w copied items.
    """
    expanded_obj = deepcopy(obj_to_expand)
    expanding_obj = deepcopy(expanding_obj)
    for item in expanding_obj:
        if item in expanded_obj:
            expanded_obj.remove(item)
        expanded_obj.append(item)
    return expanded_obj


def popped_dict(dictionary, keys_list):
    """
        Softly pop all items in [keys_list] from [dictionary]
        Return popped dictionary (new)
    """
    dictionary_copy = deepcopy(dictionary)
    [dictionary_copy.pop(key, None) for key in keys_list]
    return dictionary_copy


def find_a_match(subject, collection, default_choice):
    """ it may be deleted

        Find an item from collection which is nearest to subject.
        Args:
            subject ([type]): [str]
            collection ([type]): [iterable tuples of strings like ('2','item')]
            default ([type]): [any]
        Returns:
            [str]: [nearest item[0]]
    """
    return default_choice


def extended(obj_to_expand, expanding_obj):
    """
        Args: [list] [list]
        returns extended [list]
    """
    res = list(obj_to_expand)
    res.extend(list(expanding_obj))
    return res
