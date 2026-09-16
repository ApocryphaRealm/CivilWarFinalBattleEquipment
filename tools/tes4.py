#!/usr/bin/env python3
r"""A small TES4 plugin reader/writer - enough to lift records out of one plugin into another.

This is the shared half of the Civil War Champion build. build-esp.py holds the decisions about
WHAT to lift and why; this file holds the file format and nothing else, so the two can be read
separately.

THE ONE IDEA WORTH KNOWING
    A FormID's top byte is an index into the plugin's OWN master list, so the same record has a
    different number in every plugin that mentions it. Lifting records between plugins therefore
    means translating every FormID through a canonical form - (which plugin, which local id) -
    rather than copying the number across. `canonical()` and `Remapper` are that translation, and
    every mistake this file is designed to prevent is a FormID that was copied instead.
"""
import struct
import zlib

FORM_VERSION = 44  # Skyrim SE


# --------------------------------------------------------------------------- reading

class Record(object):
    __slots__ = ("type", "formid", "flags", "subs")

    def __init__(self, type_, formid, flags, data):
        self.type, self.formid, self.flags = type_, formid, flags
        self.subs = parse_subrecords(data)

    def get(self, sig):
        for s, d in self.subs:
            if s == sig:
                return d
        return None

    def all(self, sig):
        return [d for s, d in self.subs if s == sig]

    def edid(self):
        d = self.get(b"EDID")
        return d[:-1].decode("cp1252", "replace") if d else ""

    def full(self):
        d = self.get(b"FULL")
        return d[:-1].decode("cp1252", "replace") if d else ""

    def body(self):
        return b"".join(sub(s, d) for s, d in self.subs)


def parse_subrecords(data):
    """Split a record body into (signature, payload) pairs.

    XXXX carries the real length of the subrecord that follows it, for payloads that do not fit
    in the normal 16-bit size field. It is consumed here rather than passed on, and re-emitted by
    sub() when needed, so callers never have to think about it."""
    out, i, n, big = [], 0, len(data), None
    while i + 6 <= n:
        sig = data[i:i + 4]
        size = struct.unpack_from("<H", data, i + 4)[0]
        i += 6
        if sig == b"XXXX":
            big = struct.unpack_from("<I", data, i)[0]
            i += size
            continue
        if big is not None:
            size, big = big, None
        out.append((sig, data[i:i + size]))
        i += size
    return out


def read_plugin(path):
    """Return (records, masters). records[0] is the TES4 header."""
    raw = open(path, "rb").read()
    recs = []

    def walk(off, end):
        while off < end:
            sig = raw[off:off + 4]
            size = struct.unpack_from("<I", raw, off + 4)[0]
            if sig == b"GRUP":
                walk(off + 24, off + size)
                off += size
                continue
            flags = struct.unpack_from("<I", raw, off + 8)[0]
            formid = struct.unpack_from("<I", raw, off + 12)[0]
            data = raw[off + 24:off + 24 + size]
            if flags & 0x00040000:          # compressed record
                data = zlib.decompress(data[4:])
                flags &= ~0x00040000
            recs.append(Record(sig, formid, flags, data))
            off += 24 + size

    walk(0, len(raw))
    masters = [d[:-1].decode("cp1252") for s, d in recs[0].subs if s == b"MAST"]
    return recs, masters


# --------------------------------------------------------------------------- FormIDs

def canonical(formid, masters, self_name):
    """(plugin name, local id) - the same record has the same canonical form everywhere."""
    idx = formid >> 24
    local = formid & 0xFFFFFF
    if idx < len(masters):
        return (masters[idx].lower(), local)
    return (self_name.lower(), local)


