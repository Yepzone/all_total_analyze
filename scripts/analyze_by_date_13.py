"""
按日期分组统计 - 13台设备版本
"""

import csv
from datetime import datetime

DEVICES_WITH_DATA = {'007e', '0af6', '23dc', '25a8', '46dd', '6bc0', '75c7', 'a37b', 'aaaa', 'abe0', 'fc2a'}

START_DATE = datetime(2026, 3, 23)
END_DATE = datetime(2026, 4, 10)

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y/%m/%d')
    except:
        return None

def get_duration_minutes(duration_str):
    if not duration_str:
        return 0.0
    try:
        return float(str(duration_str).strip().replace(' ', ''))
    except:
        return 0.0

def main():
    print("=" * 80)
    print("修正版统计：13台设备按日期分组（时长单位：分钟）")
    print("=" * 80)
    
    date_stats = {}
    
    with open('QAQ.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            device_id = row.get('设备ID', '').strip()
            
            if device_id not in DEVICES_WITH_DATA:
                continue
            
            date_str = row.get('采集日期', '')
            date = parse_date(date_str)
            if not date or date < START_DATE or date > END_DATE:
                continue
            
            # 3/23-27归为一组
            if date.month == 3 and 23 <= date.day <= 27:
                date_key = '2026-03-23~27'
            else:
                date_key = date.strftime('%Y-%m-%d')
            
            if date_key not in date_stats:
                date_stats[date_key] = {
                    'approved': 0,
                    'approved_invalid': 0,
                    'pending': 0,
                    'approved_duration': 0.0,
                    'approved_invalid_duration': 0.0,
                    'pending_duration': 0.0,
                    'invalid_duration': 0.0,
                    'valid_duration': 0.0,
                }
            
            status = row.get('审批状态', '')
            total_duration = get_duration_minutes(row.get('原始上送时长', 0))
            invalid_duration = get_duration_minutes(row.get('无效时长', 0))
            valid_duration = total_duration - invalid_duration
            
            if status == '已审批':
                date_stats[date_key]['approved'] += 1
                date_stats[date_key]['approved_duration'] += total_duration
                date_stats[date_key]['invalid_duration'] += invalid_duration
                date_stats[date_key]['valid_duration'] += valid_duration
            elif status == '已审批-无效片段过长':
                date_stats[date_key]['approved_invalid'] += 1
                date_stats[date_key]['approved_invalid_duration'] += total_duration
                date_stats[date_key]['invalid_duration'] += invalid_duration
                date_stats[date_key]['valid_duration'] += valid_duration
            elif status == '待审批':
                date_stats[date_key]['pending'] += 1
                date_stats[date_key]['pending_duration'] += total_duration
    
    # 按日期顺序排列
    date_order = ['2026-03-23~27']
    for i in range(28, 32):
        date_order.append(f'2026-03-{i:02d}')
    for i in range(1, 11):
        date_order.append(f'2026-04-{i:02d}')
    
    # 生成CSV
    csv_headers = ['日期', '已审批-有效数', '已审批-无效数', '待审批数', '总时长(分钟)', '待审批时长(分钟)', '合格时长(分钟)', '总时长(小时)', '合格时长(小时)', '合格率(%)']
    csv_rows = []
    
    total_approved = 0
    total_approved_invalid = 0
    total_pending = 0
    total_approved_duration = 0.0
    total_pending_duration = 0.0
    total_valid_duration = 0.0
    total_invalid_duration = 0.0
    
    for date_key in date_order:
        if date_key not in date_stats:
            continue
        
        stat = date_stats[date_key]
        approved = stat['approved']
        approved_invalid = stat['approved_invalid']
        pending = stat['pending']
        approved_min = stat['approved_duration']
        approved_invalid_min = stat['approved_invalid_duration']
        pending_min = stat['pending_duration']
        invalid_min = stat['invalid_duration']
        valid_min = stat['valid_duration']
        total_approved_min = approved_min + approved_invalid_min
        total_min = total_approved_min + pending_min
        
        total_approved += approved
        total_approved_invalid += approved_invalid
        total_pending += pending
        total_approved_duration += total_approved_min
        total_pending_duration += pending_min
        total_valid_duration += valid_min
        total_invalid_duration += invalid_min
        
        total_hours = total_min / 60
        valid_hours = valid_min / 60
        invalid_hours = invalid_min / 60
        # 合格率 = 有效时长 / (有效时长 + 不合格时长)
        overall_rate = (valid_min / (valid_min + invalid_min) * 100) if (valid_min + invalid_min) > 0 else 0
        
        csv_rows.append([
            date_key,
            approved,
            approved_invalid,
            pending,
            f"{total_min:.2f}",
            f"{pending_min:.2f}",
            f"{valid_min:.2f}",
            f"{total_hours:.2f}",
            f"{valid_hours:.2f}",
            f"{overall_rate:.1f}"
        ])
        
        print(f"  {date_key} - 合格{approved:3d} 不合格{approved_invalid:3d} 待审{pending:3d} 有效{valid_hours:7.2f}h 不合格{invalid_hours:7.2f}h 合格率{overall_rate:5.1f}%")
    
    # 计算总合格率
    total_duration = total_approved_duration + total_pending_duration
    overall_rate = (total_valid_duration / total_approved_duration * 100) if total_approved_duration > 0 else 0
    
    # 写入汇总行到CSV
    csv_rows.append(['合计', total_approved, total_approved_invalid, total_pending,
                     f"{total_duration:.2f}", f"{total_pending_duration:.2f}", 
                     f"{total_valid_duration:.2f}", f"{total_duration/60:.2f}", 
                     f"{total_valid_duration/60:.2f}", f"{overall_rate:.1f}"])
    
    output_csv = '13台设备统计_按日期_3月23日-4月10日_修正.csv'
    with open(output_csv, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)
        writer.writerows(csv_rows)
    print(f"\n✓ 已生成: {output_csv}")
    
    print(f"\n=== 合计 ===")
    print(f"已审批-有效: {total_approved}条")
    print(f"已审批-无效: {total_approved_invalid}条")
    print(f"待审批: {total_pending}条")
    total_duration = total_approved_duration + total_pending_duration
    print(f"总时长: {total_duration/60:.2f}小时")
    print(f"已审批总时长: {total_approved_duration/60:.2f}小时（含有效和无效）")
    print(f"待审批时长: {total_pending_duration/60:.2f}小时")
    print(f"有效（合格）时长: {total_valid_duration/60:.2f}小时")
    print(f"不合格时长: {total_invalid_duration/60:.2f}小时")
    overall_rate = (total_valid_duration / total_approved_duration * 100) if total_approved_duration > 0 else 0
    print(f"合格率: {overall_rate:.1f}%")

if __name__ == '__main__':
    main()
