import asyncio

from temporalio.client import Client
from temporalio.common import WorkflowIDReusePolicy
from temporalio.converter import (
    DataConverter,
)

from codec import EncryptionCodec
from converter import PydanticPayloadConverter
from test_types import ComposeGreetingRequest
from workflow import GreetingWorkflow


async def main():

    # Start client
    client = await Client.connect(
        "localhost:7233",
        data_converter=DataConverter(
            payload_converter_class=PydanticPayloadConverter,
            payload_codec=EncryptionCodec()
        )
    )


    tasks= []
    for i in range(200):
        tasks.append(asyncio.create_task(start_workflow(client, i)))


    await  asyncio.gather(*tasks)




async def start_workflow(client, i):
    workflowId = "hello-activity-workflow-id-" + str(i)
    await client.execute_workflow(
        GreetingWorkflow.run,
        ComposeGreetingRequest(id=str(i), name="World"),
        id=workflowId,
        task_queue="hello-activity-task-queue",
        # for this example I want to terminate workflows with the same id so they start new every time
        # we run the script
        id_conflict_policy=WorkflowIDReusePolicy.TERMINATE_IF_RUNNING
    )
    print(f"completed workflow id : {workflowId}")


if __name__ == "__main__":
    asyncio.run(main())
