import os
import shutil
import subprocess
import time


def main():
    print(
        "For the program to work, you need at least 200 GB for one episode of anime, and up to 1 TB for a movie.")
    print('Also make sure you have at least an RTX 2000 series graphics card.')

    work_dir = input('Enter directory: ')
    work_dir = work_dir.replace('"', '')
    work_dir = work_dir.replace("'", '')

    os.chdir(work_dir)

    orig_path = input('Enter the full path of the original file: ')
    orig_path = orig_path.replace('"', '')
    orig_path = orig_path.replace("'", '')

    print('Converting to png...')
    p1x_dir = os.path.join(work_dir, 'pic1x')
    os.mkdir(p1x_dir)
    os.system(f'ffmpeg -y -hide_banner -i {orig_path} {p1x_dir}\\%06d.png')

    print('Upscaling to 2x...')
    p2x_dir = os.path.join(work_dir, 'pic2x')
    os.mkdir(p2x_dir)
    os.system(f'realcugan -i {p1x_dir}\\%06d.png -o {p2x_dir} -n 1 -s 2 -f jpg')

    print('Converting to opus...')
    audio_path = os.path.join(work_dir, 'audio.opus')
    os.system(f'ffmpeg -y -hide_banner -i {orig_path} -c:a libopus -b:a 192k {audio_path}')

    print('Encoding to mkv...')
    os.system(f'ffmpeg -y -hide_banner -i {audio_path} -hwaccel cuda -hwaccel_output_format cuda -hwaccel_device 0 -i {p2x_dir}\\%6d.jpg -vf "hwdownload,format=nv12" -c copy -c:v:0 hevc_nvenc -profile:v main10 -pix_fmt p010le -rc:v:0 vbr -tune hq -preset p5 -multipass 1 -bf 4 -b_ref_mode 1 -nonref_p 1 -rc-lookahead 75 -spatial-aq 1 -aq-strength 8 -temporal-aq 1 -cq 21 -qmin 1 -qmax 99 -b:v:0 20M -maxrate:v:0 40M -gpu 0 -r 24000/1001 {work_dir}\\output.mkv')

    print('Cleaning up...')
    shutil.rmtree(p1x_dir)
    shutil.rmtree(p2x_dir)
    os.remove(audio_path)


if __name__ == '__main__':
    main()
    # "E:\test"
    # "E:\[anti-raws]Fate Apocrypha ep.22[BDRemux].mkv"
