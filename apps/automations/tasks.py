from config.celery import app


@app.task(queue="automations")
def send_scheduled_followups():
    return {"ok": True}

