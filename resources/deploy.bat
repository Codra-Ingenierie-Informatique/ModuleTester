set INKSCAPE_PATH="C:\Program Files\Inkscape\bin\inkscape.exe"

@REM Deploying images and icons
copy PyTestBench.svg ..\pytestbench\data\logo
%INKSCAPE_PATH% "PyTestBench-Title.svg" -o "PyTestBench-Title.png" -w 190
copy PyTestBench-Title.png ..\doc\_static
%INKSCAPE_PATH% "PyTestBench-Banner.svg" -o "PyTestBench-Banner.png" -w 364
copy PyTestBench-Banner.png ..\doc\_static

@REM Generating icon
for %%s in (16 24 32 48 128 256) do (
  %INKSCAPE_PATH% "PyTestBench.svg" -o "tmp-%%s.png" -w %%s -h %%s
)
magick convert "tmp-*.png" "PyTestBench.ico"
del "tmp-*.png"

@REM Generating images for NSIS installer
%INKSCAPE_PATH% "win.svg" -o "temp.png" -w 164 -h 314
magick convert "temp.png" "win.bmp"
%INKSCAPE_PATH% "banner.svg" -o "temp.png" -w 300 -h 114
magick convert "temp.png" "banner.bmp"
del "temp.png"
move /y *.bmp ..\nsis\images

@REM Generating icons for NSIS installer
for %%s in (16 24 32 48 128 256) do (
  %INKSCAPE_PATH% "install.svg" -o "install-%%s.png" -w %%s -h %%s
  %INKSCAPE_PATH% "uninstall.svg" -o "uninstall-%%s.png" -w %%s -h %%s
)
magick convert "install-*.png" "install.ico"
magick convert "uninstall-*.png" "uninstall.ico"
del "install-*.png"
del "uninstall-*.png"
move /y *install.ico ..\nsis\icons
