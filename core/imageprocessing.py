# -*- coding: utf-8 -*-
import os
from PIL import Image
import numpy as np
from PIL import ImageFilter

tw,th = (270,336) # 缩放目标尺寸
scaler = 0.04
scaler_y = 0.56
chess_height = 47
crop_area_left = (0,0,0.5-scaler,scaler_y)
crop_area_right = (0.5+scaler,0,1,scaler_y)
blockheight_extra_big = 38
blockheight_big = 31
blockheight_medium = 25
blockheight_small = 17
blockheight_extra_small = 8
color_dif = 256

def analyse_image(image, directory=".", backup="text_area_2.png"):
    """
    :param image: 图像名称 带后缀名
    :param directory: 图像所在目录
    :return: 返回跳跃距离，需要进一步乘上时长因子
    """
    im = Image.open(os.path.join(directory,image)).resize((tw,th)).convert("L")
    im.save(os.path.join(directory,"new_area.png"))
    width, height = im.size
    im_mat = np.matrix(im.getdata(), dtype='float') / 255 # 灰度值
    im_mat = im_mat.reshape(height,width)
    im_arr = im_mat.getA()
    maxlist = np.where(im_arr <= np.min(im_arr)+0.2)
    im_arr[maxlist] = 0
    im_arr = im_arr * 255
    img = Image.fromarray(im_arr.astype(np.uint8))
    img.save(os.path.join(directory,"after_area.bmp"))

    # 找寻棋子位置
    (Xpos,Ypos) = find_chess("after_area.bmp", maxlist, directory=directory)
    print("棋子位置： X={} Y={}".format(Xpos,Ypos))

    # 找寻下一个方块的位置
    im = Image.open(os.path.join(directory, backup)).resize((tw, th)).convert("RGB")
    # 多通道差分边缘识别与校正
    (w, h) = im.size
    for x in range(w):
        for y in range(h-1):
            pos1 = (x, y)
            pos2 = (x, y+1)
            rgb1 = im.getpixel(pos1)
            rgb2 = im.getpixel(pos2)
            (r1, g1, b1) = rgb1
            (r2, g2, b2) = rgb2
            dif = abs(r1-r2) + abs(g1-g2) + abs(b1-b2)
            if dif > color_dif and y < h-2 and x < w-1:
                im.putpixel(pos1, (0, 0, 0))
    im.save(os.path.join(directory, "new_area.png"))

    im = Image.open(os.path.join(directory, "new_area.png")).resize((tw, th)).convert("L")
    width, height = im.size
    im_mat = np.matrix(im.getdata(), dtype='float') / 255  # 灰度值
    im_mat = im_mat.reshape(height, width)
    im_arr = im_mat.getA()
    im_arr = im_arr * 255
    im_arr[maxlist] = 255 # 去除棋子
    img = Image.fromarray(im_arr.astype(np.uint8))
    # 判别棋子区域
    if Xpos >= int(width/2):
        print("棋子在右侧，识别左侧方块")
        img = img.crop((width * crop_area_left[0], height * crop_area_left[1], width * crop_area_left[2], height * crop_area_left[3]))
    else:
        print("棋子在左侧，识别右侧方块")
        img = img.crop((width * crop_area_right[0], height * crop_area_right[1], width * crop_area_right[2],height * crop_area_right[3]))
    (w,h) = img.size
    im_mat = np.matrix(img.getdata(), dtype='float') / 255
    im_mat = im_mat.reshape(h, w)
    im_arr = im_mat.getA()
    # 求取半边图像滤波
    p = 2/4 # 越大滤波效果越差
    noiseList = np.where( im_arr >= np.min(im_arr)*p + np.max(im_arr)*(1-p) )
    im_arr[noiseList] = 1
    im_arr = im_arr * 255
    allList = np.where( im_arr < 255 )
    im_arr[allList] = 0
    # 边缘黑条去除
    im_arr[:, 0] = 255
    im_arr[0, :] = 255
    im_arr[:, -1] = 255
    im_arr[-1, :] = 255
    im_arr[:, 1] = 255
    im_arr[1, :] = 255
    im_arr[:, -2] = 255
    im_arr[-2, :] = 255
    img = Image.fromarray(im_arr.astype(np.uint8))
    img.save(os.path.join(directory, "after_area_block.bmp"))  # 覆盖保存半边裁切图
    maxlist = np.where(im_arr <= 250)
    (bXpos, bYpos) = find_block("after_area_block.bmp", maxlist, directory= directory)
    if Xpos < round(width / 2):
        bXpos += round(width * (0.5+scaler)) # 校正棋子在左侧的情况的方块横坐标
    print("下一个方块位置： X={} Y={}".format(bXpos, bYpos))
    dis = pow( pow(bXpos-Xpos,2)+pow(bYpos-Ypos,2),0.5 ) # 计算跳跃的欧氏距离
    print("跳跃的直线距离为：{}".format(dis))
    return dis


