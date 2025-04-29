#-----------------------------------------------------------------------------
# Name:        modbusTcpComTest.py
#
# Purpose:     testcase program used to test lib module <modbusTcpCom.py> 
#
# Author:      Yuancheng Liu, Jun Heng Sim
#
# Created:     2023/06/21
# Version:     v_0.1.4
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License 
#-----------------------------------------------------------------------------

import time
import threading
import modbusTcpCom

class testModbusClientThread(threading.Thread):
    """
    This class is a subclass that inherits from the threading.Thread class. 
    It extends the functionality of the thread with additional attributes and 
    methods specific to testing ModBus TCP client communication.
    
    Attributes:
        client: Represents modbusTcpClient object.

    Methods:
        __init__(): Initialises the testModbusClientThread object
        run(): Establishes a connection to a ModBus server and checks the connection. Refer
        to the method description for more details.
        closeClient(): Terminates the ModBus TCP client connection.

    Unit Test Methods:
        getCoilBitsTest(): Performs a unit test for the getCoilsBits() method of the 
        ModbusTcpClient object. Refer to the method description for more details.

        getHoldingRegsTest(): Performs a unit test for getHoldingRegs() method of the
        ModbusTcpClient object. Refer to the method description for more details.

        setCoilBitsTest(): Performs a unit test for the setCoilsBit() method of the 
        ModbusTcpClient object. Refer to the method description for more details.

        setHoldingRegsTest(): Performs a unit test for setHoldingRegs() method of the
        ModbusTcpClient object. Refer to the method description for more details.

        autoUpdateCoilTest(): Performs an integration test for updateState() method of the
        plcDataHandler object. Refer to the method description for more details.
    """
    def __init__(self, parent, threadID, name):
        super().__init__(parent)
        self.client = None

    def run(self):
        """
        Overrides the run() method from the threading.Thread class. It will
        establish a connection to a ModBus server and checks the connection.
        Returns:
            None
        Raises:
            Exception: If the creation of the ModBus TCP client fails
        Examples:
            client = testModbusClientThread(None, 1, "Client Thread")
            client.start()
        """
        networkConfig = {'hostIP':'127.0.0.1', 'hostPort': 502}
        client = modbusTcpCom.modbusTcpClient(networkConfig['hostIP'])
        if client:
            self.client = client
        else:
            raise Exception("Test Failed: Unable to initialise ModBus Client")
        while not self.client.checkConn():
            print('Attempting connection to PLC')
            print(client.getCoilsBits(0, 4))
            time.sleep(0.5)
    
    def closeClient(self):
        """
        Terminates the ModBus TCP client connection
        Returns:
            None
        Raises:
            None
        Examples:
            >>> client = testModbusClientThread(None, 1, "Client Thread")
            >>> client.start()
            >>> client.closeClient()
        """
        self.client.close()

