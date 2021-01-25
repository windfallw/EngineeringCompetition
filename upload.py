import pyboard
import time
import os


def uploadFile(src, dest=None):
    time_start = time.time()
    if dest:
        print('upload:   {0}  --------->  {1}   '.format(src, dest), end='')
        pyb.fs_put(src, dest)
    else:
        print('upload:   {0}  --------->  {0}   '.format(src), end='')
        pyb.fs_put(src, src)
    time_end = time.time()
    print('finish in {0} s'.format(time_end - time_start))


def uploadFolder(folderPath, folderDest=None):
    for filename in os.listdir(folderPath):
        if folderDest:
            src = folderPath + filename
            dest = folderDest + filename
            uploadFile(src, dest)
        else:
            src = folderPath + filename
            uploadFile(src)


device = 'bit'

if __name__ == '__main__':
    com = 'COM8'

    print('\033[1m')
    pyb = pyboard.Pyboard(com)
    pyb.enter_raw_repl()

    # pyb.fs_mkdir('py')
    print('\npy Folder')
    pyb.fs_ls('py')

    print('\nALL file')
    pyb.fs_ls('/')

    print('\nFLASH file')
    pyb.fs_ls('/flash')

    print('\n')

    # pyb.fs_cat('main.py')
    # pyb.fs_rm('config.json')

    os.chdir('main')
    # uploadFile('boot.py')
    uploadFile('main.py')

    os.chdir('py')
    # uploadFile('us100.py', 'py/us100.py')
    # uploadFile('hx711.py', 'py/hx711.py')
    # uploadFile('scales.py', 'py/scales.py')
    uploadFile('ws2812.py', 'py/ws2812.py')

    pyb.exit_raw_repl()
    pyb.close()
