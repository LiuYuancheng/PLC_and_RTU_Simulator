#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        iec61850MmsComm.py
#
# Purpose:     This module provides a minimal and dependency-free IEC61850 MMS 
#              (Manufacturing Message Specification) communication lib protocol 
#              implementation. The lib is designed from scratch to run on both 
#              Windows, MACOS and Linux without special tool-set such as C++ 
#              compiler but only the Python standard library (socket + struct).  
#
# Author:      Yuancheng Liu
#
# Created:     2026/11/24
# Version:     v_0.0.1
# Copyright:   Copyright (c) 2026 Liu Yuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import datetime
import logging
import socket
import struct

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
DEFAULT_PORT = 102
ACCESS_ERRORS = {
    0: 'object-invalidated', 
    1: 'hardware-fault', 
    2: 'temporarily-unavailable',
    3: 'object-access-denied', 
    4: 'object-undefined', 
    5: 'invalid-address',
    6: 'type-unsupported', 
    7: 'type-inconsistent', 
    8: 'object-attribute-inconsistent',
    9: 'object-access-unsupported', 
    10: 'object-non-existent', 
    11: 'object-value-invalid',
}
ACCESS_DENIED = 3
TYPE_INCONSISTENT = 7
NON_EXISTENT = 10
VALUE_INVALID = 11

# ASN.1 Basic Encoding Rules (BER) encoded Object Identifiers (OIDs)
OID_ACSE_AS = bytes.fromhex('52010001')         # 2.2.1.0.1    ACSE Abstract Syntax (ISO 8650-1)
OID_BER = bytes.fromhex('5101')                 # 2.1.1        BER Transfer Syntax (ISO 8825-1)
OID_MMS_AS = bytes.fromhex('28ca220201')        # 1.0.9506.2.1 MMS abstract syntax
OID_MMS_AC = bytes.fromhex('28ca220203')        # 1.0.9506.2.3 MMS application context
AP_TITLE_CALLED = bytes.fromhex('2901876701')   # 1.1.1.999.1
AP_TITLE_CALLING = bytes.fromhex('29018767')    # 1.1.999

PCTX_ACSE = 1       # presentation context id used for ACSE
PCTX_MMS = 3        # presentation context id used for MMS

MMS_TYPE_ALIASES = {
    'bool': 'boolean', 'boolean': 'boolean',
    'int': 'integer', 'integer': 'integer',
    'uint': 'unsigned', 'unsigned': 'unsigned',
    'float': 'float', 'float32': 'float',
    'double': 'double', 'float64': 'double',
    'str': 'string', 'string': 'string', 'visible-string': 'string',
    'octets': 'octets', 'octet-string': 'octets',
}

# --------------------------------------------------------------------------------------
# BER helper functions