#---------------------------------------------------------------------------
# Define unit tests methods for the following ModbusTCPCom client functions:
#   - getCoilsBits()
#   - getHoldingRegs()
#   - setCoilsBits()
#   - setHoldingRegs()

    def getCoilBitsTest(self, readInput, expectedOutput, testID):
        """
        Performs a unit test for getCoilsBits() method of the ModbusTcpClient object. 
        It compares the actual output with the expected output and raises an assertion 
        error if they do not match.
        Args:
            readInput (int, int): The first argument representing addressIdx and offset.
            expectedOutput (list): The second argument representing the expected output.
            testID (int): The third argument representing the ID tagged to this test run.
        Returns:
            None
        Raises:
            AssertionError: If actualOutput != expectedOutput.
        Examples:
            Assumption: 
                - Coil bits current state [1, 1, 0, 0]
            >>> getCoilBitsTest((0, 4), [1, 1, 0, 0], 1)
                [x] Test 1: getCoilsBits() passed
            >>> getCoilBitsTest((0, 4), [1, 1, 0, 1], 1)
                AssertionError: [ ] Test 1: getCoilsBits() failed
        """
        actualOutput = self.client.getCoilsBits(readInput[0], readInput[1])
        assert actualOutput == expectedOutput, f"[ ] Test {testID}: getCoilsBits() failed"
        print(f"[x] Test {testID}: getCoilsBits() passed")
        time.sleep(0.5)

    def getHoldingRegsTest(self, readInput, expectedOutput, testID):
        """
        Performs a unit test for getHoldingRegs() method of the ModbusTcpClient object. 
        It compares the actual output with the expected output and raises an assertion error 
        if they do not match.
        Args:
            readInput (int, int): The first argument representing addressIdx and offset.
            expectedOutput (list): The second argument representing the expected output.
        Returns:
            None
        Raises:
            AssertionError: If actualOutput != expectedOutput.
        Examples:
            Assumption: 
                - Holding registers current state [0, 0, 1, 1]        
            >>> getHoldingRegsTest((0, 4), [0, 0, 1, 1], 1)
                [x] Test 1: getHoldingRegs() passed
            >>> getHoldingRegsTest((0, 4), [0, 1, 1, 1], 1)
                AssertionError: [ ] Test 1: getHoldingRegs() failed
        """
        actualOutput = self.client.getHoldingRegs(readInput[0], readInput[1])
        assert actualOutput == expectedOutput, f"[ ] Test {testID}: getHoldingRegs() failed"
        print(f"[x] Test {testID}: getHoldingRegs() passed")
        time.sleep(0.5)

    def setCoilBitsTest(self, setInput, readInput, expectedOutput, testID):
        """
        Performs a unit test for setCoilsBits() method of the ModbusTcpClient object. 
        It sets a coil bit, retrieves the coil bit values, compares the actual output 
        with the expected output, and raises an assertion error if they do not match.
        Args:
            setInput (int, int): The first argument representing addressIdx and bitVal
            readInput (int, int): The second argument representing addressIdx and offset.
            expectedOutput (list): The third argument representing the expected output.
            testID (int): The fourth argument representing the ID tagged to this test run.
        Returns:
            None
        Raises:
            AssertionError: If actualOutput != expectedOutput
        Examples:
            Assumption: 
                - Coil bits current state [1, 0, 0, 0]
            >>> setCoilBitsTest((1, 1), (0, 4), [1, 1, 0, 0], 1)
                [x] Test 1: setCoilsBit() passed
            >>> setCoilBitsTest((1, 1), (0, 4), [1, 0, 0, 0], 1)
                AssertionError: [ ] Test 1: setCoilsBit() failed
        """    
        self.client.setCoilsBit(setInput[0], setInput[1])
        actualOutput = self.client.getCoilsBits(readInput[0], readInput[1])
        assert actualOutput == expectedOutput, f"[ ] Test {testID}: setCoilsBit() failed"
        print(f"[x] Test {testID}: setCoilsBit() passed")
        time.sleep(0.5)

    def setHoldingRegsTest(self, setInput, readInput, expectedOutput, testID):
        """
        Performs a unit test for setHoldingRegs() method of the ModbusTcpClient object. 
        It sets a holding register, retrieves the holding register values, compares the 
        actual output with the expected output, and raises an assertion error if they do not match.
        Args:
            setInput (int, int): The first argument representing addressIdx and bitVal
            readInput (int, int): The second argument representing addressIdx and offset.
            expectedOutput (list): The third argument representing the expected output.
            testID (int): The fourth argument representing the ID tagged to this test run.
        Returns:
            None
        Raises:
            AssertionError: If actualOutput != expectedOutput
        Examples:
            Assumption: 
                - Holding register current state [0, 0, 1, 1]
            >>> setHoldingRegsTest((1, 1), (0, 4), [0, 1, 1, 1], 1)
                [x] Test 1: setHoldingRegs() passed
            >>> setHoldingRegsTest((1, 1), (0, 4), [1, 1, 1, 1], 1)
                AssertionError: [ ] Test 1: setHoldingRegs() failed
        """ 
        self.client.setHoldingRegs(setInput[0], setInput[1])
        actualOutput = self.client.getHoldingRegs(readInput[0], readInput[1])
        assert actualOutput == expectedOutput, f"[ ] Test {testID}: setHoldingRegs() failed"
        print(f"[x] Test {testID}: setHoldingRegs() passed")
        time.sleep(0.5)

#---------------------------------------------------------------------------
# Define integration test methods for the following ModbusTCPCom plcDataHandler function:
#   - updateState()

    def autoUpdateCoilTest(self, setInput, readInput, expectedOutput, testID):
        """
        Performs an integration test for updateState() method of the plcDataHandler object. 
        It sets a holding register, retrieves the coil bit values, compares the actual output 
        with the expected output, and raises an assertion error if they do not match.
        Args:
            setInput (int, int): The first argument representing addressIdx and bitVal
            readInput (int, int): The second argument representing addressIdx and offset.
            expectedOutput (list): The third argument representing the expected output.
            testID (int): The fourth argument representing the ID tagged to this test run.
        Returns:
            None
        Raises:
            AssertionError: If actualOutput != expectedOutput
        Examples:
            Assumption: 
                - Holding register current state [0, 0, 1, 1].
                - Coil Bits current state [0, 0, 0, 0].
                - Ladder Logic is to flip all the bits
            >>> autoUpdateCoilTest((0, 1), (0, 4), [0, 1, 0, 0], 1) 
                [x] Test 1: updateState() passed
            >>> autoUpdateCoilTest((0, 1), (0, 4), [0, 0, 0, 0], 1) 
                AssertionError: [ ] Test 1: updateState() failed
        """ 
        self.client.setHoldingRegs(setInput[0], setInput[1])
        time.sleep(0.5)
        actualOutput = self.client.getCoilsBits(readInput[0], readInput[1])
        assert actualOutput == expectedOutput, f"[ ] Test {testID}: updateState() failed"
        print(f"[x] Test {testID}: updateState() passed")        
        time.sleep(0.5)

#-----------------------------------------------------------------------------
# Define all the getter functions

    def getClient(self):
        return self.client
    
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

class testModbusServerThread(threading.Thread):
    """
    This class is a subclass that inherits from the threading.Thread class. 
    It extends the functionality of the thread with additional attributes and 
    methods specific to testing ModBus TCP server communication.
    
    Attributes:
        server: Represents modbusTcpServer object.
        dataMgr: Represents the plcDataHandler object.

    Methods:
        __init__(): Initialise the testModbusServerThread object
        run(): Establishes and starts a ModBus server. Refer to the method description 
        for more details.
        closeServer(): Terminates the ModBus TCP client connection.
    """

    def __init__(self, parent, threadID, name, testDataManager):
        super().__init__(parent)
        self.server = None
        self.dataMgr = testDataManager

    def run(self):
        """
        Overrides the run() method from the threading.Thread class. It
        establishes and starts a ModBus server. 
        Returns:
            None
        Raises:
            Exception: If the creation of the ModBus TCP server fails
        Examples:
            server = testModbusServerThread(None, 2, "Server Thread")
            server.start()
        """        
        networkConfig = {'hostIP':'localhost', 'hostPort': 502}
        server = modbusTcpCom.modbusTcpServer(
            hostIp=networkConfig['hostIP'], \
            hostPort=networkConfig['hostPort'], \
            dataHandler=self.dataMgr
        )
        if server:
            self.server = server
        else:
            raise Exception("Test Failed: Unable to initialise ModBus Server")
        self.server.startServer()

    def closeServer(self):
        """
        Closes the ModBus TCP server
        Returns:
            None
        Raises:
            None
        Examples:
            >>> server = testModbusServerThread(None, 1, "Server Thread")
            >>> server.start()
            >>> server.closeServer()
        """        
        self.server.stopServer()

#-----------------------------------------------------------------------------
# Define all the getter functions

    def getServer(self):
        return self.server

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

