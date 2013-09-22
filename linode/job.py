import time

from . import base


class Job(base.BaseObject):
    def __init__(self, api_key, id, linode_id, action, label, entered, started,
                 finish, duration, message, success):
        super(Job, self).__init__(api_key, id)

        self.linode_id = linode_id
        self.action = action
        self.label = label
        self.entered = entered
        self.start = started
        self.finish = finish
        self.duration = duration
        self.message = message
        self.success = success

    @classmethod
    def from_json(cls, api_key, data):
        return cls(
            api_key,
            id=data['JOBID'],
            linode_id=data['LINODEID'],
            action=data['ACTION'],
            label=data['LABEL'],
            entered=base.convert_to_date(data['ENTERED_DT']),
            started=base.convert_to_date(data['HOST_START_DT']),
            finish=base.convert_to_date(data['HOST_FINISH_DT']),
            duration=base.convert_to_int(data['DURATION']),
            message=data['HOST_MESSAGE'],
            success=base.convert_to_bool(data['HOST_SUCCESS'])
        )

    def wait(self):
        """
        Wait for the job to finish
        """
        if self.finished:
            return self.job

        finished_job = waitany(self.api_key, self.linode_id, self.job_id)

        self.__dict__.clear()
        self.__dict__.update(finished_job.__dict__)


def convert_to_job_id(value):
    if isinstance(value, Job):
        return value.id

    if isinstance(value, (int, long)):
        return value

    return int(value)


def get(api_key, linode_id, *jobs, **kwargs):
    job_ids = map(convert_to_job_id, jobs)
    pending = kwargs.get('pending', None)

    batcher = base.APIBatcher(api_key)

    for job_id in job_ids:
        kwargs = dict(
            LinodeID=linode_id,
            JobID=job_id
        )

        if pending is not None:
            kwargs['pendingOnly'] = int(bool(pending))

        batcher.add(
            'linode.job.list',
            **kwargs
        )

    jobs = []

    for result in batcher.execute():
        try:
            data = result[0]
        except IndexError:
            yield None

            continue

        yield Job.from_json(api_key, data)


def waitall(api_key, linode_id, *jobs):
    """
    Waits for all jobs to be complete.
    """
    if not jobs:
        return []

    job_ids = map(convert_to_job_id, jobs)

    while True:
        pending_jobs = get(api_key, linode_id, *job_ids)

        if all(filter(lambda job: bool(job.finished), pending_jobs)):
            # all jobs are finished
            return jobs

        time.sleep(5)


def waitany(api_key, linode_id, *jobs):
    if not jobs:
        return []

    job_ids = map(convert_to_job_id, jobs)

    while True:
        pending_jobs = get(api_key, linode_id, *job_ids)

        for job in pending_jobs:
            if job.finished:
                return job

        time.sleep(5)
