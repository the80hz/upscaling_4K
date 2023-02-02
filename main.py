import os
import shutil
from datetime import datetime


def main():
    print(
        "For the program to work, you need at least 200 GB for one episode of anime, and up to 1 TB for a movie.")
    print('Also make sure you have at least an RTX 2000 series graphics card.')

    work_dir = input('Enter directory: ')
    work_dir = work_dir.replace('"', '')
    work_dir = work_dir.replace("'", '')
    os.mkdir(work_dir)

    os.chdir(work_dir)

    orig_path = input('Enter the full path of the original file: ')
    orig_path = orig_path.replace('"', '')
    orig_path = orig_path.replace("'", '')

    print('\n\nConverting to png...')
    os.mkdir('pic1x')
    os.system(f'ffmpeg -y -hide_banner -i "{orig_path}" pic1x\\%06d.png')

    print('\n\nUpscaling to 2x...')
    os.mkdir('pic2x')
    os.system(f'realcugan -i pic1x -o pic2x -n 1 -s 2 -f jpg')

    print('\n\nConverting to opus...')
    os.system(f'ffmpeg -y -hide_banner -i "{orig_path}" -c:a libopus -b:a 192k audio.opus')

    print('\n\nEncoding to mkv...')
    os.system(f'ffmpeg -y -hide_banner -i audio.opus -hwaccel cuda -hwaccel_output_format cuda -hwaccel_device 0 '
              f'-r 24000/1001 -i pic2x\\%6d.jpg -vf "hwdownload,format=nv12" -c copy -c:v:0 hevc_nvenc -profile:v '
              f'main10 -pix_fmt p010le -rc:v:0 vbr -tune hq -preset p5 -multipass 1 -bf 4 -b_ref_mode 1 -nonref_p 1 '
              f'-rc-lookahead 75 -spatial-aq 1 -aq-strength 8 -temporal-aq 1 -cq 21 -qmin 1 -qmax 99 -b:v:0 20M '
              f'-maxrate:v:0 40M -gpu 0 -r 24000/1001 output.mkv')

    print('\n\nCleaning up...')
    shutil.rmtree('pic1x')
    shutil.rmtree('pic2x')
    os.remove('audio.opus')


if __name__ == '__main__':
    start = datetime.now().timestamp()
    main()
    end = datetime.now().timestamp()
    print(f'The execution was {round(end - start, 2)} sec')
    # E:\test
    # "E:\[anti-raws]Fate Apocrypha ep.22[BDRemux].mkv"
