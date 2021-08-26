import time
import calendar
import requests
import pandas as pd
import numpy as np
import datetime
import Email_Sender as es
import Report_Maker as rm
import Status_Analyzer as sa

report_start_date = '2021-04-12 08:00:00'
report_end_date = '2021-04-19 08:00:00'
# 回推報表起終點時間, 預設每周一早上八點觸發, 因應時區加八小時
report_date = datetime.datetime.now().strftime("%Y-%m-%d")
# report_start_date = (datetime.datetime.now() + datetime.timedelta(days=-7)).strftime("%Y-%m-%d 08:00:00")
start = datetime.datetime.strptime(report_start_date, '%Y-%m-%d %H:%M:%S')
# report_end_date = (datetime.datetime.now() + datetime.timedelta()).strftime("%Y-%m-%d 08:00:00")

week = str(start.isocalendar().week)
year = str(start.year)


def datetime_timestamp(dt):
    time.strptime(dt, '%Y-%m-%d %H:%M:%S')
    s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
    return int(s)


# 起始時間轉換
start_date_stamp = datetime_timestamp(report_start_date)
end_date_stamp = datetime_timestamp(report_end_date)

# Grafana資料擷取
user = 'tuser'
password = 'tuser'
ip = 'http://203.75.178.67:8080/api/datasources/proxy/1/'
# ip = 'http://10.105.1.124:8080/api/datasources/proxy/1/'
name = 'iotdbfa'
measure = 'tank'
ad = ['vpi3860', 'vpi3600', 'vpi2400']
time1 = str(start_date_stamp) + 's'  # 2021-04-19 00:00:00
time2 = str(end_date_stamp) + 's'  # 2021-04-26 00:00:00


def crawler(dbip, dbname, measurement, address, timestamp1, timestamp2):
    url = f"{dbip}query?db={dbname}&q=SELECT * FROM \"{measurement}\" WHERE \"device\"= \'{address}\' " \
          f"and time >= {timestamp1} and time <= {timestamp2}"

    return url


# DB連線
url_3800 = crawler(ip, name, measure, ad[0], time1, time2)
url_3600 = crawler(ip, name, measure, ad[1], time1, time2)
url_2400 = crawler(ip, name, measure, ad[2], time1, time2)

r_3800 = requests.get(url=url_3800, params='iotdbfa', auth=(user, password))
r_3600 = requests.get(url=url_3600, params='iotdbfa', auth=(user, password))
r_2400 = requests.get(url=url_2400, params='iotdbfa', auth=(user, password))

# 確認連線
if r_3800.status_code == 200:
    print('VPI3800連線成功')
    print("=" * 20)

if r_3600.status_code == 200:
    print('VPI3600連線成功')
    print("=" * 20)

if r_2400.status_code == 200:
    print('VPI2400連線成功')
    print("=" * 20)

js = [r_3800.json(), r_3600.json(), r_2400.json()]

# 照日期切割DF子集
# 生成週間每日日期
dates = [''] * 8
for q in range(len(dates)):
    dates[q] = (start + datetime.timedelta(days=q)).strftime("%Y-%m-%d")


def report_df(js_list, dates_list, vpi_ad):
    col = js_list["results"][0]["series"][0]["columns"]
    df = pd.DataFrame(js_list["results"][0]["series"][0]["values"], columns=col)

    columns_drop = ['DI', 'DO', 'data17', 'data18', 'data19', 'data2', 'data20', 'data21', 'data22', 'device',
                    'device_1',
                    'ice_twmp', 'liquid', 'resin_pressure', 'resin_temp', 'resin_vacuum', 'ch1', 'ch2', 'ch3', 'ch4',
                    'ch5',
                    'ch6']
    df = df.drop(columns_drop, axis=1)
    # 整理時間欄位
    df['time'] = df['time'].str.replace('T', ' ').str.replace('Z', '')
    df['time'] = pd.to_datetime(df['time'], format="%Y-%m-%d %H:%M")

    # 設置真空壓力狀態值
    vac_bins = [0, 3.5, 700, 900]
    vac_labels = [0, 1, 2]
    # vac_labels = ['low','P','high']
    df['vac_status'] = pd.cut(x=df.infusion_vacuum, bins=vac_bins, labels=vac_labels)

    pre_bins = [-np.inf, 0.003, 0.08, 6.2, np.inf]
    pre_labels = [0, 1, 2, 3]
    # pre_labels = ['buttom','dropping','rsing_start','drop_start']
    df['pre_status'] = pd.cut(x=df.infusion_pressure, bins=pre_bins, labels=pre_labels)

    # df.to_csv("test_" + vpi_ad + ".csv")

    # 生成每日稼動分析報告DF
    report_col = ["日期", "稼動率(%)", "待機率(%)", "異常率(%)", "稼動工時(分)", "待機工時(分)", "異常工時(分)", "總開機工時(分)", "備註"]
    report = pd.DataFrame(columns=report_col)
    for i in range(len(dates_list) - 1):
        dates_filtered_df = df.query("time >= '" + dates_list[i] + "' and time <='" + dates_list[i + 1] + "'")
        dates_filtered_df = dates_filtered_df.reset_index(drop=True)
        report = report.append(sa.status_analyzer(dates_filtered_df, dates_list[i]), ignore_index=True)
        # print(report)

    report.set_index("日期", inplace=True)
    # report.to_csv("report_test_" + vpi_ad + ".csv", encoding="utf_8_sig")
    return report


