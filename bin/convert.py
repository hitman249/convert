# !/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Alexandr Dorohin
# 21.03.2014

import os
import subprocess
import re
import shutil

__author__ = 'neiron'
__version__ = '0.4'

MAX_WIDTH = 1280
MAX_HEIGHT = 720
MIN_WIDTH = 480
MIN_HEIGHT = 320
VIDEO_CODEC = ["h264", "x264"]
AUDIO_CODEC = ["mp3", "mp2", "mp1", "aac", "pcm", "ogg"]
MAX_VIDEO_FILE_SIZE = 64  # Mb
ROOT_PATH = os.getcwd().replace('\\', '/').decode("cp1251")
FFMPEG = '"' + ROOT_PATH + "/bin/ffmpeg/bin/ffmpeg.exe" + '"'


# Ищет объект в массиве объектов
def chk_object_to_array_object(search_object, array_object):
    if search_object in array_object:
        return True
    else:
        return False


# Запускает ffmpeg и получает ответ
def exec_ffmpeg(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = process.communicate()[0]
    return result


# Поиск в тексте по регулярке
def parse_text(regex, text):
    return re.findall(regex, text)


# Убирает расширение в имени файла
def del_ext(filename):
    temp = filename.split('.')
    del temp[len(temp) - 1]
    return ''.join(temp)


# Получает расширение в имени файла
def get_ext(filename):
    temp = filename.split('.')
    return temp[len(temp) - 1]


# Уменьшает разрешение в соответствии стандартам
def get_resize(wh):
    # В0, В1 --старое и новое значение высоты, Ш0, Ш1 --старое и новое значение ширины
    # Если задаёмся новой высотой В1, то Ш1=Ш0*В1/В0
    # Если задаёмся новой шириной Ш1, то В1=В0*Ш1/Ш0

    _width = int(wh[0]) * MAX_HEIGHT / int(wh[1])
    _height = int(wh[1]) * _width / int(wh[0])

    if MAX_HEIGHT < _height or MAX_WIDTH < _width:
        _height = int(wh[1]) * MAX_WIDTH / int(wh[0])
        _width = int(wh[0]) * _height / int(wh[1])

    return _width, _height


def get_metadata(metadata):
    vc = parse_text("(?<=Video: )[^\\s,]+", metadata)  # h264 \ x264
    if vc:
        vc = vc[0]
    else:
        vc = ""

    wh_str = parse_text("[0-9]{3,4}x[0-9]{3,4}", metadata)  # разрешение стандарт 1280x720

    if wh_str:
        wh_str = wh_str[0]
    else:
        wh_str = "1x1"

    fps = parse_text("[0-9]+(?= fps,)", metadata)  # ровно 25
    if fps:
        fps = fps[0]
    else:
        fps = ""

    tbc = parse_text("[0-9]+(?= tbc )", metadata)  # ровно 50
    if tbc:
        tbc = tbc[0]
    else:
        tbc = ""

    kbs = parse_text("(?<=, )[0-9]+(?= kb/s,)", metadata)  # не меньше 800
    if kbs:
        kbs = kbs[0]
    else:
        kbs = ""

    ac = parse_text("(?<=Audio: )[^\\s,]+", metadata)  # аудио дорожка
    if ac:
        ac = ac[0]
    else:
        ac = ""

    return vc, wh_str, fps, tbc, kbs, ac


def convert(filename, filename_rename, vc, wh_string, fps, tbc, kbs, ac, ext):
    _cnv = False
    _vc = False
    _ac = False
    _rename = False
    _width = None
    _height = None

    if int(fps) != 25:
        _cnv = True

    if int(tbc) != 50:
        _cnv = True

    if int(kbs) < 800:
        if int(fps) != 25 and int(tbc) != 50:
            _cnv = True

    if int(kbs) > 1800:
        _cnv = True

    if not chk_object_to_array_object(vc, VIDEO_CODEC):
        _cnv = True
        _vc = True

    if ac:
        if not chk_object_to_array_object(ac, AUDIO_CODEC):
            _cnv = True
            _ac = True

    if ext:
        if get_ext(filename) != 'mp4':
            _rename = True
    else:
        _cnv = True

    wh = wh_string.split('x')
    if int(wh[0]) > MAX_WIDTH:
        _width, _height = get_resize(wh)
        _cnv = True
    else:
        _width, _height = int(wh[0]), int(wh[1])

    if int(wh[1]) > MAX_HEIGHT:
        if not (_width is None and _height is None):
            _width, _height = get_resize(wh)
            _cnv = True
    else:
        _width, _height = int(wh[0]), int(wh[1])

    if int(wh[0]) < MIN_WIDTH:
        print u"У файла \"" + filename + u"\" слишком маленькое разрешение видео, он не может быть поставлен в прокат."
        return False

    if int(wh[1]) < MIN_HEIGHT:
        print u"У файла \"" + filename + u"\" слишком маленькое разрешение видео, он не может быть поставлен в прокат."
        return False

    if _cnv:
        cmd = FFMPEG + " -i \"" + ROOT_PATH + "/in/" + filename + "\" -b:v 1350k -vcodec h264 -r 25 "
        if not (_width is None and _height is None):
            cmd += "-s " + str(_width) + "x" + str(_height)
        else:
            cmd += "-s hd720"
        cmd += " -y \"" + ROOT_PATH + "/out/" + filename_rename + "\""

        return cmd
    else:
        print u"Файл \"" + filename_rename + u"\" соответствует стандарту, просто скопирован."
        shutil.copy(ROOT_PATH + "/in/" + filename, ROOT_PATH + "/out/" + filename_rename)
        return False


list_in = filter(lambda x: x.lower().endswith('.mp4') or x.lower().endswith('.avi')
                           or x.lower().endswith('.flv') or x.lower().endswith('.mkv')
                           or x.lower().endswith('.mov') or x.lower().endswith('.wmv')
                           or x.lower().endswith('.mpg') or x.lower().endswith('.mpeg')
                           or x.lower().endswith('.vob') or x.lower().endswith('.3gp')
                           or x.lower().endswith('.m2v'), os.listdir(ROOT_PATH + "/in/"))

print u"Стандартизатор:"

symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ %()",
           u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA____")
tr = dict([(ord(a), ord(b)) for (a, b) in zip(*symbols)])

for video_file_original in list_in:

    metadata = exec_ffmpeg((FFMPEG + " -i \"" + ROOT_PATH + "/in/" + video_file_original + "\"").encode("cp1251"))
    #video_file_original = video_file_original.decode("cp1251")

    vc, wh_str, fps, tbn, kbs, ac = get_metadata(metadata)

    ext = video_file_original.lower().endswith('.mp4')
    video_file_rename = (del_ext(video_file_original) + ".mp4").translate(tr)
    print u""
    print u"Файл: " + video_file_original + u" (" + vc + u"|" + ac + u"|" + wh_str + u")"

    if os.path.isfile(ROOT_PATH + "/out/" + video_file_rename):
        os.remove(ROOT_PATH + "/out/" + video_file_rename)

    #cmd = FFMPEG + " -i \"" + ROOT_PATH + "/in/" + video_file_original + "\" -vcodec h264 -r 25 -s hd720 -y -b 800K \"" + ROOT_PATH + "/out/" + video_file_rename + "\""
    cmd = convert(video_file_original, video_file_rename, vc, wh_str, fps, tbn, kbs, ac, ext)
    if cmd:
        print u"Перекодировка видеофайла: " + video_file_rename + u", ожидайте..."
        exec_ffmpeg(cmd.encode("cp1251"))

print u""
print u"Перекодировка закончена."
print u"Перекодированные файлы находятся в папке \"out\"."
print u"Чтобы выйти, нажмите любую клавишу."