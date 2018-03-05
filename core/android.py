# -*- coding: utf-8 -*-

from datetime import datetime

import os
import hashlib
import sys
import random
from PIL import Image
from PIL import ImageFilter
from PIL import ImageEnhance
from shutil import copyfile

def analyze_current_screen(crop_area, directory=".", compress_level=1):
    """
        capture the android screen now
    """
    print("截屏时间: ", datetime.now().strftime("%H:%M:%S"))
    screenshot_filename = "screenshot.png"
    save_text_area = os.path.join(directory, "text_area.png")
    save_text_area2 = os.path.join(directory, "text_area_2.png")
    capture_screen(screenshot_filename, directory)
    save_screen(directory=directory)
    parse_answer_area(os.path.join(directory, screenshot_filename), save_text_area, compress_level, crop_area, backup_file=save_text_area2)

    return get_area_data(save_text_area)


def simulate_tap(interval):
    startpos = (random.randint(200,300),random.randint(200,300))
    endpos = (random.randint(150,300),random.randint(150,300))
    interval = int(round(interval))
    os.system("adb shell input swipe {} {} {} {} {}".format(startpos[0],startpos[1],endpos[0],endpos[1],interval))


def analyze_stored_screen_text(screenshot_filename="screenshot.png", directory=".", compress_level=1):
    """
    reload screen from stored picture to store
    :param directory:
    :param compress_level:
    :return:
    """
    save_text_area = os.path.join(directory, "text_area.png")
    parse_answer_area(os.path.join(directory, screenshot_filename), save_text_area, compress_level)
    return get_area_data(save_text_area)


def capture_screen(filename="screenshot.png", directory="."):
    """
    use adb tools

    :param filename:
    :param directory:
    :return:
    """
    os.system("adb shell screencap -p /sdcard/{0}".format(filename))
    os.system("adb pull /sdcard/{0} {1}".format(filename, os.path.join(directory, filename)))


def save_screen(filename="screenshot.png", directory="."):
    """
    Save screen for further test
    :param filename:
    :param directory:
    :return:
    """
    copyfile(os.path.join(directory, filename),
             os.path.join(directory, datetime.now().strftime("%m%d_%H%M%S").join(os.path.splitext(filename))))


def parse_answer_area(source_file, text_area_file, compress_level, crop_area, backup_file="text_area_2.png"):
    image = Image.open(source_file)
    if compress_level == 1:
        image1 = image.convert("L")
        image2 = image.convert("RGB")
    elif compress_level == 2:
        image = image.convert("1")
    width, height = image.size[0], image.size[1]
    print("屏幕宽度: {0}, 屏幕高度: {1}".format(width, height))

    region1 = image1.crop((width * crop_area[0], height * crop_area[1], width * crop_area[2], height * crop_area[3]))
    region2 = image2.crop((width * crop_area[0], height * crop_area[1], width * crop_area[2], height * crop_area[3]))
    im = enhance_image(region2, 0.8, 1.3)
    im = im.filter(ImageFilter.DETAIL)
    im = im.filter(ImageFilter.MedianFilter(5))
    im = im.filter(ImageFilter.FIND_EDGES)
    im = im.filter(ImageFilter.CONTOUR)
    im.save(backup_file)
    im2 = enhance_image(region1,1.22,1.2)
    im2.save(text_area_file)

def enhance_image(image,brightness,contrast,sharp=1):
    enh_bri = ImageEnhance.Brightness(image)
    image_brightened = enh_bri.enhance(brightness)
    enh_con = ImageEnhance.Contrast(image_brightened)
    image_contrasted = enh_con.enhance(contrast)
    enh_col = ImageEnhance.Sharpness(image_contrasted)
    image_colored = enh_col.enhance(sharp)
    return image_colored

def get_area_data(text_area_file):
    """

    :param text_area_file:
    :return:
    """
    with open(text_area_file, "rb") as fp:
        # image_data = fp.read()
        md5 = sumfile(fp)
        return md5
    return ""


def sumfile(fobj):
    m = hashlib.md5()
    while True:
        d = fobj.read(8096)
        if not d:
            break
        m.update(d)
    return m.hexdigest()