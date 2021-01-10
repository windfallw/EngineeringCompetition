# This file is executed on every boot (including wake-boot from deepsleep)
import micropython
import machine
import gc

micropython.alloc_emergency_exception_buf(100)  # 设置紧急情况下的（栈溢出，普通RAM不足等）保险RAM分配，使在紧急情况下仍有RAM可用。
machine.freq(168000000)  # 设置CPU频率为240MHz
gc.enable()  # 自动回收内存碎片
