#!/usr/bin/env python3
r"""The quest half of Civil War Final Battle Equipment - authored here rather than lifted.

WHY AUTHORED AND NOT LIFTED
    The shape is Kamikaze's, from Civil War Final Battle Equipments - Reduced Cut: a Story Manager node watching
    the Change Location event, a helper quest that asks "is the city under siege one of the two
    capitals?", and a miscellaneous quest that puts an objective in the journal and hands the set
    over through one line of dialogue. That shape is the right one and it is credited.

    Every record is rebuilt rather than copied because the owner moved the handover:

        "you should recieve the armor in windhelm from ulfric before the battle of solitude starts"
        "not at the battle"
        "you would have to get it as a reward from whatever is the last civil war quest before the
         battle of solitude"

    Kamikaze hands the armour over at the FIELD COMMANDER - CWFieldCOSonsEastmarchCapital and
    FieldCOImperialHaafingarCapital, the officers standing at the siege camp. The owner wants it
    from ULFRIC, in Windhelm, at the moment the final assault is ordered and before anyone marches.
    So the quest givers become Ulfric Stormcloak and General Tullius themselves, filled as Unique
    Actor aliases rather than forced references, and the trigger stays where Kamikaze put it -
    on CWSiegeObj naming its city - because that IS the moment the last order is given, while the
    player is still standing in the Palace of the Kings.

THE TRIGGER, PRECISELY
    CWSiegeObj (00096E71) is the vanilla "Battle for <City>" quest and it runs for every siege in
    the war, Whiterun included. What separates the last one is its City alias: when that alias is
    Solitude or Windhelm, this is the final battle. The helper quest reads that alias through an
    External Alias Reference, so there is no guessing and no polling.
"""
import struct

from tes4 import sub, record, group

# ------------------------------------------------------------------ vanilla forms this leans on
CW_SIEGE_OBJ = 0x00096E71       # QUST "Battle for <Alias=City>"
CW_SIEGE_OBJ_CITY_ALIAS = 1     # its City location alias
SM_CHANGE_LOCATION = 0x0001320E  # SMEN whose event is 'CLOC'
LOC_SOLITUDE = 0x00018A5A
LOC_WINDHELM = 0x00018A57
NPC_ULFRIC = 0x0001414D
NPC_TULLIUS = 0x0001327E
FACT_IMPERIAL = 0x0002BF9A      # CWImperialFaction
FACT_SONS = 0x0002BF9B          # CWSonsFaction
PLAYER_REF = 0x00000014

# Condition function indices, read off the records this mod is modelled on rather than guessed:
# 58 appears with a quest FormID and a stage number, 71 with a faction and the player as the
# run-on reference, 72 with an NPC and the speaker as subject.
FUNC_QUEST_RUNNING = 56
FUNC_GET_STAGE = 58
FUNC_IN_FACTION = 71
FUNC_GET_IS_ID = 72

RUN_ON_SUBJECT = 0
RUN_ON_REFERENCE = 2

STAGE_OFFERED = 10
STAGE_IMPERIAL = 100
STAGE_STORMCLOAK = 110


# ------------------------------------------------------------------ small builders

def z(text):
    return text.encode("cp1252") + b"\x00"


def wstring(text):
    b = text.encode("cp1252")
    return struct.pack("<H", len(b)) + b


def ctda(function, param1=0, param2=0, comparison=1.0, operator=0,
         run_on=RUN_ON_SUBJECT, reference=0):
    """A condition, ALREADY WRAPPED as a CTDA subrecord.

    It returns the wrapped form on purpose. The first version of this returned the bare 32-byte
    struct, every call site did `body += ctda(...)`, and the conditions went into the record with
    no subrecord header at all - which silently truncated every quest record at its first
    condition. The plugin still loaded, the scripts still attached, and the quest still took a
    stage; only the objectives, the targets and the aliases quietly did not exist."""
    return sub(b"CTDA", struct.pack("<BBBBfIIIIiI", operator, 0, 0, 0, comparison, function,
                                    param1, param2, run_on, reference, 0xFFFFFFFF))


