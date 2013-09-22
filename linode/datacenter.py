from . import base, cache


class Datacenter(base.BaseObject):
    def __init__(self, api_key, id, location):
        super(Datacenter, self).__init__(api_key, id)

        self.location = location

    @classmethod
    def from_json(cls, api_key, data):
        return cls(
            api_key,
            id=data['DATACENTERID'],
            location=data['LOCATION']
        )

    def __unicode__(self):
        return self.location

    def __eq__(self, value):
        if isinstance(value, basestring):
            return self.location.lower().startswith(value.lower())

        if isinstance(value, (int, long)):
            return value == self.id

        return False

    def __repr__(self):
        return '<{} id:{} {} at 0x{}>'.format(
            self.__class__.__name__,
            self.id,
            self.location,
            format(id(self), 'x')
        )


def load_datacenters(api_key):
    try:
        result = cache.read_from_cache('datacenters')
    except:
        result = base.make_single_call(
            api_key,
            'avail.datacenters'
        )

        cache.write_to_cache('datacenters', result)

    return [Datacenter.from_json(api_key, data) for data in result]


def get_datacenter(api_key, location):
    return base.filter(load_datacenters(api_key), location)
