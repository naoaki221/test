
rmdir /s /q dist
rem convert icon.png -define icon:auto-resize pdfexp.ico
python setup.py py2exe
rem xcopy pypop3\dist dist\pypop3\dist\ /s /y
rem xcopy data dist\data\ /s /y

