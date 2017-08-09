import functools
import logging
import shlex
import subprocess
import itertools
import enum

log = logging.getLogger(__name__)


class JobStatus(enum.Enum):
    WAITING = enum.auto()
    RUNNING = enum.auto()
    FINISHED = enum.auto()
    SUSPENDED = enum.auto()


class Build:
    def __init__(self, repo, ref, cmd):
        self._repo = repo
        self._ref = ref
        self._cmd = cmd
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
        self.id = next(self._ids)
        self.priority = priority
        self.build = build
        self.sub = None
        log.debug('New %s created. %r', self.__class__.__name__, self)

    def __eq__(self, other):
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
        self.sub = subprocess.Popen(shlex.split(self.build._cmd),
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)


class JobQueue:
    def __init__(self, max_running_builds=2):
        self._max_running_builds = max_running_builds

        self._jobs = dict()
        for status in JobStatus:
            self._jobs[status] = list()

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

        job = self.get_job_by_build(build)  # check if given build has already a job
        if job:
            log.debug('Build has already a job: Job#%s Prio: %s',
                      job.id,
                      job.priority)
            return False
        else:
            job = Job(build, priority)
            self._jobs[JobStatus.WAITING].append(job)
            self._jobs[JobStatus.WAITING].sort()

            log.debug('New job #%s with priority %r', job.id, job.priority)
            return True

    def _run_next_jobs(self, n=1):
        for i in range(0, n):
            if self._jobs[JobStatus.WAITING]:
                next_job = self._jobs[JobStatus.WAITING].pop()
                next_job.run()
                self._jobs[JobStatus.RUNNING].append(next_job)
                log.debug('Job#%s is running now', next_job.id)
            else:
                log.debug('No waiting jobs!')
                break

    def get_job_by_build(self, build):
        for job in itertools.chain(self._jobs[JobStatus.FINISHED],
                                   self._jobs[JobStatus.RUNNING],
                                   self._jobs[JobStatus.SUSPENDED],
                                   self._jobs[JobStatus.WAITING]):
            if job.build == build:
                return job
        return None

    def run(self):
        for job in self._jobs[JobStatus.RUNNING]:
            if job.sub.poll() is None:
                log.debug('Job#%s:%s is still running', job.id, job.priority)
            else:
                self._jobs[JobStatus.FINISHED].append(job)
                self._jobs[JobStatus.RUNNING].remove(job)
                log.debug('Job#%s:%s is done', job.id, job.priority)
        self._run_next_jobs(self._max_running_builds - len(self._jobs[JobStatus.RUNNING]))

    def log_info(self):
        log.info('=================================')
        log.info(self)
        if self._jobs[JobStatus.WAITING]:
            log.info('Next Job: #%s priority %s (cmd: %s)',
                     self._jobs[JobStatus.WAITING][-1].id,
                     self._jobs[JobStatus.WAITING][-1].priority,
                     self._jobs[JobStatus.WAITING][-1].build._cmd)

    def __contains__(self, build):
        for job in self:
            if job.build == build:
                return True
        else:
            return False

    def __str__(self):
        return ' '.join(['{status}: {count}'.format(status=status.name, count=len(self._jobs[status])) for status in JobStatus])

    def __iter__(self):
        return itertools.chain(self._jobs[JobStatus.FINISHED],
                               self._jobs[JobStatus.RUNNING],
                               self._jobs[JobStatus.SUSPENDED],
                               self._jobs[JobStatus.WAITING])
