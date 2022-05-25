import requests
from bs4 import BeautifulSoup
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import datetime
import sqlite3
import pandas as pd

current_date = datetime.datetime.now()
gmail_address = 'marcin.automatyzacje@gmail.com'
password = 'yt5'

title = []
date = []
comment = []

def send_email_alert_new():
    subject = f'TOREBKA JEST TAŃSZA!!!!!!!!!!!!!!!!'

    msg = MIMEMultipart()
    msg['From'] = gmail_address
    msg['To'] = gmail_address
    msg['Subject'] = subject

    body = f'https://www.eobuwie.com.pl/torebka-guess-cessily-ev-hwev76-79110-bla.html?utm_source=rtbhouse&utm_medium=retargeting&utm_campaign=rtbhouse-retargeting'
    msg.attach(MIMEText(body, 'plain'))

    part = MIMEBase('application', 'octet-stream')

    text = msg.as_string()

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(gmail_address, password)
    server.sendmail(gmail_address, gmail_address, text)
    server.quit()


def input_to_database(current_date, product_name, product_price_current, product_price_old, product_amount, product_promo_text, supermarket_name):
    con = sqlite3.connect('PRODUCTS_SUPERMARKET.db')
    cur = con.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS PRODUCTS
                (
                current_date default timestamp,
                product_name text,
                product_price_current float,
                product_price_old float,
                product_amount text,
                product_promo_text text,
                supermarket_name text
                 )
                 ''')

    cur.execute('INSERT INTO PRODUCTS VALUES (?, ?, ?, ?, ?, ?, ?)', (current_date, product_name, product_price_current, product_price_old, product_amount, product_promo_text, supermarket_name))
    con.commit()
    con.close()


def scrap_products_biedronka_links():
    site = f'https://www.biedronka.pl/pl/nowa-oferta'

    page = requests.get(site)

    if page.status_code == 200:

        soup = BeautifulSoup(page.content, "html.parser")

        for linki in soup.find_all('a', class_='btn more'):
            link = linki["href"]

            if link not in "https":
                scrap_products_biedronka(link)


def scrap_products_biedronka(link):
    print(f"download products - current link: {link}")
    site = f'https://www.biedronka.pl' + link
    supermarket_name = 'Biedronka'
    try:
        page = requests.get(site)

        if page.status_code == 200:

            soup = BeautifulSoup(page.content, "html.parser")

            for linki in soup.find_all('href'):
                print(linki)

            for products_seq in soup.findAll("div", class_="productsimple-default"):
                product_name = products_seq.find("h4", class_="tile-name").text
                product_price_current = float(products_seq.find("span", class_="pln").text.strip() + '.' + products_seq.find("span", class_="gr").text.strip())
                product_amount = products_seq.find("span", class_="amount").text.strip()

                try:
                    product_price_old = float(products_seq.find("span", class_="price-old").text.strip())
                except:
                    product_price_old = 0.00

                try:
                    product_promo_text = products_seq.find("span", class_="product-promo-text").text.strip()
                except:
                    product_promo_text = ''

                input_to_database(current_date, product_name, product_price_current, product_price_old, product_amount, product_promo_text, supermarket_name)

        else:
            print(f'site is not respond!')


    except Exception as e:
        print(f'błąd: {e}')
        time.sleep(5)

# data = ({"download_date": date,"product_name": product_name, "product_price": product_price_current, "product_price_old": product_price_old, "amount": product_amount, "promo_text": product_promo_text})
# result = pd.DataFrame(data=data).to_excel("info_giełdowe.xlsx", index=False)

scrap_products_biedronka_links()