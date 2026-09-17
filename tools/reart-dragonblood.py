#!/usr/bin/env python3
r"""Re-art the Dragon Blood set from General Tullius's armour in Heavy Legion SSE (Nexus 22877).

WHY
    The owner, 2026-09-16: *"were only taking tullius armor from heavy legion and using it for
    dragon blood armor, nothing else from heavy legion"*.

    Dragon Blood previously used NordwarUA's Imperial Officer armour in black - the flat plate
    cuirass with gold dragon filigree. Tullius's own armour is a different design: a muscled
    cuirass, a horned helm, a studded skirt. It is the armour he wears in game, which is the point:
    the general hands you the harness he was wearing.

WHAT IT REPLACES, AND WHAT IT LEAVES ALONE
    Only the four armour pieces, because only those exist in Tullius's set:
      cuirass, bracers (Dragon Blood's gauntlets), boots, helmet.
    The SHIELD, SWORD and CLOAK keep the art they already have. Tullius's set has none of them, and
    the instruction was nothing else from that mod.

HOW IT AVOIDS TOUCHING THE PLUGIN
    The meshes are written under Dragon Blood's EXISTING file names, so every record in
    "Civil War Final Battle Equipment.esp" still points where it always did. Not one record changes,
    which means no FormIDs move and no save is disturbed by this - unlike the rename that broke
    saves earlier today.

GAPS IN THE SOURCE, AND WHAT IS DONE ABOUT THEM
    * no female first-person cuirass -> the male one is used for both, as the source mod itself does;
    * no female boots -> likewise;
    * no separate first-person bracers -> the worn bracers include the hands, so they serve;
    * HelmetA/K/O cover Argonian, Khajiit and Orc but are not split by sex, so each is used for the
      male and female variant of that race.
    Every one of these is a real gap in Tullius's set rather than an oversight here, and the script
    says so rather than silently leaving a hole.

Usage:  python tools/reart-dragonblood.py [--dry-run]
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, ".."))
DOWNLOADS = os.environ.get("CWFBE_DOWNLOADS", r"D:\modlists\Njordlinger\downloads")
ARCHIVE = "Heavy Legion-22877"
SEVENZIP = [r"C:\Program Files\7-Zip\7z.exe", r"C:\Program Files (x86)\7-Zip\7z.exe", "7z"]

SRC_MESH = r"Meshes\1_Soldier_Replacer\Legion\Tulius"
SRC_TEX = r"Textures\1_Soldier_Replacer\Tulius"
DST_MESH = os.path.join("Meshes", "Armor_Replacer", "2_Legion")
DST_TEX = os.path.join("Textures", "1_Soldier_Replacer", "Tulius")

# Tullius mesh -> the Dragon Blood file name it becomes. Anything not listed here keeps its art.
MAP = {
    "Cuirass_0.nif": ["DragonArmorM_0.nif"],
    "Cuirass_1.nif": ["DragonArmorM_1.nif"],
    "CuirassF_0.nif": ["DragonArmorF_0.nif"],
    "CuirassF_1.nif": ["DragonArmorF_1.nif"],
    "Cuirass_Gnd.nif": ["DragonArmor_Gnd.nif"],
    "1stpersoncuirass_0.nif": ["1stpersonDragonArmorM_0.nif", "1stpersonDragonArmorF_0.nif"],
    "1stpersoncuirass_1.nif": ["1stpersonDragonArmorM_1.nif", "1stpersonDragonArmorF_1.nif"],
    "Bracers_0.nif": ["DragonGauntletsM_0.nif", "1stPersonDragonGauntletsM_0.nif"],
    "Bracers_1.nif": ["DragonGauntletsM_1.nif", "1stPersonDragonGauntletsM_1.nif"],
    "BracersF_0.nif": ["DragonGauntletsF_0.nif", "1stPersonDragonGauntletsF_0.nif"],
    "BracersF_1.nif": ["DragonGauntletsF_1.nif", "1stPersonDragonGauntletsF_1.nif"],
    "Bracers_Gnd.nif": ["DragonGauntlets_Gnd.nif"],
    "Boots_0.nif": ["DragonBootsM_0.nif", "DragonBootsF_0.nif"],
    "Boots_1.nif": ["DragonBootsM_1.nif", "DragonBootsF_1.nif"],
    "Boots_Gnd.nif": ["DragonBoots_Gnd.nif"],
    "HelmetM.nif": ["DragonHelmet_M.nif"],
    "HelmetF.nif": ["DragonHelmet_F.nif"],
    "HelmetA.nif": ["DragonHelmet_MA.nif", "DragonHelmet_FA.nif"],
    "HelmetK.nif": ["DragonHelmet_MK.nif", "DragonHelmet_FK.nif"],
    "HelmetO.nif": ["DragonHelmet_MO.nif"],
    "Helmet_Gnd.nif": ["DragonHelmet_Gnd.nif"],
}

KEEP = ("DragonShield", "DragonSword", "CloackOfficer")
TEXPAT = re.compile(rb"[Tt]extures.{1,180}?\.dds")
VANILLA_TEX = ("textures\\actors\\", "textures\\cubemaps\\")


def fail(msg):
    raise SystemExit("reart-dragonblood: " + msg)


def sevenzip():
    for c in SEVENZIP:
        if os.path.isfile(c):
            return c
        if shutil.which(c):
            return shutil.which(c)
    fail("7-Zip not found")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    archive = next((os.path.join(DOWNLOADS, f) for f in sorted(os.listdir(DOWNLOADS))
                    if ARCHIVE.lower() in f.lower() and f.lower().endswith(".7z")), None)
    if archive is None:
        fail("no '%s' archive in %s - download Heavy Legion SSE (Nexus 22877) first"
             % (ARCHIVE, DOWNLOADS))

    work = os.path.join(REPO, "_reart")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work, exist_ok=True)
    p = subprocess.run([sevenzip(), "x", "-y", "-o" + work, archive,
                        SRC_MESH + "\\*", SRC_TEX + "\\*", "-r"],
                       capture_output=True, text=True)
    if p.returncode != 0:
        fail("7-Zip failed:\n" + p.stdout + p.stderr)

    mesh_src = next((os.path.join(dp) for dp, dn, fn in os.walk(work)
                     if os.path.basename(dp).lower() == "tulius" and any(f.lower().endswith(".nif") for f in fn)), None)
    tex_src = next((os.path.join(dp) for dp, dn, fn in os.walk(work)
                    if os.path.basename(dp).lower() == "tulius" and any(f.lower().endswith(".dds") for f in fn)), None)
    if not mesh_src or not tex_src:
        fail("the archive did not yield both a Tulius mesh folder and a Tulius texture folder")

    dst_mesh = os.path.join(REPO, "dist", DST_MESH)
    dst_tex = os.path.join(REPO, "dist", DST_TEX)
    missing = [s for s in MAP if not os.path.isfile(os.path.join(mesh_src, s))]
    if missing:
        fail("Tullius's set is missing %d mesh(es) this mapping needs: %s" % (len(missing), missing))

    placed = 0
    for src, dests in sorted(MAP.items()):
        for d in dests:
            target = os.path.join(dst_mesh, d)
            if not os.path.isfile(target):
                fail("'%s' is not a Dragon Blood file - the mapping names a piece this mod does "
                     "not have, so a record would be left pointing at nothing" % d)
            if not a.dry_run:
                shutil.copy2(os.path.join(mesh_src, src), target)
            placed += 1

    # textures the new meshes actually ask for, minus what vanilla supplies
    wanted = set()
    for f in os.listdir(mesh_src):
        if f.lower().endswith(".nif"):
            for m in TEXPAT.findall(open(os.path.join(mesh_src, f), "rb").read()):
                v = m.decode("latin-1").replace("/", "\\").lower()
                if not v.startswith(VANILLA_TEX):
                    wanted.add(os.path.basename(v))
    if not a.dry_run:
        os.makedirs(dst_tex, exist_ok=True)
    copied = 0
    for f in sorted(os.listdir(tex_src)):
        if f.lower() in wanted:
            if not a.dry_run:
                shutil.copy2(os.path.join(tex_src, f), os.path.join(dst_tex, f))
            copied += 1
    unused = sorted(f for f in os.listdir(tex_src)
                    if f.lower().endswith(".dds") and f.lower() not in wanted)

    shutil.rmtree(work, ignore_errors=True)
    print("re-arted Dragon Blood from Heavy Legion SSE's Tullius set%s" % ("  (dry run)" if a.dry_run else ""))
    print("  source ................ %s" % os.path.basename(archive))
    print("  meshes replaced ....... %d, under Dragon Blood's own file names" % placed)
    print("  textures shipped ...... %d to %s" % (copied, DST_TEX))
    print("  left alone ............ %s" % ", ".join(KEEP))
    if unused:
        print("  not shipped (unused) .. %s" % ", ".join(unused))


if __name__ == "__main__":
    main()
