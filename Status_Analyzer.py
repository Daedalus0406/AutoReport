import pandas as pd


# 製程階段判斷
# 製程開始/抽真空
def status_analyzer(filtered_df, start_date):
    cycle_col = ["vac_pump_time", "vac_pump_idx", "vac_stable_time", "vac_stable_idx", "pre_rise_time", "pre_rise_idx",
                 "pre_stable_time", "pre_stable_idx", "pre_relief_time", "pre_relief_idx", "pro_end_time",
                 "pro_end_idx",
                 "running_time"]
    cycle = pd.DataFrame(columns=cycle_col)
    cycle_temp = [0] * len(cycle_col)
    flag = 0
    df_len = len(filtered_df.index) - 1
    # print(filtered_df)

    for i, ds_temp in filtered_df.iterrows():
        if i + 1 <= df_len:
            ds_temp_next = filtered_df.loc[i + 1, ["time", "vac_status", "pre_status"]]
            # print(ds_temp)
            # 第一筆資料判斷
            if flag == 0 and i == 0:
                if ds_temp['vac_status'] == 1:  # 抽真空
                    flag == 1
                    # print("抽真空", ds_temp["time"])
                    cycle_temp[0], cycle_temp[1] = ds_temp["time"], i

                elif ds_temp['vac_status'] == 0 and ds_temp_next['vac_status'] == 0:  # 真空維持
                    # print("真空維持", ds_temp["time"])
                    flag = 2
                    cycle_temp[2], cycle_temp[3] = ds_temp["time"], i

                elif ds_temp['pre_status'] == 0 and ds_temp_next['pre_status'] > ds_temp['pre_status']:  # 加壓開始
                    # print("加壓開始", ds_temp["time"])
                    flag = 3
                    cycle_temp[4], cycle_temp[5] = ds_temp["time"], i

                elif ds_temp['pre_status'] == 3:  # 加壓維持
                    # print("加壓維持", ds_temp["time"])
                    flag = 4
                    cycle_temp[6], cycle_temp[7] = ds_temp["time"], i

                elif ds_temp['pre_status'] == 3 and ds_temp_next['pre_status'] == 2:  # 第一次洩壓
                    # print("初次洩壓", ds_temp["time"])
                    flag = 5
                    cycle_temp[8], cycle_temp[9] = ds_temp["time"], i

                elif ds_temp_next['pre_status'] <= 2:  # 洩壓中
                    # print("洩壓中", ds_temp["time"])
                    flag = 5
                    cycle_temp[8], cycle_temp[9] = ds_temp["time"], i

                elif ds_temp['pre_status'] == 2 and ds_temp_next['pre_status'] == 1:  # 完全洩壓/製程結束
                    # print("製程結束", ds_temp["time"])
                    flag = 6
                    cycle_temp[10], cycle_temp[11] = ds_temp["time"], i

            # 製程開始
            elif flag == 0 and ds_temp['vac_status'] == 2 and ds_temp_next['vac_status'] == 1:
                # print("製程開始", ds_temp["time"])
                flag = 1
                cycle_temp[0], cycle_temp[1] = ds_temp["time"], i

            # 真空維持
            elif flag == 1 and ds_temp['vac_status'] == 0 and ds_temp_next['vac_status'] == 0:
                # print("真空維持", ds_temp["time"])
                flag = 2
                cycle_temp[2], cycle_temp[3] = ds_temp["time"], i
                cycle_temp[12] = (pd.to_datetime(cycle_temp[2]) - pd.to_datetime(cycle_temp[0])).total_seconds() / 60
            # 加壓開始
            elif flag == 2 and ds_temp['pre_status'] == 0 and ds_temp_next['pre_status'] > ds_temp['pre_status']:
                # print("加壓開始", ds_temp["time"])
                flag = 3
                cycle_temp[4], cycle_temp[5] = ds_temp["time"], i
                cycle_temp[12] = cycle_temp[12] + (
                        (pd.to_datetime(cycle_temp[4]) - pd.to_datetime(cycle_temp[2])).total_seconds() / 60)
            # 加壓維持
            elif flag == 3 and ds_temp['pre_status'] == 3:
                # print("加壓維持", ds_temp["time"])
                flag = 4
                cycle_temp[6], cycle_temp[7] = ds_temp["time"], i
                cycle_temp[12] = cycle_temp[12] + (
                        (pd.to_datetime(cycle_temp[6]) - pd.to_datetime(cycle_temp[4])).total_seconds() / 60)
            # 第一次洩壓
            elif flag == 4 and ds_temp['pre_status'] == 3 and ds_temp_next['pre_status'] == 2:
                # print("初次洩壓", ds_temp["time"])
                flag = 5
                cycle_temp[8], cycle_temp[9] = ds_temp["time"], i
                cycle_temp[12] = cycle_temp[12] + (
                        (pd.to_datetime(cycle_temp[8]) - pd.to_datetime(cycle_temp[6])).total_seconds() / 60)
            # 完全洩壓/製程結束
            elif flag == 5 and ds_temp['pre_status'] == 2 and ds_temp_next['pre_status'] == 1:
                # rint("製程結束", ds_temp["time"])
                flag = 6
                cycle_temp[10], cycle_temp[11] = ds_temp["time"], i
                cycle_temp[12] = cycle_temp[12] + (
                        (pd.to_datetime(cycle_temp[10]) - pd.to_datetime(cycle_temp[8])).total_seconds() / 60)

            # 重設flag
            if flag == 6:
                # print("稼動工時 : %.1f 分鐘" % cycle_temp[12])
                # print("=" * 20)
                cycle = cycle.append(pd.Series(cycle_temp, index=cycle_col), ignore_index=True)
                cycle_temp = [0] * 13
                flag = 0

        elif flag != 0:
            l = (flag - 1) * 2
            # print(cycle_temp[l])
            cycle_temp[12] = cycle_temp[12] + (
                        (pd.to_datetime(ds_temp["time"]) - pd.to_datetime(cycle_temp[l])).total_seconds() / 60)
            # print(cycle_temp)
            # print("稼動工時 : %.1f 分鐘" % cycle_temp[12])
            # print("=" * 20)
            cycle = cycle.append(pd.Series(cycle_temp, index=cycle_col), ignore_index=True)
            break

        elif flag == 0:
            cycle_temp[12] = 0
            cycle = cycle.append(pd.Series(cycle_temp, index=cycle_col), ignore_index=True)
            break

    # cycle.to_csv("cycle_test.csv")

    # print("%s 至 %s " % (filtered_df.time[0], filtered_df.time[df_len]))

    total_time = 1440
    # print("總開機時間 : %.1f 分鐘" % total_time)

    total_run_time = cycle.loc[:, "running_time"].sum()
    total_run_time = round(total_run_time, 1)
    # print("總稼動工時 : %.1f 分鐘" % total_run_time)

    total_standby_time = total_time - total_run_time
    total_standby_time = round(total_standby_time, 1)
    # print("總待機時間 : %.1f 分鐘" % total_standby_time)

    run_time_ratio = (total_run_time / total_time) * 100
    run_time_ratio = round(run_time_ratio, 1)
    # print("稼動率 : %.1f" % run_time_ratio)

    standby_time_ratio = (total_standby_time / total_time) * 100
    standby_time_ratio = round(standby_time_ratio, 1)
    # print("待機率 : %.1f" % standby_time_ratio)
    # print("=" * 20)

    report_dict = {"日期": start_date, "稼動率(%)": run_time_ratio, "待機率(%)": standby_time_ratio, "異常率(%)": 0,
                   "稼動工時(分)": total_run_time, "待機工時(分)": total_standby_time, "異常工時(分)": 0, "總開機工時(分)": 1440}
    # print("製程分析結束")
    # print("=" * 20)
    return report_dict

