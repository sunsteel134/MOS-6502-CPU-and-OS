class mems:
    def __init__(self):
        self.memory = []
        for _ in range(65536):
            self.memory.append(0)
