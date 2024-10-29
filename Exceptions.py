class FpdbError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class FpdbParseError(FpdbError):
    def __init__(self, value="", hand_id=""):
        self.value = value
        self.hand_id = hand_id

    def __str__(self):
        if self.hand_id:
            return repr(f"Hand Id: {self.hand_id}, {self.value}")
        else:
            return repr(self.value)
