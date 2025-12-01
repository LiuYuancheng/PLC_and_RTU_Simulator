# async_opcua_server.py
import asyncio
import random
from asyncua import ua, Server


async def main():
    # Create server
    server = Server()
    await server.init()

    server.set_endpoint("opc.tcp://0.0.0.0:4840/asyncua/server/")

    # Register namespace
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    # Add object and variable
    objects_node = server.get_objects_node()
    myobj = await objects_node.add_object(idx, "AsyncDevice")
    temp_var = await myobj.add_variable(idx, "Temperature", 20.0)
    await temp_var.set_writable()

    print("Async OPC UA Server started at: opc.tcp://0.0.0.0:4840/asyncua/server/")

    async with server:
        while True:
            new_value = random.uniform(18.0, 28.0)
            await temp_var.write_value(new_value)
            print(f"Temperature updated: {new_value:.2f}")
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