def vmad_scripts(scripts):
    """scripts: [(name, [(prop_name, formid, alias)])] - object properties only, which is all any
    of these need."""
    out = struct.pack("<hhh", 5, 2, len(scripts))
    for name, props in scripts:
        out += wstring(name) + b"\x00" + struct.pack("<H", len(props))
        for pname, fid, alias in props:
            out += wstring(pname) + b"\x01\x01"
            out += struct.pack("<HHI", 0, alias & 0xFFFF, fid)
    return out


def quest_fragments(filename, fragments):
    """fragments: [(stage, item_index, script, function)]"""
    out = b"\x02" + struct.pack("<h", len(fragments)) + wstring(filename)
    for stage, item, script, func in fragments:
        out += struct.pack("<HhiB", stage, 0, item, 1) + wstring(script) + wstring(func)
    out += struct.pack("<h", 0)          # no alias fragments
    return out


def info_fragment(filename, script, func):
    # flags 2 = the fragment runs when the topic info ENDS, which is when the reward should land.
    return b"\x02\x02" + wstring(filename) + b"\x01" + wstring(script) + wstring(func)


def trdt(response_number=1, emotion_value=50):
    """emotion type, emotion value, unused, response number, unused, sound, emotion anim, unused."""
    return (struct.pack("<IiI", 0, emotion_value, 0) + struct.pack("<B3x", response_number) +
            struct.pack("<I", 0) + struct.pack("<B3x", 0))


# ------------------------------------------------------------------ the records

