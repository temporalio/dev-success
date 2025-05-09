# Python Worker and Activity Configuration

This page is to consolidate some important parts of Python worker and activity configuration.

> Please update to the latest version of the Python SDK, because we are
> frequently improving things and making configuration easier. For
> example, see [this PR](https://github.com/temporalio/sdk-python/pull/806).

## Python SDK Worker Execution Architecture

Python workers have following components for executing code:

- Your event loop, which runs tasks from async activities **plus the rest of Temporal, such as communicating with the server**
- An executor for executing activity tasks from synchronous activities. A thread pool executor is recommended
- A thread pool executor for executing workflow tasks (see forum post [here](https://community.temporal.io/t/whats-the-workflow-task-executor-in-the-python-worker-configuration/16965))

> See Also: [docs for `worker.__init__()`](https://python.temporal.io/temporalio.worker.Worker.html#__init__)

## Activity Definition

**By default, activities should be synchronous (`def`), rather than asynchronous (`async def`)**.
You should only make an activity `async def` if you are *very*
sure that it does not block the event loop.

This is because if you have blocking code in an `async def` function,
it blocks your event loop and the rest of Temporal, which can cause bugs that are
very hard to diagnose, including freezing your worker and blocking workflow progress
(because Temporal can't tell the server that workflow tasks are completing).
The reason synchronous activities help is because they
run in the `activity_executor` ([docs for `worker.__init__()`](https://python.temporal.io/temporalio.worker.Worker.html#__init__))
rather than in the global event loop,
which helps because:

1. There's no risk of accidentally blocking the global event loop
2. If you have multiple
   activity tasks running in a thread pool rather than an event loop, one bad
   activity task can't slow down the others; this is because the OS scheduler preemptively
   switches between threads, which the event loop coordinator does not do.

> See Also:
> ["Types of Activities" section of Python SDK README](https://github.com/temporalio/sdk-python#types-of-activities)
> and [Sync vs Async activity implementations](https://docs.temporal.io/develop/python/python-sdk-sync-vs-async)

### Running synchronous code from an asynchronous function

If your activity is `async def` (not `def`) and you don't want to change that,
but you need to run blocking code inside it,
then you can use python utility functions to run synchronous code
in an asynchronous function:

- [`loop.run_in_executor()`](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.run_in_executor), which is also mentioned in the ["running blocking code" section of the "developing with asyncio" guide](https://docs.python.org/3/library/asyncio-dev.html#running-blocking-code)
- [`asyncio.to_thread()`](https://docs.python.org/3/library/asyncio-task.html#running-in-threads)

## Number of Cores on your worker hardware

If the following two conditions hold, then
your worker will only use one CPU core,
and your worker would be indifferent to any additional cores:

1. You're only running one worker on your worker hardware
2. You follow the recommendation and use a thread pool executor rather than
   a process pool executor for your synchronous activities

## Other Options

To minimize risks or use more cores,
you could deploy separate workers for workflow tasks and activity tasks.

## Further Reading

Chad from the SDK team wrote a great blog about the Python SDK.
In particular, [this section](https://temporal.io/blog/durable-distributed-asyncio-event-loop#temporal-workflows-are-asyncio-event-loops)
is very relevant and can help with a deeper understanding of
how the SDK works.