class testPLCDataHandler(modbusTcpCom.plcDataHandler):
    """
    This class is a subclass that inherits from the modbusTcpCom.plcDatahandler class. 
    It extends the functionality of the data handler with additional attributes and 
    methods specific to testing ModBus TCP communication data handling.
    
    Attributes:
        serverInfo: Represents ModbusServerInfo object that contains the server information.
        testLadderLogic: Represents the stubLadderLogic object that describes the PLC ladder logic.

    Methods:
        __init__(): Initialises the testPLCDataHandler object
        presetConfigurations(): Presets the configurations for the server and data handler.

    Unit Test Methods:
        checkAllowReadTest(): Performs a unit test for the _checkAllowRead() method of the 
        modbusTcpCom.plcDatahandler parent class. Refer to the method description for more details.
        
        checkAllowWriteTest(): Performs a unit test for the _checkAllowWrite() method of the
        modbusTcpCom.plcDatahandler parent class. Refer to the method description for more details.

        setAllowReadIPTest(): Performs a unit test for setAllowReadIpaddresses() method of the
        modbusTcpCom.plcDatahandler parent class. Refer to the method description for more details.

        setAllowWriteIPTest(): Performs a unit test for setAllowWriteIpaddresses() method of the
        modbusTcpCom.plcDatahandler parent class. Refer to the method description for more details.

        updateOutputCoilsTest(): Performs a unit test for updateOutPutCoils() method of the
        modbusTcpCom.plcDatahandler parent class. Refer to the method description for more details.

        updateHoldingRegsTest(): Performs a unit test for updateHoldingRegs() method of the
        modbusTcpCom.plcDatahandler parent class. Refer to the method description for more details.
    """    
    def __init__(self, allowReadList, allowWriteList, testLadderLogic):
        super().__init__(allowRipList=allowReadList, allowWipList=allowWriteList)
        self.serverInfo = None
        self.testLadderLogic = testLadderLogic
        
    def presetConfigurations(self, serverInfo):
        """
        Presets the configurations for the server and data handler.
        Args:
            serverInfo (dict): Information about the server.
        Returns:
            None
        Raises:
            None
        Examples:
            Assumptions:
                - serverInfo contains all of the server information
            >>> dataMgr = testPLCDataHandler(ALLOW_R_L, ALLOW_W_L, ladderLogic)
            >>> dataMgr.presetConfigurations(serverInfo)
        """        
        self.serverInfo = serverInfo
        super().initServerInfo(self.serverInfo)
        super().addLadderLogic('testLogic', self.testLadderLogic)
        super().setAutoUpdate(True)
        super().updateOutPutCoils(0, [0, 0, 0, 0])
        super().updateHoldingRegs(0, [0, 0, 1, 1])

