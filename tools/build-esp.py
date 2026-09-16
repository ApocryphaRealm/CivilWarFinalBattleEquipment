#!/usr/bin/env python3
r"""Author "Civil War Final Battle Equipment.esp" from the three Civil War Champions mods already installed.

WHY THIS EXISTS AT ALL
    The owner has three mods sitting at the top of Njordlinger - Civil War Champions - My Version
    (Nexus 78892), Civil War Champions Redone (94352) and Civil War Champions - Reduced Cut (94999).
    All three are DISABLED and all three are inert, because every one of them declares
    ccffbsse001-imperialdragon.esl as a master and that Creation Club creation is not installed on
    this machine. It is paid content; the list carries only the four free creations.

    So this is not a patch. It is a standalone rebuild that takes what each of those three mods
    contributes and owes nothing to the Creation Club:

        armour and models ... Civil War Champions - My Version (NordwarUA's meshes and textures)
        enchantments ....... Civil War Champions Redone (which rebalanced them around Thaumaturgy)
        quest structure .... Civil War Champions - Reduced Cut (the champion armour arrives before
                             the final siege instead of through a duel), rebuilt here rather than
                             lifted, because the quest givers change - see below.

WHAT THE OWNER ASKED FOR, IN HIS WORDS
    "make a quest mod thats called civil war champion and uses the enchantments and armor and quest
     structure of the civil war mods i have installed at the top of njordlinger so that you get the
     armor jsut before the siege of solitude and there shouldnt be a crafting recipe, only a
     tempering recipe"
    "i like how the enchantments have unique names in the magic affects menu"
    "thaumaturgy isnt neccacery but should align with thaumaturgy values as the mod does already"
    "you should recieve the armor in windhelm from ulfric before the battle of solitude starts"
    "not at the battle"

    Each of those is a decision below, and each is marked where it is made.

THAUMATURGY WITHOUT THAUMATURGY
    Civil War Champions Redone points its enchantments at nine of Thaumaturgy's own magic effects -
    Fortify Power Attacks, Fortify Bash Damage, Resist Arrow Damage and so on, none of which exist
    in vanilla Skyrim. Mastering Thaumaturgy.esp would have made it a hard requirement, which the
    owner ruled out. Seven of those nine turn out to be plain Peak Value Modifier effects on stock
    actor values with no perk, no art and no script, so they are CLONED into this plugin at
    Thaumaturgy's own values. The two weapon debuffs are cloned with Thaumaturgy's art references
    dropped. The result runs standalone and lands on the same numbers Thaumaturgy would have given.

    The clone keeps each effect's NAME, because the owner specifically likes that the magic effects
    menu reads "Storm-Bear Helmet" rather than "Fortify Block".

Usage:  python build-esp.py [out.esp]
        Reads the three source mods and Thaumaturgy straight out of the Njordlinger instance.
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quest as questmod
from tes4 import (Record, read_plugin, canonical, Remapper, remap_vmad,
                  sub, record, group, tes4)

# --------------------------------------------------------------------------- sources

MODS = r"D:\modlists\Njordlinger\mods"
SRC_ITEMS = (os.path.join(MODS, "Civil War Champions - My Version", "CivilWarChampionsMyVersion.esp"),
             "CivilWarChampionsMyVersion.esp")
SRC_ENCH = (os.path.join(MODS, "Civil War Champions Redone - SE", "CivilWarChampionsRedone.esp"),
            "CivilWarChampionsRedone.esp")
SRC_THAUM = (os.path.join(MODS, "Thaumaturgy - An Enchanting Overhaul", "Thaumaturgy.esp"),
             "Thaumaturgy.esp")

OUT_MASTERS = ["Skyrim.esm", "Update.esm"]
SELF_INDEX = len(OUT_MASTERS) << 24          # our own records live at index 02
FIRST_ID = SELF_INDEX | 0x000800

AUTHOR = "ApocryphaRealm"
DESCRIPTION = "The champion's equipment of the Civil War, issued before the final battle"

CC = "ccffbsse001-imperialdragon.esl"        # the Creation Club master none of this needs

# --------------------------------------------------------------------------- what to take

# The twelve champion armour pieces, by their Creation Club FormID (the number is the same in
# every source because they all master the creation; only the index byte differs).
ARMOUR = [
    (0x848, "ImperialDragonHelmet"),
    (0xD69, "ImperialDragonCuirass"),
    (0x84D, "ImperialDragonGauntlets"),
    (0xD68, "ImperialDragonBoots"),
    (0x84A, "ImperialDragonShield"),
    (0x84B, "ImperialDragonCloak"),
    (0xD6B, "StormBearHelmet"),
    (0x84C, "StormBearCuirass"),
    (0xD6A, "StormBearGauntlets"),
    (0x849, "StormBearBoots"),
    (0xD6C, "StormBearShield"),
    (0x825, "StormBearCloak"),
]

WEAPONS = [
    (0x84F, "DragonsOath"),        # Imperial Dragon sword
    (0x850, "TsunsJudgement"),     # Stormcloak two-handed axe
    (0xD61, "StormBearAxe"),       # Stormcloak war axe
]

# My Version leaves two of the three champion weapons pointing at Creation Club enchantments that
# no longer exist. Redone only rebuilt one of them, so the other two are assigned here, by hand,
# to the Redone enchantment that matches what the weapon is: the Imperial sword takes Akatosh's
# Talon, both Stormcloak axes take the Storm-Bear frost enchantment. Stated plainly because it is
# a judgement call, not something recovered from the sources.
WEAPON_ENCHANT = {0x84F: 0x817, 0x850: 0x81A, 0xD61: 0x81A}

LEVELLED = [(0x878, "ImperialDragonSet"), (0x877, "StormBearSet")]

ENCHANTMENTS = [0x816, 0x817, 0x81A, 0x81B, 0x81C, 0x81D, 0x81E,
                0x83C, 0x83D, 0x83E, 0x83F, 0x840]

SET_KEYWORDS = [0x5900, 0x5903]              # Redone's own, at ITS index - resolved below

# Tempering benches. The owner: "there shouldnt be a crafting recipe, only a tempering recipe" -
# so every recipe whose bench is the FORGE is dropped on the floor, and only these two survive.
ARMOR_TABLE = 0x000ADB78
SHARPENING_WHEEL = 0x00088108
FORGE = 0x00088105

MAGIC_HAT_MARKER = 0x000435A5   # the vanilla magic-menu display object

# An armour record's model block: male and female world models, male and female first
# person, each with its texture-set companion.
MODEL_SUBS = {b"MOD2", b"MO2T", b"MOD3", b"MO3T", b"MOD4", b"MO4T", b"MOD5", b"MO5T"}

# --------------------------------------------------------------------------- naming

# THE SETS ARE THIS MOD'S OWN, AND THEY ARE NAMED THAT WAY.
#
# The owner, 2026-09-16: "i want you to frame this mod as a seperate mod ... as it is unique from
# the bethesda file in form and function", and then, choosing the names himself, "rename to ice
# veins armor and dragon blood armor".
#
# Every editor ID and every displayed name the build lifts is rewritten on the way through. The set
# names change, and so do the four different authors' prefixes that would otherwise be scattered
# through the plugin - ccFFBSSE001_, DIS_, NW_, MAG_Ench, CRSP_. What comes out is one mod with one
# naming scheme, which is what it is.
DISPLAY_RENAME = [
    ("Storm-Bear", "Ice Veins"),
    ("Imperial Dragon", "Dragon Blood"),
]
EDID_RENAME = [
    ("StormBear", "IceVeins"),
    ("Stormbear", "IceVeins"),      # the levelled list spells it with a small b
    ("Storm-Bear", "IceVeins"),
    ("ImperialDragon", "DragonBlood"),
    ("Imperial Dragon", "DragonBlood"),
]
EDID_PREFIX = [
    ("ccFFBSSE001_", "ACWFBE_"),
    ("ccFFBSSE001", "ACWFBE_"),
    ("MAG_Ench", "ACWFBE_Ench"),
    ("CRSP_", "ACWFBE_"),
    ("DIS_", "ACWFBE_"),
    ("NW_", "ACWFBE_"),
    ("Temper", "ACWFBE_Temper"),
]

# One enchantment came through the sources named "Frost Damage" while every other one carries the
# name of the piece it sits on. The owner keeps the per-piece naming deliberately - "i like how the
# enchantments have unique names in the magic affects menu" - so the odd one out is brought into
# line rather than left generic.
DISPLAY_FIXUPS = {"Frost Damage": "Ice Veins Axe"}

_seen_edids = {}


def rename_names(sig, data, formid):
    """Rewrite an EDID or a FULL on its way into the new plugin."""
    text = data[:-1].decode("cp1252")
    if sig == b"FULL":
        for old, new in DISPLAY_RENAME:
            text = text.replace(old, new)
        text = DISPLAY_FIXUPS.get(text, text)
    else:
        for old, new in EDID_RENAME:
            text = text.replace(old, new)
        for old, new in EDID_PREFIX:
            if text.startswith(old):
                text = new + text[len(old):]
                break
        if not text.startswith("ACWFBE_"):
            text = "ACWFBE_" + text
        if text in _seen_edids and _seen_edids[text] != formid:
            raise SystemExit("editor id collision after renaming: %s is wanted by %08X and %08X"
                             % (text, _seen_edids[text], formid))
        _seen_edids[text] = formid
    return text.encode("cp1252") + b"\x00"


# --------------------------------------------------------------------------- FormID handling

# Which subrecords hold FormIDs, per record type. Being explicit per type matters: MODL is a list
# of armature FormIDs inside ARMO and ARMA, and a mesh PATH inside WEAP and MGEF. One global list
# would corrupt one or the other.
FORMID_SUBS = {
    "MGEF": {b"MDOB", b"KWDA", b"ESCE"},
    "ENCH": {b"EFID"},
    "ARMA": {b"RNAM", b"MODL", b"SNDD", b"NAM0", b"NAM1", b"NAM2", b"NAM3"},
    "ARMO": {b"RNAM", b"KWDA", b"MODL", b"EITM", b"TNAM", b"BAMT", b"BIDS", b"ETYP",
             b"YNAM", b"ZNAM"},
    "WEAP": {b"EITM", b"ETYP", b"BIDS", b"BAMT", b"INAM", b"WNAM", b"SNAM", b"XNAM",
             b"NAM7", b"NAM8", b"NAM9", b"TNAM", b"UNAM", b"CNAM", b"KWDA", b"YNAM", b"ZNAM"},
    "LVLI": {b"LVLG"},
    "COBJ": {b"CNAM", b"BNAM"},
    "KYWD": set(),
}

CTDA_FORMID_OFFSETS = (12, 16, 24)           # param1, param2, run-on reference


def remap_ctda(data, remap):
    out = bytearray(data)
    for off in CTDA_FORMID_OFFSETS:
        if off + 4 <= len(data):
            v = struct.unpack_from("<I", data, off)[0]
            if v not in (0, 0xFFFFFFFF):
                struct.pack_into("<I", out, off, remap(v))
    return bytes(out)


def remap_body(rec, remap, skip=(), replace=None, new_id=None):
    """Rebuild a record body with every FormID translated into the new plugin's numbering."""
    keep = FORMID_SUBS.get(rec.type.decode(), set())
    out = b""
    for sig, data in rec.subs:
        if sig in skip:
            continue
        if sig in (b"EDID", b"FULL") and data.endswith(b"\x00"):
            out += sub(sig, rename_names(sig, data, new_id if new_id is not None else rec.formid))
            continue
        if replace and sig in replace:
            for d in replace[sig]:
                out += sub(sig, d)
            continue
        if sig == b"VMAD":
            data = remap_vmad(data, remap)
        elif sig == b"CTDA":
            data = remap_ctda(data, remap)
        elif sig == b"LVLO":
            f = struct.unpack_from("<I", data, 4)[0]
            data = data[:4] + struct.pack("<I", remap(f)) + data[8:]
        elif sig == b"CNTO":
            f = struct.unpack_from("<I", data, 0)[0]
            data = struct.pack("<I", remap(f)) + data[4:]
        elif sig in keep and data and len(data) % 4 == 0:
            ids = struct.unpack("<%dI" % (len(data) // 4), data)
            data = struct.pack("<%dI" % len(ids), *[remap(i) for i in ids])
        out += sub(sig, data)
    return out


# --------------------------------------------------------------------------- MGEF cloning

# MGEF DATA offsets that hold a FormID pointing at art, shaders or projectiles. Thaumaturgy's two
# weapon debuffs use its own art for these; a standalone plugin cannot, so they are zeroed. The
# effect still fires with the same magnitude on the same actor value - only its visuals are the
# game's defaults.
MGEF_ART_OFFSETS = (24, 32, 36, 72, 76, 92, 96, 100, 108, 116, 120, 124, 128, 132, 136)


def clone_mgef(rec, new_id, remap):
    data = bytearray(rec.get(b"DATA"))
    for off in MGEF_ART_OFFSETS:
        v = struct.unpack_from("<I", data, off)[0]
        if v and (v >> 24) >= 2:            # points into Thaumaturgy or a DLC - drop it
            struct.pack_into("<I", data, off, 0)
    body = b""
    for sig, d in rec.subs:
        # VMAD here is Thaumaturgy's enchanting-XP script and CTDA/KWDA reference its keywords;
        # none of that can travel, and none of it is what the effect DOES.
        if sig in (b"VMAD", b"CTDA", b"KSIZ", b"KWDA"):
            continue
        if sig in (b"EDID", b"FULL"):
            body += sub(sig, rename_names(sig, d, new_id))
            continue
        if sig == b"DATA":
            d = bytes(data)
        elif sig == b"MDOB":
            # The menu display object is the little model the magic menu spins next to the effect.
            # Seven of the nine already use the vanilla MagicHatMarker; the other two point at one
            # of Thaumaturgy's own, which cannot travel, so they join the seven.
            f = struct.unpack("<I", d)[0]
            d = struct.pack("<I", MAGIC_HAT_MARKER if (f >> 24) >= 2 else remap(f))
        body += sub(sig, d)
    return record(b"MGEF", new_id, body)


# --------------------------------------------------------------------------- main

def main(out_path):
    items, m_items = read_plugin(SRC_ITEMS[0])
    ench, m_ench = read_plugin(SRC_ENCH[0])
    thaum, m_thaum = read_plugin(SRC_THAUM[0])

    by_id = lambda recs: {r.formid: r for r in recs[1:]}
    I, E, T = by_id(items), by_id(ench), by_id(thaum)

    def idx_of(masters, name):
        low = [m.lower() for m in masters]
        return low.index(name.lower())

    cc_in_items = idx_of(m_items, CC) << 24
    cc_in_ench = idx_of(m_ench, CC) << 24
    self_items = len(m_items) << 24
    self_ench = len(m_ench) << 24
    thaum_in_ench = idx_of(m_ench, "Thaumaturgy.esp") << 24
    self_thaum = len(m_thaum) << 24

    table = {}                                # canonical (plugin, local) -> new FormID
    next_id = [FIRST_ID]

    def allot(plugin, local):
        key = (plugin.lower(), local)
        if key not in table:
            table[key] = next_id[0]
            next_id[0] += 1
        return table[key]

    # ---- 1. the nine Thaumaturgy magic effects the enchantments stand on
    needed_mgef = []
    for local in ENCHANTMENTS:
        r = E[cc_in_ench | local]
        for d in r.all(b"EFID"):
            f = struct.unpack("<I", d)[0]
            if (f & 0xFF000000) == thaum_in_ench and (f & 0xFFFFFF) not in needed_mgef:
                needed_mgef.append(f & 0xFFFFFF)
    mgef_bytes = b""
    for local in needed_mgef:
        src = T[self_thaum | local]
        new = allot(SRC_THAUM[1], local)
        rm = Remapper(m_thaum, SRC_THAUM[1], table, OUT_MASTERS)
        mgef_bytes += clone_mgef(src, new, rm)
        if rm.unresolved:
            raise SystemExit("MGEF %s still needs %s" % (src.edid(), rm.unresolved))

    # ---- 2. Redone's two set keywords, its twelve enchantments
    kywd_bytes = b""
    for local in SET_KEYWORDS:
        src = E[self_ench | local]
        new = allot(SRC_ENCH[1], local)
        rm = Remapper(m_ench, SRC_ENCH[1], table, OUT_MASTERS)
        kywd_bytes += record(b"KYWD", new, remap_body(src, rm, new_id=new))

    ench_bytes = b""
    for local in ENCHANTMENTS:
        src = E[cc_in_ench | local]
        new = allot(CC, local)
        rm = Remapper(m_ench, SRC_ENCH[1], table, OUT_MASTERS)
        ench_bytes += record(b"ENCH", new, remap_body(src, rm, new_id=new))
        report_unresolved(src, rm)

    # ---- 3. armour: My Version's models over Redone's stats and enchantments
    arma_needed = []
    for local, _ in ARMOUR:
        mv = I[cc_in_items | local]
        for d in mv.all(b"MODL"):
            f = struct.unpack("<I", d)[0]
            if f not in arma_needed:
                arma_needed.append(f)

    arma_bytes = b""
    for f in arma_needed:
        if f not in I:
            raise SystemExit("armature %08X is not in My Version - it must be Creation Club" % f)
        src = I[f]
        plugin = CC if (f & 0xFF000000) == cc_in_items else SRC_ITEMS[1]
        new = allot(plugin, f & 0xFFFFFF)
        rm = Remapper(m_items, SRC_ITEMS[1], table, OUT_MASTERS)
        arma_bytes += record(b"ARMA", new, remap_body(src, rm, new_id=new))
        report_unresolved(src, rm)

    armo_bytes = b""
    for local, name in ARMOUR:
        base = E[cc_in_ench | local]          # Redone: stats, keywords, enchantment, name
        mv = I[cc_in_items | local]           # My Version: the meshes and the armatures
        new = allot(CC, local)
        rm = Remapper(m_ench, SRC_ENCH[1], table, OUT_MASTERS)
        body = b""
        emitted_modl = False
        for sig, d in base.subs:
            # Same Creation Club plumbing the weapons carry: a defaultsetstageonplayeracquireitem
            # script pointed at the creation's duel quest. Nothing here has a duel to advance.
            if sig == b"VMAD":
                continue
            # The WHOLE model block comes from My Version, not just the male ground model.
            # Redone's record still carries the creation's female world model in MOD4, and
            # inheriting it shipped a mesh path into creationclubfbsse001\ that nothing on this
            # machine can supply - a silently invisible cuirass on every female character.
            if sig in MODEL_SUBS:
                d2 = mv.get(sig)
                if d2 is not None:
                    body += sub(sig, d2)
                continue
            if sig == b"MODL":
                if emitted_modl:
                    continue
                emitted_modl = True
                rmi = Remapper(m_items, SRC_ITEMS[1], table, OUT_MASTERS)
                for d2 in mv.all(b"MODL"):
                    body += sub(b"MODL", struct.pack("<I", rmi(struct.unpack("<I", d2)[0])))
                report_unresolved(mv, rmi)
                continue
            if sig in (b"EDID", b"FULL"):
                body += sub(sig, rename_names(sig, d, new))
                continue
            if sig == b"CTDA":
                d = remap_ctda(d, rm)
            elif sig in FORMID_SUBS["ARMO"] and d and len(d) % 4 == 0:
                ids = struct.unpack("<%dI" % (len(d) // 4), d)
                d = struct.pack("<%dI" % len(ids), *[rm(i) for i in ids])
            body += sub(sig, d)
        armo_bytes += record(b"ARMO", new, body)
        report_unresolved(base, rm)

    # ---- 4. the three champion weapons, wearing Redone's enchantments
    #
    # Two things have to go on the way through. The EITM is a Creation Club enchantment that no
    # longer exists, replaced by the Redone one chosen in WEAPON_ENCHANT. And the VMAD is a
    # defaultsetstageonplayeracquireitem script wired to the creation's own quest - Creation Club
    # plumbing for the duel this mod deliberately does not have.
    stat_bytes = b""
    for local, _ in WEAPONS:
        f = struct.unpack("<I", I[cc_in_items | local].get(b"WNAM"))[0]
        if f not in I:
            raise SystemExit("first-person model %08X for weapon %03X is not in My Version"
                             % (f, local))
        src = I[f]
        rm = Remapper(m_items, SRC_ITEMS[1], table, OUT_MASTERS)
        statid = allot(SRC_ITEMS[1], f & 0xFFFFFF)
        stat_bytes += record(b"STAT", statid, remap_body(src, rm, new_id=statid))
        report_unresolved(src, rm)

    weap_bytes = b""
    for local, name in WEAPONS:
        src = I[cc_in_items | local]
        new = allot(CC, local)
        rm = Remapper(m_items, SRC_ITEMS[1], table, OUT_MASTERS)
        want_ench = table[(CC, WEAPON_ENCHANT[local])]
        weap_bytes += record(b"WEAP", new,
                             remap_body(src, rm, skip=(b"VMAD",), new_id=new,
                                        replace={b"EITM": [struct.pack("<I", want_ench)]}))
        report_unresolved(src, rm)

    # ---- 5. the two levelled lists the quest hands over
    #
    # These are the creation's own "the whole set" lists, which is exactly what should land in the
    # player's pack. One entry in the Imperial list is a Creation Club form that My Version never
    # replaced, so it cannot be rebuilt and is dropped; LLCT is corrected to match, because a count
    # that disagrees with the entries is the kind of thing that loads fine and then hands out
    # nothing.
    lvli_bytes, lvli_dropped = b"", []
    for local, name in LEVELLED:
        src = I[cc_in_items | local]
        new = allot(CC, local)
        rm = Remapper(m_items, SRC_ITEMS[1], table, OUT_MASTERS)
        body, entries = b"", 0
        for sig, d in src.subs:
            if sig in (b"EDID", b"FULL"):
                body += sub(sig, rename_names(sig, d, new))
                continue
            if sig == b"LLCT":
                continue
            if sig == b"LVLO":
                f = struct.unpack_from("<I", d, 4)[0]
                probe = Remapper(m_items, SRC_ITEMS[1], table, OUT_MASTERS)
                probe(f)
                if probe.unresolved:
                    lvli_dropped.append((name, "%08X" % f))
                    continue
                d = d[:4] + struct.pack("<I", rm(f)) + d[8:]
                entries += 1
                body += sub(b"LVLO", d)
                continue
            if sig == b"LVLF":
                body += sub(sig, d)
                body += sub(b"LLCT", struct.pack("<B", 0))   # placeholder, fixed below
                continue
            body += sub(sig, d)
        body = body.replace(sub(b"LLCT", struct.pack("<B", 0)),
                            sub(b"LLCT", struct.pack("<B", entries)), 1)
        lvli_bytes += record(b"LVLI", new, body)
        report_unresolved(src, rm)

    # ---- 6. tempering recipes ONLY
    ours = {table[(CC, local)] for local, _ in ARMOUR} | {table[(CC, local)] for local, _ in WEAPONS}
    cobj_bytes, kept, dropped = b"", [], 0
    for r in items[1:]:
        if r.type != b"COBJ":
            continue
        bench = struct.unpack("<I", r.get(b"BNAM"))[0]
        result = r.get(b"CNAM")
        if result is None:
            continue
        rm = Remapper(m_items, SRC_ITEMS[1], table, OUT_MASTERS)
        if rm(struct.unpack("<I", result)[0]) not in ours:
            continue
        if bench == FORGE:
            dropped += 1
            continue
        if bench not in (ARMOR_TABLE, SHARPENING_WHEEL):
            continue
        rm = Remapper(m_items, SRC_ITEMS[1], table, OUT_MASTERS)
        new = allot(SRC_ITEMS[1], r.formid & 0xFFFFFF)
        cobj_bytes += record(b"COBJ", new, remap_body(r, rm))
        kept.append(r.edid())
        report_unresolved(r, rm)

    groups = [(b"KYWD", kywd_bytes), (b"MGEF", mgef_bytes), (b"ENCH", ench_bytes),
              (b"ARMA", arma_bytes), (b"ARMO", armo_bytes), (b"STAT", stat_bytes),
              (b"WEAP", weap_bytes),
              (b"LVLI", lvli_bytes), (b"COBJ", cobj_bytes)]

    quest_records, quest_groups = questmod.build(
        allot, table[(CC, LEVELLED[0][0])], table[(CC, LEVELLED[1][0])])
    groups += quest_groups

    count = len(table)
    blob = tes4(OUT_MASTERS, count, (next_id[0] & 0xFFFFFF), AUTHOR, DESCRIPTION)
    for label, payload in groups:
        if payload:
            blob += group(label, payload)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    open(out_path, "wb").write(blob)

    print("wrote %s  (%d bytes)" % (out_path, len(blob)))
    print("  magic effects cloned from Thaumaturgy .... %d" % len(needed_mgef))
    print("  enchantments ............................. %d" % len(ENCHANTMENTS))
    print("  armour pieces ............................ %d  (%d armatures)"
          % (len(ARMOUR), len(arma_needed)))
    print("  weapons .................................. %d" % len(WEAPONS))
    print("  levelled lists ........................... %d" % len(LEVELLED))
    for name, f in lvli_dropped:
        print("      dropped from %s: %s (Creation Club only, nothing to rebuild it from)"
              % (name, f))
    print("  TEMPERING recipes kept ................... %d" % len(kept))
    print("  crafting recipes dropped ................. %d  (as asked: tempering only)" % dropped)
    print("  quest records ............................ %d" % quest_records)
    print("  total new records ........................ %d" % len(table))


def report_unresolved(src, rm):
    if rm.unresolved:
        raise SystemExit("%s %08X references %s, which this plugin cannot reach"
                         % (src.type.decode(), src.formid,
                            ", ".join("%s:%06X" % k for k in sorted(rm.unresolved))))


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    default = os.path.normpath(os.path.join(here, "..", "dist", "Civil War Final Battle Equipment.esp"))
    main(sys.argv[1] if len(sys.argv) > 1 else default)
