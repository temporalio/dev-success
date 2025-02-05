# Observability and Worker Tuning Worksheet

This worksheet is to guide worker tuning and observability sessions.


## Understand the current place in the Temporal journey

- Are you just starting out with Temporal?
  - Do you have a Namespace?
- Are you already running in production?
  - If so, you have cloud metrics?
  - If so, do you have worker/SDK metrics?


## Understand Use Case

What is the scale, required performance, and required throughput?

Some example distinguishers:

- Is there a ton of throughput that needs quick responses and low latency?
  Compared with use cases that are background processing tasks that don't have latency requirements.


- are you rate limiting activities? (this more-or-less translates to "are you rate limiting downstream services?")
  - for example, if they're talking to a banking API that's rate limited, which means their activities will have large schedule-to-start latencies. don't alert on this
  - if they aren't rate limiting on that, then schedule-to-start would be a good thing to alert on

## Understand Tech Stack

- What SDK?
  - Be sure to look through samples repos (in temporalio GitHub, there are repos for each SDK such as *samples-python*)

## General Guidelines

- thy need checks in place to not kill their workers --
  - this is going over their resources... two of them: CPU and memory
  - the most important metric that the customers should always observe is resource utilization on their SDK workers
    - they need this before they can make any sense of the temporal metrics

- what do the server metrics represent? a view on the namespace level
  - they can't translate that into an overall state of their application
  - they may have more than one application on that namespace
  - understand that the cloud metrics are per namespace, and they don't have the ability to look more granularly
  - if we need something more specific, then we have to look at their worker metrics
  - it's easier for customers to set up cloud metrics, but it's harder for them to set up worker metrics.
- worker metrics
  - very useful to get a more fine-grained view into their situation.

- there are two sides to the worker metrics
  - worker metrics + client metrics
    - client:
      - signal, query, etc... clients that start the execution vs the clients that actually are running the code (i.e. workers)
      - such as failures to starting and signalling workflows

## Unsorted


  - rate limiting -- customer has to understand that we're multitenant on cloud... there are limits. RPS, APS, etc. We need to make sure they know how to detect if they're getting close to this
  - cloud metrics -- customers ask how to set it up, then you send them the link, then they ask how often the numbers get updated, etc.


- we don't see their worker metrics
  - because we don't have their metrics,
  - we have a dashboards repo
    - ==we should revive this== -- a lot of important things are missing from there
- let's say we have a customer who's about to run in production and they generally have their stuff set up. the difficulty becomes where to start. Temporal has a million metrics. The game is not just listing things for them. What helps is to talk about them by certain groupings
- troubleshooting -- finding issues and root causes
  - workflows getting stuck (NDE, intermittent failures, etc)
  - grouping: unexpected
  - clients doing something dumb -- somebody writes an infinite loop etc
  - unexpected high rates of signals, workflow executions, etc
  - grouping of latency metrics
  - subgroup of worker tuning
  - having a mental grouping of all the metrics up front is very helpful.
  - ask the customer... what's important to you? is it latency, is it this, is it that, etc?
