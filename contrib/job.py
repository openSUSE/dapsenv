import functools
import logging
import shlex
import subprocess
import itertools

log = logging.getLogger(__name__)


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

    def __init__(self, build, prio):
        self.id = next(self._ids)
        self.prio = prio
        self.build = build
        self.sub = None
        log.debug('New %s created. %r', self.__class__.__name__, self)

    def __eq__(self, other):
        return self.prio == other.prio

    def __lt__(self, other):
        return self.prio < other.prio

    def __str__(self):
        return 'Id:{} Prio:{} Build:{}'.format(self.id,
                                               self.prio,
                                               self.build)

    def __repr__(self):
        return self.__str__()

    def run(self):
        self.sub = subprocess.Popen(shlex.split(self.build._cmd),
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)


class JobQueue:
    def __init__(self, max_jobs=4, max_running_builds=2):
        self._max_jobs = max_jobs
        self._max_running_builds = max_running_builds
        self._waiting = []
        self._running = []
        self._finished = []

    def push(self, build, prio):
        """Add a new job to the queue

        Checks if `build` is not allready waiting, building or finished and
        pushes the new job to the waiting queue.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        job = self.get_job(build)
        if not job:
            job = Job(build, prio)
            self._waiting.append(job)
            self._waiting.sort()
            log.debug('New job #%s with prio %r', job.id, job.prio)
            return True
        else:
            log.debug('Build has allready an job: Job#%s Prio: %s',
                      job.id,
                      job.prio)
            return False

    def _run_next_jobs(self, n=1):
        for i in range(0, n):
            if self._waiting:
                next_job = self._waiting.pop()
                next_job.run()
                self._running.append(next_job)
                log.debug('Job#%s is running now', next_job.id)
            else:
                log.debug('No waiting jobs!')
                break

    def get_job(self, build):
        for job in self._waiting + self._running + self._finished:
            if job.build == build:
                return job
        return None

    def run(self):
        for job in self._running:
            if job.sub.poll() is None:
                log.debug('Job#%s:%s is still running', job.id, job.prio)
            else:
                self._finished.append(job)
                self._running.remove(job)
                log.debug('Job#%s:%s is done', job.id, job.prio)
        self._run_next_jobs(self._max_running_builds - len(self._running))

    def log_info(self):
        log.info('=================================')
        log.info('JW: %s', len(self._waiting))
        log.info('JR: %s', len(self._running))
        log.info('JF: %s', len(self._finished))
        if self._waiting:
            log.info('Next Job: #%s prio %s (cmd: %s)',
                     self._waiting[-1].id,
                     self._waiting[-1].prio,
                     self._waiting[-1].build._cmd)

    def __contains__(self, build):
        for job in self._waiting:
            if job.build == build:
                return True
        for job in self._running:
            if job.build == build:
                return True
        return False

    def __str__(self):
        return ' '.join(['{}#{}'.format(job.id, job.prio)
                        for job in self._waiting])
