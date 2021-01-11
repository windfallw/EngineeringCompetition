# This file is executed on every boot (including wake-boot from deepsleep)
import micropython
import machine
import pyb
import gc

micropython.alloc_emergency_exception_buf(100)  # 设置紧急情况下的（栈溢出，普通RAM不足等）保险RAM分配，使在紧急情况下仍有RAM可用。
machine.freq(168000000)  # 设置CPU频率为240MHz
gc.enable()  # 自动回收内存碎片

pyb.main('main.py')

# https://docs.micropython.org/en/latest/library/pyb.html#pyb.usb_mode
# pyb.usb_mode('VCP') 仅串口模式，默认串口加硬盘挂载'VCP+MSC'

print(pyb.usb_mode())
