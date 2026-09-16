Scriptname ACWFBE_EquipmentQF extends Quest Hidden
{Stage fragments for the Civil War Final Battle Equipment quest.

 Stage 10 puts the objective in the journal. Stages 100 and 110 hand over the set - one per side -
 and the stage itself is flagged "complete quest" in the record, so nothing here has to stop the
 quest by hand.}

Actor Property PlayerRef Auto
LeveledItem Property ImperialSet Auto
LeveledItem Property StormcloakSet Auto

Function Fragment_0()
	SetObjectiveDisplayed(10)
EndFunction

Function Fragment_1()
	PlayerRef.AddItem(ImperialSet, 1, true)
	SetObjectiveCompleted(10)
EndFunction

Function Fragment_2()
	PlayerRef.AddItem(StormcloakSet, 1, true)
	SetObjectiveCompleted(10)
EndFunction
