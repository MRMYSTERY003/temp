import requests as re
import telegram
from bs4 import BeautifulSoup
import time
from datetime import date
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot


ID = 1410223644
main_url = "https://answersq.com/udemy-paid-courses-for-free-with-certificate/"
bot = telegram.Bot(token="6067716718:AAHGGVsOcBJfunLopsndYz-rqP5fqipW-gU")


def gettime():
    res = re.get("http://worldtimeapi.org/api/timezone/Asia/Kolkata").json()
    datetime = res["datetime"].split(":")

    return int((datetime[0].split("T")[1])), int(datetime[1])


def get_cource_links():
    response = re.get(main_url)
    soup = BeautifulSoup(response.text, "html.parser")  # elementor-widget-wrap
    table = soup.find_all("div", class_="elementor-widget-wrap")
    links = []
    for i in table:
        l = i.find_all("a")
        if len(l) != 0:
            for link in l:
                if link["href"].startswith("https://www.udemy.com/course/"):
                    links.append(link["href"])

    return links


def get_course_info(link):
    res = re.get(link)
    soup = BeautifulSoup(res.text, "html.parser")
    img = soup.find("span", class_="intro-asset--img-aspect--3fbKk").find("img")["src"]
    info = list(soup.find("div", class_="ud-text-sm clp-lead"))

    title = info[0].text
    rating_and_studenst = info[2].text.split(" ")
    rating = rating_and_studenst[1]
    students = rating_and_studenst[-2].split(")")[-1]
    auther = info[3].text

    return title, img, rating, students, auther


def send_cources(li, old_data):
    for i in li:
        if i[0][0] == 1 and i[0][1] not in old_data:
            send_message(i[1], i[0][1], i[2], 1000 - i[6], i[5], i[6], i[3])
        else:
            log(f"some error with url shorterner!!! for the link {i[0][1]}")
        time.sleep(120)


def getlink(url):
    status = re.get(
        f"https://gplinks.in/api?api=b7932b0e8d28f1b95387b0d195c2e4888f119bae&url={url}"
    )
    url = status.json()["shortenedUrl"]
    sat = status.json()["status"]
    if sat == "success":
        return [1, url]
    else:
        return [0, 0]


def log(text):
    url = f"https://api.telegram.org/bot6067716718:AAHGGVsOcBJfunLopsndYz-rqP5fqipW-gU/sendMessage"
    payload = {"chat_id": ID, "text": text}

    re.post(url, json=payload)


def send_message(img, url, title, rating, rating_no, author):
    button = InlineKeyboardButton(text="Click to Register", url=url)

    keyboard = InlineKeyboardMarkup([[button]])

    img_template = f"""🔰 {title}

    ⏳ FREE for: First 1000 enrolls ⚠️
    🧾 Certificate : provided 
    📶 Rating: {rating} ⭐️
    ✅ No of Students: {rating_no} students

    👤 Instructor: {author}"""

    bot.send_photo(
        chat_id="@free_udemycourse_with_certificat",
        photo=img,
        caption=img_template,
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=keyboard,
    )


def data_log(mode, cour=None):
    if mode == 1:
        with open("log.txt", "w") as f:
            for i in cour:
                print(i[0])
                f.write(str(i[0][1]) + "\n")
    elif mode == 0:
        try:
            with open("log.txt", "r") as f:
                data = f.readlines()
                return [i.replace("\n", "") for i in data]
        except Exception as e:
            with open("log.txt", "w") as f:
                print("log file created")
                print(e)
            return []


def getdata(path, mode, data=""):
    """1- read one,

    0 - write one

    11 - read multiple

    2 - write multiple

    22 - append"""
    try:
        if mode == 1:  # read single line
            with open(path, "r") as f:
                data = f.readline()
                return data
        if mode == 0:  # write single line
            with open(path, "w") as f:
                f.writeline(data)
    except:
        with open(path, "w") as f:
            f.write(str(data))
    try:
        if mode == 11:  # read multiple line
            with open(path, "r") as f:
                data = f.readlines()
                data = [i.replace("\n", "") for i in data]
                return data
        if mode == 2:  # write multiple line
            with open(path, "w") as f:
                for i in data:
                    f.write(i + "\n")
        if mode == 22:  # append
            with open(path, "a") as f:
                f.write(data + "\n")
    except:
        print("error")
        with open(path, "w") as f:
            f.write(str(data))


def one_startup():
    writtern_date = getdata("flag.txt", 1, date.today())
    if writtern_date != str(date.today()):
        links = get_cource_links()
        log("totoal couses found: " + str(len(links)))
        getdata("links.txt", 2, links)
        print("linkes file updated!!")
        log("linkes file updated!!")
        getdata("flag.txt", 0, str(date.today()))
        sent_links = getdata("send links.txt", 0)

    else:
        links = getdata("links.txt", 11)
        sent_links = getdata("send links.txt", 11)

    return links, sent_links


data = one_startup()


def send_cources(links, old_links):
    for i in links:
        if i not in old_links:
            info = get_course_info(i)
            sh_url = getlink(i)
            if sh_url[0] == 1:
                send_message(info[1], sh_url[1], info[0], info[2], info[3], info[4])
                getdata("send links.txt", 22, i)
            else:
                continue


while True:
    hr, min = gettime()

    if min % 10 == 0:
        send_cources(data[0], data[1])
    else:
        sleep_time = 10 - (min % 10)
        time.sleep(sleep_time)

