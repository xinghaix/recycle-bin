# -*- coding: utf-8 -*-

import sys
from PySide2.QtWidgets import *


# noinspection PyArgumentList
class Window(QWidget):
    def __init__(self):
        # 初始化构造用户界面类的基础类，QWidget提供了默认的构造方法
        super().__init__()
        self.initUI()

    def initUI(self):
        # 设置窗口名
        self.setWindowTitle("这是是标题")
        # 设置窗口大小
        self.resize(800, 530)
        # 设置窗口位置
        self.move(1200, 200)

        self.show()


if __name__ == "__main__":
    # 所有应用必须创建一个应用（Application）对象
    app = QApplication(sys.argv)
    test = Window()
    sys.exit(app.exec_())
