Scriptname ACWC_TIF extends TopicInfo Hidden
{The two "I'll take the champion's armour" lines. Each one only moves the stage; the quest's own
 fragments do the giving, so the reward lives in one place.}

Function Fragment_0(ObjectReference akSpeakerRef)
	GetOwningQuest().SetStage(100)
EndFunction

Function Fragment_1(ObjectReference akSpeakerRef)
	GetOwningQuest().SetStage(110)
EndFunction
