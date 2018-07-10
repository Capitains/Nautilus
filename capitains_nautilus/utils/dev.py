class DevPool:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def map(self, func, kwargs):
        for kwarg in kwargs:
            yield func(kwarg)

    def close(self):
        pass

    def join(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass