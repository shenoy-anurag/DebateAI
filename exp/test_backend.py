#!/usr/bin/env python

import asyncio
import websockets
import os
import json

COUNTER = 0

DEBATE_TOPIC = "Should the Transformer model be used as the primary architecture for all natural language processing tasks?"

RESPONSES = {
    0: "But Transformers are computationally expensive and overkill for simpler tasks like tokenization or spell-checking, where lightweight models suffice.",
    1: "Versatility doesn’t justify inefficiency—specialized architectures like RNNs or CNNs can achieve similar results with far fewer resources.",
    2: "Transfer learning still requires fine-tuning, which can be resource-intensive and impractical for low-resource languages or domains.",
    3: "Interpretability is limited—attention maps are often noisy and don’t always correlate with meaningful linguistic features.",
}


# Removed 'path' parameter as it's no longer needed in newer websockets versions
async def echo(websocket):
    try:
        async for message in websocket:
            print("Received message:", message, flush=True)
            # Echo the message back
            # global COUNTER, RESPONSES
            # await websocket.send(RESPONSES[COUNTER])
            # COUNTER += 1
            await websocket.send(message)
            await websocket.send("[END]")
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)


async def main():
    print("WebSocket server starting", flush=True)

    # Create the server with CORS headers
    async with websockets.serve(
        echo,
        "0.0.0.0",
        int(os.environ.get('PORT', 8090))
    ) as server:
        print("WebSocket server running on port 8090", flush=True)
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
