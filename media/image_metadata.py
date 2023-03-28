# Original: https://codeby.net/threads/izvlekaem-metadannye-iz-foto-audio-i-video-fajlov-s-pomoschju-python.80200/

# pip install Pillow ffmpeg-python

import os.path
from pprint import pprint

import ffmpeg
from PIL import Image, ExifTags


def image_metadata(path_f):
    img = Image.open(path_f)
    info_dict = {
        "File name": os.path.split(path_f)[1],
        "Image size": img.size,
        "Image height": img.height,
        "Image width": img.width,
        "Image format": img.format,
        "Image mode": img.mode,
        "Is animated": getattr(img, "is_animated", False),
        "Frames": getattr(img, "n_frames", 1)
    }
    try:
        exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}

        print(f'\n[+] Metadata: {os.path.split(path_f)[1]:27}\n')
        for info in exif:
            if info == 'GPSInfo':
                print(f'{info:27}: lat {exif[info][2]} {exif[info][1]} - long {exif[info][4]} {exif[info][3]}')
            else:
                if isinstance(exif[info], bytes):
                    info_d = exif[info].decode()
                    print(f'{info:25}: {info_d}')
                else:
                    print(f'{info:25}: {exif[info]}')
    except AttributeError:
        print(f'\n[+] Image info: {os.path.split(path_f)[1]:27}\n')
        for k, v in info_dict.items():
            print(f"{k:27}: {v}")
        exit(0)


def vid_aud_matadata(patn_f):
    try:
        print(f'\n[+] Metadata: {os.path.split(patn_f)[-1]}\n')
        pprint(ffmpeg.probe(patn_f)["streams"])
    except ffmpeg._run.Error:
        print('[-] Unsupported format')


if __name__ == "__main__":
    path_file = input('[~] Enter file path: ')
    if not os.path.exists(path_file):
        print('[-] File does not exist')
    else:
        if path_file.endswith(".jpg"):
            image_metadata(path_file)
        elif path_file.endswith(".jpeg"):
            image_metadata(path_file)
        else:
            vid_aud_matadata(path_file)