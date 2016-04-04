# coding: utf-8

from bs4 import BeautifulSoup
import yaml, requests
import sys

MATCH_RESULT_URL = "http://www.football-lab.jp/{}/match/?year={}"
MATCH_RESULT_YEAR = '2015'

def get_target_urls():
    """
    チームリストとフットボールラボにおけるチーム名のYAMLファイルを読み込んで
    クローリング対象のURLを生成する
    """
    with open('./resources/teams.yml', 'r') as file_teams, open('./resources/fblab.yml', 'r') as file_fblab:
        teams = yaml.load(file_teams)
        fblab = yaml.load(file_fblab)
        return {t: MATCH_RESULT_URL.format(fblab['fblab'][t], MATCH_RESULT_YEAR) for t in teams['teams']}

def parse_html_text(data):
    """
    クローリングしたHTMLのテキストデータから試合結果を切り抜く関数
    """
    records = []
    html = BeautifulSoup(data, 'html.parser')
    schedule_table = html.find('table', id='schedule')
    results = schedule_table.find_all('tr')
    for r in results[1:]: # skip header
        elem = r.find_all('td')
        records.append([e.text.strip() for e in elem])
    return records

def save_results_to_csv(key, results):
    """
    クローリングしてスクレイピングしたデータをCSVで保存する関数
    保存ファイル名: ./data/{team}_{year}.csv
    """
    with open("./data/{}_{}.csv".format(key, MATCH_RESULT_YEAR), 'w') as f:
        for r in results:
            f.write(','.join(r) + '\n')

def main():
    """
    フットボールラボ（http://www.football-lab.jp/）
    から試合結果を取得してCSVに保存するバッチスクリプト
    python crontab/get_match_result_from_footballlab.py
    """
    urls = get_target_urls()
    for key, url in urls.items():
        text_data = requests.get(url).text
        results = parse_html_text(text_data)
        save_results_to_csv(key, results)

if __name__ == '__main__':
    main()
