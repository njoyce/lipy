from . import base, datacenter, plan, ip, job, disk


class Linode(base.BaseObject):
    def __init__(self, api_key, id, label, datacenter_id, plan_id,
                 loaded=False):
        super(Linode, self).__init__(api_key, id)

        self.label = label
        self.datacenter_id = datacenter_id
        self.plan_id = plan_id

    @classmethod
    def from_json(cls, api_key, data):
        return cls(
            api_key,
            id=data['LINODEID'],
            datacenter_id=data['DATACENTERID'],
            plan_id=data['PLANID'],
            label=data['LABEL'],
            loaded=True
        )

    @property
    def plan(self):
        if hasattr(self, '_plan'):
            return self._plan

        if not self.plan_id:
            return

        self._plan = plan.get_plan(self.api_key, self.plan_id)

        return self._plan

    @plan.setter
    def plan(self, value):
        self.plan_id = value.id
        self._plan = value

    @property
    def datacenter(self):
        if hasattr(self, '_datacenter'):
            return self._datacenter

        if not self.datacenter_id:
            return

        self._datacenter = datacenter.get_datacenter(self.datacenter_id)

        return self._datacenter

    @datacenter.setter
    def datacenter(self, value):
        self.datacenter_id = value.id
        self._dc = value

    def boot(self, block=True):
        """
        Boot the linode.
        """
        return boot_linode(self.api_key, self.id, block=block)

    def get_public_ip(self):
        for addr in self.get_ips():
            if addr.public:
                return addr

    def get_private_ip(self):
        for addr in self.get_ips():
            if not addr.public:
                return addr

    def get_ips(self):
        return ip.get_by_linode(self.api_key, self.id)

    def add_private_ip(self):
        addr = ip.add_private_ip(self.api_key, self.id)

        return addr

    def disks(self):
        return disk.get_by_linode(self.api_key, self.id)

    def remove(self, skip_check):
        self.client(
            'linode.delete',
            LinodeID=self.id
        )


def list_linodes(api_key, linode_id=None):
    kwargs = {}

    if linode_id:
        kwargs['LinodeID'] = linode_id

    response = base.make_single_call(
        api_key,
        'linode.list',
        **kwargs
    )

    return [Linode.from_json(api_key, data) for data in response]


def get_by_id(api_key, linode_id):
    """
    Helper method to get a linode by a specific id
    """
    try:
        return list_linodes(api_key, linode_id)[0]
    except IndexError:
        return None


def boot_linode(api_key, linode_id, config_id=None, block=True):
    """
    Boot a linode.

    If `block` is `True` then block the current thread until the boot
    completes.

    :returns: The Job instances associated with the build request.
    """
    kwargs = {
        'LinodeID': linode_id
    }

    if config_id:
        kwargs['ConfigID'] = config_id

    response = base.make_single_call(
        api_key,
        'linode.boot',
        **kwargs
    )

    boot_job = job.get(api_key, linode_id, response['JobID'])

    if block:
        boot_job.wait()

    return boot_job


def clone_linode(api_key, linode_id, datacenter_id, plan_id, payment_term):
    """
    Creates a new Linode, assigns you full privileges, and then clones the
    specified `linode_id` to the new Linode. There is a limit of 5 active clone
    operations per source Linode. It is recommended that the source Linode be
    powered down during the clone.
    """
    response = base.make_single_call(
        api_key,
        'linode.clone',
        LinodeID=linode_id,
        DatacenterID=datacenter_id,
        PlanID=plan_id,
        PaymentTerm=payment_term
    )

    cloned_id = response['LinodeID']

    return get_by_id(api_key, cloned_id)


def create_linode(api_key, datacenter_id, plan_id, payment_term):
    """
    Creates a Linode and assigns you full privileges. There is a
    75-linodes-per-hour limiter in place.
    """
    response = base.make_single_call(
        api_key,
        'linode.create',
        DatacenterID=datacenter_id,
        PlanID=plan_id,
        PaymentTerm=payment_term
    )

    return get_by_id(api_key, response['LinodeID'])


def delete_linode(api_key, linode_id, skip_checks=False):
    """
    Immediately removes a Linode from your account and issues a pro-rated
    credit back to your account, if applicable.

    To prevent accidental deletes, this requires the Linode has no Disk images.
    You must first delete its disk images.
    """
    base.make_single_call(
        api_key,
        'linode.delete',
        LinodeID=linode_id,
        skipChecks=skip_checks
    )


def reboot_linode(api_key, linode_id, config_id=None, block=True):
    """
    Reboot a linode.

    If `block` is `True` then block the current thread until the boot
    completes, otherwise return the `Job` instance.
    """
    kwargs = {
        'LinodeID': linode_id
    }

    if config_id:
        kwargs['ConfigID'] = config_id

    response = base.make_single_call(
        api_key,
        'linode.reboot',
        **kwargs
    )

    reboot_job = job.get(api_key, linode_id, response['JobID'])

    if block:
        reboot_job.wait()

    return reboot_job


def resize_linode(api_key, linode_id, plan_id):
    """
    This is a weird one - would have expected a JobID response here.
    """
    base.make_single_call(
        api_key,
        'linode.resize',
        LinodeID=linode_id,
        PlanID=plan_id
    )

    # expect some sort of Job here


def shutdown_linode(api_key, linode_id, block=True):
    """
    Issues a shutdown job for a given LinodeID.

    If `block` is `True` then block the current thread until the shutdown
    completes.
    """
    response = base.make_single_call(
        api_key,
        'linode.shutdown',
        LinodeID=linode_id,
    )

    shutdown_job = job.get(api_key, linode_id, response['JobID'])

    if block:
        shutdown_job.wait()

    return shutdown_job
