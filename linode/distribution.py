import re

from . import base, cache


class Distribution(base.BaseObject):
    def __init__(self, api_key, id, label, x64, min_size, vops_kernel):
        super(Distribution, self).__init__(api_key, id)

        self.label = label
        self.x64 = x64
        self.min_size = min_size
        self.vops_kernel = vops_kernel

    @classmethod
    def from_json(cls, api_key, data):
        return cls(
            api_key,
            id=data['DISTRIBUTIONID'],
            label=data['LABEL'],
            x64=data['IS64BIT'],
            min_size=data['MINIMAGESIZE'],
            vops_kernel=data['REQUIRESPVOPSKERNEL']
        )

    def __unicode__(self):
        return self.label

    def __eq__(self, value):
        if isinstance(value, basestring):
            return bool(re.search(value.lower(), self.label.lower()))

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


def load_distributions(api_key):
    try:
        result = cache.read_from_cache('distributions')
    except:
        result = base.make_single_call(
            api_key,
            'avail.distributions'
        )

        cache.write_to_cache('distributions', result)

    for data in result:
        yield Distribution.from_json(api_key, data)


def get_distribution(api_key, label):
    return base.filter(load_distributions(api_key), label)
