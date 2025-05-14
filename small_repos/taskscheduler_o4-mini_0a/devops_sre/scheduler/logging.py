import logging

def attach_log_context(job_id, target_host, schedule_type):
    logger = logging.getLogger(__name__)
    extra = {'job_id': job_id, 'target_host': target_host, 'schedule_type': schedule_type}
    return logging.LoggerAdapter(logger, extra)
