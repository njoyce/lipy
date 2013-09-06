import re

from . import base, cache


class Kernel(base.BaseObject):
    def __init__(self, api_key, id, label):
        super(Kernel, self).__init__(api_key, id)

        self.label = label

    @classmethod
    def from_json(cls, api_key, data):
        return cls(
            api_key,
            id=data['KERNELID'],
            label=data['LABEL']
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


def load_kernels(api_key):
    try:
        result = cache.read_from_cache('kernels')
    except:
        result = base.make_single_call(
            api_key,
            'avail.kernels'
        )

        cache.write_to_cache('kernels', result)

    return [Kernel.from_json(api_key, data) for data in result]


def get_kernel(api_key, label):
    return base.filter(load_kernels(api_key), label)
