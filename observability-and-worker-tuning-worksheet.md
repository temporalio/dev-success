# Observability and Worker Tuning Worksheet

This worksheet is to guide worker tuning and observability sessions.

Note that we highly recommended watching this [in-depth Temporal Worker Q&A](https://www.youtube.com/watch?v=pwr-Ss6WEco&list=PLytZkHFJwKUcMbOKCQmiVnoGUQTJOAndQ).

## Understand the current place in the Temporal journey

- Are you just starting out with Temporal?
  - Do you have a Namespace?
- Are you already running in production?
  - If so, do you have cloud metrics?
  - If so, do you have worker/SDK metrics?

## Understand Use Case

### Scale, performance, and throughput requirements

What are the scale, required performance, and required throughput?
Is there a ton of throughput that needs quick responses and low latency?
Contrast this with use cases that are background processing tasks that don't have latency requirements.

### Rate limiting activities

Are you rate limiting activities?
This oftentimes translates to "are you rate limiting downstream services?"
For example, if your application calls a banking API that's rate limited, then your activities will need to be rate limited, so they will have large schedule-to-start latencies.
In this case, you wouldn't want to alert on schedule-to-start latencies.
Contrast that with if you aren't rate limited on activities or downstream services -- in this case, then schedule-to-start would be a good thing to alert on.

## Understand Tech Stack

What SDK are you using?
Be sure to look through its samples repos (in [temporalio GitHub](https://github.com/orgs/temporalio/repositories), there are repos for each SDK such as [samples-python](https://github.com/temporalio/samples-python)).

## General Guidelines

### Monitor worker CPU and memory usage

You should always have a way to monitor your worker memory and CPU usage.
This is often a prerequisite to understanding any other metrics.

### Server metrics are at the namespace level

Server metrics operate at the namespace level -- they don't get more granular than that.
If you have more than one application running in your namespace, and you need fine-grained visibility into them individually, you can only do that with worker/SDK metrics.

### Worker metrics and client metrics

There are two sides to the SDK metrics: worker metrics and client metrics.

- client:
  - signal, query, etc... clients that start the execution vs the clients that actually are running the code (i.e. workers)
  - such as failures to starting and signalling workflows

### Yet-to-be-sorted

  - rate limiting -- customer has to understand that we're multitenant on cloud... there are limits. RPS, APS, etc. We need to make sure they know how to detect if they're getting close to this

## Yet-to-be-sorted


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
