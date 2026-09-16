# Whose work this is, and what that means for publishing it

**Read this before the mod goes anywhere except the owner's own load order.**

Almost nothing in Civil War Champion was written here. It is an assembly, and it has four upstreams
plus one piece of lineage that matters more than any of them. This file states each one honestly so
the publishing decision is made with the facts on the table rather than after the fact.

---

## 1. The Creation Club, and why this is the hard one

Every armour record in this mod descends from **Civil War Champions**, a paid Creation Club creation
(`ccffbsse001-imperialdragon.esl`) by FrankFamily, published by Bethesda. What descends from it is:

* the two sets' **names** - Imperial Dragon and Storm-Bear, and each piece's name;
* the **statistics** - armour rating, value, weight, and which keywords each piece carries;
* the **enchantment layout** - which effect sits on which piece, and at what magnitude;
* the two **levelled lists** that define "the whole set".

**That creation is not installed on this machine and was not read.** It could not be: the Njordlinger
instance carries only the four free creations, and `Stock Game\Data` has no `ccff` file at all. Every
one of the facts above was recovered from the three community mods that override the creation, which
is precisely why those three mods are all disabled and inert in the list - each declares the creation
as a master and none of them can load.

The meshes and textures are **not** Bethesda's. The creation's own art was never on this machine
either; what ships here is NordwarUA's, because Civil War Champions - My Version replaced the
creation's models with his and that replacement is what was taken.

**What this means - stated carefully, because the first draft of this paragraph got it wrong.**

Nexus hosts Creation Club-dependent mods without difficulty. The three mods this was built from are
all on Nexus and all three master the creation; patches, rebalances and replacers for paid creations
are ordinary there. What Nexus prohibits is redistributing Bethesda's paid FILES, and those three
stay clear of it: Redone and Reduced Cut ship a plugin and nothing else, My Version ships its own
replacement meshes, and not one of them does anything unless the creation is already installed. They
need you to own it.

This mod does not. It ships no Bethesda file - the meshes are NordwarUA's, the plugin is generated,
there is no Creation Club master - but it reconstructs a paid creation's two armour sets, with their
names, their statistics and their enchantment layout, for somebody who never bought it. **That is a
paywall question, not an asset-redistribution one**, and it is the thing to weigh before publishing.

How Nexus moderation actually treats a standalone recreation of that kind was NOT established.
Their permissions and content-policy pages return HTTP 403 to anything that is not a browser, so
nobody here has read them; the paragraph above reasons from what the three neighbouring mods do, not
from the rules themselves. **Somebody should read the policy before this is published.**

For the owner's own load order none of this arises - it is a rebuild of content he already owns the
mods for and cannot otherwise load. If it is to be published, the clean route is to rename and
re-stat the sets so what ships is NordwarUA's armour under our own names and numbers, with no
Creation Club lineage at all.

---

## 2. Civil War Champions - My Version — [Nexus 78892](https://www.nexusmods.com/skyrimspecialedition/mods/78892)

Source of the armour: 12 ARMO, 18 ARMA, 3 WEAP, 3 STAT, 2 LVLI, the tempering recipes, and **all 76
meshes and 44 textures** in this package.

Those assets are **NordwarUA's**, from his Sons of Skyrim and Legion armour work; that mod is a
redistribution of them, not original art. The owner's standing position on NordwarUA, given on
2026-09-16 while the Jarl Ulfric Armor Replacer was being built, is *"because this is Nordwar UA, all
assets are free use"*.

**Mod 78892's own permissions block has not been read.** Nexus returns HTTP 403 to anything that is
not a browser, so it could not be checked from here. Somebody should open that page before this is
published, and record here what it says.

## 3. Civil War Champions Redone — [Nexus 94352](https://www.nexusmods.com/skyrimspecialedition/mods/94352)

Source of the enchantments: 12 ENCH records and 2 keywords, and the per-piece armour statistics that
the ARMO records are built on. Its author rebalanced the creation's enchantments around Thaumaturgy
and gave each one its own name, which is the thing the owner singled out as worth keeping:
*"i like how the enchantments have unique names in the magic affects menu"*.

**Permissions not read** - same 403.

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

**Permissions not read.**

---

## What IS ours

`tools/` - the plugin generator, the asset extractor and the verifier - and `scripts/source/` - the
three Papyrus scripts. Those are GPL-3.0-or-later, and they carry none of anyone else's data: they
read the installed mods at build time, so this repository redistributes nothing.
