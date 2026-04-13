"""
按设备分组统计 - 13台设备版本（含4台空值）
"""

import csv
from datetime import datetime

TARGET_DEVICES = ['0023', '007e', '0af6', '23dc', '25a8', '46dd', '5222', '6bc0', '75c7', 'a37b', 'aaaa', 'abe0', 'fc2a']
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
    print("修正版统计：13台设备QAQ数据（按设备分组，时长单位：分钟）")
    print("=" * 80)
    
    stats = {}
    for device in TARGET_DEVICES:
        stats[device] = {
            'approved': 0,
            'approved_invalid': 0,
            'pending': 0,
            'approved_duration': 0.0,
            'approved_invalid_duration': 0.0,
            'pending_duration': 0.0,
            'invalid_duration': 0.0,
            'valid_duration': 0.0,
            'has_data': device in DEVICES_WITH_DATA
        }
    
    with open('QAQ.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        row_count = 0
        for row in reader:
            row_count += 1
            device_id = row.get('设备ID', '').strip()
            
            if device_id not in DEVICES_WITH_DATA:
                continue
            
            date_str = row.get('采集日期', '')
            date = parse_date(date_str)
            if not date or date < START_DATE or date > END_DATE:
                continue
            
            status = row.get('审批状态', '')
            total_duration = get_duration_minutes(row.get('原始上送时长', 0))
            invalid_duration = get_duration_minutes(row.get('无效时长', 0))
            valid_duration = total_duration - invalid_duration
            
            if status == '已审批':
                stats[device_id]['approved'] += 1
                stats[device_id]['approved_duration'] += total_duration
                stats[device_id]['invalid_duration'] += invalid_duration
                stats[device_id]['valid_duration'] += valid_duration
            elif status == '已审批-无效片段过长':
                stats[device_id]['approved_invalid'] += 1
                stats[device_id]['approved_invalid_duration'] += total_duration
                stats[device_id]['invalid_duration'] += invalid_duration
                stats[device_id]['valid_duration'] += valid_duration
            elif status == '待审批':
                stats[device_id]['pending'] += 1
                stats[device_id]['pending_duration'] += total_duration
    
    print(f"✓ 读取 {row_count} 行数据\n")
    
    # 生成CSV
    csv_headers = ['设备', '已审批-有效数', '已审批-无效数', '待审批数', '总时长(分钟)', '待审批时长(分钟)', '有效时长(分钟)', '总时长(小时)', '有效时长(小时)', '合格率(%)']
    csv_rows = []
    
    total_approved = 0
    total_approved_invalid = 0
    total_pending = 0
    total_approved_duration = 0.0
    total_approved_invalid_duration = 0.0
    total_pending_duration = 0.0
    total_valid_duration = 0.0
    total_invalid_duration = 0.0
    
    for device in TARGET_DEVICES:
        stat = stats[device]
        
        if not stat['has_data']:
            # 无数据的设备显示空值
            csv_rows.append([
                device,
                '',  # 空值
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                ''
            ])
            print(f"  {device:6s} - 无数据（留空值）")
        else:
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
                device,
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
            print(f"  {device:6s} - 合格{approved:3d} 不合格{approved_invalid:3d} 待审{pending:3d} 有效{valid_hours:7.2f}h 不合格{invalid_hours:7.2f}h 合格率{overall_rate:5.1f}%")
    
    # 写入汇总行
    total_duration = total_approved_duration + total_pending_duration
    overall_rate = (total_valid_duration / total_approved_duration * 100) if total_approved_duration > 0 else 0
    csv_rows.append(['合计', total_approved, total_approved_invalid, total_pending,
                     f"{total_duration:.2f}", f"{total_pending_duration:.2f}", 
                     f"{total_valid_duration:.2f}", f"{total_duration/60:.2f}", 
                     f"{total_valid_duration/60:.2f}", f"{overall_rate:.1f}"])
    
    output_csv = '13台设备统计_修正版_3月23日-4月10日.csv'
    with open(output_csv, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)
        writer.writerows(csv_rows)
    print(f"\n✓ 已生成: {output_csv}")
    
    # 输出统计摘要
    print(f"\n=== 11台有数据的设备合计 ===")
    print(f"已审批-有效: {total_approved}条")
    print(f"已审批-无效: {total_approved_invalid}条")
    print(f"待审批: {total_pending}条")
    print(f"总时长: {total_duration/60:.2f}小时")
    print(f"已审批时长: {total_approved_duration/60:.2f}小时（含有效和无效）")
    print(f"待审批时长: {total_pending_duration/60:.2f}小时")
    print(f"有效（合格）时长: {total_valid_duration/60:.2f}小时")
    print(f"不合格时长: {total_invalid_duration/60:.2f}小时")
    print(f"合格率: {overall_rate:.1f}%")

if __name__ == '__main__':
    main()
