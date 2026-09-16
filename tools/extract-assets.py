#!/usr/bin/env python3
r"""Copy the meshes and textures the built plugin actually names, and nothing else.

WHY IT READS THE PLUGIN RATHER THAN A LIST
    Civil War Champions - My Version ships 192 meshes and 182 textures, because it replaces the
    whole Legion and Stormcloak wardrobe. This mod is two champion sets. A hand-written list of
    what to take would drift the moment the record list changes, so the list IS the record list:
    every model path in the built ESP is collected, each mesh is opened and asked which textures it
    names, and only those files travel.

    Both weight variants travel for every mesh. Skyrim derives the "_0" file from the "_1" the
    record names, so taking only what the plugin spells out would ship half a wardrobe.

EXTRACTING NOTHING MUST BE LOUD
    A missing source file raises rather than warns. A silent miss here produces a mod that installs,
    loads, and renders a purple or invisible cuirass - and the only way to find out is in game.
"""
import os
import re
import shutil
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tes4 import read_plugin

SOURCE = r"D:\modlists\Njordlinger\mods\Civil War Champions - My Version"

MODEL_SUBS = (b"MOD2", b"MOD3", b"MOD4", b"MOD5", b"MODL")
# MODL is a list of armature FormIDs inside ARMO and ARMA; it is a mesh path everywhere else.
MODL_IS_A_PATH = {b"STAT", b"WEAP", b"MGEF"}

DDS = re.compile(rb"[0-9A-Za-z_\\./ -]{4,200}\.dds", re.IGNORECASE)


def model_paths(recs):
    out = set()
    for r in recs[1:]:
        for sig, d in r.subs:
            if sig not in MODEL_SUBS:
                continue
            if sig == b"MODL" and r.type not in MODL_IS_A_PATH:
                continue
            if b"\x00" not in d:
                continue
            p = d.split(b"\x00")[0].decode("cp1252")
            if p.lower().endswith(".nif"):
                out.add(p.replace("/", "\\"))
    return sorted(out)


def weight_variants(path):
    """The record names one file; Skyrim needs the pair."""
    stem, ext = os.path.splitext(path)
    if stem.endswith("_1"):
        return [path, stem[:-2] + "_0" + ext]
    if stem.endswith("_0"):
        return [path, stem[:-2] + "_1" + ext]
    return [path]


def textures_in(nif_path):
    data = open(nif_path, "rb").read()
    out = set()
    for m in DDS.finditer(data):
        t = m.group(0).decode("cp1252").replace("/", "\\").lstrip("\\")
        if t.lower().startswith("textures\\"):
            t = t[len("textures\\"):]
        out.add(t)
    return out


def copy(src_root, rel, dest_root, missing):
    src = os.path.join(src_root, rel)
    if not os.path.isfile(src):
        missing.append(rel)
        return False
    dst = os.path.join(dest_root, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return True


def main(esp, dest):
    recs, _ = read_plugin(esp)

    for sub in ("Meshes", "Textures"):
        p = os.path.join(dest, sub)
        if os.path.isdir(p):
            shutil.rmtree(p)

    wanted, missing = [], []
    for p in model_paths(recs):
        wanted.extend(weight_variants(p))
    wanted = sorted(set(wanted))

    meshes = 0
    for rel in wanted:
        if copy(SOURCE, os.path.join("Meshes", rel), dest, missing):
            meshes += 1

    textures, vanilla = set(), set()
    for rel in wanted:
        nif = os.path.join(dest, "Meshes", rel)
        if os.path.isfile(nif):
            textures |= textures_in(nif)

    copied_tex = 0
    for t in sorted(textures):
        if copy(SOURCE, os.path.join("Textures", t), dest, missing):
            copied_tex += 1
        else:
            # Anything the source does not have is a base-game texture the mesh is reusing, which
            # is right and proper - it must NOT be shipped. missing[] caught it; move it across.
            vanilla.add(missing.pop())

    print("models named by the plugin ... %d" % len(model_paths(recs)))
    print("meshes copied (both weights) . %d" % meshes)
    print("textures copied .............. %d" % copied_tex)
    if vanilla:
        print("textures left to the base game %d" % len(vanilla))
        for t in sorted(vanilla):
            print("      %s" % t[len("Textures\\"):])
    if missing:
        raise SystemExit("MISSING %d mesh(es) in %s:\n  %s"
                         % (len(missing), SOURCE, "\n  ".join(missing)))


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    main(os.path.normpath(os.path.join(here, "..", "dist", "Civil War Champion.esp")),
         os.path.normpath(os.path.join(here, "..", "dist")))
