"Detect  New Pools Created on Solana Raydium DEX"

# TODO Add Buys ,Sells price and liquidity pool tracking management
from flask import Flask, render_template
from flask_socketio import SocketIO
from threading import Thread 
import asyncio
import sys
import websockets
import json
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solders.signature import Signature
import pandas as pd
from tabulate import tabulate


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

wallet_address = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
seen_signatures = set()
solana_client = Client("https://api.mainnet-beta.solana.com")


def getTokens(str_signature):
    signature = Signature.from_string(str_signature)
    transaction = solana_client.get_transaction(signature, encoding="jsonParsed",
                                                max_supported_transaction_version=0).value
    instruction_list = transaction.transaction.transaction.message.instructions

    for instructions in instruction_list:
        if instructions.program_id == Pubkey.from_string(wallet_address):
            print("============NEW POOL DETECTED====================")
            Token0 = instructions.accounts[8]
            Token1 = instructions.accounts[9]
            # Your data
            data = {'Token_Index': ['Token0', 'Token1'],
                    'Account Public Key': [Token0, Token1]}

            df = pd.DataFrame(data)
            table = tabulate(df, headers='keys', tablefmt='fancy_grid')
            print(table)

            return data
    return None


async def run():
    # uri = "wss://api.mainnet-beta.solana.com"
    uri = "ws://api.mainnet-beta.solana.com"

    async with websockets.connect(uri) as websocket:
        # Send subscription request
        await websocket.send(json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "logsSubscribe",
            "params": [
                {"mentions": [wallet_address]},
                {"commitment": "finalized"}
            ]
        }))

        first_resp = await websocket.recv()
        response_dict = json.loads(first_resp)
        if 'result' in response_dict:
            print("Subscription successful. Subscription ID: ", response_dict['result'])

        # Continuously read from the WebSocket
        async for response in websocket:

            response_dict = json.loads(response)

            if response_dict['params']['result']['value']['err'] == None:
                signature = response_dict['params']['result']['value']['signature']

                if signature not in seen_signatures:
                    seen_signatures.add(signature)
                    log_messages_set = set(response_dict['params']['result']['value']['logs'])

                    search = "initialize2"
                    if any(search in message for message in log_messages_set):
                        print(f"True, https://solscan.io/tx/{signature}")
                        data = getTokens(signature)
                        if data:
                            socketio.emit('new_pair', data)

            else:
                pass


async def main():
    await run()


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


# asyncio.run(main())
def start_websocket_listener():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run())


if __name__ == '__main__':
    # Start the WebSocket listener in a separate thread
    websocket_thread = Thread(target=start_websocket_listener)
    websocket_thread.start()

    # Start the Flask application with SocketIO
    socketio.run(app, debug=True)





# streamlit code
# from datetime import datetime


# async def get_transaction_info(str_signature):
#     signature = Signature.from_string(str_signature)
#     try:
#         transaction = solana_client.get_transaction(signature, encoding="jsonParsed",
#                                                     max_supported_transaction_version=0).value
#         instruction_list = transaction.transaction.transaction.message.instructions

#         new_pools = []
#         for instructions in instruction_list:
#             if instructions.program_id == Pubkey.from_string(wallet_address):
#                 Token0 = instructions.accounts[8]
#                 Token1 = instructions.accounts[9]
#                 timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#                 new_pools.append((Token0, Token1, timestamp))
#         return new_pools
#     except Exception as e:
#         print(f"Error getting transaction info for {str_signature}: {e}")
#         return []

# async def run(output_queue):
#     uri = "wss://api.mainnet-beta.solana.com"
#     async with websockets.connect(uri) as websocket:
#         await websocket.send(json.dumps({
#             "jsonrpc": "2.0",
#             "id": 1,
#             "method": "logsSubscribe",
#             "params": [
#                 {"mentions": [wallet_address]},
#                 {"commitment": "finalized"}
#             ]
#         }))

#         await websocket.recv()  # Ignore the response for subscription confirmation

#         async for response in websocket:
#             response_dict = json.loads(response)
#             if response_dict.get('params', {}).get('result', {}).get('value', {}).get('err') is None:
#                 signature = response_dict['params']['result']['value']['signature']

#                 if signature not in seen_signatures:
#                     seen_signatures.add(signature)
#                     new_pools = await get_transaction_info(signature)
#                     if new_pools:
#                         output_queue.put_nowait(new_pools)

# async def tracker_main(output_queue):
#     await run(output_queue)

# if __name__ == "__main__":
#     output_queue = asyncio.Queue()
#     asyncio.run(tracker_main(output_queue))