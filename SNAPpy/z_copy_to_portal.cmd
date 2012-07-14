copy .\Portal\*.py "%homepath%\Documents\Portal\"
copy .\*.py "%homepath%\Documents\Portal\snappyImages\"
xcopy .\contrib %USERPROFILE%\Documents\Portal\snappyImages\contrib  /E /I /Y
pause
