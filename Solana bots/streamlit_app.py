import streamlit as st
from NewPairTracker import tracker_main
import asyncio

# not working with asyncio
st.title("Main Page")
st.write("This is the main page for the Solana Bot")

def run_tracker(output_queue):
    asyncio.run(tracker_main(output_queue))

output_queue = asyncio.Queue()

# start tracking
if st.button('Start Tracking'):
    asyncio.run(tracker_main(output_queue))

# show new pairs
st.write("Detected New Pools:")
container = st.container()
while not output_queue.empty():
    new_pool_info = output_queue.get_nowait()
    Token0, Token1, timestamp = new_pool_info
    container.write(f"Token0: {Token0}, Token1: {Token1}, Detected at: {timestamp}")

# import streamlit as st
# import asyncio
# from datetime import datetime
# from NewPairTracker import tracker_main
# from asyncio import Queue


# output_queue = Queue()

# async def tracker_runner(output_queue):
#     await tracker_main(output_queue)

# def main():
#     # Layout your app beforehand, with st.empty for widgets that the async function would populate
#     status_text = st.empty()
#     start_button = st.button('Start Tracking')

#     # Place to display new pools
#     new_pools_display = st.empty()

#     if start_button:
#         status_text.text('Tracking started...')

#         # Use asyncio.create_task to run tracker_main without blocking
#         asyncio.create_task(tracker_runner(output_queue))

#         # Display a message that tracking has started
#         status_text.text('Tracking new pools. Please wait...')

#     # Display new pool info from output_queue
#     try:
#         while True:
#             # Check if there are items in the queue without blocking
#             if not output_queue.empty():
#                 new_pool_info = output_queue.get_nowait()
#                 Token0, Token1, timestamp = new_pool_info
#                 new_pools_display.write(f"Token0: {Token0}, Token1: {Token1}, Detected at: {timestamp}")

#             # Sleep for a short period to ensure UI remains responsive
#             asyncio.sleep(0.1)
#     except asyncio.CancelledError:
#         # Handle cancellation of the tracker_runner task if needed
#         status_text.text('Tracking stopped.')

# if __name__ == '__main__':
#     asyncio.run(main())

