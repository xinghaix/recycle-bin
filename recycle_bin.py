# -*- coding: utf-8 -*-

import os
import win32api
import win32con
import win32gui_struct
import win32gui
import datetime

import subprocess
# noinspection PyUnresolvedReferences
from win32com.shell import shell, shellcon

Main = None
iconEmpty = 'images/recycle-bin.ico'
iconFull = 'images/recycle-bin-full.ico'


class RecycleBin:

    def __init__(self):
        pass

    @staticmethod
    def is_empty(path):
        """
        检查指定位置的回收站是否为空
        :param path: 回收站的路径。可以是驱动器，文件夹 or None. None 就是查询所有的回收站
        :return:
        """
        (bytes_used, num_files) = shell.SHQueryRecycleBin(path)
        return num_files == 0

    @staticmethod
    def get_bytes(path):
        """
        获取指定位置回收站内总文件大小
        :param path: 回收站的路径。可以是驱动器，文件夹 or None. None 就是查询所有的回收站
        :return: 回收站内总文件大小
        """
        (bytes_used, num_files) = shell.SHQueryRecycleBin(path)
        return bytes_used

    @staticmethod
    def empty(confirm=False, show_progress=False, sound=False):
        """
        清空回收站
        :param confirm: 是否弹出确认对话框
        :param show_progress: 是否展示处理进度条
        :param sound: 完成时是否声音提示
        :return:
        """
        if not RecycleBin.is_empty(None):
            flags = 0
            if not confirm:
                flags |= shellcon.SHERB_NOCONFIRMATION
            if not show_progress:
                flags |= shellcon.SHERB_NOPROGRESSUI
            if not sound:
                flags |= shellcon.SHERB_NOSOUND
            shell.SHEmptyRecycleBin(None, None, flags)

    @staticmethod
    def open():
        """
        通过shell命令打开回收站窗口
        """
        # subprocess.Popen('start shell:RecycleBinFolder', shell=True)
        subprocess.Popen('explorer shell:RecycleBinFolder', shell=True)


