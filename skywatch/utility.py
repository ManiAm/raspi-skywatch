
import operator
from functools import reduce


def elapsed_format(sec_elapsed, short=False):

    if not sec_elapsed:
        return ""

    intervals = (
        ('days', 86400),    # 60 * 60 * 24
        ('hours', 3600),    # 60 * 60
        ('minutes', 60),
        ('seconds', 1),
    )

    format_t = {}
    for name, count in intervals:
        value = sec_elapsed // count
        if value:
            sec_elapsed -= value * count
        format_t[name] = value

    d = format_t['days']
    h = format_t['hours']
    m = format_t['minutes']
    s = format_t['seconds']

    if not short:

        if d > 0:
            return "%s days and %s hours and %s minutes and %s seconds" % (format(d, '.2f'), format(h, '.2f'), format(m, '.2f'), format(s, '.2f'))
        if h > 0:
            return "%s hours and %s minutes and %s seconds" % (format(h, '.2f'), format(m, '.2f'), format(s, '.2f'))
        if m > 0:
            return "%s minutes and %s seconds" % (format(m, '.2f'), format(s, '.2f'))
        if s > 0:
            return "%s seconds" % (format(s, '.2f'))
        if not any([d, h, m, s]):
            return "%s milliseconds" % (format(sec_elapsed*100, '.2f'))

    else:

        if d > 0:
            return "%sd %sh %sm %ss" % (format(d, '.2f'), format(h, '.2f'), format(m, '.2f'), format(s, '.2f'))
        if h > 0:
            return "%sh %sm %ss" % (format(h, '.2f'), format(m, '.2f'), format(s, '.2f'))
        if m > 0:
            return "%sm %ss" % (format(m, '.2f'), format(s, '.2f'))
        if s > 0:
            return "%ss" % (format(s, '.2f'))
        if not any([d, h, m, s]):
            return "%sms" % (format(sec_elapsed*100, '.2f'))

    return ""


def get_value(dictionary, key_list):

    try:
        return reduce(operator.getitem, key_list, dictionary)
    except Exception:
        return None
