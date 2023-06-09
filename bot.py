import requests as re
import telegram
from bs4 import BeautifulSoup
import time
from datetime import datetime



ID = 1410223644
main_url = "https://courson.xyz/"
bot = telegram.Bot(token='6067716718:AAHGGVsOcBJfunLopsndYz-rqP5fqipW-gU')





def get_cources():
    response = re.get(main_url+"coupons")
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find_all('a', class_='course-preview-link')

    cources = []


    for data in table:
        url = main_url + str(data['href'])
        img = data.find('img')['src']
        title = data.find('h6').text
        author = data.find('p').text.strip()
        rating = data.find('span').text
        temp = rating.split('(')
        rating_no = temp[0]
        rating_stu = int(temp[1].split(" ")[0])
        new_url = getlink(url)
        cources.append([new_url, img, title, author, rating, rating_no, rating_stu])

    return cources
        

def send_cources(li, old_data):
    for i in li:
        if i[0][0] == 1 and i[0][1] not in old_data:
            send_message(i[1], i[0][1], i[2], 1000-i[6], i[5], i[6], i[3])
        else:
            log(f"some error with url shorterner!!! for the link {i[0][1]}")
        time.sleep(60)


def getlink(url):
    status = re.get(f"https://gyanilinks.com/api?api=13dd85fde8ad9970f29b74a8b672af6cf44de39c&url={url}")
    url = status.json()["shortenedUrl"]
    sat = status.json()["status"]
    if sat == "success":
        return [1,url]
    else:
        return [0,0]

def log(text):
    url = f"https://api.telegram.org/bot6067716718:AAHGGVsOcBJfunLopsndYz-rqP5fqipW-gU/sendMessage"
    payload = {"chat_id": ID, "text": text}

    re.post(url, json=payload)



def send_message(img, url, title, rem, rat, rat_no, author):

    img_template = f'''🔰 {title}

    ⏳ FREE for: First 1000 enrolls ⚠️
    🧾 Certificate : provided 
    📖 Remaining Enrolments : {rem} ⚠️
    📶 Rating: {rat} ⭐️
    ✅ Rated by: {rat_no} students

    👤 Instructor: {author}'''

    msg_template = f'''Don't Wait, Go a head and <i>enroll</i> while the Course available for <i>free</i>. For Enrolment Click  <a href="{url}">Here</a>'''

    bot.send_photo(chat_id="@free_udemycourse_with_certificat", photo=img, caption=img_template,  parse_mode=telegram.ParseMode.HTML)
    bot.send_message(chat_id="@free_udemycourse_with_certificat", text= msg_template, parse_mode=telegram.ParseMode.HTML,disable_web_page_preview=True)

def data_log(mode, cour = None):
    if mode == 1:
        with open("log.txt", 'w') as f:
            for i in cour:
                f.write(i[0] + "\n")
    elif mode == 0:
        datas = []
        try : 
            with open("log.txt", 'r') as f:
                data = f.readlines()
                datas.append(data)
            return data
        except:
            with open("log.txt", "w") as f:
                print("log file created")
            return []


while True:
    now = datetime.now()
    min = int(now.strftime("%M"))
    if min == 0 or min == 1 or min == 59 or min == 2 or min == 45:
        logs = data_log(0)
        cour = get_cources()
        log(f"total course found : {len(cour)}")
        send_cources(cour, logs)
        data_log(1, cour)

    else:
        log(f"Going to sleep for {60-min} min")
        time.sleep((60 - min)*60)





    
