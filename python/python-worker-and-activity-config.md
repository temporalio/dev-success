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
