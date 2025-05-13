import threading
from queue import Queue, Empty

class Stage:
    def process(self, records):
        raise NotImplementedError("Stage.process must be implemented by subclasses")

class Pipeline:
    def __init__(self, parallel=False, concurrency=1):
        self.stages = []
        self.parallel = parallel
        self.concurrency = concurrency

    def add_stage(self, stage):
        self.stages.append(stage)

    def run(self, records):
        data = records
        for stage in self.stages:
            if hasattr(stage, 'process'):
                data = stage.process(data)
            else:
                raise RuntimeError(f"Stage {stage} has no process method")
        return data

    def run_async(self, records):
        if not self.parallel or self.concurrency < 1:
            return self.run(records)
        input_queue = Queue()
        output_queue = Queue()
        for r in records:
            input_queue.put(r)
        def worker():
            while True:
                try:
                    item = input_queue.get_nowait()
                except Empty:
                    break
                data = [item]
                for stage in self.stages:
                    data = stage.process(data)
                for out in data:
                    output_queue.put(out)
                input_queue.task_done()
        threads = []
        for _ in range(self.concurrency):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        results = []
        while not output_queue.empty():
            results.append(output_queue.get())
        return results
