from . import base, job


class Disk(base.BaseObject):
    def __init__(self, api_key, id, label, type, linode_id, status, size,
                 read_only):
        super(Disk, self).__init__(api_key, id)

        self.label = label
        self.type = type
        self.linode_id = linode_id
        self.status = status
        self.size = size

    @classmethod
    def from_json(cls, api_key, data):
        return cls(
            api_key,
            id=data['DISKID'],
            label=data['LABEL'],
            type=data['TYPE'],
            linode_id=data['LINODEID'],
            read_only=data['ISREADONLY'],
            status=data['STATUS'],
            size=data['SIZE']
        )

    def delete(self, block=True):
        """
        Delete this disk from the associated linode.
        """
        response = self.make_call(
            'linode.disk.delete',
            LinodeID=self.linode_id,
            DiskID=self.id
        )

        delete_job = job.get(self.api_key, self.linode_id, response['JobID'])

        if block:
            delete_job.wait()

        return delete_job

    def update(self):
        self.make_call(
            'linode.disk.update',
            LinodeID=self.linode_id,
            DiskID=self.id,
            Label=self.label,
            isReadOnly=self.read_only
        )

    def resize(self, new_size, block=True):
        response = self.make_call(
            'linode.disk.resize',
            LinodeID=self.linode_id,
            DiskID=self.id,
            size=new_size
        )

        self.size = new_size

        resize_job = job.get(self.api_key, self.linode_id, response['JobID'])

        if block:
            resize_job.wait()

        return resize_job


def get_by_linode(api_key, linode_id):
    """
    Returns the Disk objects associated with a given Linode
    """
    response = base.make_linode_call(
        api_key,
        'linode.disk.list',
        LinodeID=linode_id
    )

    for data in response['DATA']:
        yield Disk.from_json(api_key, data)


def _get_disk_from_response(api_key, linode_id, response, block):
    disk_id = response['DiskID']
    job_id = response['JobID']

    for disk in get_by_linode(api_key, linode_id):
        if disk.id == disk_id:
            break

        disk = None

    if not disk:
        raise RuntimeError('Could not find disk from Linode API')

    disk_job = job.get(api_key, linode_id, job_id)

    if not disk_job:
        return disk, None

    if block:
        disk_job.wait()

    return disk, disk_job


def create_from_distribution(api_key, linode_id, distribution_id, label, size,
                             root_pass, block=True):
    response = base.make_single_call(
        api_key,
        'linode.disk.createfromdistribution',
        LinodeID=linode_id,
        DistributionID=distribution_id,
        Label=label,
        Size=size,
        rootPass=root_pass
    )

    return _get_disk_from_response(api_key, linode_id, response, block)


def create_swap(api_key, linode_id, size, label=None, block=True):
    label = label or '{}MB Swap Image'.format(size)

    response = base.make_single_call(
        api_key,
        'linode.disk.create',
        LinodeID=linode_id,
        Label=label,
        Type='swap',
        Size=size
    )

    return _get_disk_from_response(api_key, linode_id, response, block)
