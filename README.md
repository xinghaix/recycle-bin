# Recycle-Bin
这是Windows 10下的一个回收站工具【This is a  recycle bin tool for Windows 10】

# Package
```
# 获取代码【get the code】
git clone https://github.com/zishuangzhu/recycle-bin.git
cd recycle-bin

# 安装依赖【install pypiwin32】
pip install pypiwin32

# 安装打包工具【install pyinstaller】
pip install pyinstaller

# 打包【package】
pyinstaller.exe -w -F --add-data "images;images" -i images\recycle-bin.ico .\recycle_bin.py

# 打包后的文件在.\dist\recycle_bin\目录下【The target files in the .\dist\recycle_bin\】
# 运行【run】
.\dist\recycle_bin\recycle_bin.exe
```

# License
This package is released under [MIT](https://mit-license.org/)
