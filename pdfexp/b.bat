
rmdir /s /q dist
convert icon.png -define icon:auto-resize pdfexp.ico
python setup.py py2exe
xcopy pypop3\dist dist\pypop3\dist\ /s /y
xcopy data dist\data\ /s /y