null_report_col = ["日期", "稼動率(%)", "待機率(%)", "異常率(%)", "稼動工時(分)", "待機工時(分)", "異常工時(分)", "總開機工時(分)", "備註"]
if js[0] != {"results": [{"statement_id": 0}]}:
    report_3800 = report_df(js[0], dates, ad[0])
    print("vpi3800分析完成")
    print("=" * 20)

else:

    report_3800 = pd.DataFrame(columns=null_report_col)
    report_3800.set_index("日期", inplace=True)
    print("vpi3800無資料")
    print("=" * 20)

if js[1] != {"results": [{"statement_id": 0}]}:
    report_3600 = report_df(js[1], dates, ad[1])
    print("vpi3600分析完成")
    print("=" * 20)

else:

    report_3600 = pd.DataFrame(columns=null_report_col)
    report_3600.set_index("日期", inplace=True)
    print("vpi3600無資料")
    print("=" * 20)

if js[2] != {"results": [{"statement_id": 0}]}:
    report_2400 = report_df(js[2], dates, ad[2])
    print("vpi2400分析完成")
    print("=" * 20)

else:

    report_2400 = pd.DataFrame(columns=null_report_col)
    report_2400.set_index("日期", inplace=True)
    print("vpi2400無資料")
    print("=" * 20)

if datetime.datetime.now().month == start.month:
    rm.weekly_report_maker(report_3800, report_3600, report_2400, report_date, year, week)
    es.email_sender(dates[0], dates[7], year, week, report_date)

# 判斷是否需要製作月報
if datetime.datetime.now().month > start.month:
    month = str(start.month)
    month_start_date = datetime.date(start.year, start.month, 1).strftime("%Y-%m-%d 08:00:00")
    month_emd_date = datetime.date(start.year, start.month + 1, 1).strftime("%Y-%m-%d 08:00:00")

    month_start = datetime.date(start.year, start.month, 1)
    monthrange = calendar.monthrange(start.year, start.month)[1]

    month_start_stamp = datetime_timestamp(month_start_date)
    month_emd_stamp = datetime_timestamp(month_emd_date)

    time1_m = str(month_start_stamp) + 's'
    time2_m = str(month_emd_stamp) + 's'

    url_3800_m = crawler(ip, name, measure, ad[0], time1_m, time2_m)
    url_3600_m = crawler(ip, name, measure, ad[1], time1_m, time2_m)
    url_2400_m = crawler(ip, name, measure, ad[2], time1_m, time2_m)

    r_3800_m = requests.get(url=url_3800_m, params='iotdbfa', auth=(user, password))
    r_3600_m = requests.get(url=url_3600_m, params='iotdbfa', auth=(user, password))
    r_2400_m = requests.get(url=url_2400_m, params='iotdbfa', auth=(user, password))

    js_m = [r_3800_m.json(), r_3600_m.json(), r_2400_m.json()]

    # 生成月間每日日期
    dates_m = [''] * monthrange
    for p in range(len(dates_m)):
        dates_m[p] = (month_start + datetime.timedelta(days=p)).strftime("%Y-%m-%d")

    if js[0] != {"results": [{"statement_id": 0}]}:
        report_3800_m = report_df(js_m[0], dates_m, ad[0])
        print("vpi3800分析完成")
        print("=" * 20)

    else:
        report_3800_m = pd.DataFrame(columns=null_report_col)
        report_3800_m.set_index("日期", inplace=True)
        print("vpi3800無資料")
        print("=" * 20)

    if js[1] != {"results": [{"statement_id": 0}]}:
        report_3600_m = report_df(js_m[1], dates_m, ad[1])
        print("vpi3600分析完成")
        print("=" * 20)

    else:
        report_3600_m = pd.DataFrame(columns=null_report_col)
        report_3600_m.set_index("日期", inplace=True)
        print("vpi3600無資料")
        print("=" * 20)

    if js[2] != {"results": [{"statement_id": 0}]}:
        report_2400_m = report_df(js_m[2], dates_m, ad[2])
        print("vpi2400分析完成")
        print("=" * 20)

    else:
        report_2400_m = pd.DataFrame(columns=null_report_col)
        report_2400_m.set_index("日期", inplace=True)
        print("vpi2400無資料")
        print("=" * 20)
    rm.monthly_report_maker(report_3800_m, report_3600_m, report_2400_m, report_date, year, month, monthrange)
    rm.weekly_report_maker(report_3800, report_3600, report_2400, report_date, year, week)
    es.email_sender_m(dates[0], dates[7], year, week, month, report_date)