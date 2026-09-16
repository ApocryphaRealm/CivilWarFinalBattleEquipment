Scriptname ACWFBE_SetEffects extends ReferenceAlias
{Puts each piece's effect on the wearer, and takes it off again.

 WHY THE EFFECTS ARE NOT ENCHANTMENTS

 An object enchantment shows itself on the inventory item card, and there is no flag that stops it:
 the magic effect flag "Hide in UI" hides an effect from the ACTIVE EFFECTS list instead, which is
 the one place these are meant to be read. The base game settles the question - it ships pairs like
 AbDamageHealRate and AbDamageHealRateVisible, the second existing purely so the player CAN see it
 under Magic.

 So the armour carries no enchantment at all. Each piece is paired with an ability, applied here on
 equip and removed on unequip. The item card shows only what the piece is and who it is given to;
 what it does is under Magic, named for the piece it came from.

 Pieces and Abilities are parallel lists - index N in one matches index N in the other.}

FormList Property Pieces Auto
FormList Property Abilities Auto
Actor Property PlayerRef Auto

Event OnObjectEquipped(Form akBaseObject, ObjectReference akReference)
	Spell ability = AbilityFor(akBaseObject)
	If ability
		PlayerRef.AddSpell(ability, false)
	EndIf
EndEvent

Event OnObjectUnequipped(Form akBaseObject, ObjectReference akReference)
	Spell ability = AbilityFor(akBaseObject)
	If ability
		PlayerRef.RemoveSpell(ability)
	EndIf
EndEvent

Event OnPlayerLoadGame()
	; A save made while the set was worn comes back with the abilities already on the player, but a
	; save made before this mod was installed does not - and neither does one where something else
	; stripped them. Re-syncing on load costs nothing and means the set is never silently inert.
	Int i = 0
	While i < Pieces.GetSize()
		Form piece = Pieces.GetAt(i)
		Spell ability = Abilities.GetAt(i) as Spell
		If ability
			If PlayerRef.IsEquipped(piece)
				PlayerRef.AddSpell(ability, false)
			Else
				PlayerRef.RemoveSpell(ability)
			EndIf
		EndIf
		i += 1
	EndWhile
EndEvent

Spell Function AbilityFor(Form akBaseObject)
	Int i = Pieces.Find(akBaseObject)
	If i < 0
		Return None
	EndIf
	Return Abilities.GetAt(i) as Spell
EndFunction
