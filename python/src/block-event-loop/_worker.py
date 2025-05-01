import asyncio
import concurrent

from temporalio.client import Client
from temporalio.converter import (
    DataConverter,
)
from temporalio.runtime import Runtime, TelemetryConfig, PrometheusConfig
from temporalio.worker import Worker

from activity import compose_greeting
from codec import EncryptionCodec
from converter import PydanticPayloadConverter
from workflow import GreetingWorkflow


def init_runtime_with_prometheus(port: int) -> Runtime:
    # Create runtime for use with Prometheus metrics
    return Runtime(
        telemetry=TelemetryConfig(
            metrics=PrometheusConfig(
                bind_address=f"127.0.0.1:{port}",
                histogram_bucket_overrides={
                    "temporal_workflow_task_execution_latency":
                        [100, 200, 500, 1000, 2000, 4000, 8000, 16000, 32000, 64000],
                },
            )
        )
    )


async def main():
    # Uncomment the lines below to see logging output
    # import logging

    #    os.environ["RUST_LOG"] = "temporal_sdk_core=DEBUG"

    #    logging.basicConfig(level=logging.DEBUG)

    runtime = init_runtime_with_prometheus(8086)

    # Start client
    client = await Client.connect(
        "localhost:7233",
        runtime=runtime,
        data_converter=DataConverter(
            payload_converter_class=PydanticPayloadConverter,
            payload_codec=EncryptionCodec()
        )
    )

    with concurrent.futures.ThreadPoolExecutor(max_workers=400) as activity_executor:
        worker = Worker(
            client,
            task_queue="hello-activity-task-queue",
            workflows=[GreetingWorkflow],
            activities=[compose_greeting],
            # max_cached_workflows=4,
            # max_concurrent_workflow_tasks=10,
            max_concurrent_workflow_task_polls=50,
            nonsticky_to_sticky_poll_ratio=0.5,
            max_concurrent_activity_task_polls=20,
            max_concurrent_activities=400,
            activity_executor=activity_executor,
        )

        await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
