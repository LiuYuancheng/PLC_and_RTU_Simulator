import asyncio
import opcuaComm

async def main():
    client = opcuaComm.opcuaClient("opc.tcp://localhost:4840/testServer/server/")
    await client.connect()
    val = await client.getVariableVal('newNameSpace01', 'newObject01', 'newVariable01')
    print(val)
    await client.setVariableVal('newNameSpace01', 'newObject01', 'newVariable01', 0.22)
    val = await client.getVariableVal('newNameSpace01', 'newObject01', 'newVariable01')
    print(val)
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())