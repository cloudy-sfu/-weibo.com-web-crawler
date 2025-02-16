import json
import logging
import os
import time

import pandas as pd

from winapi import select_file


def get_cookies(output_path):
    logging.info("Select \"xiaohongshu.com\" cookies file.")
    cookies_path = select_file()
    with open(cookies_path) as f:
        cookies_dict = json.load(f)
    cookies = pd.DataFrame(cookies_dict['cookies'])
    cookies.to_csv(output_path, index=False)


def check_cookies_expiry(cookies_path):
    if not os.path.isfile(cookies_path):
        return False
    cookies = pd.read_csv(cookies_path)
    if time.time() > cookies['expirationDate'].min():  # np.False_ is not False
        return False
    return True


if __name__ == '__main__':
    # guide users to get cookies
    logging.info("Select \"weibo.com\" cookies file.")
    os.makedirs("raw", exist_ok=True)
    cookies_path_ = "raw/cookies.csv"
    if not check_cookies_expiry(cookies_path_):
        get_cookies(cookies_path_)
