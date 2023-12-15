import serial
import math
import time
from matplotlib import pyplot as plt
import pyautogui


def calculate_coordinates(length, angle_degrees, mode=1):
    """mode = 1 for single otherwise multiple"""
    x = []
    y = []
    if mode != 1:
        for index in range(len(length)):
            x.append(length[index] * math.cos(angle_degrees[index]))
            y.append(length[index] * math.sin(angle_degrees[index]))

        return x, y
    else:
        return length * math.cos(angle_degrees), length * math.sin(angle_degrees)


def cvt(l, d):
    x = l * math.cos(d)
    y = l * math.sin(d)
    return x, y


class LidarData:
    def __init__(
        self,
        FSA,
        LSA,
        CS,
        Speed,
        TimeStamp,
        Confidence_i,
        Angle_i,
        Distance_i,
        Angle_norm,
        Distance_norm,
    ):
        self.FSA = FSA
        self.LSA = LSA
        self.CS = CS
        self.Speed = Speed
        self.TimeStamp = TimeStamp

        self.Confidence_i = Confidence_i
        self.Angle_i = Angle_i
        self.Distance_i = Distance_i
        self.Angle_norm = Angle_norm
        self.Distance_norm = Distance_norm


def CalcLidarData(str):
    str = str.replace(" ", "")

    minus_311 = (360 - 31.1) * math.pi / 180
    plus_311 = 31.1 * math.pi / 180

    Speed = int(str[2:4] + str[0:2], 16) / 100
    FSA = float(int(str[6:8] + str[4:6], 16)) / 100
    LSA = float(int(str[-8:-6] + str[-10:-8], 16)) / 100
    TimeStamp = int(str[-4:-2] + str[-6:-4], 16)
    CS = int(str[-2:], 16)

    Confidence_i = list()
    Angle_i = list()
    Distance_i = list()
    Angle_norm = list()
    Distance_norm = list()

    count = 0
    if LSA - FSA > 0:
        angleStep = float(LSA - FSA) / (12)

    else:
        angleStep = float((LSA + 360) - FSA) / (12)

    counter = 0
    circle = lambda deg: deg - 360 if deg >= 360 else deg
    for i in range(0, 6 * 12, 6):
        Distance_i.append(
            int(str[8 + i + 2 : 8 + i + 4] + str[8 + i : 8 + i + 2], 16) / 10
        )
        Confidence_i.append(int(str[8 + i + 4 : 8 + i + 6], 16))
        Angle_i.append(
            circle(angleStep * counter + FSA) * math.pi / 180.0
        )  # deg to rad
        counter += 1

    # for i in Angle_i:
    #     if i <= plus_311 or i >= minus_311:
    #         if Distance_i[Angle_i.index(i)] >= 50:
    #             Distance_norm.append(Distance_i[Angle_i.index(i)])
    #             Angle_norm.append(i)

    # for i in Angle_i:
    #     if i <= plus_311:
    #         Distance_norm.append(Distance_i[Angle_i.index(i)])
    #         Angle_norm.append(0.5 + (i / plus_311) * 0.5)

    #     elif i >= minus_311:
    #         Distance_norm.append(Distance_i[Angle_i.index(i)])
    #         Angle_norm.append(((i - minus_311) / plus_311) * 0.5)
    # print(i, (i / (2*math.pi)) * 0.5, Distance_i[Angle_i.index(i)])

    # Angle_norm = (np.array(Angle_norm) + plus_311).tolist()
    # if len(Angle_norm) >= 2:
    #     # Angle_norm = (1 - (np.array(Angle_norm) - np.min(Angle_norm)) / (np.max(Angle_norm) - np.min(Angle_norm))).tolist()
    #     # Angle_norm = ((np.array(Angle_norm) - np.min(Angle_norm)) / (np.max(Angle_norm) - np.min(Angle_norm))).tolist()
    #     Angle_norm = (1 - (np.array(Angle_norm) - plus_311) / (minus_311 - plus_311)).tolist()

    lidarData = LidarData(
        FSA,
        LSA,
        CS,
        Speed,
        TimeStamp,
        Confidence_i,
        Angle_i,
        Distance_i,
        Angle_norm,
        Distance_norm,
    )
    return lidarData


