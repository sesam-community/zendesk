@echo off
set ZEN_USER=mofsesam
for /f "delims=" %%A in ('keyring get Test_zen %ZEN_USER%') do set "ZEN_PW=%%A"