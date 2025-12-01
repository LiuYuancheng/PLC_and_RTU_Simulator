import asyncio
from asyncua import Client


async def main():
    client = Client("opc.tcp://0.0.0.0:4840/testServer/server/")
    await client.connect()

    print("Client connected!")

    # Browse for the variable
    root = client.get_root_node()
    
    # Path to our object → "Objects" → "AsyncDevice" → "Temperature"
    temp_var = await root.get_child(["0:Objects", "2:newObject01", "2:newVariable01"])

    try:
        while True:
            val = await temp_var.read_value()
            print("Temperature:", val)
            await asyncio.sleep(1)

    finally:
        await client.disconnect()
        print("Client disconnected.")


if __name__ == "__main__":
    asyncio.run(main())