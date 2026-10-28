@echo off
rem Aquest entorn te NoDefaultCurrentDirectoryInExePath=1, i run.bat/winrun.bat cerquen els .bat germans al directori actual.
set NoDefaultCurrentDirectoryInExePath=
set ODM_NONINTERACTIVE=1
set P=E:\User\Documents\Drone_fotogrametria\test_6_camp\processats
call "E:\WebODM\resources\app\apps\ODX\run.bat" --project-path "%P%" run1_vol2_realcades --auto-boundary --cog --dem-resolution 5 --dsm --geo "%P%\run1_vol2_realcades\gcp\geo.txt" --gltf --max-concurrency 8 --orthophoto-resolution 3 --pc-ept --pc-quality high > "%P%\run1_vol2_realcades\task_output.txt" 2>&1
echo FI codi=%ERRORLEVEL% >> "%P%\run1_vol2_realcades\task_output.txt"
