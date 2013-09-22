from . import config as linode_config
from . import datacenter as linode_datacenter
from . import disk as linode_disk
from . import distribution as linode_distribution
from . import kernel as linode_kernel
from . import linode
from . import plan as linode_plan


def provision(api_key, root_password, datacenter, distribution, plan='1024',
              kernel=None, disk_size=None, swap=256, payment_term=1):
    """
    Create and boot a linode

    :param api_key: Linode API Key.
    :param root_password: The password to set for the distribution.
    :param datacenter: The location of the datacenter. See
        https://www.linode.com/wiki/index.php/Network
    :param distribution: The Linux distribution. See
        https://www.linode.com/faq.cfm#which-distributions-do-you-offer
    :param plan: Size in MB of RAM for linode. See
        https://manager.linode.com/signup/#plans
    :param kernel: The kernel version that you want to use. See
        https://www.linode.com/kernels/ The default is to use 'latest' for the
        distribution that you choose.
    :param disk_size: The size of the disk. The default is to use the maximum
        for the plan.
    :param swap: How much swap you want to create.
    :param payment_term: 1 = monthly, 12 = yearly, 24 = biannually
    """
    datacenter = linode_datacenter.get_datacenter(api_key, datacenter)
    plan = linode_plan.get_plan(api_key, plan)
    distribution = linode_distribution.get_distribution(api_key, distribution)

    if kernel:
        kernel = linode_kernel.get_kernel(api_key, kernel)
    else:
        kernel = 'Latest '

        if distribution.x64:
            kernel += '64 bit'
        else:
            kernel += '32 bit'

        kernel = linode_kernel.get_kernel(api_key, kernel)

    linode_instance = linode.create_linode(
        api_key,
        datacenter.id,
        plan.id,
        payment_term
    )

    try:
        create_disk(
            api_key,
            linode_instance,
            distribution,
            root_password,
            disk_size,
            swap
        )
        create_config(
            api_key,
            linode_instance,
            distribution,
            kernel
        )

        linode_instance.boot()
    except:
        linode_instance.delete(True)

        raise

    return linode_instance


def create_disk(api_key, linode_obj, distribution, root_password, size=None,
                swap=256, block=True):
    """
    Given an existing Linode instance, create a disk from the distribution and
    give it the maximum possible size (assuming that `size` is not provided).

    :param api_key: Linode API Key.
    :param linode_obj: The `linode` instance from `linode.create_instance` or
        similar.
    :param distribution: The `Distribution` instance to build the disk from.
    :param root_password: The password to set for the disk.
    :param size: Size to allocate for the disk. The default is to use the
        maximum.
    :param swap: The amount of swap to allocate for the instance.
    :param block: Whether to wait for the operation to complete.
    """
    jobs = []

    main_disk, main_job = linode_disk.create_from_distribution(
        api_key,
        linode_obj.id,
        distribution.id,
        '{} Disk Image'.format(distribution.label),
        linode_obj.plan.disk_size - swap,
        root_pass=root_password,
        block=False
    )

    jobs.append(main_job)

    if swap:
        swap_disk, swap_job = linode_disk.create_swap(
            api_key,
            linode_obj.id,
            swap,
            block=False
        )

        jobs.append(swap_job)

    if not block:
        return jobs

    for job in jobs:
        job.wait()


def create_config(api_key, linode_obj, distribution, kernel, **extra):
    if 'disk_list' not in extra:
        extra['disk_list'] = linode_obj.disks

    return linode_config.create_config(
        api_key,
        linode_obj.id,
        kernel.id,
        'My {} Profile'.format(distribution.label),
        **extra
    )