def tlv(tag, content=b''):
    """Encode one BER element (single byte tag)."""
    berLen = None
    conLen = len(content)
    if conLen < 0x80:
        berLen = bytes([conLen])
    else:
        raw = conLen.to_bytes((conLen.bit_length() + 7) // 8, "big")
        berLen = bytes([0x80 | len(raw)]) + raw
    return bytes([tag]) + berLen + content

# --------------------------------------------------------------------------------------
def parse_tlv(buf, pos=0):
    """Parse one BER element at pos -> (tag, content, next_pos)."""
    if pos + 2 > len(buf):
        raise ValueError('truncated BER element')
    tag = buf[pos]
    if tag & 0x1F == 0x1F:
        raise ValueError('multi-byte BER tags are not supported')
    length = buf[pos + 1]
    pos += 2
    if length & 0x80:
        n = length & 0x7F
        if n == 0 or n > 4 or pos + n > len(buf):
            raise ValueError('unsupported BER length')
        length = int.from_bytes(buf[pos:pos + n], 'big')
        pos += n
    end = pos + length
    if end > len(buf):
        raise ValueError('truncated BER element')
    return tag, buf[pos:end], end

# --------------------------------------------------------------------------------------
def parse_all(buf):
    """Split a buffer into a list of (tag, content)."""
    items, pos = [], 0
    while pos < len(buf):
        tag, val, pos = parse_tlv(buf, pos)
        items.append((tag, val))
    return items

# --------------------------------------------------------------------------------------
def dig(buf, path):
    """Walk down a BER tree following a list of tags; return the content found."""
    for tag in path:
        pos = 0
        while True:
            if pos >= len(buf):
                raise ValueError('BER tag 0x%02X not found' % tag)
            t, v, nxt = parse_tlv(buf, pos)
            if t == tag:
                buf = v
                break
            pos = nxt
    return buf

# --------------------------------------------------------------------------------------
def enc_int(v):
    """Minimal two's complement BER integer content."""
    n = 1
    while True:
        try:
            return v.to_bytes(n, 'big', signed=True)
        except OverflowError:
            n += 1


# --------------------------------------------------------------------------------------
# MMS data values process functions

def normalize_type(name):
    try:
        return MMS_TYPE_ALIASES[name.lower()]
    except KeyError:
        raise ValueError(" normalize_type(): unknown type %s (use boolean, integer, unsigned, float, double, string, octets)" % str(name))

# --------------------------------------------------------------------------------------
def types_compatible(a, b):
    ints, floats = ('integer', 'unsigned'), ('float', 'double')
    return a == b or (a in ints and b in ints) or (a in floats and b in floats)

# --------------------------------------------------------------------------------------
def encode_data(mms_type, value):
    """Python value -> MMS Data element convert function."""
    if mms_type == 'boolean':
        return tlv(0x83, b'\xff' if value else b'\x00')
    if mms_type == 'integer':
        return tlv(0x85, enc_int(int(value)))
    if mms_type == 'unsigned':
        if int(value) < 0:
            raise ValueError('unsigned value must be >= 0')
        return tlv(0x86, enc_int(int(value)))
    if mms_type == 'float':
        return tlv(0x87, b'\x08' + struct.pack('>f', float(value)))
    if mms_type == 'double':
        return tlv(0x87, b'\x0b' + struct.pack('>d', float(value)))
    if mms_type == 'string':
        return tlv(0x8A, str(value).encode('utf-8'))
    if mms_type == 'octets':
        return tlv(0x89, bytes(value))
    raise ValueError('cannot encode MMS type %r' % mms_type)

# --------------------------------------------------------------------------------------
def decode_data(tag, val):
    """MMS Data element -> (type_name, python_value)."""
    if tag == 0x83:
        return 'boolean', val[:1] != b'\x00'
    if tag == 0x85:
        return 'integer', int.from_bytes(val, 'big', signed=True)
    if tag == 0x86:
        return 'unsigned', int.from_bytes(val, 'big', signed=False)
    if tag == 0x87:
        raw = val[1:]
        if len(raw) == 4:
            return 'float', struct.unpack('>f', raw)[0]
        if len(raw) == 8:
            return 'double', struct.unpack('>d', raw)[0]
        raise ValueError('bad floating-point length')
    if tag in (0x8A, 0x90):
        return 'string', val.decode('utf-8', 'replace')
    if tag == 0x89:
        return 'octets', bytes(val)
    if tag == 0x84:
        bits = ''.join('{:08b}'.format(b) for b in val[1:])
        return 'bitstring', bits[:len(bits) - val[0]] if val else ''
    if tag == 0x91 and len(val) == 8:
        secs = int.from_bytes(val[:4], 'big')
        frac = int.from_bytes(val[4:7], 'big') / 16777216.0
        ts = datetime.datetime.fromtimestamp(secs + frac, datetime.timezone.utc)
        return 'utctime', ts.strftime('%Y-%m-%d %H:%M:%S.%f UTC')
    if tag in (0xA1, 0xA2):
        kind = 'array' if tag == 0xA1 else 'structure'
        return kind, [decode_data(t, v) for t, v in parse_all(val)]
    return 'unknown(0x%02X)' % tag, bytes(val)

# --------------------------------------------------------------------------------------
def format_value(mms_type, value):
    if mms_type == 'float':
        return '%.7g' % value
    if mms_type == 'octets':
        return value.hex()
    if isinstance(value, list):
        return '[' + ', '.join(format_value(t, v) for t, v in value) + ']'
    return str(value)

# --------------------------------------------------------------------------------------
def parse_value(mms_type, text):
    """Command line text -> python value of the given MMS type."""
    if mms_type == 'boolean':
        low = text.strip().lower()
        if low in ('1', 'true', 'on', 'yes', 't'):
            return True
        if low in ('0', 'false', 'off', 'no', 'f'):
            return False
        raise ValueError('boolean value must be true/false/1/0')
    if mms_type in ('integer', 'unsigned'):
        return int(text, 0)
    if mms_type in ('float', 'double'):
        return float(text)
    if mms_type == 'string':
        return text
    if mms_type == 'octets':
        return bytes.fromhex(text)
    raise ValueError('unsupported type %r' % mms_type)

# --------------------------------------------------------------------------------------
# MMS variable process functions:

def build_variable_list(names):
    """[(domain, item), ...] -> listOfVariable [0] (used by Read and Write requests)."""
    out = b''
    for domain, item in names:
        obj = tlv(0xA1, tlv(0x1A, domain.encode()) + tlv(0x1A, item.encode()))
        out += tlv(0x30, tlv(0xA0, obj))
    return tlv(0xA0, out)


def parse_variable_list(content):
    """content of listOfVariable [0] -> [(domain or None, item), ...]"""
    names = []
    for tag, val in parse_all(content):
        if tag != 0x30:
            raise ValueError('bad variable list')
        for t, v in parse_all(val):
            if t != 0xA0:
                continue            # alternateAccess is not supported / ignored
            ntag, nval, _ = parse_tlv(v)
            if ntag == 0xA1:        # domain-specific
                parts = [x for _, x in parse_all(nval)]
                names.append((parts[0].decode(), parts[1].decode()))
            elif ntag in (0x80, 0x82):   # vmd-specific / aa-specific
                names.append((None, nval.decode()))
            else:
                raise ValueError('bad object name')
    return names

# --------------------------------------------------------------------------------------
# TPKT (ISO Transport Service on top of TCP) and COTP (Connection-Oriented Transport Protocol, 
# ISO 8073 / RFC 905) (python socket implementation transport) functions: 

def recv_exact(sock, n):
    buf = b''
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError('connection closed by peer')
        buf += chunk
    return buf

def send_tpkt(sock, payload):
    sock.sendall(b'\x03\x00' + struct.pack('>H', len(payload) + 4) + payload)

def recv_tpkt(sock):
    hdr = recv_exact(sock, 4)
    if hdr[0] != 3:
        raise ConnectionError('not a TPKT packet')
    length = struct.unpack('>H', hdr[2:4])[0]
    if length < 5:
        raise ConnectionError('bad TPKT length')
    payload = recv_exact(sock, length - 4)
    return payload

def build_cotp_connect(code, dst_ref, src_ref, size_code, calling, called):
    """COTP CR (0xE0) or CC (0xD0) TPDU."""
    body = bytes([code]) + struct.pack('>HH', dst_ref, src_ref) + b'\x00'
    body += b'\xC0\x01' + bytes([size_code])
    body += b'\xC1' + bytes([len(calling)]) + calling
    body += b'\xC2' + bytes([len(called)]) + called
    return bytes([len(body)]) + body

def parse_cotp_connect(tpdu):
    """-> (dst_ref, src_ref, {param_code: value})"""
    li = tpdu[0]
    dst, src = struct.unpack('>HH', tpdu[2:6])
    params, pos = {}, 7
    while pos + 2 <= li + 1:
        code, ln = tpdu[pos], tpdu[pos + 1]
        params[code] = tpdu[pos + 2:pos + 2 + ln]
        pos += 2 + ln
    return dst, src, params

def send_cotp_data(sock, data, tpdu_size=1024):
    """Send user data in COTP DT TPDUs (segmented when larger than the TPDU size)."""
    step = tpdu_size - 3
    chunks = [data[i:i + step] for i in range(0, len(data), step)] or [b'']
    for n, chunk in enumerate(chunks):
        eot = 0x80 if n == len(chunks) - 1 else 0x00
        send_tpkt(sock, b'\x02\xF0' + bytes([eot]) + chunk)

def recv_cotp(sock):
    """-> ('DT', reassembled_user_data) or (tpdu_type_code, whole_tpdu)"""
    data = b''
    while True:
        tpdu = recv_tpkt(sock)
        tpdu_type = tpdu[1] & 0xF0
        if tpdu_type != 0xF0:
            return tpdu_type, tpdu
        data += tpdu[tpdu[0] + 1:]
        if tpdu[2] & 0x80:
            return 'DT', data

# --------------------------------------------------------------------------------------
# Session layer (X.225)

def ses_len(n):
    return bytes([n]) if n < 255 else b'\xff' + struct.pack('>H', n)

def ses_param(pi, data):
    return bytes([pi]) + ses_len(len(data)) + data

def build_ses_connect(user_data, accept=False):
    """CONNECT (0x0D) / ACCEPT (0x0E) SPDU."""
    params = bytes.fromhex('0506130100160102')      # protocol options + version 2
    params += bytes.fromhex('14020002')             # session requirement: duplex
    if not accept:
        params += bytes.fromhex('3302000134020001')  # calling / called session selector
    params += ses_param(0xC1, user_data)
    return bytes([0x0E if accept else 0x0D]) + ses_len(len(params)) + params

def build_ses_release(si, user_data):
    """FINISH (0x09) / DISCONNECT (0x0A) SPDU."""
    params = ses_param(0xC1, user_data)
    return bytes([si]) + ses_len(len(params)) + params

def build_ses_data(user_data):
    """Give-tokens + data-transfer SPDU."""
    return b'\x01\x00\x01\x00' + user_data

def parse_spdu(data):
    """-> (SPDU identifier, user data)"""
    if not data:
        raise ValueError('empty SPDU')
    si = data[0]
    if si == 0x01:
        if data[:4] != b'\x01\x00\x01\x00':
            raise ValueError('unsupported session data SPDU')
        return si, data[4:]
    if len(data) < 2:
        return si, b''
    length, off = data[1], 2
    if length == 0xFF:
        length, off = struct.unpack('>H', data[2:4])[0], 4
    params = data[off:off + length]
    user, pos = b'', 0
    while pos + 2 <= len(params):
        pi, pl = params[pos], params[pos + 1]
        pos += 2
        if pl == 0xFF:
            pl = struct.unpack('>H', params[pos:pos + 2])[0]
            pos += 2
        if pi == 0xC1:
            user = params[pos:pos + pl]
        pos += pl
    return si, user

# --------------------------------------------------------------------------------------
# Presentation layer (X.226) and ACSE (X.227)
def build_cp_type(aarq):
    """Presentation CP-type (connect request) carrying the ACSE AARQ."""
    contexts = tlv(0xA4,
                   tlv(0x30, tlv(0x02, bytes([PCTX_ACSE])) + tlv(0x06, OID_ACSE_AS) +
                       tlv(0x30, tlv(0x06, OID_BER))) +
                   tlv(0x30, tlv(0x02, bytes([PCTX_MMS])) + tlv(0x06, OID_MMS_AS) +
                       tlv(0x30, tlv(0x06, OID_BER))))
    user = tlv(0x61, tlv(0x30, tlv(0x02, bytes([PCTX_ACSE])) + tlv(0xA0, aarq)))
    normal = tlv(0xA2, tlv(0x81, b'\x00\x00\x00\x01') + tlv(0x82, b'\x00\x00\x00\x01') +
                 contexts + user)
    return tlv(0x31, tlv(0xA0, tlv(0x80, b'\x01')) + normal)

def build_cpa_type(aare):
    """Presentation CPA-type (connect accept) carrying the ACSE AARE."""
    accepted = tlv(0x30, tlv(0x80, b'\x00') + tlv(0x81, OID_BER))
    user = tlv(0x61, tlv(0x30, tlv(0x02, bytes([PCTX_ACSE])) + tlv(0xA0, aare)))
    normal = tlv(0xA2, tlv(0x83, b'\x00\x00\x00\x01') + tlv(0xA5, accepted + accepted) + user)
    return tlv(0x31, tlv(0xA0, tlv(0x80, b'\x01')) + normal)

def build_pres_data(mms_pdu):
    """Presentation user-data (context id 3 = MMS)."""
    return tlv(0x61, tlv(0x30, tlv(0x02, bytes([PCTX_MMS])) + tlv(0xA0, mms_pdu)))

def build_pres_acse(acse_apdu):
    """Presentation user-data (context id 1 = ACSE) e.g. release request / response."""
    return tlv(0x61, tlv(0x30, tlv(0x02, bytes([PCTX_ACSE])) + tlv(0xA0, acse_apdu)))

def _external(mms_pdu):
    return tlv(0xBE, tlv(0x28, tlv(0x06, OID_BER) + tlv(0x02, bytes([PCTX_MMS])) +
                         tlv(0xA0, mms_pdu)))

def build_aarq(mms_initiate_request):
    body = (tlv(0xA1, tlv(0x06, OID_MMS_AC)) +
            tlv(0xA2, tlv(0x06, AP_TITLE_CALLED)) + tlv(0xA3, tlv(0x02, b'\x0c')) +
            tlv(0xA6, tlv(0x06, AP_TITLE_CALLING)) + tlv(0xA7, tlv(0x02, b'\x0c')) +
            _external(mms_initiate_request))
    return tlv(0x60, body)

def build_aare(mms_initiate_response):
    body = (tlv(0xA1, tlv(0x06, OID_MMS_AC)) +
            tlv(0xA2, tlv(0x02, b'\x00')) +                       # result: accepted
            tlv(0xA3, tlv(0xA1, tlv(0x02, b'\x00'))) +            # diagnostic: null
            _external(mms_initiate_response))
    return tlv(0x61, body)

RLRQ = tlv(0x62, tlv(0x80, b'\x00'))    # ACSE release request  (reason: normal)
RLRE = tlv(0x63, tlv(0x80, b'\x00'))    # ACSE release response (reason: normal)


# --------------------------------------------------------------------------------------
# MMS Initiate
SERVICES_CLIENT = bytes.fromhex('03ee1c00000408000079ef18')
SERVICES_SERVER = bytes([3, 0x4C]) + bytes(10)      # getNameList, read, write
PARAMETER_CBB = bytes.fromhex('05f100')

def build_initiate(is_request, max_pdu=64000, outstanding=10, nesting=5):
    detail = tlv(0xA4, tlv(0x80, b'\x01') + tlv(0x81, PARAMETER_CBB) +
                 tlv(0x82, SERVICES_CLIENT if is_request else SERVICES_SERVER))
    body = (tlv(0x80, enc_int(max_pdu)) + tlv(0x81, enc_int(outstanding)) +
            tlv(0x82, enc_int(outstanding)) + tlv(0x83, enc_int(nesting)) + detail)
    return tlv(0xA8 if is_request else 0xA9, body)

def parse_initiate(pdu):
    """-> dict with max_pdu / outstanding / nesting of an Initiate request / response."""
    tag, val, _ = parse_tlv(pdu)
    if tag not in (0xA8, 0xA9):
        raise ValueError('not an MMS initiate PDU')
    f = dict(parse_all(val))
    num = lambda t, d: int.from_bytes(f[t], 'big') if t in f else d
    return {'max_pdu': num(0x80, 65000), 'outstanding': num(0x81, 10), 'nesting': num(0x83, 5)}

# --------------------------------------------------------------------------------------
# Transport wrapper used by both client and server
class Transport(object):
    """Sends / receives MMS PDUs over an established TCP socket."""

    def __init__(self, sock, tpdu_size=1024):
        self.sock = sock
        self.tpdu_size = tpdu_size

    def send_spdu(self, spdu):
        send_cotp_data(self.sock, spdu, self.tpdu_size)

    def send_mms(self, mms_pdu):
        self.send_spdu(build_ses_data(build_pres_data(mms_pdu)))

    def recv_spdu(self):
        kind, data = recv_cotp(self.sock)
        if kind != 'DT':
            raise ConnectionError('transport connection released by peer')
        return parse_spdu(data)
