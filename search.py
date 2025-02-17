import json
import random
import string
import re
import sqlite3
from time import sleep
from urllib.parse import quote
import pandas as pd
from bs4 import BeautifulSoup
from requests import Session
from tqdm import tqdm
from argparse import ArgumentParser

sess = Session()
sess.trust_env = False


def get_first_page(search_string, header, st, et, rest_time=(2, 5)):
    url = (f"https://s.weibo.com/weibo?q={quote(search_string)}&typeall=1&suball=1&"
           f"timescope=custom:{st}:{et}&Refer=g")
    response = sess.get(url, headers=header, verify=True)
    assert response.status_code == 200, (
        f'[Error] Cannot retrieve the first page {url}\nResponse code {response.status_code}.')
    sleep(round(random.uniform(rest_time[0], rest_time[1]), 2))
    response = BeautifulSoup(response.text, features='html.parser')
    assert response, f'[Error] Cannot retrieve the first page {url}'
    max_page = response.find('ul', {
        'node-type': 'feed_list_page_morelist', 'action-type': 'feed_list_page_morelist'
    })
    max_page = len(max_page.find_all('li')) if max_page else 1
    return response, max_page


def get_subseq_page(search_string, header, st, et, page, rest_time=(2, 5)):
    url = (f"https://s.weibo.com/weibo?q={quote(search_string)}&typeall=1&suball=1"
           f"&timescope=custom:{st}:{et}&Refer=g&page={page}")
    response = sess.get(url, headers=header, verify=True)
    if response.status_code != 200:
        print(f"[Warning] Fail to fetch page {url}\nResponse code {response.status_code}.")
        return
    sleep(round(random.uniform(rest_time[0], rest_time[1]), 2))
    response = BeautifulSoup(response.text, features='html.parser')
    if not response:
        print(f"[Warning] Fail to parse page {url}")
        return
    return response


def get_posts(web_text, header, db, table, rest_time=(2, 5)):
    posts = web_text.find_all('div', {
        'class': 'card-wrap', 'action-type': 'feed_list_item'})
    posts_df = []
    for post in posts:
        attributes = dict()
        try:
            attributes['avatar'] = post.find('div', {
                'class': 'avator'}).find('img').get('src')
        except AttributeError:
            pass
        try:
            attributes['nickname'] = post.find('a', {'class': 'name'}).get('nick-name')
        except AttributeError:
            pass
        try:
            # profile https://weibo.com/u/$user_id
            attributes['user_id'] = post.find('a', {
                'class': 'name'}).get('href').split('/')[-1].split('?')[0]
        except AttributeError:
            pass
        try:
            attributes['posted_time'] = post.find('a', {
                'suda-data': re.compile('wb_time')}).text.strip()
        except AttributeError:
            pass
        try:
            attributes['source'] = post.find('a', {'rel': 'nofollow'}).text.strip()
        except AttributeError:
            pass
        try:
            # post https://weibo.com/$user_id/$weibo_id
            attributes['weibo_id'] = post.find('a', text=re.compile('复制微博地址')).get(
                '@click', '').split('/')[-1].split('?')[0]
        except AttributeError:
            pass
        try:
            unfold_link = post.find('a', {'action-type': "fl_unfold"})
            if unfold_link and 'weibo_id' in attributes.keys():
                response = sess.get(
                    url="https://weibo.com/ajax/statuses/longtext", headers=header,
                    verify=True, params={'id': attributes['weibo_id']})
                sleep(round(random.uniform(rest_time[0], rest_time[1]), 2))
                if response.status_code == 200:
                    attributes['content'] = response.json().get('data').get('longTextContent')
        except AttributeError:
            pass
        if 'content' not in attributes.keys():
            try:
                attributes['content'] = post.find('p', {
                    'class': 'txt', 'node-type': 'feed_list_content'}).text.strip()
                attributes['content'] = re.sub('\u200b', '', attributes['content'])
                attributes['content'] = re.sub('\ue627', '', attributes['content'])
            except AttributeError:
                pass
        # SQLite 3 doesn't support list
        # try:
        #     attributes['images'] = [x.get('src') for x in post.find('div', {
        #         'node-type': 'feed_list_media_prev'}).find_all('img')]
        # except AttributeError:
        #     pass
        try:
            reposts = post.find('a', {'action-type': 'feed_list_forward'}).text.strip()
            if reposts == "转发":
                attributes['reposts'] = 0
            elif "万" in reposts:
                attributes['reposts'] = int(float(reposts) * 10000)
            else:
                attributes['reposts'] = int(reposts)
        except (AttributeError, ValueError):
            pass
        try:
            comments = post.find('a', {'action-type': 'feed_list_comment'}).text.strip()
            if comments == "评论":
                attributes['comments'] = 0
            elif "万" in comments:
                attributes['comments'] = int(float(comments) * 10000)
            else:
                attributes['comments'] = int(comments)
        except AttributeError:
            pass
        try:
            likes = post.find('span', {'class': 'woo-like-count'}).text.strip()
            attributes['likes'] = "0" if likes == "赞" else likes
        except AttributeError:
            pass
        posts_df.append(attributes)
    posts_df = pd.DataFrame(
        data=posts_df,
        columns=['avatar', 'nickname', 'user_id', 'posted_time', 'source', 'weibo_id',
                 'content', 'reposts', 'comments', 'likes'])
    c = sqlite3.connect(db)
    posts_df.to_sql(table, c, if_exists='append', index=False)
    c.close()