class LidarNormData:
    def __init__(self, angles_norm, distances_norm, angles, distances):
        self.angles_norm = angles_norm
        self.distances_norm = distances_norm
        self.angles = angles
        # self.angles = [int(i * 100) for i in angles]
        self.distances = distances


def lidarfunc(lidar_time):
    ser = serial.Serial(
        port="COM7", baudrate=230400, timeout=5.0, bytesize=8, parity="N", stopbits=1
    )

    tmpString = ""
    lines = list()
    angles = list()
    distances = list()
    angles_norm = list()
    distances_norm = list()

    i = 0
    while True:
        loopFlag = True
        flag2c = False

        if i % 40 == 39:
            lidarnormdata = LidarNormData(
                angles_norm, distances_norm, angles, distances
            )
            return lidarnormdata
            angles.clear()
            distances.clear()
            i = 0

        while loopFlag:
            b = ser.read()
            tmpInt = int.from_bytes(b, "big")  # Transfer bit to INT

            if tmpInt == 0x54:
                tmpString += b.hex() + " "
                flag2c = True
                continue

            elif tmpInt == 0x2C and flag2c:
                tmpString += b.hex()
                if not len(tmpString[0:-5].replace(" ", "")) == 90:
                    tmpString = ""
                    loopFlag = False
                    flag2c = False
                    continue

                lidarData = CalcLidarData(tmpString[0:-5])

                angles.extend(lidarData.Angle_i)
                distances.extend(lidarData.Distance_i)
                angles_norm.extend(lidarData.Angle_norm)
                distances_norm.extend(lidarData.Distance_norm)

                tmpString = ""
                loopFlag = False
            else:
                tmpString += b.hex() + " "

            flag2c = False

        i += 1
        lidar_time -= 1

    ser.close()


fig, ax = plt.subplots()

display_w = 1370
display_h = 770

touch_duration_threshold = 0.5


timer = 0
detected = 0
not_detected = 0


# def box(x, y):
#     xmi = 5
#     xma = 50
#     ymi = 5
#     yma = 25
#     xavg = 0
#     yavg = 0
#     c = 0
#     for num, i in enumerate(x):
#         if (xma + (2 * xmi) > i > xmi) and (yma + (2 * ymi) > y[num] > ymi):
#             xavg += i
#             yavg += y[num]
#             c += 1

#     if xavg != 0:
#         return (((xavg / c) / (xmi + xma)) - (xmi / (xmi + xma))) * display_w, (
#             ((yavg / c) / (ymi + yma)) - (ymi / (ymi + yma))
#         ) * display_h

#     return None


def box(x, y):
    xmi = -10
    xma = -1 * xmi

    ymi = 3
    yma = 20

    c = 0

    xavg = 0
    yavg = 0
    for num, i in enumerate(x):
        if yma + (2 * ymi) >= y[num] and y[num] >= ymi:
            if 0 < i < xma:
                xavg += i
                yavg += y[num] + ymi
                c += 1

            elif 0 >= i > xmi:
                xavg += i
                yavg += y[num] + ymi
                c += 1

    if xavg != 0:
        return (
            ((xavg / c) / (-1 * xmi + xma)) - (xmi / (-1 * xmi + xma))
        ) * display_w, (
            ((yavg / c) / (ymi + yma)) - ((2 * ymi) / (ymi + yma))
        ) * display_h

    return None


detected = True

while 1:
    lidar_data = lidarfunc(10)
    angles = lidar_data.angles
    distance = lidar_data.distances
    ang_p = []
    dis_p = []
    ax.clear()
    x, y = [], []

    for num, i in enumerate(angles):
        if i >= 0 and i <= 1.9:
            res = calculate_coordinates(distance[num], i, mode=1)
            x.append(res[0])
            y.append(res[1])

    # ax.scatter(x, y, s=2)
    # plt.pause(0.03)
    v = None
    for i in range(len(x)):
        v = box(x, y)

    if v is not None:
        print(v)

        if detected:
            timer = time.time()
            detected = False
    else:
        if detected == False:
            tt = time.time() - timer
            if tt < 0.4:
                print("click")
                pyautogui.click(button="left")
            detected = True

    # Move the mouse cursor if the coordinates are available
    if v is not None:
        pyautogui.moveTo(abs(int(v[0]) - display_w), abs(int(v[1]) - display_h))
