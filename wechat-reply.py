#根据预定的csv数据自动回复
import numpy as np
import pandas as pd
from uiautomation import WindowControl
import time
import requests
import re
import keyboard

is_running = True
def modify_variable():
    global is_running
    is_running = False
    print(f"运行中: {is_running}")

# 监听 Ctrl + K 快捷键
keyboard.add_hotkey('ctrl + k', modify_variable)

# 绑定微信主窗口
wx = WindowControl(Name='微信', searchDepth=1)   #searchDepth=1参数指定在查找窗口时只搜索直接子级窗口，以提高查找效率
# 切换窗口
wx.ListControl()
wx.SwitchToThisWindow()#ListControl()方法用于列出所有子级窗口，而SwitchToThisWindow()方法则将焦点切换到微信主窗口
# 寻找会话控件绑定
hw = wx.ListControl(Name='会话')
# 通过pd读取数据
df = pd.read_csv('回复数据.csv', encoding='utf-8')
# print(df)

temp_concat_name = '文件传输助手'
target_concat_name = '牧心CP'
 
conversations = hw.GetChildren()  # GetChildren()方法，获取会话列表中的所有子控件。

# 死循环接收消息
while is_running and True:
    time.sleep(20)  # 参数是秒为单位，所以 2000ms 对应 2 秒
    for conversation in conversations:
        contact_name = conversation.Name
        if contact_name.startswith(target_concat_name):
            # 获取未读消息数量
            new_msg_num = re.findall(r'\d+', contact_name)  # 匹配连续的数字
            new_msg_num = [int(num) for num in new_msg_num]
            new_msg_num = new_msg_num[0] if new_msg_num else 0  # 三元表达式，空列表时返回 0
            print(f'new_msg_num {new_msg_num}')
            if new_msg_num != 0:
                # 光标选中，进行 UI 操作
                conversation.Click(simulateMove=False)
                message_list = wx.ListControl(Name='消息').GetChildren()  # 获取消息列表中的所有子控件
                # 目前仅回复最后一条消息（TODO: 判断消息方及是否回复后进行多消息回复）
                lastMsg = message_list[-1] if message_list else ''
                lastMsg = lastMsg.Name if lastMsg else ''
                print(f"最后一条消息 {lastMsg}");
                # 判断关键字
                msg = df.apply(lambda x: x['回复内容'] if x['关键词'] in lastMsg else None, axis=1)
                # 返回的结果是一个包含处理结果的Series对象，msg和列表差不多
                print(f"匹配到的回复内容：{msg}")
                msg.dropna(axis=0, how='any', inplace=True)  # 这行代码移除回复内容中的空数据（NaN值）
                ar = np.array(msg).tolist()  # 这行代码将筛选后的回复内容转换为列表
                print(f"ar:{ar}")
                ########### 能够匹配到数据时
                if ar:
                    # 将数据输入
                    # 替换换行符号
                    wx.SendKeys(ar[0].replace('{br}', '{Shift}{Enter}'), waitTime=0)
                    # 发送消息，回车键
                    wx.SendKeys('{Enter}', waitTime=1)
                    # 通过消息匹配检索会话栏的联系人
                    print(f"回复内容是 {ar[0]}")
                    #wx.TextControl(SubName=ar[0][:5]).RightClick()
                    # break
                ######### 不能匹配到数据，用机器人回复
                else:
                    wx.SendKeys('不知道你在说什么', waitTime=0)
                    wx.SendKeys('{Enter}', waitTime=0)
            else:
                print("没有新消息")
        elif contact_name.startswith(temp_concat_name):
            # 光标选中其他消息框，解决下次消息数量获取问题
            conversation.Click(simulateMove=False)
            