#---------------------------------------------------------------------------
# Define unit tests for the following ModbusTCPCom plcDataHandler functions:
#   - _checkAllowRead()
#   - _checkAllowWrite()
#   - setAllowReadIpaddresses()
#   - setAllowWriteIpaddresses()
#   - updateOutPutCoils()
#   - updateHoldingRegs()

    def checkAllowReadTest(self, ipaddress, expectedOutput, testID):
        """
        Performs a unit test for _checkAllowRead() method of the plcDataHandler object.
        It checks if the given IP address is allowed for read access, compares the actual 
        output with the expected output, and raises an assertion error if they do not match.
        Args:
            ipaddress (str): The first argument representing the ip addresses that you plan to check wrt read permissions.
            expectedOutput (bool): The second argument representing the expected output.
            testID (int): The third argument representing the ID tagged to this test run.
        Returns:
            None
        Raises:
            AssertionError: If actualOutput != expectedOutput
        Examples:
            Assumption: 
                - Allow Read List State ['127.0.0.1', '192.168.0.10']
            >>> checkAllowReadTest('127.0.0.1', True, 1)
                [x] Test 1: _checkAllowRead() passed
            >>> checkAllowReadTest('192.168.0.11', True, 1)
                AssertionError: [ ] Test 1: _checkAllowRead() failed
        """ 
        actualOutput = self._checkAllowRead(ipaddress)
        assert actualOutput == expectedOutput, f"[ ] Test {testID}: _checkAllowRead() failed"
        print(f"[x] Test {testID}: _checkAllowRead() passed")    

    def checkAllowWriteTest(self, ipaddress, expectedOutput, testID):
        """
        Performs a unit test for _checkAllowWrite() method of the plcDataHandler object.
        It checks if the given IP address is allowed for write access, compares the actual 
        output with the expected output, and raises an assertion error if they do not match.
        Args:
            ipaddress (str): The first argument representing the ip addresses that you plan to check wrt write permissions.
            expectedOutput (bool): The second argument representing the expected output.
            testID (int): The third argument representing the ID tagged to this test run.
        Returns:
            None
        Raises:
            AssertionError: If actualOutput != expectedOutput
        Examples:
            Assumption: 
                - Allow Write List State ['127.0.0.1']
            >>> checkAllowWriteTest('127.0.0.1', True, 1)
                [x] Test 1: _checkAllowWrite() passed
            >>> checkAllowWriteTest('192.168.0.11', True, 1)
                AssertionError: [ ] Test 1: _checkAllowWrite() failed
        """ 
        actualOutput = self._checkAllowWrite(ipaddress)
        assert actualOutput == expectedOutput, f"[ ] Test {testID}: _checkAllowWrite() failed"
        print(f"[x] Test {testID}: _checkAllowWrite() passed")

    def setAllowReadIPTest(self, ipList, ipInput, expectedOutput, testID):
        """
        Performs a unit test for setAllowReadIpaddresses() method of the plcDataHandler object. 
        It sets the allowable read IP list, checks if the given IP address is allowed for read access 
        after the change, compares the actual output with the expected output, and raises an assertion 
        error if they do not match.
        Args:
            ipList (list/tuple): The first argument representing the ip addresses that you want to give read permissions to.
            ipInput (str): The second argument representing the ip address that you plan to check wrt read permissions.
            expectedOutput (bool): The third argument representing the expected output.
            testID (int): The fourth argument representing the ID tagged to this test run.
        Returns:
            None
        Raises:
            AssertionError: If actualOutput != expectedOutput
        Examples:
            Assumption: 
                - Allow Read List State ['127.0.0.1', '192.168.0.10']
            >>> setAllowReadIPTest(('192.168.25.1', '127.0.0.1', '192.168.0.10'), "192.168.25.1", True, 1)
                [x] Test 1: setAllowReadIpaddresses() passed
            >>> setAllowReadIPTest(('192.168.25.2', '127.0.0.1', '192.168.0.10'), "192.168.25.1", True, 1)
                AssertionError: [ ] Test 1: setAllowReadIpaddresses() failed
        """        
        self.setAllowReadIpaddresses(ipList)
        actualOutput = self._checkAllowRead(ipInput)
        assert actualOutput == expectedOutput, f"[ ] Test {testID}: setAllowReadIpaddresses() failed"
        print(f"[x] Test {testID}: setAllowReadIpaddresses() passed")

    def setAllowWriteIPTest(self, ipList, ipInput, expectedOutput, testID):
        """
        Performs a unit test for setAllowWriteIpaddresses() method of the plcDataHandler object. 
        It sets the allowable Write IP list, checks if the given IP address is allowed for write access 
        after the change, compares the actual output with the expected output, and raises an assertion 
        error if they do not match.
        Args:
            ipList (list/tuple): The first argument representing the ip addresses that you want to give write permissions to.
            ipInput (str): The second argument representing the ip address that you plan to check wrt write permissions.
            expectedOutput (bool): The third argument representing the expected output.
            testID (int): The fourth argument representing the ID tagged to this test run.
        Returns:
            None
        Raises:
            AssertionError: If actualOutput != expectedOutput
        Examples:
            Assumption: 
                - Allow Write List State ['127.0.0.1']
            >>> setAllowWriteIPTest(('127.0.0.1', '192.168.0.10'), "192.168.0.10", True, 1)
                [x] Test 1: setAllowWriteIpaddresses() passed
            >>> setAllowWriteIPTest(('127.0.0.1', '192.168.0.10'), "192.168.25.1", True, 1)
                AssertionError: [ ] Test 1: setAllowWriteIpaddresses() failed
        """    
        self.setAllowWriteIpaddresses(ipList)
        actualOutput = self._checkAllowWrite(ipInput)
        assert actualOutput == expectedOutput, f"[ ] Test {testID}: setAllowWriteIpaddresses() failed"
        print(f"[x] Test {testID}: setAllowWriteIpaddresses() passed")

    def updateOutputCoilsTest(self, client, setInput, readInput, expectedOutput, testID):
        """
        Performs a unit test for updateOutPutCoils() method of the plcDataHandler object. 
        It sets the output coils, retrieves the output coils values, compares the 
        actual output with the expected output, and raises an assertion error if they do not match.
        Args:
            client (object): The first argument representing client stub.
            setInput (int, list/tuple): The second argument representing addressIdx and bit value list.
            readInput (int, int): The third argument representing addressIdx and offset.
            expectedOutput (list): The fourth argument representing the expected output.
            testID (int): The fifth argument representing the ID tagged to this test run.
        Returns:
            None
        Raises:
            AssertionError: If actualOutput != expectedOutput
        Examples:
            Assumption: 
                - Coil bits current state [1, 0, 0, 0]
                - The client is a modbusTcpClient stub object 
            >>> updateOutputCoilsTest(client, (0, [0, 0, 0, 0]), (0, 4), [0, 0, 0, 0], 1)
                [x] Test 1: updateOutPutCoils() passed
            >>> updateOutputCoilsTest(client, (0, [1, 0, 0, 0]), (0, 4), [0, 0, 0, 0], 1)
                AssertionError: [ ] Test 1: updateOutPutCoils() failed
        """    
        self.updateOutPutCoils(setInput[0], setInput[1])
        actualOutput = client.getCoilsBits(readInput[0], readInput[1])
        assert actualOutput == expectedOutput, f"[ ] Test {testID}: updateOutPutCoils() failed"
        print(f"[x] Test {testID}: updateOutPutCoils() passed")

    def updateHoldingRegsTest(self, client, setInput, readInput, expectedOutput, testID):
        """
        Performs a unit test for updateHoldingRegs() method of the plcDataHandler object. 
        It sets the holding registers, retrieves the holding register values, compares the 
        actual output with the expected output, and raises an assertion error if they do not match.
        Args:
            client (object): The first argument representing client stub.
            setInput (int, list/tuple): The second argument representing addressIdx and bit value list.
            readInput (int, int): The third argument representing addressIdx and offset.
            expectedOutput (list): The fourth argument representing the expected output.
            testID (int): The fifth argument representing the ID tagged to this test run.
        Returns:
            None
        Raises:
            AssertionError: If actualOutput != expectedOutput
        Examples:
            Assumption: 
                - Holding registers current state [1, 0, 0, 0]
                - The client is a modbusTcpClient stub object 
            >>> updateHoldingRegsTest(client, (0, [0, 0, 1, 1]), (0, 4), [0, 0, 1, 1], 1)
                [x] Test 1: updateHoldingRegs()passed
            >>> updateHoldingRegsTest(client, (0, [0, 0, 1, 1]), (0, 4), [1, 0, 1, 1], 1)
                AssertionError: [ ] Test 1: updateHoldingRegs() failed
        """    
        self.updateHoldingRegs(setInput[0], setInput[1])
        actualOutput = client.getHoldingRegs(readInput[0], readInput[1])
        assert actualOutput == expectedOutput, f"[ ] Test {testID}: updateHoldingRegs() failed"
        print(f"[x] Test {testID}: updateHoldingRegs() passed")
    
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

