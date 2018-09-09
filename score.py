"""LeetCode Contest Country Scoreboard"""

import argparse

from tabulate import tabulate
from unidecode import unidecode
import grequests


BATCH_SIZE = 10
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/69.0.3497.81 Safari/537.36'}
HTTP_TIMEOUT = 10  # 10 sec

TABLE_HEADERS = ['Rank', 'Name', 'Score']

COUNTRY_FLAG_PATTERN = '/static/flags/%s.gif'
URL_PATTERN = 'https://leetcode.com/contest/api/ranking/%s/?pagination=%d'


def main():
    """Shows the scoreboard"""
    parser = argparse.ArgumentParser()
    parser.add_argument('CONTEST', help='e.g. weekly-contest-101')
    parser.add_argument('COUNTRY', help='e.g. hk')
    args = parser.parse_args()
    contest = args.CONTEST
    country_flag = COUNTRY_FLAG_PATTERN % args.COUNTRY
    data = []
    page = 1
    while True:
        res_list = []
        for _ in range(BATCH_SIZE):
            url = URL_PATTERN % (contest, page)
            res_list.append(grequests.get(url, timeout=HTTP_TIMEOUT, headers=HEADERS))
            page += 1
        res_list = grequests.map(res_list)
        done = False
        for res in res_list:
            res.raise_for_status()
            res_js = res.json()
            rank = res_js['total_rank']
            if not rank:
                done = True
                break
            for datum in rank:
                if datum['country_flag'] == country_flag:
                    data.append([datum['rank'], unidecode(datum['username']), datum['score']])
        print 'Loaded %d pages' % (page - 1)
        if done:
            break
    table = tabulate(data, headers=TABLE_HEADERS)
    print ''
    print table


if __name__ == '__main__':
    main()