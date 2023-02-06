"""
This program upscale anime in 2x resolution and encode it to HEVC using hevc_nvenc. The program uses
ffmpeg and realcugan. You need to install them yourself and add them to PATH. Also make sure you have at least
RTX 2000 series graphics card. Average encoding time 6 hours for a single 24 minute 1080p anime episode and
200 GB of free hard disk space. The program optimized not for speed, but for quality.
"""

import os
import shutil
from datetime import datetime

# import pyqt6
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QLineEdit


# noinspection PyUnresolvedReferences
class MainWindow(QMainWindow):
    """
    Main window
    """
    def __init__(self):
        super().__init__()
        self.button_start = None
        self.output_file_name_line = None
        self.button_choose_file = None
        self.button_work_dir = None

        self.work_dir = ''
        self.file_name = ''

        self.initui()

    def initui(self):
        self.setWindowTitle('Video upscaler')
        self.setFixedSize(500, 355)

        self.button_work_dir = QPushButton(f'Select a working directory. Current path: \n{self.work_dir}', self)
        self.button_work_dir.move(20, 20)
        self.button_work_dir.resize(460, 50)
        self.button_work_dir.clicked.connect(self.open_work_dir)
        self.button_work_dir.show()

        self.button_choose_file = QPushButton(f'Select a file', self)
        self.button_choose_file.move(20, 80)
        self.button_choose_file.resize(460, 50)
        self.button_choose_file.clicked.connect(self.open_file)
        self.button_choose_file.show()

        self.output_file_name_line = QLineEdit(self)
        self.output_file_name_line.move(20, 140)
        self.output_file_name_line.resize(460, 30)
        self.output_file_name_line.setText('output.mp4')
        self.output_file_name_line.show()

        self.button_start = QPushButton('Start', self)
        self.button_start.move(20, 180)
        self.button_start.resize(460, 50)
        self.button_start.clicked.connect(self.start)
        self.button_start.show()

        self.open_work_dir()

    def open_work_dir(self):
        while self.work_dir == '':
            self.work_dir = QFileDialog.getExistingDirectory(self, 'Select a working directory')
        os.chdir(self.work_dir)
        print(f'The working directory has been changed to {self.work_dir}')
        self.button_work_dir.setText(f'Select a working directory. Current path: \n{self.work_dir}')

    def open_file(self):
        self.file_name = QFileDialog.getOpenFileName(self, 'Select a file', '', 'Video files (*.mkv *.mp4)')[0]
        if self.file_name != '':
            print(f'File selected {self.file_name}')
            self.button_choose_file.setText(f'Select a file. Current file: \n{self.file_name}')
            self.output_file_name_line.setText(self.file_name[:-4].split('/')[-1].split('\\')[-1] + '_2x.mkv')

    def start(self):
        if self.file_name == '':
            print('No file selected')
            return
        if self.work_dir == '':
            print('No working directory selected')
            return

        print('Start')
        start = datetime.now().timestamp()

        print('\n\nConverting to png...')
        s = datetime.now().timestamp()
        png1x(self.file_name)
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
        audio_encoding(self.file_name)
        e = datetime.now().timestamp()
        print(f'Converting to opus took {round(e - s, 2)} sec')

        print('\n\nEncoding to mkv...')
        s = datetime.now().timestamp()
        mkv_encoding(self.output_file_name_line.text())
        e = datetime.now().timestamp()
        print(f'Encoding to mkv took {round(e - s, 2)} sec')

        print('\n\nCleaning up...')
        os.remove('audio.opus')
        shutil.rmtree('pic2x')

        end = datetime.now().timestamp()
        print(f'Total time: {round(end - start, 2)} sec')


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
    Extract audio from source file and convert it to opus
    :param orig_path:
    :return:
    """
    os.system(f'ffmpeg -y -hide_banner -i "{orig_path}" -c:a libopus -b:a 192k -vbr 1 audio.opus')


def mkv_encoding(output: str) -> None:
    """
    Merge the JPGs and audio into a single file
    :return:
    """
    os.system(f'ffmpeg -y -hide_banner -i audio.opus -hwaccel cuda -hwaccel_output_format cuda -hwaccel_device 0 '
              f'-r 24000/1001 -i pic2x\\%6d.jpg -vf "hwdownload,format=nv12" -c copy -c:v:0 hevc_nvenc -profile:v '
              f'main10 -pix_fmt p010le -rc:v:0 vbr -tune hq -preset p5 -multipass 1 -bf 4 -b_ref_mode 1 -nonref_p 1 '
              f'-rc-lookahead 75 -spatial-aq 1 -aq-strength 8 -temporal-aq 1 -cq 21 -qmin 1 -qmax 99 -b:v:0 20M '
              f'-maxrate:v:0 40M -gpu 0 -r 24000/1001 "{output}"')


'''
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
'''


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

    '''
    start = datetime.now().timestamp()
    main()
    end = datetime.now().timestamp()
    print(f'The full execution was {round(end - start, 2)} sec')
    '''
