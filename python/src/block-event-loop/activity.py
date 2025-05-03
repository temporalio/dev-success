import time

from temporalio import activity

from test_types import ComposeGreetingInput

@activity.defn
def compose_greeting(input_data: ComposeGreetingInput) -> str:

    start_time = time.time()

    for i in range(5):
        # Simulate some work
       time.sleep(0.1) # This blocks the event loop

    end_time = time.time()

    return f"{input_data.greeting}, {input_data.name}, Activity duration: {end_time - start_time} seconds!"
