import os
from PIL import Image

folders = os.listdir('../static/images/')
for folder in folders:
    files = os.listdir('../static/images/' + folder)
    for file in files:
        img = Image.open('../static/images/' + folder + '/' + file)
        img = img.convert('RGBA')
        data = img.load()
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                if data[x, y][0] > 200 and data[x, y][1] > 200 and data[x, y][2] > 200:
                    data[x, y] = (255, 255, 255, 0)
                else:
                    data[x, y] = (0, 0, 0, 255)
        img.save('../static/images/' + folder + '/' + file)
