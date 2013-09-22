from . import base


_missing = object()

_field_mapping = {
    'linode_id': 'LinodeID',
    'config_id': 'ConfigID',
    'kernel_id': 'KernelID',
    'label': 'Label',
    'comments': 'Comments',
    'ram_limit': 'RAMLimit',
    'disk_list': 'DiskList',
    'run_level': 'RunLevel',
    'root_device_num': 'RootDeviceNum',
    'root_device_custom': 'RootDeviceCustom',
    'root_device_ro': 'RootDeviceRO',
    'disable_update_db': 'helper_disableUpdateDB',
    'xen': 'helper_xen',
    'depmod': 'helper_depmod',
    'devtmpfs_automount': 'devtmpfs_automount',
}


class Config(base.BaseObject):
    def __init__(self, api_key, id, **kwargs):
        super(Config, self).__init__(api_key, id)

        for py_name in _field_mapping:
            value = kwargs[py_name]

            setattr(self, py_name, value)

    @classmethod
    def from_json(cls, api_key, data):
        config_dict = {}

        for py_name, li_name in _field_mapping.items():
            config_dict[py_name] = data[li_name]

        config_dict.pop('ConfigID', None)

        return cls(
            api_key,
            data['ConfigID'],
            **config_dict
        )

    def update(self):
        fields = self.__dict__.copy()

        fields.pop('api_key')
        fields.pop('linode_id')
        fields.pop('config_id')

        update_config(self.api_key, self.linode_id, self.id, **fields)

    def delete(self):
        delete_config(self.api_key, self.linode_id, self.id)


def get_disk_list(value):
    if isinstance(value, basestring):
        return value

    if not isinstance(value, list):
        return value

    ret = []

    for disk in value:
        if isinstance(disk, (basestring, int)):
            ret.append(str(disk))

            continue

        ret.append(str(disk.id))

    for _ in xrange(9 - len(ret)):
        ret.append('')

    return ','.join(ret)


def _dict_to_request(obj):
    """
    Convert a dict of python keyword arguments to a form suitable for
    consumption by the Linode API.
    """
    ret = {}

    for py_name, li_name in _field_mapping.items():
        value = obj.get(py_name, _missing)

        if value is _missing:
            continue

        if py_name == 'disk_list':
            value = get_disk_list(value)

        ret[li_name] = value

    return ret


def create_config(api_key, linode_id, kernel_id, label, **kwargs):
    """
    Creates a Linode Configuration Profile.
    """
    request = _dict_to_request(kwargs)

    request.update({
        'LinodeID': linode_id,
        'KernelID': kernel_id,
        'Label': label
    })

    response = base.make_single_call(
        api_key,
        'linode.config.create',
        **request
    )

    return list_config(api_key, linode_id, response['ConfigID'])[0]


def update_config(api_key, linode_id, config_id, **kwargs):
    request = _dict_to_request(kwargs)

    request.update({
        'LinodeID': linode_id,
        'ConfigID': config_id,
    })

    base.make_single_call(
        api_key,
        'linode.config.update',
        **request
    )


def delete_config(api_key, config_id, linode_id):
    """
    Deletes a Linode Configuration Profile.
    """
    base.make_single_call(
        api_key,
        'linode.config.delete',
        LinodeID=linode_id,
        ConfigID=config_id,
    )


def list_config(api_key, linode_id, config_id=None):
    """
    Lists a Linode's Configuration Profiles.
    """
    kwargs = {
        'LinodeID': linode_id,
    }

    if config_id:
        kwargs['ConfigID'] = config_id

    response = base.make_single_call(
        api_key,
        'linode.config.list',
        **kwargs
    )

    return [Config.from_json(api_key, data) for data in response]
