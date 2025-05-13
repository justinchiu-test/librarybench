from flask import Flask, jsonify, request

def create_app(scheduler):
    app = Flask(__name__)

    @app.route("/jobs/<tenant_id>", methods=["GET"])
    def list_jobs(tenant_id):
        jobs = scheduler.list_jobs(tenant_id)
        return jsonify(jobs), 200

    @app.route("/jobs/<job_id>/pause", methods=["POST"])
    def pause_job(job_id):
        scheduler.pause_job(job_id)
        return "", 204

    @app.route("/jobs/<job_id>/resume", methods=["POST"])
    def resume_job(job_id):
        scheduler.resume_job(job_id)
        return "", 204

    @app.route("/jobs/<job_id>/cancel", methods=["POST"])
    def cancel_job(job_id):
        scheduler.cancel_job(job_id)
        return "", 204

    @app.route("/jobs/<job_id>", methods=["DELETE"])
    def remove_job(job_id):
        scheduler.remove_job(job_id)
        return "", 204

    @app.route("/jobs/<job_id>/concurrency", methods=["POST"])
    def set_concurrency(job_id):
        data = request.get_json()
        scheduler.set_concurrency(job_id, data.get("limit"))
        return "", 204

    @app.route("/global/concurrency", methods=["POST"])
    def set_global_concurrency():
        data = request.get_json()
        scheduler.set_global_concurrency(data.get("limit"))
        return "", 204

    @app.route("/jobs/<job_id>/priority", methods=["POST"])
    def set_priority(job_id):
        data = request.get_json()
        scheduler.set_priority(job_id, data.get("level"))
        return "", 204

    @app.route("/dump", methods=["POST"])
    def dump_jobs():
        data = request.get_json()
        path = data.get("path")
        scheduler.dump_jobs(path)
        return "", 204

    @app.route("/load", methods=["POST"])
    def load_jobs():
        data = request.get_json()
        path = data.get("path")
        scheduler.load_jobs(path)
        return "", 204

    @app.route("/catchup", methods=["POST"])
    def catchup():
        scheduler.catch_up_missed_jobs()
        return "", 204

    return app
