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

There are two sides to the [SDK metrics](https://docs.temporal.io/references/sdk-metrics): worker metrics and client metrics.
This difference can be seen in the "Emitted by" column of the chart in the docs.

The client has metrics around number of requests (both long and short), their latency, and the number of failures.

The worker has more metrics. Some high-level groups are:

- activity execution (latencies, errors, cancellations, failures, etc)
- local activity execution (failed, cancelled, latencies, etc)
- pollers (number of them, etc)
- sticky cache (size, misses, hits, evictions)
- workers (task slots available and used)
- workflow execution (cancelled, completed, continued as new, failed, etc)
- workflow task execution (failed, latency, task queue polling, latencies)
- nexus (polling, task execution, etc)

### Rate limiting

Temporal Cloud is multitenant, so there are rate limits, such as actions per second (APS).
See the [documentation on Temporal Cloud's namespace level limits](https://docs.temporal.io/cloud/limits#namespace-level).

Because of this, we recommend setting up some metrics to detect if you're close to this limit.

### Scenarios and use-cases

#### Troubleshooting

You will use metrics to help troubleshoot and find root causes of issues.

Some of these might be

- workflows getting stuck (NDE, intermittent failures, etc)
- unexpected scenarios such as an infinite loop accidentally gets deployed to production
- unexpected high rates of signals, workflow executions, etc
- high latencies in specific areas, and you want to find what's causing it

#### Worker tuning

You may want a group of metrics to help guide you on further fine-tuning your worker fleet by scaling it up or down.