def search(db, query, start_time, end_time, max_page=None):
    table = ''.join(random.choice(string.ascii_letters) for _ in range(16))
    meta = pd.DataFrame([{'query': query, 'start_time': start_time, 'end_time': end_time,
                          'table': table}])
    c = sqlite3.connect(db)
    meta.to_sql(name='search', con=c, index=False, if_exists='append')
    c.close()

    cookies = pd.read_csv("raw/cookies.csv")
    cookies = [f"{row['name']}={row['value']}" for _, row in cookies.iterrows()]
    cookies = '; '.join(cookies)
    with open("scripts/_https_header.json") as f:
        chrome_122 = json.load(f)
    chrome_122['Cookies'] = cookies
    pbar = tqdm(total=max_page)
    response, existed_page = get_first_page(
        search_string=query, header=chrome_122, st=start_time, et=end_time)
    if response:
        get_posts(db=db, table=table, header=chrome_122, web_text=response)
    pbar.update(1)

    # reset max page
    if max_page:
        max_page = min(max_page, existed_page)
    else:
        max_page = existed_page
    pbar.total = max_page
    pbar.refresh()

    for page in range(2, max_page + 1):
        response = get_subseq_page(search_string=query, header=chrome_122, st=start_time,
                                   et=end_time, page=page)
        if response:
            get_posts(db=db, table=table, header=chrome_122, web_text=response)
        pbar.update(1)
    pbar.close()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--db', type=str, default='./posts.db',
                        help='The path of the database, where to store the cookies and '
                             'fetched posts. If blank, data is saved at posts.db of this '
                             'program\'s root directory.')
    parser.add_argument('--query', type=str,
                        help='Search query submitted to https://weibo.com All posts '
                             'containing this string will be recorded, 50 pages at most.')
    parser.add_argument('--start_time', type=str,
                        help='Format code: https://docs.python.org/3/library/datetime.html'
                             '#strftime-and-strptime-format-codes\n'
                             'Posts from this hour will be collected. The time zone is the '
                             'same as https://weibo.com '
                             'server. Date format is \'%Y-%m-%d-%H\'.')
    parser.add_argument('--end_time', type=str,
                        help='Posts till this hour will be collected. The format is the same '
                             'as \'start_time\'.')
    parser.add_argument('--max_page', type=int,
                        help='The maximum page to collect. If existed pages are less than '
                             'this number, the result will be fewer.')
    command, _ = parser.parse_known_args()
    search(**vars(command))
