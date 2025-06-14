cd %1
if %2 == "python" (
  cls
  python %3
)
if %2 == "cpp" (
  cls
  %5 %3 -o %4 -finput-charset=UTF-8 -fexec-charset=GBK
  %4
)
pause
exit