"""Firebase Cloud Functions for Tasks."""

import datetime
import json

from firebase_admin import initialize_app
from google.cloud import tasks_v2
from firebase_functions import tasks, https
from firebase_functions.options import SupportedRegion, RetryConfig, RateLimits

app = initialize_app()


@tasks.on_task_dispatched(
    retry_config=RetryConfig(max_attempts=5),
    rate_limits=RateLimits(max_concurrent_dispatches=10),
    region=SupportedRegion.US_CENTRAL1,
)
def on_task_dispatched_function(req: tasks.CallableRequest):
    """
    The endpoint which will be executed by the enqueued task.
    """
    print(req)


@https.on_request()
def enqueue_task() -> https.Response:
    """
    Enqueues a task to the queue `on_task_dispatched_function`.
    """
    client = tasks_v2.CloudTasksClient()

    # The URL of the `on_task_dispatched_function` function.
    # Must be set to the URL of the deployed function.
    url = "https://on-task-dispatched-function-4afum6lama-uc.a.run.app"

    payload: dict = {
        "name": "John Doe",
    }
    task: tasks_v2.Task = tasks_v2.Task(
        **{
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": url,
                "headers": {
                    "Content-type": "application/json"
                },
                "body": json.dumps(payload).encode(),
            },
            "schedule_time":
                datetime.datetime.utcnow() + datetime.timedelta(minutes=1),
        })

    parent = client.queue_path(
        app.project_id,
        SupportedRegion.US_CENTRAL1,
        on_task_dispatched_function.__name__.replace("_", "-"),
    )

    client.create_task(request={"parent": parent, "task": task})
    return https.Response("Task enqueued.")
