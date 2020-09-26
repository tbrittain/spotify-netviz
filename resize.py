# use to resize album arts because the raw files are in excess of 600x600 pixels which could add up
# adapted from https://pythontic.com/image-processing/pillow/resize
import PIL.Image as Image
import os
from tqdm import tqdm
from pathlib import Path


def resize_arts():
    path = os.getcwd()
    print(path)

    try:
        os.chdir('album_arts')
        original_art_path = os.getcwd()
        print(original_art_path)
    except FileNotFoundError:
        print(
            f'No album arts folder found in {path}. Please run main.py to download album arts before using this script.')
        exit()

    try:  # if ../album_arts/ exists, then create new folder
        os.chdir(path=path)
        os.mkdir('album_arts_resized')
        os.chdir('album_arts_resized')
        new_art_path = os.getcwd()
        print(new_art_path)

    except FileExistsError:
        os.chdir(path=path)
        os.chdir('album_arts_resized')
        new_art_path = os.getcwd()
        print(new_art_path)

    os.chdir(original_art_path)
    outer = tqdm(desc='Art resizing', unit='images', total=len(os.listdir(original_art_path)), leave=True)
    for art in os.listdir(original_art_path):
        try:
            image = Image.open(art)
        except FileNotFoundError:
            print('No album arts found in folder.')
            exit()
        # halves the dimensions of the images, so they'll be roughly 300x300 each
        # this is a reduction of approx 80kb/image to 20kb/image
        resized_image = image.resize((round(image.size[0] * .5), round(image.size[1] * .5)))
        os.chdir(new_art_path)
        resized_art_path = str(os.getcwd() + '/' + art)
        resized_art_path.replace('\\', '/')
        resized_art_path = Path(resized_art_path)
        if resized_art_path.is_file():  # introduce check to determine if art present, and if so, no need to re-convert
            pass
        else:
            resized_image.save(art)
        os.chdir(original_art_path)
        outer.update(1)
