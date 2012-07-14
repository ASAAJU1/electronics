"""
Clock modules will provide the following functions:
displayClockTime
displayClockDate
checkClockYear
writeClockTime(Year,Month,Day,DOW,Hour,Minute,Second)
writeClockAlarm(Hour,Minute,Second)
getClockDT	Returns 12 character string
getDOW(DOW)	Returns  3 chcaracter string
getHour		Returns int
getMinute	Returns int
getSecond	Returns int
Clock modules will provide the global variable timeSynched
This variable is used to help prevent a node from going to sleep when it will not wake at the right time.

"""