def build(allot, lvli_imperial, lvli_stormcloak):
    """Returns (record count, [(group label, payload)])."""
    q_champion = allot("acwc", 0x900)
    q_trigger = allot("acwc", 0x901)
    smqn = allot("acwc", 0x902)
    flst = allot("acwc", 0x903)
    dlbr = allot("acwc", 0x904)
    dial = allot("acwc", 0x905)
    info_imperial = allot("acwc", 0x906)
    info_sons = allot("acwc", 0x907)

    in_imperial = ctda(FUNC_IN_FACTION, FACT_IMPERIAL, run_on=RUN_ON_REFERENCE, reference=PLAYER_REF)
    in_sons = ctda(FUNC_IN_FACTION, FACT_SONS, run_on=RUN_ON_REFERENCE, reference=PLAYER_REF)

    # ---------------------------------------------------------------- the champion quest
    body = z_sub(b"EDID", "ACWFBE_EquipmentQuest")
    body += sub(b"VMAD", vmad_scripts([("ACWFBE_EquipmentQF", [
        ("PlayerRef", PLAYER_REF, 0xFFFF),
        ("ImperialSet", lvli_imperial, 0xFFFF),
        ("StormcloakSet", lvli_stormcloak, 0xFFFF),
    ])]) + quest_fragments("ACWFBE_EquipmentQF", [
        # Stage 10 carries TWO stage items, one per side, so that the journal entry can name the
        # right commander - and a fragment attaches to a stage ITEM, not to the stage. Attaching
        # Fragment_0 only to item 0 would have shown the objective to Stormcloaks and silently
        # skipped it for Imperials, which is the sort of thing that only ever shows up in game.
        (STAGE_OFFERED, 0, "ACWFBE_EquipmentQF", "Fragment_0"),
        (STAGE_OFFERED, 1, "ACWFBE_EquipmentQF", "Fragment_0"),
        (STAGE_IMPERIAL, 0, "ACWFBE_EquipmentQF", "Fragment_1"),
        (STAGE_STORMCLOAK, 0, "ACWFBE_EquipmentQF", "Fragment_2"),
    ]))
    body += z_sub(b"FULL", "Civil War Final Battle Equipment")
    # flags 0x0100 = run once; priority 30; quest type 6 = Miscellaneous, so it sits in the
    # journal's Misc list exactly as Reduced Cut's did.
    body += sub(b"DNAM", struct.pack("<HBBII", 0x0100, 30, 0xFF, 0, 6))
    body += sub(b"NEXT", b"")

    body += sub(b"INDX", struct.pack("<HBB", STAGE_OFFERED, 0, 0))
    body += sub(b"QSDT", b"\x00") + in_sons + z_sub(b"CNAM",
        "Ulfric Stormcloak has given the order to march on Solitude. Before we go, there is a "
        "set of Ice Veins armour waiting for me in the Palace of the Kings.")
    body += sub(b"QSDT", b"\x00") + in_imperial + z_sub(b"CNAM",
        "General Tullius has given the order to march on Windhelm. Before we go, there is a "
        "set of Dragon Blood armour waiting for me in Castle Dour.")

    body += sub(b"INDX", struct.pack("<HBB", STAGE_IMPERIAL, 0, 0))
    body += sub(b"QSDT", b"\x01") + z_sub(b"CNAM",
        "General Tullius has given me the Dragon Blood armour. I will wear it into Windhelm.")

    body += sub(b"INDX", struct.pack("<HBB", STAGE_STORMCLOAK, 0, 0))
    body += sub(b"QSDT", b"\x01") + z_sub(b"CNAM",
        "Ulfric Stormcloak has given me the Ice Veins armour. I will wear it into Solitude.")

    body += sub(b"QOBJ", struct.pack("<h", STAGE_OFFERED))
    body += sub(b"FNAM", struct.pack("<I", 0))
    body += z_sub(b"NNAM", "Collect your armour from your commander")
    body += sub(b"QSTA", struct.pack("<II", 1, 0)) + in_sons
    body += sub(b"QSTA", struct.pack("<II", 2, 0)) + in_imperial

    body += sub(b"ANAM", struct.pack("<I", 3))
    body += alias_unique(1, "UlfricRef", NPC_ULFRIC)
    body += alias_unique(2, "TulliusRef", NPC_TULLIUS)
    champion = record(b"QUST", q_champion, body)

    # ---------------------------------------------------------------- the trigger quest
    body = z_sub(b"EDID", "ACWFBE_TriggerQuest")
    body += sub(b"VMAD", vmad_scripts([("ACWFBE_TriggerScript", [
        ("ChampionQuest", q_champion, 0xFFFF),
        ("FinalSiegeLocations", flst, 0xFFFF),
        ("SiegeCity", q_trigger, 1),
    ])]))
    body += sub(b"DNAM", struct.pack("<HBBII", 0, 0, 0xFF, 0, 0))
    body += sub(b"ENAM", b"CLOC")
    body += sub(b"NEXT", b"")
    body += sub(b"ANAM", struct.pack("<I", 2))
    body += sub(b"ALLS", struct.pack("<I", 1))
    body += z_sub(b"ALID", "SiegeCity")
    body += sub(b"FNAM", struct.pack("<I", 0))
    body += sub(b"ALEQ", struct.pack("<I", CW_SIEGE_OBJ))
    body += sub(b"ALEA", struct.pack("<I", CW_SIEGE_OBJ_CITY_ALIAS))
    body += sub(b"ALED", b"")
    trigger = record(b"QUST", q_trigger, body)

    # ---------------------------------------------------------------- Story Manager node
    body = z_sub(b"EDID", "ACWFBE_TriggerNode")
    body += sub(b"PNAM", struct.pack("<I", SM_CHANGE_LOCATION))
    body += sub(b"CITC", struct.pack("<I", 2))
    # Only while the siege quest is actually running, and only once - the champion quest having
    # moved off stage 0 is what "already done" looks like.
    body += ctda(FUNC_GET_STAGE, q_champion, comparison=0.0)
    body += ctda(FUNC_QUEST_RUNNING, CW_SIEGE_OBJ, comparison=1.0)
    body += sub(b"DNAM", struct.pack("<I", 0x00020000))
    body += sub(b"XNAM", struct.pack("<I", 0))
    body += sub(b"QNAM", struct.pack("<I", 1))
    body += sub(b"NNAM", struct.pack("<I", q_trigger))
    node = record(b"SMQN", smqn, body)

    # ---------------------------------------------------------------- form list
    body = z_sub(b"EDID", "ACWFBE_FinalSiegeLocations")
    body += sub(b"LNAM", struct.pack("<I", LOC_SOLITUDE))
    body += sub(b"LNAM", struct.pack("<I", LOC_WINDHELM))
    formlist = record(b"FLST", flst, body)

    # ---------------------------------------------------------------- dialogue
    body = z_sub(b"EDID", "ACWFBE_EquipmentBranch")
    body += sub(b"QNAM", struct.pack("<I", q_champion))
    body += sub(b"TNAM", struct.pack("<I", 0))
    body += sub(b"DNAM", struct.pack("<I", 1))
    body += sub(b"SNAM", struct.pack("<I", dial))
    branch = record(b"DLBR", dlbr, body)

    body = z_sub(b"EDID", "ACWFBE_EquipmentTopic")
    body += z_sub(b"FULL", "I'll take the armour, then.")
    body += sub(b"PNAM", struct.pack("<f", 50.0))
    body += sub(b"BNAM", struct.pack("<I", dlbr))
    body += sub(b"QNAM", struct.pack("<I", q_champion))
    body += sub(b"DATA", struct.pack("<I", 0))
    body += sub(b"SNAM", b"CUST")
    body += sub(b"TIFC", struct.pack("<I", 2))
    topic = record(b"DIAL", dial, body)

    infos = info(info_sons, 0, NPC_ULFRIC, q_champion, "Fragment_1",
                 "Let me lead the assault, and give me the harness for it.",
                 "Then wear this. Ice runs in the veins of the men who took Solitude before. "
                 "See that it runs in yours.")
    infos += info(info_imperial, info_sons, NPC_TULLIUS, q_champion, "Fragment_0",
                  "Let me lead the assault, General, and give me the harness for it.",
                  "Take it. There is dragon blood in that steel, and four hundred years of the Legion "
                  "behind it. Don't be the one who disgraces it.")

    groups = [
        (b"QUST", champion + trigger),
        (b"SMQN", node),
        (b"FLST", formlist),
        (b"DLBR", branch),
        (b"DIAL", topic + group(dial, infos, group_type=7)),
    ]
    return 8, groups