def find_block(image, maxlist, directory="."):
    im = Image.open(os.path.join(directory, image)).convert("L")
    X_pos = maxlist[0]
    Y_pos = maxlist[1]
    X_pos = X_pos.tolist()
    Y_pos = Y_pos.tolist()
    Xmin = min(X_pos)
    (whereisXmin,final_knot) = find_medium(X_pos,Xmin,anotherCor=Y_pos)
    YCorOfXin = Y_pos[final_knot]
    blockalign = []
    Xmax = []
    for s in range(-2,2):
        for i in range(len(X_pos)):
            if YCorOfXin>2:
                if Y_pos[i]==YCorOfXin+s:
                    blockalign.append(X_pos[i])
        if len(blockalign)>0:
            Xmax.append(max(blockalign))
    Xmax = max(Xmax)
    if Xmax - Xmin > 102:
        print("识别下一个为超大方块")
        Y_center = Xmin + blockheight_extra_big
    elif Xmax - Xmin > 93:
        print("识别下一个为大方块")
        Y_center = Xmin + blockheight_big
    elif Xmax - Xmin > 80:
        print("识别下一个为中方块")
        Y_center = Xmin + blockheight_medium
    elif Xmax - Xmin > 60:
        print("识别下一个为小方块")
        Y_center = Xmin + blockheight_small
    else:
        print("识别下一个为超小药瓶等物体")
        Y_center = Xmin + blockheight_extra_small
    X_center = whereisXmin
    return (X_center, Y_center)


def find_chess(image, maxlist, directory="."):
    im = Image.open(os.path.join(directory, image)).convert("L")
    cover_arr = np.zeros((th,tw))
    cover_arr[maxlist] = 1
    max_x = 0
    xpos = 0
    for i in range(tw):
        sum = 0
        for j in range(th):
            sum += cover_arr[(j,i)]
        if sum > max_x:
            xpos = i
            max_x = sum
    cover_arr = cover_arr[:,xpos]
    maxlist = np.where(cover_arr == max(cover_arr))
    ypos = min(maxlist[0])
    ypos += chess_height
    xpos += 2
    return (xpos,ypos)


def find_medium(source, elmt, anotherCor = []):
    elmt_index = []
    s_index = 0
    e_index = len(source)
    while (s_index < e_index):
        try:
            temp = source.index(elmt, s_index, e_index)
            elmt_index.append(temp)
            s_index = temp + 1
        except ValueError:
            break
    max_knot = anotherCor[max(elmt_index)]
    min_knot = anotherCor[min(elmt_index)]
    avg_knot = round((max_knot+min_knot)/2)

    avg = sum(elmt_index)/len(elmt_index)
    last_dif = max(elmt_index)
    final_knot = 0
    for x in elmt_index:
        if abs(x-avg)<last_dif:
            final_knot = x
        last_dif = abs(x-avg)

    return avg_knot,final_knot