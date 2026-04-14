import pandas as pd
from datetime import datetime

# 配置
DEVICES_TO_EXTRACT = ['2f59', 'ee38', '22ad', '5683', '4f53', '082c', '1af8', 'd8db']
START_DATE = '2026-02-02'
END_DATE = '2026-03-31'
PROBLEM_STATUSES = ['已审批-无效片段过长', '待审批']  # 视频有问题的状态

# 读取 QAQ.csv
print("正在读取 QAQ.csv...")
df = pd.read_csv('QAQ.csv')

# 转换日期列
df['采集日期'] = pd.to_datetime(df['采集日期'])

# 筛选条件
print(f"\n筛选条件:")
print(f"  设备: {', '.join(DEVICES_TO_EXTRACT)}")
print(f"  时间: {START_DATE} ~ {END_DATE}")
print(f"  性质: 审批状态为 {PROBLEM_STATUSES}")

# 应用筛选
df_filtered = df[
    (df['设备ID'].isin(DEVICES_TO_EXTRACT)) &
    (df['采集日期'] >= START_DATE) &
    (df['采集日期'] <= END_DATE) &
    (df['审批状态'].isin(PROBLEM_STATUSES))
].copy()

# 按日期和设备排序
df_filtered = df_filtered.sort_values(['采集日期', '设备ID'])

# 统计信息
print(f"\n筛选结果:")
print(f"  总数据行: {len(df_filtered)}")
print(f"  涉及设备: {df_filtered['设备ID'].unique().tolist()}")

# 按审批状态统计
print(f"\n按审批状态统计:")
status_counts = df_filtered['审批状态'].value_counts()
for status, count in status_counts.items():
    print(f"  {status}: {count}")

# 按设备统计
print(f"\n按设备统计:")
device_counts = df_filtered['设备ID'].value_counts().sort_index()
for device, count in device_counts.items():
    print(f"  {device}: {count}")

# 按无效原因统计
print(f"\n按无效原因统计:")
reason_counts = df_filtered[df_filtered['无效片段标记原因'].notna()]['无效片段标记原因'].value_counts()
if len(reason_counts) > 0:
    for reason, count in reason_counts.items():
        print(f"  {reason}: {count}")
else:
    print("  无具体原因标记")

# 输出到 CSV
output_filename = '8台设备问题数据_02-02到03-31.csv'
df_filtered.to_csv(output_filename, index=False, encoding='utf-8-sig')
print(f"\n✓ 已生成: {output_filename}")

# 生成每日统计
print(f"\n生成每日统计...")
daily_stats = df_filtered.groupby('采集日期').agg({
    '设备ID': 'nunique',
    '审批状态': 'count',
    '原始上送时长': 'sum',
    '无效时长': 'sum'
}).rename(columns={
    '设备ID': '涉及设备数',
    '审批状态': '数据条数',
    '原始上送时长': '总时长(分)',
    '无效时长': '无效时长(分)'
})

daily_stats_filename = '8台设备每日统计_02-02到03-31.csv'
daily_stats.to_csv(daily_stats_filename, encoding='utf-8-sig')
print(f"✓ 已生成: {daily_stats_filename}")

print(f"\n任务完成!")
