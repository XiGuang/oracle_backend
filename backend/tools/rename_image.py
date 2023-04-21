import PIL.Image as Image
import os

files=os.scandir('../resources')
for file in files:
    if file.is_dir():
        images=os.scandir(file.path)
        for image in images:
            if image.is_file():
                img=Image.open(image.path)
                if img.size != (224,224):
                    img=img.resize((224,224))
                    img.save(image.path)
                else:
                    print(image.path)