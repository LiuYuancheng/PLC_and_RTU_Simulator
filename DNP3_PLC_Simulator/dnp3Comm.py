#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        dnp3Comm.py
#
# Purpose:     This module provides a minimal and dependency-free (IEEE 1815) DNP3 
#              communication lib protocol implementation. The lib is designed from
#              scratch to run on both Windows and Linux with nothing but the Python
#              standard library (socket + struct).  
#
# Author:      Yuancheng Liu
#
# Created:     2026/07/17
# Version:     v_0.0.1
# Copyright:   Copyright (c) 2026 Liu Yuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
""" Program Design :

    The function implemented in this module will be enough of the Data Link, Transport 
    and Application layers to:
     - Open a TCP session on the standard DNP3 port (20000)
     - READ (function 0x01) Binary Inputs (Group1Var2), Analog Inputs
        (Group30Var1), Binary Output status (Group10Var2) and Analog Output
        status (Group40Var1)
     - DIRECT_OPERATE (function 0x05) a Binary Output (Group12Var1 / CROB) or
        an Analog Output (Group41Var1) to let a master WRITE a value into the
        outstation's point database
     - build syntactically correct DNP3 frames (valid sync bytes, length,
        control byte, addresses and CRC-16/DNP checksums) so the traffic is
        recognised natively by Wireshark's "dnp3.0" dissector on port 20000.

    Remark: 
    This is NOT a full/compliant DNP3 stack (no unsolicited responses, no
    multi-fragment transport reassembly, no confirm/retry handling, no serial
    support). It is intended for lab / training / detection-content use, not
    for production ICS deployments.
"""

import socket
import struct

# --------------------------------------------------------------------------
# Constants
DNP3_PORT = 20000   # default DNP3 port
SYNC = b"\x05\x64"  # default TCP sync bytes

# Link layer function codes (lower 4 bits of the control byte)
LINK_FUNC_UNCONFIRMED_USER_DATA = 0x04

# Application layer function codes
FUNC_CONFIRM = 0x00
FUNC_READ = 0x01
FUNC_WRITE = 0x02
FUNC_DIRECT_OPERATE = 0x05
FUNC_DIRECT_OPERATE_NR = 0x06
FUNC_RESPONSE = 0x81
FUNC_UNSOLICITED_RESPONSE = 0x82

FUNC_NAMES = {
    0x00: "CONFIRM", 
    0x01: "READ", 
    0x02: "WRITE",
    0x05: "DIRECT_OPERATE", 
    0x06: "DIRECT_OPERATE_NR",
    0x81: "RESPONSE", 
    0x82: "UNSOLICITED_RESPONSE",
}

# Object group/variation pairs used by this implementation
GRP_BINARY_INPUT = (1, 2)           # Binary Input w/ flags        (1 byte/obj)
GRP_BINARY_OUTPUT_STATUS = (10, 2)  # Binary Output status w/flags (1 byte/obj)
GRP_CROB = (12, 1)                  # Control Relay Output Block  (11 bytes/obj)
GRP_ANALOG_INPUT = (30, 1)          # 32-bit Analog Input w/flag   (5 bytes/obj)
GRP_ANALOG_OUTPUT_STATUS = (40, 1)  # 32-bit Analog Output status  (5 bytes/obj)
GRP_ANALOG_OUTPUT_CMD = (41, 1)     # 32-bit Analog Output cmd     (5 bytes/obj)

QUAL_ALL_POINTS = 0x06         # request: "give me all of this object type"
QUAL_8BIT_START_STOP = 0x00    # response: packed range, 8-bit start/stop
QUAL_8BIT_INDEX_PREFIX = 0x17  # request: 1-byte index prefix, 1-byte count

# CROB control codes (Group12Var1 control_code field, low nibble = op type)
CROB_LATCH_ON = 0x03
CROB_LATCH_OFF = 0x04

FLAG_ONLINE = 0x01
FLAG_STATE_BIT = 0x80  # bit7 of a binary flag byte carries the boolean value

