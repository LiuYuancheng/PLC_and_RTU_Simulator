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
# https://softwaretoolbox.com/resources/what-is-iec61850

import random
import datetime
import socket
import socketserver
import struct
import threading
import traceback
import Log

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
DEFAULT_HOST = '0.0.0.0'
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

# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
class MmsError(Exception):
    """Generic MMS / protocol error."""

class MmsAccessError(MmsError):
    """MMS DataAccessError (a single variable could not be read / written)."""
    def __init__(self, code):
        MmsError.__init__(self, ACCESS_ERRORS.get(code, 'data-access-error-%d' % code))
        self.code = code

def coerce(mms_type, value):
    if mms_type == 'float':      # keep what a 32 bit float can really hold
        return struct.unpack('>f', struct.pack('>f', float(value)))[0]
    if mms_type == 'double':
        return float(value)
    if mms_type in ('integer', 'unsigned'):
        value = int(value)
        if mms_type == 'unsigned' and value < 0:
            raise MmsAccessError(VALUE_INVALID)
        return value
    if mms_type == 'boolean':
        return bool(value)
    return value

# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
class IedModel(object):
    """Thread-safe store of all variables."""

    def __init__(self, data):
        self.lock = threading.RLock()
        self.data = {d: {i: [t, coerce(t, v), bool(w)] for i, (t, v, w) in items.items()}
                     for d, items in data.items()}

    def domains(self):
        return sorted(self.data)

    def variables(self, domain):
        with self.lock:
            return sorted(self.data.get(domain, {}))

    def _entry(self, domain, item):
        try:
            return self.data[domain][item]
        except KeyError:
            raise MmsAccessError(NON_EXISTENT)

    def read(self, domain, item):
        with self.lock:
            entry = self._entry(domain, item)
            return entry[0], entry[1]

    def write(self, domain, item, mms_type, value):
        with self.lock:
            entry = self._entry(domain, item)
            if not entry[2]:
                raise MmsAccessError(ACCESS_DENIED)
            if not types_compatible(entry[0], mms_type):
                raise MmsAccessError(TYPE_INCONSISTENT)
            entry[1] = coerce(entry[0], value)

# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
class MmsHandler(socketserver.BaseRequestHandler):
    """ One thread per client connection. the handler will get the 'model' obj directly 
        from the server obj in its handle() function. 
    """

    def handle(self):
        self.peer = '%s:%d' % self.client_address[:2]
        self.model = self.server.model
        self.request.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        Log.info('[%s] TCP connection opened', self.peer)
        try:
            self.conn = Transport(self.request)
            if self.associate():
                self.serve()
        except (ConnectionError, OSError) as exc:
            Log.info('[%s] connection ended (%s)', self.peer, exc)
        except Exception:
            Log.error('[%s] protocol error\n%s', self.peer, traceback.format_exc())
        finally:
            Log.info('[%s] closed', self.peer)

    # ---- association (COTP connect + session/presentation/ACSE/MMS initiate) ------------
    def associate(self):
        kind, tpdu = recv_cotp(self.request)
        if kind != 0xE0:
            Log.warning('[%s] expected COTP connect request', self.peer)
            return False
        dst, src, params = parse_cotp_connect(tpdu)
        size_code = min(params.get(0xC0, b'\x0a')[0], 0x0D)
        self.conn.tpdu_size = 1 << size_code
        send_tpkt(self.request, build_cotp_connect(
            0xD0, src, 0x0001, size_code,
            params.get(0xC1, b'\x00\x01'), params.get(0xC2, b'\x00\x01')))

        si, user = self.conn.recv_spdu()
        if si != 0x0D:
            Log.warning('[%s] expected session CONNECT', self.peer)
            return False
        aarq = dig(user, [0x31, 0xA2, 0x61, 0x30, 0xA0])
        request = dig(aarq, [0x60, 0xBE, 0x28, 0xA0])
        want = parse_initiate(request)
        response = build_initiate(False, min(want['max_pdu'], 64000),
                                  min(want['outstanding'], 10), min(want['nesting'], 5))
        self.conn.send_spdu(build_ses_connect(build_cpa_type(build_aare(response)), accept=True))
        Log.info('[%s] MMS association established', self.peer)
        return True

    # ---- main request loop --------------------------------------------------------------
    def serve(self):
        while True:
            kind, data = recv_cotp(self.request)
            if kind != 'DT':
                return
            si, user = parse_spdu(data)
            if si == 0x01:
                reply = self.process(dig(user, [0x61, 0x30, 0xA0]))
                if reply:
                    self.conn.send_mms(reply)
            elif si == 0x09:        # session FINISH (ACSE release request)
                self.conn.send_spdu(build_ses_release(0x0A, build_pres_acse(RLRE)))
                Log.info('[%s] association released', self.peer)
                return
            else:                   # ABORT / DISCONNECT
                return

    def process(self, pdu):
        tag, val, _ = parse_tlv(pdu)
        if tag == 0xA0:
            return self.confirmed_request(val)
        if tag == 0x8B:             # conclude request
            Log.info('[%s] MMS conclude', self.peer)
            return b'\x8c\x00'
        Log.warning('[%s] ignoring MMS PDU 0x%02X', self.peer, tag)
        return None

    def confirmed_request(self, val):
        items = parse_all(val)
        invoke = items[0][1]
        svc_tag, svc_val = items[1]
        try:
            if svc_tag == 0xA4:
                body = self.svc_read(svc_val)
            elif svc_tag == 0xA5:
                body = self.svc_write(svc_val)
            elif svc_tag == 0xA1:
                body = self.svc_get_name_list(svc_val)
            else:
                Log.warning('[%s] unsupported service 0x%02X', self.peer, svc_tag)
                return tlv(0xA4, tlv(0x80, invoke) + tlv(0x81, b'\x01'))   # reject: unrecognized-service
        except (ValueError, IndexError) as exc:
            Log.warning('[%s] invalid request: %s', self.peer, exc)
            return tlv(0xA4, tlv(0x80, invoke) + tlv(0x81, b'\x04'))       # reject: invalid-argument
        return tlv(0xA1, tlv(0x02, invoke) + body)

    # ---- MMS services -------------------------------------------------------------------
    def svc_read(self, content):
        names = parse_variable_list(dig(content, [0xA1, 0xA0]))
        results = b''
        for domain, item in names:
            try:
                mms_type, value = self.model.read(domain, item)
                results += encode_data(mms_type, value)
                Log.info('[%s] READ  %s/%s = %s', self.peer, domain, item, format_value(mms_type, value))
            except MmsAccessError as exc:
                results += tlv(0x80, bytes([exc.code]))
                Log.info('[%s] READ  %s/%s -> %s', self.peer, domain, item, exc)
        return tlv(0xA4, tlv(0xA1, results))

    def svc_write(self, content):
        items = parse_all(content)
        names = parse_variable_list(items[0][1])
        values = parse_all(items[1][1])
        if items[0][0] != 0xA0 or items[1][0] != 0xA0 or len(names) != len(values):
            raise ValueError('variable / data list mismatch')
        results = b''
        for (domain, item), (tag, raw) in zip(names, values):
            try:
                mms_type, value = decode_data(tag, raw)
                self.model.write(domain, item, mms_type, value)
                results += tlv(0x81, b'')
                Log.info('[%s] WRITE %s/%s = %s', self.peer, domain, item, format_value(mms_type, value))
            except MmsAccessError as exc:
                results += tlv(0x80, bytes([exc.code]))
                Log.info('[%s] WRITE %s/%s -> %s', self.peer, domain, item, exc)
        return tlv(0xA5, results)

    def svc_get_name_list(self, content):
        obj_class, scope, after = None, (0x80, b''), None
        for tag, val in parse_all(content):
            if tag == 0xA0:
                obj_class = int.from_bytes(parse_tlv(val)[1], 'big')
            elif tag == 0xA1:
                scope = parse_tlv(val)[:2]
            elif tag == 0x82:
                after = val.decode()
        if obj_class == 9:                              # domains (Logical devices)
            names = self.model.domains()
        elif obj_class == 0 and scope[0] == 0x81:       # named variables of one domain
            names = self.model.variables(scope[1].decode())
        else:
            names = []
        if after is not None:
            names = [n for n in names if n > after]
        Log.info('[%s] GetNameList class=%s -> %d names', self.peer, obj_class, len(names))
        ids = b''.join(tlv(0x1A, n.encode()) for n in names)
        return tlv(0xA1, tlv(0xA0, ids) + tlv(0x81, b'\x00'))

# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
class Iec61850MmsServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, pollInterval=0.5):
        self.host = host
        self.port = int(port)
        self.pollInterval = float(pollInterval)
        socketserver.ThreadingTCPServer.__init__(self, (self.host, self.port), MmsHandler)
        self.modelDict = {}
        self.model = None

    def addModel(self, iedName, venderName='IDE_Simulator', version='0.0.1', state=1):
        # { item : (mms_type, initial_value, writable) }
        self.modelDict[iedName] = {
            'LLN0$DC$NamPlt$vendor' : ['string', str(venderName), False],
            'LLN0$DC$NamPlt$swRev'  : ['string', str(version), False],
            'LLN0$ST$Beh$stVal'     : ['integer', int(state), False],
        }

    def addLogicNode(self, iedName, item, mms_type, value, writable=False):
        if iedName not in self.modelDict.keys(): return False
        self.modelDict[iedName][item] = [mms_type, value, writable]
        return True

    def startService(self):
        print("Start MMS server on %s:%d" % (self.host, self.port))
        self.model = IedModel(self.modelDict)
        self.serve_forever(poll_interval=self.pollInterval)

    def getIDEModelObj(self):
        return self.model

    def getParamterVal (self, iedName, item):
        if iedName not in self.modelDict.keys(): return None
        if item not in self.modelDict[iedName].keys(): return None
        return self.model.read(iedName, item)

    def setParamterVal (self, iedName, item, value):
        if iedName not in self.modelDict.keys(): return False
        if item not in self.modelDict[iedName].keys(): return False
        #if self.model[iedName][item][2] == False: return False
        self.model.write(iedName, item, self.modelDict[iedName][item][0], value)
        return True

    def stopService(self):
        self.shutdown()
        self.server_close()

# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
class Iec61850MmsClient(object):
    def __init__(self, host, port=DEFAULT_PORT, timeout=5.0):
        self.host, self.port, self.timeout = host, port, timeout
        self.sock = None
        self.conn = None
        self.invoke_id = 0

    # --------------------------------------------------------------------------------------
    def connect(self):
        try:
            self.sock = socket.create_connection((self.host, self.port), self.timeout)
        except OSError as exc:
            raise MmsError('cannot connect to %s:%d - %s' % (self.host, self.port, exc))
        self.sock.settimeout(self.timeout)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.conn = Transport(self.sock)
        try:
            self._associate()
        except (ConnectionError, OSError, ValueError) as exc:
            self.sock.close()
            raise MmsError('association failed: %s' % exc)

    # --------------------------------------------------------------------------------------
    def _associate(self):
        ref = random.randint(1, 0xFFFE)
        send_tpkt(self.sock, build_cotp_connect(0xE0, 0, ref, 0x0A, b'\x00\x01', b'\x00\x01'))
        kind, tpdu = recv_cotp(self.sock)
        if kind != 0xD0:
            raise MmsError('COTP connection refused')
        _, _, params = parse_cotp_connect(tpdu)
        self.conn.tpdu_size = 1 << params.get(0xC0, b'\x0a')[0]

        aarq = build_aarq(build_initiate(True))
        self.conn.send_spdu(build_ses_connect(build_cp_type(aarq)))
        si, user = self.conn.recv_spdu()
        if si != 0x0E:
            raise MmsError('association refused by server (SPDU 0x%02X)' % si)
        aare = dig(user, [0x31, 0xA2, 0x61, 0x30, 0xA0])
        if int.from_bytes(dig(aare, [0x61, 0xA2, 0x02]), 'big') != 0:
            raise MmsError('ACSE association rejected')
        self.negotiated = parse_initiate(dig(aare, [0x61, 0xBE, 0x28, 0xA0]))

    # --------------------------------------------------------------------------------------
    def _request(self, service):
        """Send one confirmed request, return (service_tag, service_content) of the response."""
        if not self.sock:
            raise MmsError('not connected')
        self.invoke_id += 1
        pdu = tlv(0xA0, tlv(0x02, enc_int(self.invoke_id)) + service)
        try:
            self.conn.send_mms(pdu)
            while True:
                si, user = self.conn.recv_spdu()
                if si != 0x01:
                    raise MmsError('connection released by server')
                tag, val, _ = parse_tlv(dig(user, [0x61, 0x30, 0xA0]))
                if tag == 0xA1:
                    items = parse_all(val)
                    if int.from_bytes(items[0][1], 'big', signed=True) == self.invoke_id:
                        return items[1]
                elif tag == 0xA2:
                    raise MmsError('server returned a confirmed-error')
                elif tag == 0xA4:
                    raise MmsError('server rejected the request')
                # anything else (e.g. unconfirmed reports) is skipped
        except socket.timeout:
            raise MmsError('timeout waiting for the server')
        except (ConnectionError, OSError, ValueError, IndexError) as exc:
            raise MmsError('communication error: %s' % exc)

    # --------------------------------------------------------------------------------------
    def _name_list(self, object_class, scope):
        names, after = [], b''
        while True:
            service = tlv(0xA1, tlv(0xA0, tlv(0x80, bytes([object_class]))) + tlv(0xA1, scope) + after)
            tag, val = self._request(service)
            if tag != 0xA1:
                raise MmsError('unexpected GetNameList response')
            page, more = [], True
            for t, v in parse_all(val):
                if t == 0xA0:
                    page = [x.decode() for _, x in parse_all(v)]
                elif t == 0x81:
                    more = v != b'\x00'
            names += page
            if not more or not page:
                return names
            after = tlv(0x82, page[-1].encode())

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *exc):
        self.close()

    # --------------------------------------------------------------------------------------
    def read_many(self, names):
        """[(domain, item), ...] -> list of (type, value); a failed item is a MmsAccessError."""
        tag, val = self._request(tlv(0xA4, tlv(0xA1, build_variable_list(names))))
        if tag != 0xA4:
            raise MmsError('unexpected read response')
        results = []
        for t, v in parse_all(dig(val, [0xA1])):
            results.append(MmsAccessError(v[0]) if t == 0x80 else decode_data(t, v))
        return results

    # --------------------------------------------------------------------------------------
    def read(self, domain, item):
        """-> (mms_type, value); raises MmsAccessError when the server denies access."""
        result = self.read_many([(domain, item)])[0]
        if isinstance(result, MmsAccessError):
            raise result
        return result

    # --------------------------------------------------------------------------------------
    def write(self, domain, item, mms_type, value):
        mms_type = normalize_type(mms_type)
        data = encode_data(mms_type, value)
        tag, val = self._request(tlv(0xA5, build_variable_list([(domain, item)]) + tlv(0xA0, data)))
        if tag != 0xA5:
            raise MmsError('unexpected write response')
        for t, v in parse_all(val):
            if t == 0x80:
                raise MmsAccessError(v[0])

    # --------------------------------------------------------------------------------------
    def write_auto(self, domain, item, text, mms_type=None):
        """Write a value given as text; the data type is read from the server when not given."""
        if mms_type is None:
            mms_type = self.read(domain, item)[0]
        else:
            mms_type = normalize_type(mms_type)
        self.write(domain, item, mms_type, parse_value(mms_type, text))
        return mms_type

    # --------------------------------------------------------------------------------------
    def get_domains(self):
        """Names of the logical devices (MMS domains)."""
        return self._name_list(9, tlv(0x80, b''))

    def get_variables(self, domain):
        """Names of all variables (LN$FC$DO$DA) of one domain."""
        return self._name_list(0, tlv(0x81, domain.encode()))

    # --------------------------------------------------------------------------------------
    def close(self):
        """Graceful release: MMS conclude, then ACSE release (session FINISH)."""
        if not self.sock:
            return
        try:
            self.conn.send_mms(b'\x8b\x00')
            self.conn.recv_spdu()
            self.conn.send_spdu(build_ses_release(0x09, build_pres_acse(RLRQ)))
            self.conn.recv_spdu()
        except (ConnectionError, OSError, ValueError):
            pass
        finally:
            self.sock.close()
            self.sock = None

# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
def main():
    server = Iec61850MmsServer()
    server.addModel('IED1')
    server.addLogicNode('IED1', 'MMXU1$MX$Hz$mag$f', 'float', 50.0)
    server.startService()
    print("Test get data value")
    print(server.getParamterVal('IED1', 'MMXU1$MX$Hz$mag$f'))

# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
if __name__ == '__main__':
    main()    