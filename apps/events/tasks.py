from config.celery import app

from .services import ingest_event


@app.task(queue="events")
def ingest_event_task(payload):
    event = ingest_event(payload)
    return event.id
