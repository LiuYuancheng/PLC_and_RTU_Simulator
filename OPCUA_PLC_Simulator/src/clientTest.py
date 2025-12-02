import asyncio
import opcuaComm

VAR_ID1 = 'variable01'
VAR_ID2 = 'variable02'
VAR_ID3 = 'variable03'
VAR_ID4 = 'variable04'

def showTestResult(expectVal, val, message):
    rst = "[o] %s pass." %message if val == expectVal else "[x] %s error, expect:%s, get: %s." %(message, str(expectVal), str(val))
    print(rst)


async def main():

    print("[_] Test client connection")
    serverName = 'TestPlc01'
    serverUrl = "opc.tcp://localhost:4840/%s/server/" %serverName
    client = opcuaComm.opcuaClient(serverUrl)
    await client.connect()

    #r1 = await client.getVariableVal('newNameSpace01', 'newObject01', VAR_ID1)
    #showTestResult(1, r1, "client read int value1")
    #asyncio.sleep(1)
    #await client.disconnect()
    
    r2 = asyncio.run(client.getVariableVal('newNameSpace01', 'newObject01', VAR_ID2))
    showTestResult(1.1, r2, "client read float value1")
    #r3 = asyncio.run(client.getVariableVal('newNameSpace01', 'newObject01', VAR_ID3))
    #showTestResult(True, r3, "client read float value1")
    #r4 = asyncio.run(client.getVariableVal('newNameSpace01', 'newObject01', VAR_ID4))
    #showTestResult('1.1', r4, "client read float value1")


    # client = opcuaComm.opcuaClient("opc.tcp://localhost:4840/TestPlc01/server/")
    # await client.connect()
    # val = await client.getVariableVal('newNameSpace01', 'newObject01', 'newVariable01')
    # print(val)
    # await client.setVariableVal('newNameSpace01', 'newObject01', 'newVariable01', 0.22)
    # val = await client.getVariableVal('newNameSpace01', 'newObject01', 'newVariable01')
    # print(val)
    # await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())