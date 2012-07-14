copy "%USERPROFILE%\My Documents\Portal\snappyImages\SNARF*.py" .\
copy "%USERPROFILE%\My Documents\Portal\snappyImages\*_m.py" .\
copy "%USERPROFILE%\My Documents\Portal\snappyImages\SB*.py" .\
copy "%USERPROFILE%\My Documents\Portal\snappyImages\rf_*.py" .\
copy "%USERPROFILE%\My Documents\Portal\JC-*.py" .\Portal\
copy "%USERPROFILE%\My Documents\Portal\p*m.py" .\Portal\

xcopy "%USERPROFILE%\Documents\Portal\snappyImages\contrib" .\contrib\ /E /I /Y

@rem copy %homepath%\Documents\Portal\snappyImages\SNARF*.py .\
@rem copy %homepath%\Documents\Portal\snappyImages\SNARF*.py .\
@rem copy %homepath%\Documents\Portal\snappyImages\SNARF*.py .\

pause
