import hashlib

import cv2

import PIL.Image as Image
import numpy as np

import backend.configs.config as config
from backend.modules import Word
from backend.modules import Image as ImageDB


def cv2PIL(img_cv):
    return Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))


def PIL2cv(img_pil):
    return cv2.cvtColor(np.asarray(img_pil), cv2.COLOR_RGB2BGR)

def setBackgroundColor(img, color=None):
    new_img=img.copy()
    if color is None:
        color = [255, 255, 255]
    new_img[np.where((new_img[:, :, 3] == 0))] = [*color,255]
    return new_img

def url_for(path):
    path = path.replace('\\', '/')
    return config.server_path + 'static/' + path


def to_path(path):
    return path.replace('\\', '/')


def renameWithHash(image):
    image_arr=np.asarray(image)
    hash_value = hashlib.md5(image_arr).hexdigest()
    new_name = str(hash_value) + ".png"
    return new_name


def getIdiomImage(paths):
    image_1 = Image.open(paths[0])
    image_2 = Image.open(paths[1])
    image_3 = Image.open(paths[2])
    image_4 = Image.open(paths[3])
    # 获取图片的宽度和高度，假设四张图片大小相同
    width, height = image_1.size

    # 沿着水平方向（axis=1）将四个数组连接起来，得到一个新的数组
    img_new = np.concatenate((image_1, image_2, image_3, image_4), axis=1)

    # 将新的数组转换为Image对象
    img_new = Image.fromarray(img_new)
    return img_new


def getSentenceImage(paths):
    max_row = 6  # 每行最多显示的图片数量
    images = []
    for path in paths:
        images.append(Image.open(path))
    # 图片大小相同，将他们拼接成一张大图
    width, height = images[0].size
    col = len(images) // max_row + 1
    result = Image.new('RGBA', (width * (len(images) if len(images) < max_row else max_row), height * col),
                       (0, 0, 0, 0))
    for i in range(len(images)):
        result.paste(images[i], (width * (i % max_row), height * (i // max_row)))
    return result


def getCardImage(card_cv, words):
    card_pil = cv2PIL(card_cv)
    card_pil = card_pil.convert("RGBA")
    w, h = card_pil.size
    for word in words:
        word_db = Word.query.filter_by(word=word['word']).first()
        if word_db is None:
            continue
        word_pil = Image.open(to_path("backend/static/images/" + ImageDB.query.filter_by(id=word_db.image_id).first().image))
        word_pil = word_pil.resize((120, 120))
        width, height = word_pil.size
        for i in range(width):
            for j in range(height):
                word_pil.putpixel((i,j),tuple(word['color']+[word_pil.getpixel((i,j))[-1],]))
        alpha = word_pil.split()[-1]
        card_pil.paste(word_pil, (int(word['position'][0] * w), int(word['position'][1] * h)), mask=alpha)
    return card_pil
