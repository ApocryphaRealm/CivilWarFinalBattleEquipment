#!/usr/bin/env python3
r"""Read the built plugin back and prove the things a build log cannot.

A generated plugin that loads is not the same as one that works. This checks the three ways this
build could be quietly wrong:

  * a FormID pointing at a master index the plugin does not declare - in game that reference
    resolves to nothing at all, and nothing announces it;
  * a record pointing at one of its own siblings that was never written;
  * a recipe at the forge, after the whole point of the exercise was tempering only.

It looks ONLY where FormIDs actually live - the per-type subrecord list the builder uses, the
three FormID slots inside a condition, and a properly parsed script-property block. An earlier
version scanned every four-byte window instead and reported 680 problems, almost all of which
were the letters of words like "quest" inside a script name."""
import collections
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tes4 import read_plugin

FORMID_SUBS = {
    "MGEF": {b"MDOB", b"KWDA", b"ESCE"},
    "ENCH": {b"EFID"},
    "ARMA": {b"RNAM", b"MODL", b"SNDD", b"NAM0", b"NAM1", b"NAM2", b"NAM3"},
    "ARMO": {b"RNAM", b"KWDA", b"MODL", b"EITM", b"TNAM", b"BAMT", b"BIDS", b"ETYP",
             b"YNAM", b"ZNAM"},
    "WEAP": {b"EITM", b"ETYP", b"BIDS", b"BAMT", b"INAM", b"WNAM", b"SNAM", b"XNAM",
             b"NAM7", b"NAM8", b"NAM9", b"TNAM", b"UNAM", b"CNAM", b"KWDA", b"YNAM", b"ZNAM"},
    "STAT": set(),
    "LVLI": {b"LVLG"},
    "COBJ": {b"CNAM", b"BNAM"},
    "KYWD": set(),
    "QUST": {b"ALFR", b"ALEQ", b"ALUA", b"VTCK"},
    "SMQN": {b"PNAM", b"SNAM", b"NNAM"},
    "FLST": {b"LNAM"},
    "DLBR": {b"QNAM", b"SNAM", b"TNAM"},
    "DIAL": {b"QNAM", b"BNAM"},
    "INFO": {b"PNAM"},
}
ARMOR_TABLE, SHARPENING_WHEEL, FORGE = 0x000ADB78, 0x00088108, 0x00088105
BENCH = {ARMOR_TABLE: "Armor Table", SHARPENING_WHEEL: "Sharpening Wheel", FORGE: "FORGE"}


def vmad_formids(data):
    out = []
    version, obj_format, script_count = struct.unpack_from("<hhh", data, 0)
    i = 6

    def ws(pos):
        return pos + 2 + struct.unpack_from("<H", data, pos)[0]

    def value(pos, ptype):
        if ptype == 1:
            out.append(struct.unpack_from("<I", data, pos if obj_format == 1 else pos + 4)[0])
            return pos + 8
        if ptype == 2:
            return ws(pos)
        if ptype in (3, 4):
            return pos + 4
        if ptype == 5:
            return pos + 1
        if 11 <= ptype <= 15:
            n = struct.unpack_from("<I", data, pos)[0]
            pos += 4
            for _ in range(n):
                pos = value(pos, ptype - 10)
            return pos
        raise ValueError("property type %d" % ptype)

    for _ in range(script_count):
        i = ws(i)
        if version >= 4:
            i += 1
        n = struct.unpack_from("<H", data, i)[0]
        i += 2
        for _ in range(n):
            i = ws(i)
            t = data[i]
            i += 1
            if version >= 4:
                i += 1
            i = value(i, t)
    return out


def main(path):
    recs, masters = read_plugin(path)
    self_index = len(masters)
    ours = {r.formid for r in recs[1:]}
    counts = collections.Counter(r.type.decode() for r in recs[1:])
    print("masters (%d): %s" % (len(masters), ", ".join(masters)))
    print("records: %d" % len(recs[1:]))
    print("  " + "  ".join("%s=%d" % kv for kv in sorted(counts.items())))

    problems = []

    def check(rec, sig, value):
        if value in (0, 0xFFFFFFFF):
            return
        idx = value >> 24
        if idx == self_index and value not in ours:
            problems.append("%s %08X %s -> %08X: own record never written"
                            % (rec.type.decode(), rec.formid, sig.decode(), value))
        elif idx > self_index:
            problems.append("%s %08X %s -> %08X: needs master index %d, only %d declared"
                            % (rec.type.decode(), rec.formid, sig.decode(), value, idx, len(masters)))

    for r in recs[1:]:
        keep = FORMID_SUBS.get(r.type.decode(), set())
        for sig, d in r.subs:
            if sig == b"VMAD":
                for f in vmad_formids(d):
                    check(r, sig, f)
            elif sig == b"CTDA" and len(d) >= 28:
                for off in (12, 16, 24):
                    check(r, sig, struct.unpack_from("<I", d, off)[0])
            elif sig == b"LVLO":
                check(r, sig, struct.unpack_from("<I", d, 4)[0])
            elif sig == b"CNTO":
                check(r, sig, struct.unpack_from("<I", d, 0)[0])
            elif sig in keep and d and len(d) % 4 == 0:
                for f in struct.unpack("<%dI" % (len(d) // 4), d):
                    check(r, sig, f)

    benches = collections.Counter()
    for r in recs[1:]:
        if r.type == b"COBJ":
            benches[struct.unpack("<I", r.get(b"BNAM"))[0]] += 1
    print("recipes by bench:")
    for k, v in benches.items():
        print("   %-18s %d" % (BENCH.get(k, "%08X" % k), v))
    if benches.get(FORGE):
        problems.append("%d recipe(s) still at the FORGE; this mod ships tempering only"
                        % benches[FORGE])

    seen = set()
    for r in recs[1:]:
        if r.formid in seen:
            problems.append("duplicate FormID %08X" % r.formid)
        seen.add(r.formid)

    if problems:
        print("\nPROBLEMS (%d):" % len(problems))
        for p in sorted(set(problems)):
            print("   " + p)
        return 1
    print("\nOK - every reference resolves, no duplicates, tempering only.")
    return 0


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    default = os.path.normpath(os.path.join(here, "..", "dist", "Civil War Final Battle Equipment.esp"))
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else default))
