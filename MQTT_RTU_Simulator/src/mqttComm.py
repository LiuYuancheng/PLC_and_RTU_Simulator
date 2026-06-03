#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        mqttComm.py
#
# Purpose:     This module will provide the ISO/IEC-20922 MQTT (Message Queuing 
#              Telemetry Transport) broker and client communication API to test 
#              or simulate the data/control connection between RTU/IoT/IIoT devices 
#              and the SCADA system. The module is implemented based on the python 
#              MQTTv3.1.1 paho-mqtt Lib: 
#              https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html
#
# Author:      Yuancheng Liu
#
# Created:     2026/05/24
# Version:     v_0.0.3
# Copyright:   Copyright (c) 2026 Liu Yuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
"""_summary_

Raises:
    ConnectionResetError: _description_
    TimeoutError: _description_

Returns:
    _type_: _description_
"""
import time
import socket
import struct
import threading
import paho.mqtt.client as mqtt

MQTT_PORT = 1883 # Default mqtt port number 

# MQTT packet type constants (currently what we need, may add more in the future)
CONNECT     = 0x10
CONNACK     = 0x20
PUBLISH_Q0  = 0x30  # QoS level 0 (At most once) currently we use the QoS level0 DUP = 0, Retain = 0
PUBLISH_Q1  = 0x32  # QoS level 1 (At least once)
PUBLISH_Q2  = 0x34  # QoS level 2 (Exactly once)
PUBACK      = 0x40
SUBSCRIBE   = 0x82
SUBACK      = 0x90
PINGREQ     = 0xC0
PINGRESP    = 0xD0
DISCONNECT  = 0xE0

# Parameter Path String
PARM_SET = 'parameters/set/'
PARM_GET = 'parameters/get/'
PARM_VAL = 'parameters/value/'

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

def _encode_remaining_length(length: int) -> bytes:
    """ Encode an integer as MQTT variable-length remaining-length bytes. """
    result = bytearray()
    while True:
        byte = length & 0x7F
        length >>= 7
        if length: byte |= 0x80
        result.append(byte)
        if not length: break
    return bytes(result)