# --------------------------------------------------------------------------
# CRC-16/DNP  (poly=0x3D65 reflected=0xA6BC, init=0x0000, refin/refout=True,
# xorout=0xFFFF).  This is the exact checksum DNP3 uses on the wire, both
# for the 8-byte link-layer header and for every 16-byte user-data block.
# --------------------------------------------------------------------------
_POLY = 0xA6BC
def crc16_dnp(data: bytes) -> int:
    crc = 0x0000
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ _POLY
            else:
                crc >>= 1
    return (crc ^ 0xFFFF) & 0xFFFF

def _append_crc(data: bytes) -> bytes:
    return data + struct.pack("<H", crc16_dnp(data))

def _check_crc(block: bytes) -> bool:
    payload, crc_bytes = block[:-2], block[-2:]
    return struct.pack("<H", crc16_dnp(payload)) == crc_bytes

# --------------------------------------------------------------------------
# Data Link Layer framing
# --------------------------------------------------------------------------
def build_link_frame(user_data: bytes, dest: int, src: int, from_master: bool) -> bytes:
    """ Wrap transport+application bytes in a DNP3 data-link frame. 'user_data' is 
        the transport-layer segment (transport header byte + application layer bytes). 
        It is split into <=16 byte blocks, each followed by its own CRC-16/DNP, per spec.
    """
    length = 5 + len(user_data)  # control+dest+src (5) + user data
    if length > 255:
        raise ValueError("message too long for a single DNP3 frame (no multi-frame transport in this lib)")
    # control byte: DIR | PRM | FCB | FCV | function(4 bits)
    dir_bit = 0x80 if from_master else 0x00
    control = dir_bit | 0x40 | LINK_FUNC_UNCONFIRMED_USER_DATA  # PRM=1, FCB/FCV=0
    header = struct.pack("<BBHH", length, control, dest, src)
    # NOTE: per spec, the header CRC covers START + LENGTH + CONTROL + DEST + SOURCE
    header_with_crc = SYNC + header + struct.pack("<H", crc16_dnp(SYNC + header))
    blocks = b""
    for i in range(0, len(user_data), 16):
        chunk = user_data[i:i + 16]
        blocks += _append_crc(chunk)
    return header_with_crc + blocks

def parse_link_frame(frame: bytes):
    """ Parse one data-link frame, return (dest, src, from_master, user_data)."""
    if frame[0:2] != SYNC:
        raise ValueError("bad sync bytes, not a DNP3 frame")
    header_block = frame[0:10]  # sync(2) + length,control,dest,src(6) + crc(2)
    if not _check_crc(header_block):
        raise ValueError("link header CRC failed")
    length, control, dest, src = struct.unpack("<BBHH", frame[2:8])
    from_master = bool(control & 0x80)
    data_area = frame[10:]
    user_data_len = length - 5
    user_data = b""
    pos = 0
    remaining = user_data_len
    while remaining > 0:
        take = min(16, remaining)
        block = data_area[pos:pos + take + 2]
        if not _check_crc(block):
            raise ValueError("data block CRC failed")
        user_data += block[:-2]
        pos += take + 2
        remaining -= take
    return dest, src, from_master, user_data

def frame_byte_length(user_data_len: int) -> int:
    """Total on-the-wire byte length of a link frame carrying user_data_len bytes."""
    n_blocks = (user_data_len + 15) // 16 if user_data_len else 0
    return 10 + user_data_len + 2 * n_blocks

# --------------------------------------------------------------------------
# Transport Layer (single-segment only: FIR=1, FIN=1)
# --------------------------------------------------------------------------
def build_transport_segment(app_bytes: bytes, seq: int = 0) -> bytes:
    if len(app_bytes) > 249:
        raise ValueError("application fragment too large for a single transport segment in this lib")
    header = 0xC0 | (seq & 0x3F)  # FIN=1, FIR=1, SEQ
    return bytes([header]) + app_bytes

def parse_transport_segment(user_data: bytes):
    header = user_data[0]
    fin = bool(header & 0x80)
    fir = bool(header & 0x40)
    seq = header & 0x3F
    return fir, fin, seq, user_data[1:]

# --------------------------------------------------------------------------
# Application Layer: object encode/decode helpers
# --------------------------------------------------------------------------
def encode_binary_point(value: bool) -> bytes:
    flag = FLAG_ONLINE | (FLAG_STATE_BIT if value else 0x00)
    return bytes([flag])

def decode_binary_point(b: bytes):
    flag = b[0]
    return bool(flag & FLAG_STATE_BIT)

