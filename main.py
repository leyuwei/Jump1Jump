# -*- coding:utf-8 -*-

import time
from random import uniform
from core.android import *
from core.imageprocessing import *

crop_area = (0,2/10,1,9/10) # 全屏幕截图
factor = 5.4 # 距离时间因子 单位ms/px 靠手感调节

def main():
    # 检测截图目录是否存在，否则创建
    cur_path = os.path.abspath(os.curdir)
    path = cur_path + "\\screenshots"
    if not os.path.exists(path):
        os.makedirs(path)

    lastmd5 = ""
    while True:
        x = input("按任意键开始识别并跳跃, 输入Q退出")
        if x.strip().lower() == "q":
            break
        try:
            while(True):
                md5 = analyze_current_screen(crop_area, directory="screenshots")
                if lastmd5.strip()==md5.strip():
                    print("不在游戏状态内，退出自动操控...")
                    break
                else:
                    lastmd5 = md5
                dis = analyse_image("text_area.png", directory="screenshots",backup="text_area_2.png")
                simulate_tap( dis * factor )
                timeduration = random.uniform(0.6,0.8)
                time.sleep(timeduration)
                #break # Debug
        except Exception as e:
            print("操作过程遇到问题: " + str(e))
            break



if __name__=="__main__":
    main()