# Whose work this is, and what that means for publishing it

**Read this before the mod goes anywhere except the owner's own load order.**

Almost nothing in Civil War Champion was written here. It is an assembly, and it has four upstreams
plus one piece of lineage that matters more than any of them. This file states each one honestly so
the publishing decision is made with the facts on the table rather than after the fact.

---

## 1. Lineage, and the decision the owner took about it

The two sets in this mod began as a reconstruction. The armour statistics and the enchantment
layout - which effect sits on which piece, at what magnitude - were recovered from three community
mods that override a paid Creation Club creation, because that creation is not installed here and
could not be read. No Bethesda file of any kind is in this package, and the plugin declares no
Creation Club master.

**The owner's decision, 2026-09-16:**

> *"i want you to frame this mod as a seperate mod from the cc mod as it is unique from the
> bethesda file in form and function ... furthermore we shouldnt even compare the two files in the
> discription as they are distinct obviously"*

He is right on the substance, and the rename he asked for in the same breath closed the last thread:

* **Form.** Every mesh and texture is NordwarUA's. None of the creation's art was ever on this
  machine and none of it is here.
* **Function.** The gear is issued by Ulfric Stormcloak or General Tullius, in his own hall, when
  the final assault is ordered. There is no duel, no champions' fight, and no Creation Club quest.
  The quest, the Story Manager node, the dialogue and all three Papyrus scripts were written here.
* **Names.** The sets are **Ice Veins** and **Dragon Blood** - his names, chosen 2026-09-16. Every
  displayed name and every editor ID in the plugin was rewritten to match; not one record still
  carries a name from anywhere else.

What remains shared with the creation is a set of numbers: armour ratings, values, weights, and the
magnitudes on each enchantment. Numbers balanced against vanilla Skyrim are not meaningfully
ownable, and they are the part a player would never see as anything but "this is balanced like
heavy armour should be".

**For publishing**, the page describes the mod on its own terms and makes no comparison to anything
- that is the owner's instruction and it is also simply accurate. Credit to the three authors whose
work fed into it stays in the Credit section, where it belongs, and in the sections below.

---

## 2. Civil War Champions - My Version (page now titled "The Armor They Deserved"), by NordWarUA and DraugrOfRagnarok — [Nexus 78892](https://www.nexusmods.com/skyrimspecialedition/mods/78892)

Source of the armour: 12 ARMO, 18 ARMA, 3 WEAP, 3 STAT, 2 LVLI, the tempering recipes, and **all 76
meshes and 44 textures** in this package.

Those assets are **NordwarUA's**, from his Sons of Skyrim and Legion armour work; that mod is a
redistribution of them, not original art. The owner's standing position on NordwarUA, given on
2026-09-16 while the Jarl Ulfric Armor Replacer was being built, is *"because this is Nordwar UA, all
assets are free use"*.

**Permissions, settled 2026-09-16.** The owner ruled on what these mods' permissions require of us:
*"for any of the permissions on this mod and the last few equipment related mods just add links back to
the original mods and the credit section of each mod"*. The Credit section of the Nexus page names this
mod and links to its page. The permissions BLOCK itself still cannot be read from this machine - Nexus
returns 403 to anything that is not a browser - and by his decision that is no longer a gate on release.

## 3. Civil War Champions Redone — [Nexus 94352](https://www.nexusmods.com/skyrimspecialedition/mods/94352)

Source of the enchantments: 12 ENCH records and 2 keywords, and the per-piece armour statistics that
the ARMO records are built on. Its author rebalanced the creation's enchantments around Thaumaturgy
and gave each one its own name, which is the thing the owner singled out as worth keeping:
*"i like how the enchantments have unique names in the magic affects menu"*.

**Permissions, settled 2026-09-16.** The owner ruled on what these mods' permissions require of us:
*"for any of the permissions on this mod and the last few equipment related mods just add links back to
the original mods and the credit section of each mod"*. The Credit section of the Nexus page names this
mod and links to its page. The permissions BLOCK itself still cannot be read from this machine - Nexus
returns 403 to anything that is not a browser - and by his decision that is no longer a gate on release.

## 4. Civil War Champions - Reduced Cut — [Nexus 94999](https://www.nexusmods.com/skyrimspecialedition/mods/94999), by Kamikaze

Source of the **idea**, and of nothing else. His readme ships with the mod and grants permission in
writing:

> You may distribute and modify this mod as you see fit as long as you abide by the following:
> 1) You credit me (Kamikaze) as the original author.
> 2) You provide a link back to the original download page on Nexus.
> 3) You do not attempt to profit off of my mod -- unless you give me a fair cut. ;)

His design is the one this mod follows: throw out the creation's "Battle of Champions" duel, and hand
the champion's armour over just before the final siege instead. His own words: *"It doesn't make sense
for armies to fight duels let alone do it with highly enchanted one-of-a-kind armor."*

**No record and no script of his is shipped.** The quest, the Story Manager node, the form list, the
dialogue and all three Papyrus scripts were written here, because the owner moved the handover to
Ulfric Stormcloak and General Tullius themselves where Kamikaze used the field commanders. Credit and
the link above are owed regardless, and are on the mod page.

## 5. Thaumaturgy - An Enchanting Overhaul

Nine magic effects are **cloned** from it - Fortify Power Attacks, Fortify Bash Damage, Fortify Shout
Power and Duration, Fortify Movement Speed, Resist Arrow Damage, Resist Spell Damage, Weakness to Fire
and Damage Armor - at its own values, with its own names and descriptions.

They are cloned rather than referenced because the owner ruled out the dependency:
*"thaumaturgy isnt neccacery but should align with thaumaturgy values as the mod does already"*.
Seven of the nine are plain Peak Value Modifier effects on stock actor values with no perk, art or
script behind them, so the clone is exact. The two weapon debuffs are cloned with Thaumaturgy's own
art, shader and projectile references dropped, since those cannot travel.

**Permissions, settled 2026-09-16.** The owner ruled on what these mods' permissions require of us:
*"for any of the permissions on this mod and the last few equipment related mods just add links back to
the original mods and the credit section of each mod"*. The Credit section of the Nexus page names this
mod and links to its page. The permissions BLOCK itself still cannot be read from this machine - Nexus
returns 403 to anything that is not a browser - and by his decision that is no longer a gate on release.

---

## What IS ours

`tools/` - the plugin generator, the asset extractor and the verifier - and `scripts/source/` - the
three Papyrus scripts. Those are GPL-3.0-or-later, and they carry none of anyone else's data: they
read the installed mods at build time, so this repository redistributes nothing.
