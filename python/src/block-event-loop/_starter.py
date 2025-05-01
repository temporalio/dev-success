import asyncio
import concurrent

from temporalio.client import Client
from temporalio.common import WorkflowIDReusePolicy
from temporalio.converter import (
    DataConverter,
)
from temporalio.worker import Worker

from activity import compose_greeting
from codec import EncryptionCodec
from converter import PydanticPayloadConverter
from test_types import ComposeGreetingRequest
from workflow import GreetingWorkflow


async def main():

    # runtime = init_runtime_with_prometheus(8086)

    # Start client
    client = await Client.connect(
        "localhost:7233",
        # runtime=runtime,
        data_converter=DataConverter(
            payload_converter_class=PydanticPayloadConverter,
            payload_codec=EncryptionCodec()
        )
    )


    tasks= []
    for i in range(200):
        tasks.append(asyncio.create_task(start_workflow(client, i)))

#    tasks = [asyncio.create_task(start_workflow(client, i))
#         for i in range(100)]


    await  asyncio.gather(*tasks)




async def start_workflow(client, i):
    workflowId = "hello-activity-workflow-id-" + str(i)
    result = await client.execute_workflow(
        GreetingWorkflow.run,
        ComposeGreetingRequest(id=str(i), name="World"),
        id=workflowId,
        task_queue="hello-activity-task-queue",
        # task_timeout=timedelta(seconds=120)
        id_conflict_policy=WorkflowIDReusePolicy.ALLOW_DUPLICATE
    )
    print(f"completed workflow id : {workflowId}")


if __name__ == "__main__":
    asyncio.run(main())
