Scriptname ACWC_TriggerScript extends Quest
{Notices that the final siege has been ordered, and nothing else.

 This quest is driven by the Story Manager's Change Location event, so it wakes up whenever the
 player moves between locations. It asks one question - is the city the Civil War siege quest is
 currently pointed at one of the two capitals? - and if it is, it opens the champion quest and
 stands down. Every other change of location it sleeps through.

 The check is on CWSiegeObj's OWN city alias rather than on where the player is standing, because
 the moment that matters is when the final assault is ORDERED, which happens in the Palace of the
 Kings or in Castle Dour, not at the gates of the city being attacked.}

LocationAlias Property SiegeCity Auto
{Filled from CWSiegeObj's City alias - the hold currently under siege.}

FormList Property FinalSiegeLocations Auto
{Solitude and Windhelm. Reaching either one means this is the last battle.}

Quest Property ChampionQuest Auto

Event OnStoryChangeLocation(ObjectReference akActor, Location akOldLocation, Location akNewLocation)
	If FinalSiegeLocations.HasForm(SiegeCity.GetLocation())
		If !ChampionQuest.IsRunning()
			ChampionQuest.Start()
		EndIf
		ChampionQuest.SetStage(10)
		Stop()
	EndIf
EndEvent
