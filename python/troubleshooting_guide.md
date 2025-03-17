# Python Troubleshooting Guide

This section provides a list of common issues and solutions for troubleshooting when using the 
[Temporal Python SDK](https://github.com/temporalio/sdk-python). Always refer first to the [sdk-python documentation](https://github.com/temporalio/sdk-python) and the 
[official documentation](https://docs.temporal.io/develop/python/) for the most up-to-date information.

If you landed here by accident, please feel free to reach out through the [community channels](https://temporal.io/community) or open a 
[support ticket](https://support.temporal.io/) if you are a Temporal Cloud customer.

## WorkflowTaskTimeout
- [What is a Workflow Task Timeout?](https://docs.temporal.io/encyclopedia/detecting-workflow-failures#workflow-task-timeout)


### Possible Causes and Solutions

#### The gRPC payload size exceed the [limit](https://docs.temporal.io/cloud/limits#per-message-grpc-limit).

A common scenario is when there is a large number of activities (or child workflows) scheduled concurrently in a loop. This can cause the gRPC payload size to exceed the limit.

##### Possible solutions
- Split the loop in batches to reduce the payload size.
- Use data converters to compress the payloads or 
[store the data in an external storage service](https://docs.temporal.io/production-deployment/data-encryption#working-with-large-payloads).


#### The thread inside an async def Python function is blocked
According to the [Python SDK Documentation](https://github.com/temporalio/sdk-python?tab=readme-ov-file#asynchronous-activities)
`⚠️ WARNING: Do not block the thread in async def Python functions. This can stop the processing of the rest of the Temporal.`

Blocking the thread can significantly delay execution, potentially leading to a WorkflowTaskTimeout. 

##### Possible solutions
- configure the workers to run activities in a different thread  https://github.com/temporalio/sdk-python?tab=readme-ov-file#synchronous-multithreaded-activities
- use `asyncio.to_thread(my_blocking_func)` or `asyncio.get_running_loop().run_in_executor(None, my_blocking_func)` to run the blocking code inside the async function.
- if you are unsure if an activity makes blocking calls, convert the async activities into synchronous ones ([docs](https://docs.temporal.io/develop/python/python-sdk-sync-vs-async#when-should-you-use-async-activities)).
- see the ["Registering Activities" page of the Python 101 course](https://temporal.talentlms.com/catalog/info/id:143) for guidance on sync and async activities.
