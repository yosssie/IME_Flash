from ctypes import *

import wx
import wx.adv

import win32api
import win32con
import win32gui


ICON = 'icon/A.ico'
ICONS = ["icon/A.ico", "icon/Jp_1.png", "icon/Jp_2.png", "icon/Jp_3.png", "icon/Jp_4.png", "icon/Jp_5.png", "icon/Jp_6.png", "icon/Jp_7.png", "icon/Jp_8.png"]

imm32 = WinDLL("imm32")

X = [1,0]
Inum = 1
speed = 30

class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        self.frame = frame
        self.toggle = 0
        wx.adv.TaskBarIcon.__init__(self)
        self.OnSetIcon(ICON)
        self.OnEnableTimer(None)

    def OnSetIcon(self, path):
        icon = wx.Icon(path)
        self.SetIcon(icon, 'IME Flash')

    def CreatePopupMenu(self):
        menu = wx.Menu()
        
        # ON/OFF設定
        flashm = wx.MenuItem(menu, 1, 'ON', kind=wx.ITEM_RADIO)
        disablem = wx.MenuItem(menu, 2, 'OFF', kind=wx.ITEM_RADIO)
        menu.Append(flashm)
        menu.Append(disablem)
        
        menu.Bind(wx.EVT_MENU, self.OnEnableTimer, id=flashm.GetId())
        menu.Bind(wx.EVT_MENU, self.OnDisableTimer, id=disablem.GetId())
        
        # ここで自分の保持している状態に合わせてチェック状態を設定
        # 例: self.timer_state が True のときは "ON" をチェック
        if getattr(self, "timer_state", True):
            menu.Check(flashm.GetId(), True)
        else:
            menu.Check(disablem.GetId(), True)
        
        menu.AppendSeparator()
        
        
        # 速さ設定
        fastm = wx.MenuItem(menu, 3, 'Fast', kind=wx.ITEM_RADIO)
        midm = wx.MenuItem(menu, 4, 'Mid', kind=wx.ITEM_RADIO)
        slowm = wx.MenuItem(menu, 5, 'Slow', kind=wx.ITEM_RADIO)
        menu.Append(fastm)
        menu.Append(midm)
        menu.Append(slowm)
        
        menu.Bind(wx.EVT_MENU, self.OnFast, id=fastm.GetId())
        menu.Bind(wx.EVT_MENU, self.OnMid, id=midm.GetId())
        menu.Bind(wx.EVT_MENU, self.OnSlow, id=slowm.GetId())
        
        # 例: self.speed_mode に 'Fast', 'Mid', 'Slow' を設定しておく
        mode = getattr(self, "speed_mode", "Mid")
        if mode == "Fast":
            menu.Check(fastm.GetId(), True)
        elif mode == "Mid":
            menu.Check(midm.GetId(), True)
        else:
            menu.Check(slowm.GetId(), True)
        
        menu.AppendSeparator()
        
        quitm = wx.MenuItem(menu, 6, 'Quit')
        menu.Append(quitm)
        menu.Bind(wx.EVT_MENU, self.OnQuit, id=quitm.GetId())
        
        return menu

    def OnEnableTimer(self, event):
        global speed
        self.timer_state = True  # 状態を更新
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnInUseTimer)
        self.timer.Start(speed)
        

    def OnInUseTimer(self, event):
        hwnd1 = win32gui.GetForegroundWindow()
        hwnd2 = imm32.ImmGetDefaultIMEWnd(hwnd1)
        #     下記の0x005は、IMC_GETOPENSTATUSを示しています。
        imestatus = win32api.SendMessage(hwnd2, win32con.WM_IME_CONTROL, 0x005, 0)

        if imestatus == 1:
            global Inum, speed
            use_icon = ICONS[Inum]
            if Inum < 8:
                Inum += 1
            else:
                Inum = 1
        else:
            speed = 600
            use_icon = ICONS[0]
        self.OnSetIcon(use_icon)

    def OnDisableTimer(self, event):
        self.timer_state = False  # 状態を更新
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnToggle)
        self.timer.Start(60)

    def OnToggle(self, event):
        hwnd1 = win32gui.GetForegroundWindow()
        hwnd2 = imm32.ImmGetDefaultIMEWnd(hwnd1)
        #     下記の0x005は、IMC_GETOPENSTATUSを示しています。
        imestatus = win32api.SendMessage(hwnd2, win32con.WM_IME_CONTROL, 0x005, 0)

        if imestatus == 1:
            use_icon = ICONS[5]
        else:
            use_icon = ICONS[0]
        self.OnSetIcon(use_icon)


    def OnFast(self, event):
        global speed
        self.speed_mode = 'Fast'
        speed = 15
        self.timer.Start(speed)

    def OnMid(self, event):
        global speed
        self.speed_mode = 'Mid'
        speed = 30
        self.timer.Start(speed)

    def OnSlow(self, event):
        global speed
        self.speed_mode = 'Slow'
        speed = 60
        self.timer.Start(speed)


    def OnQuit(self, event):
        self.RemoveIcon()
        wx.CallAfter(self.Destroy)
        self.frame.Close()

if __name__ == '__main__':
    app = wx.App()
    frame=wx.Frame(None, -1, title='IME Flash')
    TaskBarIcon(frame)
    app.MainLoop()