class stubLadderLogic(modbusTcpCom.ladderLogic):
    """
    A subclass that inherits from the modbusTcpCom.ladderLogic class.
    Description:
        This subclass represents a stub implementation of ladder logic for Modbus TCP communication.
        It provides methods to initialize ladder information and run ladder logic.

    Attributes:
        parent: The parent object or instance.

    Methods:
        __init__(): Initializes the stubLadderLogic object.
        initLadderInfo(): Initializes the ladder information with default values.
        runLadderLogic(): Runs the ladder logic based on the input registers' state. Please
        refer to the method description for more information.    
    """

    def __init__(self, parent) -> None:
        super().__init__(parent)

    def initLadderInfo(self):
        """
        Initializes the ladder information with default values.
        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        self.holdingRegsInfo['address'] = 0
        self.holdingRegsInfo['offset'] = 4
        self.srcCoilsInfo['address'] = 0
        self.srcCoilsInfo['offset'] = 4
        self.destCoilsInfo['address'] = 0
        self.destCoilsInfo['offset'] = 4

    def runLadderLogic(self, regsList, coilList=None):
        """
        Runs the ladder logic based on the input registers' state. The ladder logic
        defined in this stub class reverses the input registers' state
        Args:
            regsList (list): The list of input registers' states.
            coilList (list, optional): The list of coil states. Defaults to None.
        Returns:
            list: The resulting coil states as a list.
        Raises:
            None
        """
        result = []
        for state in regsList:
            result.append(not state)
        return result

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

def createTestObjects():
    print("======================================= Creating Test Objects ========================================")
    ALLOW_R_L = ['127.0.0.1', '192.168.0.10']
    ALLOW_W_L = ['127.0.0.1']
    ladderLogic = stubLadderLogic(None)
    dataMgr = testPLCDataHandler(ALLOW_R_L, ALLOW_W_L, ladderLogic)
    server = testModbusServerThread(None, 1, "Server Thread", dataMgr)
    client = testModbusClientThread(None, 2, "Client Thread")
    # Initialise and start both client and server
    server.start()
    client.start()
    # Preset the basic configurations for data manager
    dataMgr.presetConfigurations(server.getServer().getServerInfo())
    # Wait for the client thread to finish its execution
    client.join()
    return (client, server, dataMgr)    

def runTestCases(client, server, dataMgr):    
    print("========================== Running Test Cases for ModBus TCP Communications ==========================")
    print("(Modbus Client Unit Test Cases)")
    client.getCoilBitsTest((0, 4), [1, 1, 0, 0], 1)
    client.getHoldingRegsTest((0, 4), [0, 0, 1, 1], 2)
    client.setCoilBitsTest((1, 1), (0, 4), [1, 1, 0, 0], 3)
    client.setHoldingRegsTest((1, 1), (0, 4), [0, 1, 1, 1], 4)
    print("\n(PLC Data Handler Unit Test Cases)")
    dataMgr.checkAllowReadTest('127.0.0.1', True, 1)
    dataMgr.checkAllowReadTest('192.168.25.1', False, 2)
    dataMgr.checkAllowWriteTest('127.0.0.1', True, 3)
    dataMgr.checkAllowWriteTest('192.168.0.10', False, 4)
    dataMgr.setAllowReadIPTest(('192.168.25.1', '127.0.0.1', '192.168.0.10'), "192.168.25.1", True, 5)
    dataMgr.setAllowReadIPTest(('127.0.0.1', '192.168.0.10'), "192.168.25.1", False, 6)
    dataMgr.setAllowWriteIPTest(('127.0.0.1', '192.168.0.10'), "192.168.0.10", True, 7)
    dataMgr.setAllowWriteIPTest(('127.0.0.1', '192.168.0.10'), "192.168.25.1", False, 8)
    dataMgr.updateOutputCoilsTest(client.getClient(), (0, [0, 0, 0, 0]), (0, 4), [0, 0, 0, 0], 9)
    dataMgr.updateHoldingRegsTest(client.getClient(), (0, [0, 0, 1, 1]), (0, 4), [0, 0, 1, 1], 10)
    print("\n(Integration Test Cases)")   
    client.autoUpdateCoilTest((0, 1), (0, 4), [0, 1, 0, 0], 1) 
    client.closeClient()
    server.closeServer()

if __name__ == '__main__':
    client, server, dataMgr = createTestObjects()
    runTestCases(client, server, dataMgr)