def encode_analog_point(value: int) -> bytes:
    flag = FLAG_ONLINE
    return bytes([flag]) + struct.pack("<i", int(value))

def decode_analog_point(b: bytes):
    flag = b[0]
    (value,) = struct.unpack("<i", b[1:5])
    return value

def build_object_header_range(group: int, variation: int, qualifier: int, start: int = None, stop: int = None) -> bytes:
    hdr = bytes([group, variation, qualifier])
    if qualifier == QUAL_8BIT_START_STOP:
        hdr += bytes([start, stop])
    return hdr

def build_read_request(points: list) -> bytes:
    """points: list of (group, variation) -- requests ALL instances of each type."""
    out = b""
    for group, variation in points:
        out += build_object_header_range(group, variation, QUAL_ALL_POINTS)
    return out

def build_response_objects(group, variation, indexed_values: dict, encoder) -> bytes:
    """indexed_values: {index: value}. Emits one packed range object header
    covering min..max index (per spec, packed format assumes contiguous
    coverage -- gaps are filled with a default so the byte layout stays
    simple and standards-shaped for the dissector)."""
    if not indexed_values:
        return b""
    idx_sorted = sorted(indexed_values)
    start, stop = idx_sorted[0], idx_sorted[-1]
    out = build_object_header_range(group, variation, QUAL_8BIT_START_STOP, start, stop)
    for i in range(start, stop + 1):
        out += encoder(indexed_values.get(i, 0))
    return out

def build_direct_operate_crob(index: int, turn_on: bool) -> bytes:
    """Group12Var1 CROB, single object, 1-byte index prefix (qualifier 0x17)."""
    hdr = bytes([12, 1, QUAL_8BIT_INDEX_PREFIX, 1])  # group, var, qual, count=1
    control_code = CROB_LATCH_ON if turn_on else CROB_LATCH_OFF
    obj = struct.pack("<BBIIB", control_code, 1, 1000, 1000, 0)  # code,count,on_ms,off_ms,status
    return hdr + bytes([index]) + obj

def build_direct_operate_analog(index: int, value: int) -> bytes:
    """Group41Var1 Analog Output command, single object, 1-byte index prefix."""
    hdr = bytes([41, 1, QUAL_8BIT_INDEX_PREFIX, 1])
    obj = struct.pack("<iB", int(value), 0)  # value, status(=0 in request)
    return hdr + bytes([index]) + obj

def build_app_request(function: int, seq: int, objects: bytes = b"") -> bytes:
    control = 0xC0 | (seq & 0x0F)  # FIR=1, FIN=1, CON=0, UNS=0
    return bytes([control, function]) + objects

def build_app_response(function: int, seq: int, iin1: int, iin2: int, objects: bytes = b"") -> bytes:
    control = 0xC0 | (seq & 0x0F)
    return bytes([control, function, iin1, iin2]) + objects

def parse_app_header(app_bytes: bytes):
    control = app_bytes[0]
    function = app_bytes[1]
    seq = control & 0x0F
    if function in (FUNC_RESPONSE, FUNC_UNSOLICITED_RESPONSE):
        iin1, iin2 = app_bytes[2], app_bytes[3]
        return function, seq, iin1, iin2, app_bytes[4:]
    return function, seq, None, None, app_bytes[2:]

# --------------------------------------------------------------------------
# tiny TCP send/receive helpers shared by client & server
# --------------------------------------------------------------------------
def send_frame(sock: socket.socket, frame: bytes):
    sock.sendall(frame)

def recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("peer closed connection")
        buf += chunk
    return buf

def recv_link_frame(sock: socket.socket) -> bytes:
    """Read exactly one DNP3 data-link frame off the wire."""
    sync = recv_exact(sock, 2)
    if sync != SYNC:
        raise ValueError("desynced stream, expected DNP3 sync bytes")
    header_rest = recv_exact(sock, 8)  # length,control,dest,src,crc
    length = header_rest[0]
    user_data_len = length - 5
    n_blocks = (user_data_len + 15) // 16 if user_data_len else 0
    data_area = recv_exact(sock, user_data_len + 2 * n_blocks)
    return sync + header_rest + data_area


# --------------------------------------------------------------------------
# DNP server module
# --------------------------------------------------------------------------