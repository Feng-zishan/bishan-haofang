#!/usr/bin/env python3
# 璧山好房 · 数据更新工具
# 用于合并爬虫数据 → shared/ JSON 文件

import json
import os
from datetime import datetime

SHARED_DIR = os.path.join(os.path.dirname(__file__), '..', 'shared')


def load_json(filename):
    path = os.path.join(SHARED_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filename, data):
    path = os.path.join(SHARED_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'✅ 已更新 {filename}')


def update_price_history(new_prices):
    """追加价格走势数据"""
    data = load_json('price_history.json')
    today = datetime.now().strftime('%Y-%m')

    for zone, price in new_prices.items():
        if zone not in data['history']:
            data['history'][zone] = []
        # 如果当月已有记录则更新，否则追加
        existing = [h for h in data['history'][zone] if h['date'] == today]
        if existing:
            existing[0]['avgPrice'] = price
        else:
            data['history'][zone].append({'date': today, 'avgPrice': price})

    data['lastUpdated'] = today
    save_json('price_history.json', data)


def update_loupan_list(new_loupan_list):
    """批量更新楼盘数据"""
    data = load_json('loupan_list.json')
    existing_ids = {lp['id'] for lp in data['loupanList']}

    for lp in new_loupan_list:
        if lp['id'] in existing_ids:
            # 更新已有楼盘
            for i, existing in enumerate(data['loupanList']):
                if existing['id'] == lp['id']:
                    data['loupanList'][i].update(lp)
                    break
        else:
            # 新增楼盘
            data['loupanList'].append(lp)
            existing_ids.add(lp['id'])

    data['totalCount'] = len(data['loupanList'])
    data['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')
    save_json('loupan_list.json', data)


if __name__ == '__main__':
    print('🏠 璧山好房 · 数据更新工具')
    print('==========================')
    print(f'共享数据目录：{SHARED_DIR}')
    print('用法：')
    print('  update_price_history({"璧泉街道": 6500, "绿岛新区": 7900})')
    print('  update_loupan_list([{...}])')
