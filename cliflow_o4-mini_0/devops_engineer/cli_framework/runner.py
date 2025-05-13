import subprocess
from .context import Context

def run_dry_run(context, cmd, **kwargs):
    if not isinstance(context, Context):
        raise ValueError("context must be a Context instance")
    context.run_hooks('pre-command', cmd)
    if context.dry_run:
        print(f"DRY RUN: {cmd}")
        result = subprocess.CompletedProcess(cmd, 0, stdout=b'', stderr=b'')
    else:
        try:
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, **kwargs)
            context.run_hooks('post-command', cmd, result)
        except subprocess.CalledProcessError as e:
            context.run_hooks('on-error', cmd, e)
            raise
    return result
