from . import base


class IP(base.BaseObject):
    def __init__(self, api_key, id, linode_id, address, public):
        super(IP, api_key, id)

        self.linode_id = linode_id
        self.address = address
        self.public = public

    @classmethod
    def from_json(cls, api_key, data):
        return cls(
            api_key,
            id=data['IPADDRESSID'],
            linode_id=data['LINODEID'],
            address=data['IPADDRESS'],
            public=data['ISPUBLIC']
        )


def get_by_linode(api_key, linode_id, address_id=None):
    response = base.make_single_call(
        api_key,
        'linode.ip.list',
        LinodeID=linode_id,
        IPAddressID=address_id
    )

    if address_id:
        return IP.from_json(api_key, response[0])

    return [IP.from_json(api_key, data) for data in response]


def add_private(api_key, linode_id):
    """
    Assigns a Private IP to a Linode.

    :returns: An `IP` instance corresponding to the version created.
    """
    response = base.make_single_call(
        api_key,
        'linode.ip.addprivate',
        LinodeID=linode_id
    )

    return get_by_linode(api_key, linode_id, response['IPAddressID'])
