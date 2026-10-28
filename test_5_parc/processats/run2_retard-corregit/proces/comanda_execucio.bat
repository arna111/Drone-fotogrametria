@echo off
rem Aquest entorn te NoDefaultCurrentDirectoryInExePath=1, i run.bat/winrun.bat cerquen els .bat germans al directori actual.
set NoDefaultCurrentDirectoryInExePath=
set ODM_NONINTERACTIVE=1
set P=E:\User\Documents\Drone_fotogrametria\test_5_parc\processats
call "E:\WebODM\resources\app\apps\ODX\run.bat" --project-path "%P%" run2_retard-corregit --auto-boundary --cog --dem-resolution 2 --dsm --geo "%P%\run2_retard-corregit\gcp\geo.txt" --gltf --max-concurrency 8 --orthophoto-resolution 1 --pc-ept --pc-quality high > "%P%\run2_retard-corregit\task_output.txt" 2>&1
echo FI codi=%ERRORLEVEL% >> "%P%\run2_retard-corregit\task_output.txt"
