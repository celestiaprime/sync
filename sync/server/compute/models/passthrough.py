class PassthroughModel:
    def __init__(self):
        pass

    def run(self, inputs):
        return inputs["content"]