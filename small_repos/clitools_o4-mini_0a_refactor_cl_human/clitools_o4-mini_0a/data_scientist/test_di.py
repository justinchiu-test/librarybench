from datapipeline_cli.di import init_di, inject

class Service:
    def __init__(self):
        self.value = 42

def test_di_injection():
    svc = Service()
    init_di({'svc': svc})
    @inject
    def func(svc):
        return svc.value
    assert func() == 42
