class Counter:

    def __init__(self):
        self.error = 0
        self.success = 0
        self.checkpoint = 0
        self.unverified = 0
        self.verified = 0
        self.consecutive_failures = 0
        self.consecutive_disabled = 0

    def get_success_checkpoint_rate(self):
        total = self.get_total_attempts()
        if total == 0:
            return 0.0, 0.0
        success_rate = round((self.success / total) * 100, 2)
        checkpoint_rate = round((self.checkpoint / total) * 100, 2)
        return success_rate, checkpoint_rate

    def get_total_attempts(self) -> int:
        total = self.success + self.checkpoint
        return total
