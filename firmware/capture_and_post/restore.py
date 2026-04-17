## Have permission issue, even in Administrator Mode

import serial
import struct

# 设置串口参数
ser = serial.Serial('COM7', 115200, timeout=60)

while True:
    try:
        # 读取图像大小（4字节）
        length_bytes = ser.read(4)
        if len(length_bytes) < 4:
            continue

        length = struct.unpack('<I', length_bytes)[0]

        # 读取图像数据
        image_data = ser.read(length)
        if len(image_data) < length:
            continue

        # 保存图像数据到文件
        with open('received_image.jpg', 'wb') as f:
            f.write(image_data)

        print('Image received and saved.')
    except Exception as e:
        print(f"Error: {e}")