def _read_utf8(data: bytes, offset: int):
    """ Read a 2-byte-prefixed UTF-8 string from data. Return (string, new_offset)."""
    length = struct.unpack_from("!H", data, offset)[0]
    offset += 2
    return data[offset:offset + length].decode("utf-8"), offset + length

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class ClientHandler(threading.Thread):
    """ The handler ojb running in the broker obj with starting a new thread to 
        response the client request. 
    """
    def __init__(self, parent, sock: socket.socket, addr):
        """ Init the client handler with the socket and address. 
            Args:
                parent (obj): The parent MQTT broker <MQTTBroker> object.
                sock (socket.socket): The TCP socket when a new connection is accepted.
                addr (tuple): The client address.
        """
        super().__init__(daemon=True)
        self.parent = parent
        self.sock = sock
        self.addr = addr
        self.client_id = str(addr)

    #-----------------------------------------------------------------------------
    def _recv_exact(self, n: int):
        """ Receive exactly n bytes from the socket. """
        buf = b""
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk: raise ConnectionResetError("Client disconnected")
            buf += chunk
        return buf

    #-----------------------------------------------------------------------------
    def _recv_packet(self):
        """ Receive a single MQTT packet from the socket, return split MQTT request
            protocol type and the detailed payload.
        """
        header = self._recv_exact(1)
        ptype = header[0]
        # decode remaining length
        length = 0
        multiplier = 1
        while True:
            b = self._recv_exact(1)[0]
            length += (b & 0x7F) * multiplier
            multiplier *= 128
            if not (b & 0x80): break
        payload = self._recv_exact(length) if length else b""
        return ptype, payload

    #-----------------------------------------------------------------------------
    def _handle_connect(self, payload: bytes):
        """ Handle the MQTT CONNECT packet (new client coming in). """
        # Skip protocol name + level + flags + keepalive (fixed header portion)
        offset = 0
        proto_name, offset = _read_utf8(payload, offset)
        proto_level = payload[offset]; offset += 1
        connect_flags = payload[offset]; offset += 1
        keepalive = struct.unpack_from("!H", payload, offset)[0]; offset += 2
        client_id, offset = _read_utf8(payload, offset)
        self.client_id = client_id or str(self.addr)
        print("INFO : Client connected: id=%s from %s"  % (self.client_id, self.addr))
        # Send CONNACK (session present=0, return code=0 accepted)
        self.sock.sendall(bytes([CONNACK, 0x02, 0x00, 0x00]))

    #-----------------------------------------------------------------------------
    def _handle_subscribe(self, payload: bytes):
        """ Handle the data subscribe request and reply the value. """
        offset = 0
        packet_id = struct.unpack_from("!H", payload, offset)[0]; offset += 2
        return_codes = []
        while offset < len(payload):
            topic, offset = _read_utf8(payload, offset)
            qos = payload[offset]
            offset += 1
            self.parent.subscribeClient(topic, self.sock)
            return_codes.append(min(qos, 0))   # grant QoS 0
            print("INFO : Client %s subscribed to %s" %(self.client_id, topic))
            # If subscribing to parameters/get/<name>, deliver current value immediately
            if topic.startswith(PARM_GET):
                name = topic[len(PARM_GET):]
                value = self.parent.getParmVal(name)
                if value is not None:
                    self.parent.deliver(PARM_VAL+str(name), value.encode("utf-8"))
        # Send SUBACK
        body = struct.pack("!H", packet_id) + bytes(return_codes)
        self.sock.sendall(bytes([SUBACK]) + _encode_remaining_length(len(body)) + body)

    #-----------------------------------------------------------------------------
    def _handle_publish(self, first_byte: int, payload: bytes):
        """ Handle the MQTT PUBLISH packet (new message from client). """
        qos = (first_byte >> 1) & 0x03
        offset = 0
        topic, offset = _read_utf8(payload, offset)
        if qos > 0:
            packet_id = struct.unpack_from("!H", payload, offset)[0]
            offset += 2
            # Send PUBACK
            self.sock.sendall(bytes([PUBACK, 0x02]) + struct.pack("!H", packet_id))
        message = payload[offset:].decode("utf-8", errors="replace")
        print("PUBLISH  topic=%s  payload=%s  from=%s" %(topic, message, self.client_id))
        if topic.startswith(PARM_SET):
            name = topic[len(PARM_SET):]
            self.parent.setParmVal(name, message)
            # execute the control logic if value modified
            self.parent.executeLogic()
            # Broadcast new value to subscribers of parameters/value/<name>
            self.parent.deliver(PARM_VAL+str(name), message.encode("utf-8"))
        elif topic.startswith(PARM_GET):
            # A client can also request a value via publish (optional pattern)
            name = topic[len(PARM_GET):]
            value = self.parent.getParmVal(name)
            if value is not None:
                self.parent.deliver(PARM_VAL+str(name), value.encode("utf-8"))
        else:
            # Generic topic forwarding (pass-through pub/sub)
            self.parent.deliver(topic, payload[offset:])

    #-----------------------------------------------------------------------------
    def run(self):
        try:
            while True:
                ptype, payload = self._recv_packet()
                print("INFO : Received packet type ptype: 0x%02X " % ptype)
                if ptype == CONNECT:
                    self._handle_connect(payload)
                elif ptype == SUBSCRIBE:
                    self._handle_subscribe(payload)
                elif ptype == PUBLISH_Q0 or ptype == PUBLISH_Q1 or ptype == PUBLISH_Q2:
                    self._handle_publish(ptype, payload)
                elif ptype == PINGREQ:
                    self.sock.sendall(bytes([PINGRESP, 0x00]))
                elif ptype == DISCONNECT:
                    print("Client %s disconnected gracefully" % self.client_id)
                    break
                else:
                    print("Unknown packet type 0x%02X ignoring" % ptype)
        except (ConnectionResetError, BrokenPipeError, OSError):
            print("Client %s connection lost" % self.client_id)
        finally:
            self.parent.unSubscribeClient(self.sock)
            try:
                self.sock.close()
            except Exception as err:
                print("run() - Error to close socket :%s" %str(err))

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class MQTTBroker(object):
    """ The MQTT Broker class. """
    def __init__(self, host="0.0.0.0", port=MQTT_PORT):
        self.host = host
        self.port = port
        self.parm = {}  # parm is a dictionary to store the MQTT broker parameters
        self.subscription = {}
        self.serverSock = None
        self.terminate = False

    #-----------------------------------------------------------------------------
    def addParm(self, name, value=None):
        self.parm[name] = value
    
    def getParmVal(self, name):
        return self.parm[name] if name in self.parm.keys() else None 

    def setParmVal(self, name, value):
        if name in self.parm.keys():
            self.parm[name] = value
            return True 
        return False

    def subscribeClient(self, topic, client_sock):
        if topic not in self.subscription.keys(): self.subscription[topic] = []
        if client_sock not in self.subscription[topic]:
                self.subscription[topic].append(client_sock)

    def unSubscribeClient(self, client_sock):
        for subsList in self.subscription.values():
            if client_sock in subsList: subsList.remove(client_sock)

    def deliver(self, topic: str, payload: bytes):
        """Send a PUBLISH packet to every subscriber of *topic*."""
        # message body
        encoded = topic.encode("utf-8")
        body = struct.pack("!H", len(encoded)) + encoded + payload
        packet = bytes([PUBLISH_Q0]) + _encode_remaining_length(len(body)) + body
        targets = list(self.subscription.get(topic, []))
        for sock in targets:
            try:
                sock.sendall(packet)
            except Exception as err:
                print("deliver() - Error to deliver data :%s" %str(err))

    #-----------------------------------------------------------------------------
    def executeLogic(self):
        """ Interface function in the main loop for the MQTT broker to execute 
            the control logic.
        """
        pass

    #-----------------------------------------------------------------------------
    def run(self):
        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_sock.bind((self.host, self.port))
        self._server_sock.listen(50)
        print("INFO : MQTT Broker is listening on port %s: %d" %(self.host, self.port))
        try:
            while not self.terminate:
                client_sock, addr = self._server_sock.accept()
                newHandler = ClientHandler(self, client_sock, addr)
                newHandler.start()
        except KeyboardInterrupt:
            print("Broker shutting down…")
        finally:
            if self._server_sock: self._server_sock.close()

    def stop(self):
        self.terminate = True

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class MQTTClient(object):
    """ The MQTT Client class."""

    def __init__(self, id, broker_ip:str, port=MQTT_PORT, timeout=5.0):
        self.id = id
        self.broker_ip = broker_ip
        self.port = port
        self.timeout = timeout
        # paho.mqtt.client
        self._mqtt = mqtt.Client(client_id=str(self.id), protocol=mqtt.MQTTv311)
        self._mqtt.on_connect    = self._on_connect
        self._mqtt.on_message    = self._on_message
        self._mqtt.on_disconnect = self._on_disconnect
        # Internal state
        self._connected = threading.Event()
        self._pending: dict[str, threading.Event] = {}   # param → event
        self._values:  dict[str, str]             = {}   # param → latest value
        self._watchers: dict[str, list]           = {}   # param → [callback, ...]
        self._lock = threading.Lock()

    #-----------------------------------------------------------------------------
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker %s:%d", self.broker_ip, self.port)
            self._connected.set()
        else:
            print("_on_connect() - Connection refused, return code %d", rc)

    def _on_disconnect(self, client, userdata, rc):
        self._connected.clear()
        if rc != 0: print("Unexpected disconnection (rc=%d)", rc)

    #-----------------------------------------------------------------------------
    def _on_message(self, client, userdata, msg):
        """ Handle message call back."""
        topic = str(msg.topic)
        payload = str(msg.payload.decode("utf-8", errors="replace"))
        # Extract parameter name from  parameters/value/<name>
        name = topic[len(PARM_VAL):] if topic.startswith(PARM_VAL) else None 
        if name is None : return
        with self._lock:
            self._values[name] = payload
            # Resolve any pending GET
            evt = self._pending.pop(name, None)
            # Collect watchers
            named_cbs  = list(self._watchers.get(name, []))
            wildcard_cbs = list(self._watchers.get("*", []))
        if evt: evt.set()
        for cb in named_cbs + wildcard_cbs:
            try:
                cb(name, payload)
            except Exception as exc:
                print("Watcher callback error: %s", exc)

    #-----------------------------------------------------------------------------
    def connect(self):
        """Connect to the broker and block until the connection is established."""
        print("Connecting to broker at %s:%d …" %(self.broker_ip, self.port))
        self._mqtt.connect(self.broker_ip, self.port, keepalive=60)
        self._mqtt.loop_start()
        if not self._connected.wait(timeout=self.timeout):
            raise TimeoutError("Could not connect to broker at %s:%s" % (str(self.broker_ip), str(self.port)))

    def disconnect(self):
        """Gracefully disconnect from the broker."""
        self._mqtt.loop_stop()
        self._mqtt.disconnect()
        print("Disconnected from broker %s", self.broker_ip)

    #-----------------------------------------------------------------------------
    def getParmVal(self, name: str):
        """ Request the current value of parameter = name from the broker. Blocks up 
            to self.timeout seconds and returns the value string, or None on timeout.
        """
        evt = threading.Event()
        with self._lock: self._pending[name] = evt
        # Subscribe to the value topic before requesting
        value_topic = PARM_VAL+str(name)
        self._mqtt.subscribe(value_topic, qos=0)
        # Request current value
        self._mqtt.publish("parameters/get/%s" % str(name), payload="", qos=0)
        if not evt.wait(timeout=self.timeout):
            print("WARN:Timeout waiting for parameter %s" % str(name))
            with self._lock:
                self._pending.pop(name, None)
            return None
        with self._lock:
            return self._values.get(name)

    #-----------------------------------------------------------------------------
    def setParmVal(self, name: str, value: str):
        """Publish a new value for parameter = name to the broker."""
        self._mqtt.publish("parameters/set/%s" %str(name), payload=str(value), qos=0)
        print("SET  %s = %s for  broker %s" % (name, value, self.broker_ip))

    #-----------------------------------------------------------------------------
    def watch(self, name: str, callback=None, block: bool = True):
        """ Subscribe to live updates of *name*. If *callback* is provided it is called as 
            callback(name, value) on every change.  Otherwise changes are printed to stdout.
            If *block* is True the call blocks until KeyboardInterrupt.
        """
        if callback is None:
            callback = lambda n, v: print("%s = %s" % (str(n), str(v)))
        with self._lock:
            self._watchers.setdefault(name, []).append(callback)
        value_topic = PARM_VAL+str(name)
        self._mqtt.subscribe(value_topic, qos=0)
        print("Watching parameter %s  (topic: %s)" %(name, value_topic))
        if block:
            try:
                while True:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("Stopped watching %s" %str(name))

    #-----------------------------------------------------------------------------
    def watch_all(self, callback=None, block: bool = True):
        """ Subscribe to live updates for ALL parameters (wildcard). Calls callback(name, value) 
            on every change.
        """
        if callback is None:
            callback = lambda n, v: print("%s = %s" % (str(n), str(v)))
        self._mqtt.subscribe(PARM_VAL+"#", qos=0)
        with self._lock:
            self._watchers.setdefault("*", []).append(callback)
        print("Watching ALL parameters on broker %s" %str(self.broker_ip))
        if block:
            try:
                while True:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("Stopped watching all parameters")

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def testBroker():
    broker = MQTTBroker()
    broker.addParm('temperature', '25.0')
    broker.addParm('humidity', '60')
    broker.addParm('mode', 'auto')
    broker.addParm('speed', '1500')
    broker.run()

if __name__ == "__main__":
    testBroker()
