# Civil War Final Battle Equipment - changelog

## 1.0.3 - 2026-10-26 - untested

### Fixed
- Rebuilt the compiled scripts so their headers no longer carry the build machine's account and computer name (the Papyrus compiler writes both into every .pex). The script code is byte-for-byte the same as 1.0.2's; no gameplay change.

## 1.0.2 - 2026-09-16 - untested

### Changed
- **Dragon Blood is re-arted from General Tullius's own armour in Heavy Legion SSE** (Nexus 22877; the owner, 2026-09-16: *"were only taking tullius armor from heavy legion and using it for dragon blood armor, nothing else from heavy legion"*). The cuirass, gauntlets, boots and helmet now wear the muscled cuirass, studded skirt and horned helm the general himself wears - 31 meshes and 12 textures, written under Dragon Blood's existing file names by `tools/reart-dragonblood.py`, so not one record in the plugin changed and no save is disturbed. The shield, sword and cloak keep their art; Tullius's set has none.
- **The plugin is an ESPFE** - `Civil War Final Battle Equipment.esp` carrying the light flag - so it sorts among ordinary plugins.

## 1.0.1

* Adds the four Dragon Blood meshes NordwarUA ships that this package was missing:
  `DragonShieldOnBack`, `DragonShieldOnBackClk`, `DragonSwordLeft` and `DragonSwordSheath`.
  They are the shield as it hangs on the back and the sword sheathed or held in the off hand.
* Nothing references them by record - not this mod's plugin, and not NordwarUA's own. Simple Dual
  Sheath, Immersive Equipment Displays and the like find them by file name, which is why shipping
  the files is the whole change. No plugin edit, no version-dependent behaviour.
* Without them, a player running those mods saw the generic shield and scabbard against the Dragon
  Blood set.
* **The plugin is renamed from `.esl` to `.esp`.** It keeps the light flag, so it still costs no
  full load-order slot, but the game forces every `.esl` FILE to load in the master block at the
  very top of the order where nothing can sort below it. As a `.esp` carrying the light flag - an
  ESPFE - it sorts among the ordinary plugins and can be placed relative to them.
* **That rename breaks saves made with 1.0.0.** A save records a plugin by file name, so anything
  from this mod that a 1.0.0 character was carrying or had progressed will be gone. Start the quest
  fresh, or stay on 1.0.0.
* No mesh, texture or record changed otherwise.

## 1.0.0 - 2026-09-16

First build. Two sets of Civil War war gear, issued before the final battle.

- **The sets.** Ice Veins for the Stormcloaks and Dragon Blood for the Legion: six pieces each,
  plus three weapons. NordwarUA's meshes and textures throughout - 76 meshes, 44 textures, 18
  armatures, three first-person weapon models.
- **Effects as abilities, not enchantments.** The armour carries no object enchantment at all -
  its item card shows only what the piece is and who it is given to. Each piece is paired with an
  ability, applied on equip and removed on unequip by a player-alias script, so what it does shows
  under Magic, named for the piece. The vanilla precedent is the Thieves Guild and Dark Brotherhood
  set bonuses, which work the same way. The three weapons keep real enchantments, because a weapon
  enchantment has to be on the weapon to fire on hit.
- **Nine magic effects of its own**, including six the base game has no equivalent for - Fortify
  Power Attacks, Fortify Bash Damage, Resist Arrow Damage, Resist Spell Damage, Fortify Shout Power
  and Shout Duration. Defined inside the plugin, so the mod requires nothing.
- **The quest.** Opens when the final assault is ordered. Ulfric Stormcloak or General Tullius
  hands the set over in his own hall, before the march - not at the battle.
- **Tempering only.** Thirteen recipes, ten at the armour workbench and three at the grindstone.
  The sets cannot be forged, by design.
