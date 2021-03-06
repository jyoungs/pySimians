import datetime
import logging
import os.path
import random

from supermonkey import Monkey

logger = logging.getLogger('chaos')


class ChaosMonkey(Monkey):

    CONFIG_SECTION = "chaos"

    def __init__(self, config_file, scheduler, tweet):
        super(ChaosMonkey, self).__init__(config_file, scheduler, tweet)
        if self.is_enabled():
            scheduler.add_job(self.time_of_the_monkey, trigger='cron',
                              **dict(self.get_schedule()))
        self.last_run = None

    def time_of_the_monkey(self):
        """Create some chaos"""
        if not self.should_run():
            return
        chaos_script = random.choice(self.load_scripts())
        chaos = os.path.basename(chaos_script)
        logger.info("Selected random script: '%s'" % chaos)
        vm = random.choice(self.get_all_ips())
        logger.info("Selected random machine '%s'" % vm)
        ret_code, _, stderr = self.run_script_on_host(vm, chaos_script,
                                                      daemonize=True)
        if ret_code == 0:
            self.tweet("Haha! Just ran '%s' on '%s'." % (chaos, vm))
            logger.info("Ran '%s' on '%s'." % (chaos, vm))
            self.last_run = datetime.datetime.now()
        else:
            logger.info(stderr)

    def should_run(self):
        cooloff = int(self.config.get("chaos", "cooloff"))
        if self.last_run and datetime.datetime.now() - datetime.timedelta(
                hours=cooloff) < self.last_run:
            logger.info("Cooloff period. Chaos monkey will not run.")
            return False
        probability = float(self.config.get("chaos", "probability"))
        if random.random() > probability:
            return False
        return True
