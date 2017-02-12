
#csc.exe /target:winexe /lib:.\ /reference:itextsharp.dll test.cs
csc.exe /lib:.\ /reference:itextsharp.dll pdf1.cs
#csc.exe /lib:.\ /reference:itextsharp.dll /res:itextsharp.dll test.cs
csc.exe /lib:.\ /reference:itextsharp.dll /win32icon:filename pdf1.cs