# noinspection SpellCheckingInspection,PyShadowingBuiltins,PyAttributeOutsideInit,PyUnusedLocal
class SysTrayIcon(object):
    QUIT = 'QUIT'
    SPECIAL_ACTIONS = [QUIT]
    FIRST_ID = 1314
    lastClick = None

    def __init__(self, icon, hover_text, menu_options, on_quit=None,
                 default_menu_index=None,
                 window_class_name=None):
        self.icon = icon
        self.hover_text = hover_text
        self.on_quit = on_quit

        menu_options = menu_options + (('退出', None, self.QUIT),)
        self._next_action_id = self.FIRST_ID
        self.menu_actions_by_id = set()
        self.menu_options = self._add_ids_to_menu_options(list(menu_options))
        self.menu_actions_by_id = dict(self.menu_actions_by_id)
        del self._next_action_id

        self.default_menu_index = (default_menu_index or 0)
        self.window_class_name = window_class_name or "SysTrayIconPy"

        message_map = {win32gui.RegisterWindowMessage("TaskbarCreated"): self.refresh_icon,
                       win32con.WM_DESTROY: self.destroy,
                       win32con.WM_COMMAND: self.command,
                       win32con.WM_USER + 20: self.notify}
        # 注册窗口类
        window_class = win32gui.WNDCLASS()
        window_class.hInstance = win32gui.GetModuleHandle(None)
        window_class.lpszClassName = self.window_class_name
        window_class.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
        window_class.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        window_class.hbrBackground = win32con.COLOR_WINDOW
        # 也可以指定wndproc
        window_class.lpfnWndProc = message_map
        self.classAtom = win32gui.RegisterClass(window_class)

    def show_icon(self):
        # 创建窗口
        hinst = win32gui.GetModuleHandle(None)
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow(self.classAtom, self.window_class_name, style, 0, 0,
                                          win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, 0, 0, hinst, None)
        win32gui.UpdateWindow(self.hwnd)
        self.notify_id = None
        self.refresh_icon()

        win32gui.PumpMessages()

    def show_menu(self):
        menu = win32gui.CreatePopupMenu()
        self.create_menu(menu, self.menu_options)
        # win32gui.SetMenuDefaultItem(menu, 1000, 0)

        pos = win32gui.GetCursorPos()
        win32gui.SetForegroundWindow(self.hwnd)
        win32gui.TrackPopupMenu(menu,
                                win32con.TPM_LEFTALIGN,
                                pos[0],
                                pos[1],
                                0,
                                self.hwnd,
                                None)
        win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)

    def destroy(self, hwnd, msg, wparam, lparam):
        # 运行传递的on_quit
        if self.on_quit:
            self.on_quit(self)
        # 退出托盘图标
        nid = (self.hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0)

    def notify(self, hwnd, msg, wparam, lparam):
        """ 可能的鼠标事件：
        WM_MOUSEMOVE
        WM_LBUTTONDOWN
        WM_LBUTTONUP
        WM_LBUTTONDBLCLK
        WM_RBUTTONDOWN
        WM_RBUTTONUP
        WM_RBUTTONDBLCLK
        WM_MBUTTONDOWN
        WM_MBUTTONUP
        WM_MBUTTONDBLCLK
        """
        # 双击左键
        if lparam == win32con.WM_LBUTTONDBLCLK:
            # self.execute_menu_option(self.default_menu_index + self.FIRST_ID)
            RecycleBin.empty()
        # 单击右键
        elif lparam == win32con.WM_RBUTTONUP:
            self.show_menu()
        # 单击中键
        elif lparam == win32con.WM_LBUTTONDOWN:
            if self.lastClick is not None:
                now = self.get_current_time()
                interval = (now - self.lastClick).microseconds / 1200
                print(interval)
                if interval > 1000:
                    RecycleBin.open()
                    self.lastClick = now
            else:
                self.lastClick = self.get_current_time()

        return True

    def _add_ids_to_menu_options(self, menu_options):
        result = []
        for menu_option in menu_options:
            text, icon, action = menu_option
            if callable(action) or action in self.SPECIAL_ACTIONS:
                self.menu_actions_by_id.add((self._next_action_id, action))
                result.append(menu_option + (self._next_action_id,))
            else:
                result.append((text, icon,
                               self._add_ids_to_menu_options(action),
                               self._next_action_id))
            self._next_action_id += 1
        return result

    def refresh_icon(self, **data):
        hinst = win32gui.GetModuleHandle(None)
        # 尝试找到自定义图标
        if os.path.isfile(self.icon):
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            hicon = win32gui.LoadImage(hinst, self.icon, win32con.IMAGE_ICON,
                                       0, 0, icon_flags)
        # 找不到图标文件 - 使用默认值
        else:
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        if self.notify_id:
            message = win32gui.NIM_MODIFY
        else:
            message = win32gui.NIM_ADD
        self.notify_id = (self.hwnd, 0,
                          win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,
                          win32con.WM_USER + 20, hicon, self.hover_text)
        win32gui.Shell_NotifyIcon(message, self.notify_id)

    def create_menu(self, menu, menu_options):
        for option_text, option_icon, option_action, option_id in menu_options[::-1]:
            if option_icon:
                option_icon = self.prep_menu_icon(option_icon)

            if option_id in self.menu_actions_by_id:
                item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text,
                                                                hbmpItem=option_icon,
                                                                wID=option_id)
                win32gui.InsertMenuItem(menu, 0, 1, item)
            else:
                submenu = win32gui.CreatePopupMenu()
                self.create_menu(submenu, option_action)
                item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text,
                                                                hbmpItem=option_icon,
                                                                hSubMenu=submenu)
                win32gui.InsertMenuItem(menu, 0, 1, item)

    @staticmethod
    def prep_menu_icon(icon):
        # 首先加载图标
        ico_x = win32api.GetSystemMetrics(win32con.SM_CXSMICON)
        ico_y = win32api.GetSystemMetrics(win32con.SM_CYSMICON)
        hicon = win32gui.LoadImage(0, icon, win32con.IMAGE_ICON, ico_x, ico_y, win32con.LR_LOADFROMFILE)

        hdc_bitmap = win32gui.CreateCompatibleDC(0)
        hdc_screen = win32gui.GetDC(0)
        hbm = win32gui.CreateCompatibleBitmap(hdc_screen, ico_x, ico_y)
        hbm_old = win32gui.SelectObject(hdc_bitmap, hbm)
        # 填满背景
        brush = win32gui.GetSysColorBrush(win32con.COLOR_MENU)
        win32gui.FillRect(hdc_bitmap, (0, 0, 16, 16), brush)
        # "GetSysColorBrush返回缓存的画笔而不是分配新的画笔"
        # - 暗示没有DeleteObject
        # 画出图标
        win32gui.DrawIconEx(hdc_bitmap, 0, 0, hicon, ico_x, ico_y, 0, 0, win32con.DI_NORMAL)
        win32gui.SelectObject(hdc_bitmap, hbm_old)
        win32gui.DeleteDC(hdc_bitmap)

        return hbm

    def command(self, hwnd, msg, wparam, lparam):
        id = win32gui.LOWORD(wparam)
        self.execute_menu_option(id)

    def execute_menu_option(self, id):
        menu_action = self.menu_actions_by_id[id]
        if menu_action == self.QUIT:
            win32gui.DestroyWindow(self.hwnd)
        else:
            menu_action(self)

    @staticmethod
    def get_current_time():
        return datetime.datetime.now()


# noinspection PyAttributeOutsideInit
class _Main:

    def main(self):
        # 悬浮于图标上方时的提示
        hover_text = "回收站"
        menu_options = (('Language', None, (('中文简体', None, self.switch_icon),
                                            ('English', None, self.switch_icon))),
                        ('打开', None, self.open_recycle_bin),
                        ('清空', None, self.empty_recycle_bin))
        self.sysTrayIcon = SysTrayIcon(iconEmpty, hover_text, menu_options,
                                       on_quit=self.exit, default_menu_index=2)
        self.unmap()
        # import tkinter
        # self.root = tkinter.Tk()
        # self.root.iconbitmap(iconEmpty)
        # self.root.title('回收站')
        # self.root.geometry('240x120')
        # self.root.resizable(0, 0)
        # self.root.bind("<Unmap>", lambda event: self.Unmap if self.root.state() == 'iconic' else False)
        # self.root.protocol('WM_DELETE_WINDOW', self.unmap)
        # self.root.mainloop()

    @staticmethod
    def switch_icon(_sys_tray_icon, icons=iconEmpty):
        if icons is not None:
            _sys_tray_icon.icon = icons
            _sys_tray_icon.refresh_icon()

    def open_recycle_bin(self, _sys_tray_icon, icons=None):
        self.switch_icon(_sys_tray_icon, icons)
        RecycleBin.open()

    def empty_recycle_bin(self, _sys_tray_icon, icons=None):
        self.switch_icon(_sys_tray_icon, icons)
        RecycleBin.empty()

    def unmap(self):
        # self.root.withdraw()
        self.sysTrayIcon.show_icon()

    def exit(self, _sys_tray_icon=None):
        # self.root.destroy()
        pass


if __name__ == '__main__':
    _Main().main()
