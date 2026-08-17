import time

class Timer:
    def __init__(self, duration:float):
        self.duration = duration # in seconds
        self.time_left = 0
        self.active = False
        self.paused = False
        self.start_time = 0

    def start(self):
        """Starts or resets the timer."""
        self.active = True
        self.paused = False
        self.time_left = self.duration
        self.start_time = time.monotonic()
        # Monotonic: continuously ticks forward + won't break if system clock changes abruptly.

    def toggle_pause(self, force:bool|None=None):
        """ Toggles the paused state. force=True explicitly pauses, force=False explicitly resumes. """
        # We can't pause or resume a timer that isn't running
        if not self.active:
            return

        # Determine the intended state: toggle if None, otherwise use the forced state
        pause_intended = not self.paused if force is None else force

        # Pause
        if pause_intended and not self.paused:
            self.update()  # Lock in time_left right now
            self.paused = True
        # Resume
        elif not pause_intended and self.paused:
            already_elapsed = self.duration - self.time_left
            self.start_time = time.monotonic() - already_elapsed
            self.paused = False

    def update(self):
        """Calculates elapsed time and updates the timer state."""
        if self.active:
            elapsed_time = time.monotonic() - self.start_time
            # Ensure time_left doesn't drop below 0
            self.time_left = max(0, self.duration - elapsed_time)
            self.active = self.time_left > 0
        return self.active
    
    def progress(self, scale:float=1.0):
        """Returns the completion progress scaled to the given value."""
        if self.duration <= 0:
            return 0
        return min(1.0, (self.duration - self.time_left)/self.duration) * scale