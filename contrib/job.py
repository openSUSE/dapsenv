import functools
import logging
import shlex
import subprocess
import itertools
import enum

log = logging.getLogger(__name__)


class JobStatus(enum.Enum):
    WAITING, RUNNING, FINISHED, SUSPENDED = range(4)


class Build:
    def __init__(self, repo, ref, cmd):
        self._repo = repo
        self._ref = ref
        self.cmd = cmd
        log.debug("New %s created: %r",
                  self.__class__.__name__,
                  self)

    def __str__(self):
        return 'Repo:{} Ref:{}'.format(self._repo, self._ref)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (self._repo, self._ref) == (other._repo, other._ref)

    def __hash__(self):
        return hash((self._repo, self._ref))


@functools.total_ordering
class Job:
    _ids = itertools.count(0)

    def __init__(self, build, priority):
        """ Create a new Job.

        Args:
            build (object): Build instance
            priority (int): Priority, high value means high priority
        """
        self.id = next(self._ids)
        self.priority = priority
        self.build = build
        self.sub = None  # subprocess
        self.status = JobStatus.WAITING
        log.debug('New %s created. %r', self.__class__.__name__, self)

    def __eq__(self, other):
        """ Two jobs are considered equal if their prioritys are equal. """
        return self.priority == other.priority

    def __lt__(self, other):
        return self.priority < other.priority

    def __str__(self):
        return 'Id:{} Prio:{} Build:{}'.format(self.id,
                                               self.priority,
                                               self.build)

    def __repr__(self):
        return self.__str__()

    def run(self):
        """ Starts the build as subprocess. """
        self.sub = subprocess.Popen(shlex.split(self.build.cmd),
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)


class JobQueue:
    def __init__(self, max_running_builds=2):
        self._max_running_builds = max_running_builds

        self._jobs = list()

    def push(self, build, priority):
        """Add a new job to the queue

        Checks if `build` is not allready waiting, building or finished and
        pushes the new job to the waiting queue.

        Args:
            build (obj): Build object
            priority (int): Job priority.
        Returns:
            bool: True if successful, False otherwise.
        """

        job = self.get_job_by_build(build)  # check if build has already a job
        if job:
            log.debug('Build has already a job: Job#%s Prio: %s',
                      job.id,
                      job.priority)
            return False
        else:
            job = Job(build, priority)
            self._jobs.append(job)

            log.debug('New job #%s with priority %r', job.id, job.priority)
            return job.id

    def _run_next_jobs(self, n=1):
        for i in range(0, n):
            if self.jobs_of_status(JobStatus.WAITING):
                next_job = max(self.jobs_of_status(JobStatus.WAITING))
                next_job.run()
                next_job.status = JobStatus.RUNNING
                log.debug('Job#%s is running now', next_job.id)
            else:
                log.debug('No waiting jobs!')
                break

    def get_job_by_build(self, build):
        for job in self._jobs:
            if job.build == build:
                return job
        return None

    def run(self):
        for job in self.jobs_of_status(JobStatus.RUNNING):
            if job.sub.poll() is None:
                log.debug('Job#%s:%s is still running', job.id, job.priority)
            else:
                job.status = JobStatus.FINISHED
                log.debug('Job#%s:%s is done', job.id, job.priority)
        self._run_next_jobs(self._max_running_builds -
                            len(self.jobs_of_status(JobStatus.RUNNING)))

    def jobs_of_status(self, status):
        """ Return a list of jobs with the given status
        Args:
            status (enum): Status from JobStatus
        """
        return [job for job in self._jobs if job.status == status]

    def log_info(self):
        log.info('=================================')
        log.info(self)
        if self.jobs_of_status(JobStatus.WAITING):
            next_job = max(self.jobs_of_status(JobStatus.WAITING))
            log.info('Next Job: #%s priority %s (cmd: %s)',
                     next_job.id,
                     next_job.priority,
                     next_job.build.cmd)

    def __contains__(self, build):
        for job in self:
            if job.build == build:
                return True
        else:
            return False

    def __str__(self):
        stats = [(status.name, len(self.jobs_of_status(status)))
                 for status in JobStatus]
        return ' '.join(['{status}: {count}'.format(status=stat[0],
                                                    count=stat[1])
                         for stat in stats])

    def __iter__(self):
        return itertools.chain(self._jobs[JobStatus.FINISHED],
                               self._jobs[JobStatus.RUNNING],
                               self._jobs[JobStatus.SUSPENDED],
                               self._jobs[JobStatus.WAITING])
