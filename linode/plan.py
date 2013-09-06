import re

from . import base, cache


class Plan(base.BaseObject):
    def __init__(self, api_key, id, label, disk_size):
        super(Plan, self).__init__(api_key, id)

        self.label = label
        self.disk_size = disk_size

    @classmethod
    def from_json(cls, api_key, data):
        return cls(
            api_key,
            id=data['PLANID'],
            label=data['LABEL'],
            disk_size=data['DISK'] * 1024
        )

    def __unicode__(self):
        return self.label

    def __eq__(self, value):
        if isinstance(value, basestring):
            return bool(re.search(value.lower() + '$', self.label.lower()))

        if isinstance(value, (int, long)):
            return value == self.id

        return False

    def __repr__(self):
        return '<{} id:{} {} at 0x{}>'.format(
            self.__class__.__name__,
            self.id,
            self.label,
            format(id(self), 'x')
        )


def load_plans(api_key):
    try:
        result = cache.read_from_cache('plans')
    except:
        result = base.make_single_call(
            api_key,
            'avail.linodeplans'
        )

        cache.write_to_cache('plans', result)

    for data in result:
        yield Plan.from_json(api_key, data)


def get_plan(api_key, label):
    return base.filter(load_plans(api_key), label)
