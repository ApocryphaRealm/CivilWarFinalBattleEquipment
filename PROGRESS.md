# Civil War Champion - state

**1.0.0, built 2026-09-16. Installed in Njordlinger as `test Civil War Champion 1.0.0`. NOT yet
run in game.**

## What it is

A standalone quest-and-armour mod assembled from three mods the owner already has installed and
cannot use. See `NOTICE.md` for whose work each part is - that file also holds the one thing that
must be decided before this is ever published.

## The finding that shaped it

All three Civil War Champions mods at the top of Njordlinger - My Version (78892), Redone (94352)
and Reduced Cut (94999) - are DISABLED and inert. Every one declares `ccffbsse001-imperialdragon.esl`
as a master and that Creation Club creation is not installed: `Stock Game\Data` holds Skyrim.esm,
Update.esm and the vanilla archives, and the CC mod folder carries only the four free creations
(fish, Saints & Seducers, Rare Curios, Survival Mode). So there was nothing to patch, and this is a
rebuild that declares two masters and nothing else.

## How it is built

`tools/build-esp.py` reads the three mods and Thaumaturgy out of the Njordlinger instance and writes
the plugin; `tools/extract-assets.py` copies only the meshes and textures the built plugin names;
`tools/verify-esp.py` reads the result back and fails on a dangling reference, a duplicate FormID or
a forge recipe. Nothing of anyone else's is stored in this repository - see `.gitignore`.

    82 records   9 MGEF, 2 KYWD, 12 ENCH, 18 ARMA, 12 ARMO, 3 STAT, 3 WEAP, 2 LVLI,
                 13 COBJ, 2 QUST, 1 SMQN, 1 FLST, 1 DLBR, 1 DIAL, 2 INFO
    76 meshes, 44 textures, 96 MB
    3 Papyrus scripts, compiled against the vanilla sources

## Open items

* **NOT SEEN IN GAME.** Everything so far is static: the plugin parses, every reference resolves,
  the assets are all present and the seven textures left behind were confirmed vanilla with BSArch.
  What that cannot prove is whether the quest actually fires, whether Ulfric offers the line, and
  whether the armour renders.
* **The publishing question in `NOTICE.md` section 1.** Unresolved, and it is the blocking one.
* **One Imperial set entry could not be rebuilt** - Creation Club form `02000D62`, which none of the
  three mods override, so nothing on this machine knows what it is. The Imperial set ships seven
  pieces instead of eight; the Stormcloak set is complete.
* **The dialogue is unvoiced.** Ulfric and General Tullius both have unique voice types, so the
  trick Reduced Cut used - borrowing a vanilla shared response - cannot supply audio for them. The
  line shows as a subtitle. Shipping a silent voice file would hold it on screen properly.
* **Rule 66, the eleven languages.** The quest and dialogue strings are inline in the plugin, so
  translating means either translated plugins or a Dynamic String Distributor file. Not started.
