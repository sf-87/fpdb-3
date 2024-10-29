import base64
import win32event

class InterProcessLockWin32(object):
    def __init__(self, name=None):
        self.name = name
        self.has_lock = False
        self.mutex = None

    def get_hashed_name(self):
        return base64.b64encode(self.name.encode()).replace(b"=", b"").decode()

    def acquire(self, source):
        if source is None:
            source = "Unknown"

        if self.has_lock:  # make sure 2nd acquire in same process fails
            return False

        self.mutex = win32event.CreateMutex(None, 0, self.get_hashed_name())
        self.has_lock = True

        return True

    def release(self):
        self.mutex.Close()
        self.has_lock = False
