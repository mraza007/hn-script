import requests as req
import pandas as pd 
import time 
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



pre = int((datetime.now() - timedelta(1)).timestamp())
today = str(datetime.today().strftime('%Y-%m-%d'))


file_loader = FileSystemLoader('.')
env = Environment(loader=file_loader)
template = env.get_template('index.html')


story_titles = []
story_links = []
story_comments = []


def hn_links():
    url = req.get('https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty').json()
    links = []
    for u in url:
        links.append(f'https://hacker-news.firebaseio.com/v0/item/{u}.json?print=pretty')
    return links

links = hn_links()

for link in links:
    url = req.get(link).json()
    if url['score'] > 25 and url['time'] > pre and 'Ask' in url['title']:
        story_titles.append(url['title'])
        story_links.append(f"https://news.ycombinator.com/item?id={url['id']}")
        story_comments.append(f"https://news.ycombinator.com/item?id={url['id']}")
    elif url['score'] > 25 and url['time'] > pre:
        story_titles.append(url['title'])
        story_links.append(url['url'])
        story_comments.append(f"https://news.ycombinator.com/item?id={url['id']}")


print(len(story_links))
print(len(story_titles))

def json_data(l1,l2,l3):
    data = pd.DataFrame({
        'story_title':l1,
        'story_link':l2,
        'story_comment':l3
    })
    api_data = json.loads(data.to_json(orient='records'))
    return api_data



output = template.render(json_data=json_data(story_titles,story_links,story_comments))



def mail_server(send_to,send_from,pas,html_msg):
    msg = MIMEMultipart('alternative')
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"HackerNews Digest {today}"
    msg['From'] = send_from
    msg['To'] = send_to
    html = f"""\
    {html_msg}"""
    html_part = MIMEText(html, 'html')
    msg.attach(html_part)
    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    mail.login(send_from, pas)
    mail.sendmail(send_from, send_to, msg.as_string())
    mail.quit()
