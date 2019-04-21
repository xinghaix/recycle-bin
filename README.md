# recycle-bin
This is a recycle-bin on the system tray of Windows10

# build & package

```
# install pyinstaller
pip install pyinstaller

# download upx
https://github.com/upx/upx/releases/download/v3.95/upx-3.95-win64.zip

# package
pyinstaller.exe -w --add-data "images;images" -i images\recycle-bin.ico .\recycle_bin.py

# The target files in the .\dist\recycle_bin\
cd .\dist\recycle_bin\

# run 
.\recycle_bin.exe
```