def z_sub(sig, text):
    return sub(sig, z(text))


def alias_unique(alias_id, name, npc):
    # 0x0002 Optional (only one side's commander is ever reachable in a playthrough) and
    # 0x0200 Allow Reserved (Ulfric and Tullius are both already in vanilla quest aliases).
    body = sub(b"ALST", struct.pack("<I", alias_id))
    body += z_sub(b"ALID", name)
    body += sub(b"FNAM", struct.pack("<I", 0x0202))
    body += sub(b"ALUA", struct.pack("<I", npc))
    body += sub(b"VTCK", struct.pack("<I", 0))
    body += sub(b"ALED", b"")
    return body


def info(form, previous, speaker, quest, fragment, player_line, response):
    body = sub(b"VMAD", vmad_scripts([("ACWFBE_TIF", [])]) +
               info_fragment("ACWFBE_TIF", "ACWFBE_TIF", fragment))
    body += sub(b"ENAM", struct.pack("<HH", 0, 0))
    body += sub(b"PNAM", struct.pack("<I", previous))
    body += sub(b"CNAM", b"\x00")
    body += ctda(FUNC_GET_IS_ID, speaker, comparison=1.0)
    body += ctda(FUNC_GET_STAGE, quest, comparison=float(STAGE_OFFERED))
    body += sub(b"TRDT", trdt())
    body += z_sub(b"NAM1", response)
    body += sub(b"NAM2", b"\x00")
    body += sub(b"NAM3", b"\x00")
    body += z_sub(b"RNAM", player_line)
    return record(b"INFO", form, body)
