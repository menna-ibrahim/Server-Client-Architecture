class Packet:
    def __init__(self, msg, timestamp):
        self.msg = msg
        self.timestamp = timestamp
        self.thread_id = thread_id

    def __lt__(self, other):
        return self.timestamp < other.timestamp