import os

class CLIManager:
    def scaffold_experiment(self, name):
        path = os.path.join("experiments", name)
        os.makedirs(path, exist_ok=True)
        return path

    def run_pipeline_locally(self, pipeline_func, verbose=False):
        if verbose:
            print(f"Running in verbose mode")
        return pipeline_func()
