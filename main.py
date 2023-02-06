"""
This program is designed to convert anime to 2x resolution and encode it to HEVC using hevc_nvenc. The program uses
ffmpeg and realcugan. You need to install them yourself and add them to the PATH. Also make sure you have at least
An RTX 2000 series video card. Average encoding time is 6 hours for one 24-minute anime episode in 1080p resolution and
200 GB of free space on the hard drive. The program is not optimized for speed, but for quality.
"""


import os
import shutil
from datetime import datetime


def png1x(orig_path: str) -> None:
    """
    Extracting images from the original file
    :param orig_path:
    :return:
    """
    os.mkdir('pic1x')
    os.system(f'ffmpeg -y -hide_banner -i "{orig_path}" pic1x\\%06d.png')


def png2x() -> None:
    """
    Upscaling images to 2x resolution
    :return:
    """
    os.mkdir('pic2x')
    os.system(f'realcugan -i pic1x -o pic2x -n 1 -s 2 -f jpg')


def audio_encoding(orig_path: str) -> None:
    """
    Extracting audio from the original file and converting it to opus
    :param orig_path:
    :return:
    """
    os.system(f'ffmpeg -y -hide_banner -i "{orig_path}" -c:a libopus -b:a 192k -vbr 1 audio.opus')


def mkv_encoding() -> None:
    """
    Merge the jpg's and audio into a single file
    :return:
    """
    os.system(f'ffmpeg -y -hide_banner -i audio.opus -hwaccel cuda -hwaccel_output_format cuda -hwaccel_device 0 '
              f'-r 24000/1001 -i pic2x\\%6d.jpg -vf "hwdownload,format=nv12" -c copy -c:v:0 hevc_nvenc -profile:v '
              f'main10 -pix_fmt p010le -rc:v:0 vbr -tune hq -preset p5 -multipass 1 -bf 4 -b_ref_mode 1 -nonref_p 1 '
              f'-rc-lookahead 75 -spatial-aq 1 -aq-strength 8 -temporal-aq 1 -cq 21 -qmin 1 -qmax 99 -b:v:0 20M '
              f'-maxrate:v:0 40M -gpu 0 -r 24000/1001 output.mkv')


def main() -> None:
    """
    Main function
    :return:
    """
    work_dir = input('Enter directory: ')
    work_dir = work_dir.replace('"', '')
    work_dir = work_dir.replace("'", '')
    os.mkdir(work_dir)

    os.chdir(work_dir)

    orig_path = input('Enter the full path of the original file: ')
    orig_path = orig_path.replace('"', '')
    orig_path = orig_path.replace("'", '')

    print('\n\nConverting to png...')
    s = datetime.now().timestamp()
    png1x(orig_path)
    e = datetime.now().timestamp()
    print(f'Converting to png took {round(e - s, 2)} sec')

    print('\n\nUpscaling to 2x...')
    s = datetime.now().timestamp()
    png2x()
    e = datetime.now().timestamp()
    print(f'Upscaling to 2x took {round(e - s, 2)} sec')

    print('\n\nCleaning up...')
    shutil.rmtree('pic1x')

    print('\n\nConverting to opus...')
    s = datetime.now().timestamp()
    audio_encoding(orig_path)
    e = datetime.now().timestamp()
    print(f'Converting to opus took {round(e - s, 2)} sec')

    print('\n\nEncoding to mkv...')
    s = datetime.now().timestamp()
    mkv_encoding()
    e = datetime.now().timestamp()
    print(f'Encoding to mkv took {round(e - s, 2)} sec')

    print('\n\nCleaning up...')
    os.remove('audio.opus')
    shutil.rmtree('pic2x')


if __name__ == '__main__':
    start = datetime.now().timestamp()
    main()
    end = datetime.now().timestamp()
    print(f'The full execution was {round(end - start, 2)} sec')
