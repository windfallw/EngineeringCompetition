# EngineeringCompetition

工训赛-智能分类垃圾桶（硬件）

止步于校赛 🙂

![demo video](sources/readme/demo.gif)

![demo jpg](sources/readme/demo.jpg)

## 说明

此仓库主要为硬件端部分

`STM32F407VGT6`做主控连接了

- 4个`US100`超声波测距模块
- `WS2812` RGB 灯环
- 霍尔传感器
- `HX711` + 5KG 压力传感器
- 连接到树莓派串口
- (可选) 二个`NEMA17`电机，驱动板用`A4988`或者`DRV8825`

MCU通过串口跟树莓派交互, 传输协议是自定的附带CRC32校验。

因为后期时间太赶，通过树莓派控制STM32在控制电机太麻烦了直接把电机部分接到了树莓派上。

`STM32F407VGT6`的`MicroPython`固件需要自己编译 ( 协程加多线程用起来特爽

使用了好多开源库在此表示感谢。

- [micropython-ws2812](https://github.com/JanBednarik/micropython-ws2812)
- [micropython-hx711](https://github.com/SergeyPiskunov/micropython-hx711)
- [microbit_us100](https://github.com/fizban99/microbit_us100)

## 很有用的参考资料

- [MCUDEV_DEVEBOX_F407VGT6](https://github.com/mcauser/MCUDEV_DEVEBOX_F407VGT6)
- [fix the board always go in safe boot mode](https://forum.micropython.org/viewtopic.php?f=12&t=4872&start=10)
- [micropython crc32模块编译](https://forum.micropython.org/viewtopic.php?t=648)
- [Stm32 GPIO模式详解](https://www.cnblogs.com/chris-cp/p/3937762.html)
- [Pyboard基础功能-定时器](https://www.cnblogs.com/iBoundary/p/11514209.html)
- [UART lost bytes / buffer overflow issue](https://forum.micropython.org/viewtopic.php?t=6244)