class Remapper(object):
    """Translates FormIDs out of one source plugin and into the plugin being written.

    `table` maps a canonical (plugin, local) to a FormID in the new plugin. Anything not in the
    table has to resolve to one of the new plugin's own masters, or it is a dangling reference and
    the build stops - a dangling FormID is the failure mode that produces a plugin which loads,
    looks right in xEdit, and does nothing in game."""

    def __init__(self, masters, self_name, table, out_masters):
        self.masters, self.self_name, self.table = masters, self_name, table
        self.out_index = {m.lower(): i for i, m in enumerate(out_masters)}
        self.unresolved = set()

    def __call__(self, formid):
        if formid == 0:
            return 0
        key = canonical(formid, self.masters, self.self_name)
        if key in self.table:
            return self.table[key]
        if key[0] in self.out_index:
            return (self.out_index[key[0]] << 24) | key[1]
        self.unresolved.add(key)
        return formid


# --------------------------------------------------------------------------- VMAD

def remap_vmad(data, remap):
    """Rewrite the FormIDs inside a script-property block, leaving everything else byte-identical.

    A VMAD holds each script's property fills, and an object property IS a FormID - the one the
    Creation Kit shows as "None" when it cannot be resolved. Fragment data (quest/topic/scene
    fragments) follows the scripts and holds no FormIDs, so parsing stops at the end of the
    property lists and the tail is copied through untouched."""
    out = bytearray(data)
    version, obj_format, script_count = struct.unpack_from("<hhh", data, 0)
    i = 6

    def skip_wstring(pos):
        ln = struct.unpack_from("<H", data, pos)[0]
        return pos + 2 + ln

    def property_value(pos, ptype):
        # Returns the position after the value, remapping object FormIDs in place.
        if ptype == 1:                              # object
            if obj_format == 1:                     # formid, alias, unused
                fid = struct.unpack_from("<I", data, pos)[0]
                struct.pack_into("<I", out, pos, remap(fid))
            else:                                   # unused, alias, formid
                fid = struct.unpack_from("<I", data, pos + 4)[0]
                struct.pack_into("<I", out, pos + 4, remap(fid))
            return pos + 8
        if ptype == 2:                              # wstring
            return skip_wstring(pos)
        if ptype in (3, 4, 5):                      # int32, float, bool(1 byte)
            return pos + (1 if ptype == 5 else 4)
        if 11 <= ptype <= 15:                       # arrays of the above
            count = struct.unpack_from("<I", data, pos)[0]
            pos += 4
            for _ in range(count):
                pos = property_value(pos, ptype - 10)
            return pos
        raise ValueError("unknown VMAD property type %d" % ptype)

    for _ in range(script_count):
        i = skip_wstring(i)
        if version >= 4:
            i += 1                                   # status
        prop_count = struct.unpack_from("<H", data, i)[0]
        i += 2
        for _ in range(prop_count):
            i = skip_wstring(i)
            ptype = data[i]
            i += 1
            if version >= 4:
                i += 1                               # status
            i = property_value(i, ptype)
    return bytes(out)


# --------------------------------------------------------------------------- writing

def sub(sig, data):
    if len(data) > 0xFFFF:
        return b"XXXX" + struct.pack("<HI", 4, len(data)) + sig + struct.pack("<H", 0) + data
    return sig + struct.pack("<H", len(data)) + data


def record(sig, formid, body, flags=0):
    return (sig + struct.pack("<I", len(body)) + struct.pack("<I", flags) +
            struct.pack("<I", formid) + struct.pack("<I", 0) +
            struct.pack("<H", FORM_VERSION) + struct.pack("<H", 0) + body)


def group(label, payload, group_type=0):
    if isinstance(label, int):
        label = struct.pack("<I", label)
    return (b"GRUP" + struct.pack("<I", len(payload) + 24) + label +
            struct.pack("<I", group_type) + struct.pack("<I", 0) + struct.pack("<I", 0) + payload)


def tes4(masters, record_count, next_object_id, author, description):
    body = sub(b"HEDR", struct.pack("<fiI", 1.7, record_count, next_object_id))
    body += sub(b"CNAM", author.encode("cp1252") + b"\x00")
    body += sub(b"SNAM", description.encode("cp1252") + b"\x00")
    for m in masters:
        body += sub(b"MAST", m.encode("cp1252") + b"\x00")
        body += sub(b"DATA", struct.pack("<Q", 0))
    return record(b"TES4", 0, body)
