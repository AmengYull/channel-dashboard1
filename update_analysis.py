#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 dashboard.html 中的分析、原因、策略内容
基于最新的 data.js 数据
"""

import re
import json

# 读取 data.js 提取关键数据
def parse_data_js():
    with open('data.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 CHANNELS
    channels_match = re.search(r'var CHANNELS = (\[.*?\]);', content, re.DOTALL)
    channels = json.loads(channels_match.group(1)) if channels_match else []
    
    # 提取 DAILY
    daily_match = re.search(r'var DAILY = (\[.*?\]);', content, re.DOTALL)
    daily = json.loads(daily_match.group(1)) if daily_match else []
    
    # 提取 CITY
    city_match = re.search(r'var CITY = (\[.*?\]);', content, re.DOTALL)
    cities = json.loads(city_match.group(1)) if city_match else []
    
    # 提取 INDUSTRY
    industry_match = re.search(r'var INDUSTRY = (\[.*?\]);', content, re.DOTALL)
    industries = json.loads(industry_match.group(1)) if industry_match else []
    
    # 计算汇总数据
    total_orders = sum(c['orders'] for c in channels)
    new_orders = sum(c['orders'] for c in channels if c.get('channelType') == '新渠道')
    old_orders = sum(c['orders'] for c in channels if c.get('channelType') != '新渠道')
    
    avg_arrival = sum(c['arrivalRate'] for c in channels) / len(channels) if channels else 0
    avg_success = sum(c['successRate'] for c in channels) / len(channels) if channels else 0
    
    # 找出表现最好和最差的城市
    cities_sorted = sorted(cities, key=lambda x: x.get('cancelRate', 0), reverse=True)
    worst_cities = cities_sorted[:5]
    best_cities = sorted(cities, key=lambda x: x.get('successRate', 0), reverse=True)[:5]
    
    # 找出表现最好和最差的行业
    industries_sorted = sorted(industries, key=lambda x: x.get('orders', 0), reverse=True)
    top_industries = industries_sorted[:5]
    
    return {
        'total_orders': total_orders,
        'new_orders': new_orders,
        'old_orders': old_orders,
        'channel_count': len(channels),
        'avg_arrival': avg_arrival,
        'avg_success': avg_success,
        'worst_cities': worst_cities,
        'best_cities': best_cities,
        'top_industries': top_industries,
        'daily_avg': sum(d['total'] for d in daily) / len(daily) if daily else 0
    }

def update_dashboard():
    data = parse_data_js()
    
    with open('dashboard.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 更新 AI 洞察面板 - 第一板块（渠道周度分析）
    old_ai1 = '''<div class="ai-item"><strong>渠道健康度评分</strong>：TOP10渠道综合评分62/100，较上周-4分。煜志网络(新)拉分最严重，建议设为本周重点帮扶对象</div>
          <div class="ai-item"><strong>流量质量预警</strong>：抖音渠道品类错误率3.2%高于均值2.3%，判断5月15日算法更新后推流精准度下降，建议暂停品类扩展投放</div>
          <div class="ai-item"><strong>周度预测</strong>：按当前日均4595单趋势，月末预计完成142,441单（目标136,390单），有望超额完成。需日均维持4187单即可达标</div>
          <div class="ai-item"><strong>建议</strong>：优先将资源从低效渠道(成功率<22%)转移至高潜力渠道；吉时雨家政重新评估投放策略</div>'''
    
    new_ai1 = f'''<div class="ai-item"><strong>渠道健康度评分</strong>：TOP10渠道综合评分{data['avg_success']:.0f}/100。宜昌玖源商贸({data['top_industries'][0]['orders'] if data['top_industries'] else 0}单)表现最佳，建议复制其成功模式</div>
          <div class="ai-item"><strong>流量质量分析</strong>：平均上门率{data['avg_arrival']:.1f}%，成功率{data['avg_success']:.1f}%。新渠道成功率偏低，需加强质量把控</div>
          <div class="ai-item"><strong>数据趋势</strong>：当前总单量{data['total_orders']:,}单，新渠道{data['new_orders']:,}单，老渠道{data['old_orders']:,}单，渠道结构持续优化中</div>
          <div class="ai-item"><strong>建议</strong>：优先扶持高潜力渠道(成功率>25%)；对成功率<20%渠道进行专项诊断；加强城市差异化运营策略</div>'''
    
    html = html.replace(old_ai1, new_ai1)
    
    # 更新 AI 洞察面板 - 第二板块（行业拓展分析）
    old_ai2 = '''<div class="ai-item"><strong>拓展优先级</strong>：家政类(ROI最高) > 媒体类(质量好) > 网站类(稳定) > 电商类(有空间)。采买类维持现状不扩量</div>
          <div class="ai-item"><strong>线索转化瓶颈</strong>：725条线索成功率仅5.8%，主因合作模式不匹配(97条)和无效需求(61条)。建议设计3种合作模板：CPS分成/换量合作/品类专供</div>
          <div class="ai-item"><strong>家装行业机会</strong>：29条待跟进线索(最大AI存量)，近期集中登记。建议本周统一建联，目标转化5家</div>
          <div class="ai-item"><strong>转介绍杠杆</strong>：成功率76%远超其他渠道，建议设计老客户/合作伙伴推荐激励机制</div>'''
    
    top_industry = data['top_industries'][0] if data['top_industries'] else {'name': '采买类', 'orders': 0}
    new_ai2 = f'''<div class="ai-item"><strong>行业结构分析</strong>：{top_industry['name']}占比最高({top_industry['orders']:,}单)，是核心业务支柱。建议深耕该行业，同时拓展高价值行业</div>
          <div class="ai-item"><strong>渠道质量评估</strong>：{data['channel_count']}家产单渠道中，平均成功率{data['avg_success']:.1f}%。建议对低效渠道进行优化或淘汰</div>
          <div class="ai-item"><strong>城市分布洞察</strong>：重点城市表现分化明显，建议针对高取消率城市制定专项改善方案</div>
          <div class="ai-item"><strong>增长建议</strong>：聚焦高成功率城市复制成功经验；加强工程师培训提升上门率；优化价格策略提升转化率</div>'''
    
    html = html.replace(old_ai2, new_ai2)
    
    # 更新 AI 洞察面板 - 第三板块（城市综合诊断）
    worst_city = data['worst_cities'][0] if data['worst_cities'] else {'name': '乌鲁木齐', 'cancelRate': 50}
    best_city = data['best_cities'][0] if data['best_cities'] else {'name': '重庆', 'successRate': 30}
    
    old_ai3 = '''<div class="ai-item"><strong>城市分级建议</strong>：S级(上门>58%+成功>30%)：沈阳；A级：成都/重庆/苏州/上海/广州/西安/深圳/贵阳/武汉/杭州；B级：天津/北京/东莞/乌鲁木齐/太原</div>
          <div class="ai-item"><strong>取消根因</strong>：乌鲁木齐58%取消率中，天气因素占35%(沙尘暴)、工程师不足占40%、价格因素占25%。建议先解决工程师密度</div>
          <div class="ai-item"><strong>产品-城市匹配</strong>：北京热水器取消率偏高，判断为老旧小区安装难度大；建议北京收缩热水器品类，加大水电品类投放</div>
          <div class="ai-item"><strong>天气窗口</strong>：5月下旬全国升温，空调/热水器需求将上升。建议提前在S/A级城市储备安装工程师</div>'''
    
    new_ai3 = f'''<div class="ai-item"><strong>城市表现分级</strong>：优秀城市({best_city['name']}等)成功率>{best_city.get('successRate', 30):.0f}%，建议复制经验；关注城市({worst_city['name']}等)取消率>{worst_city.get('cancelRate', 50):.0f}%，需重点改善</div>
          <div class="ai-item"><strong>核心问题诊断</strong>：高取消率城市主要受工程师密度不足、价格敏感度、服务覆盖范围等因素影响</div>
          <div class="ai-item"><strong>改善策略</strong>：补充工程师资源、优化价格话术、收缩不服务品类投放、加强渠道数据质量管控</div>
          <div class="ai-item"><strong>资源配置建议</strong>：向高成功率城市倾斜资源，同时改善低效城市的服务能力和用户体验</div>'''
    
    html = html.replace(old_ai3, new_ai3)
    
    # 更新行业分析洞察
    old_industry = '''<div class="issue-item"><strong>家政类</strong>：上门率79%、成功率68%，质量最高但体量仅1200单，需加速复制</div>
      <div class="issue-item"><strong>采买类</strong>：占比92%（69215单），上门率54%、成功率28%，拉低大盘主因</div>
      <div class="issue-item"><strong>媒体类</strong>：上门率74%、成功率49%，质量高但仅1085单，应重点拓展</div>
      <div class="strategy-item">复制家政/网站类模式；采买类做话术优化；媒体类目标新增5家<span class="assignee-badge">商务组</span></div>'''
    
    if data['top_industries']:
        ind1 = data['top_industries'][0]
        ind2 = data['top_industries'][1] if len(data['top_industries']) > 1 else {'name': '网站类', 'orders': 0, 'arrivalRate': 60, 'successRate': 30}
        new_industry = f'''<div class="issue-item"><strong>{ind1['name']}</strong>：占比最高({ind1['orders']:,}单)，上门率{ind1.get('arrivalRate', 0):.0f}%、成功率{ind1.get('successRate', 0):.0f}%，是核心业务支柱</div>
      <div class="issue-item"><strong>{ind2['name']}</strong>：{ind2['orders']:,}单，上门率{ind2.get('arrivalRate', 0):.0f}%、成功率{ind2.get('successRate', 0):.0f}%，质量表现{'优秀' if ind2.get('successRate', 0) > 35 else '良好'}</div>
      <div class="strategy-item">深耕{ind1['name']}核心业务；复制成功经验至其他行业；重点拓展高价值行业渠道<span class="assignee-badge">商务组</span></div>'''
        html = html.replace(old_industry, new_industry)
    
    # 更新城市诊断
    if data['worst_cities']:
        wc1 = data['worst_cities'][0]
        wc2 = data['worst_cities'][1] if len(data['worst_cities']) > 1 else {'name': '北京', 'cancelRate': 50}
        old_city = '乌鲁木齐58.63%'
        new_city = f"{wc1['name']}{wc1.get('cancelRate', 50):.1f}%"
        html = html.replace(old_city, new_city)
    
    # 更新核心问题分析
    old_core = '''<div class="issue-item">
            <strong>【问题1】目标达成风险</strong><br>
            完成率78.5%，日均需4187单，近一周回升趋势<br>
            <em>策略①</em>：扶持煜志/小补快，新渠道占比提至16%<br>
            <em>策略②</em>：成都/上海/苏州加大老渠道推广
          </div>'''
    
    new_core1 = f'''<div class="issue-item">
            <strong>【问题1】目标达成进度</strong><br>
            当前总单量{data['total_orders']:,}单，新渠道{data['new_orders']:,}单，老渠道{data['old_orders']:,}单<br>
            <em>策略①</em>：扶持高潜力渠道，提升整体成功率至30%以上<br>
            <em>策略②</em>：加大优质城市渠道推广力度，复制成功经验
          </div>'''
    
    html = html.replace(old_core, new_core1)
    
    # 保存更新后的文件
    with open('dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✅ dashboard.html 分析内容已更新")
    print(f"\n关键数据:")
    print(f"  - 总单量: {data['total_orders']:,}")
    print(f"  - 新渠道: {data['new_orders']:,}")
    print(f"  - 老渠道: {data['old_orders']:,}")
    print(f"  - 渠道数: {data['channel_count']}")
    print(f"  - 平均上门率: {data['avg_arrival']:.1f}%")
    print(f"  - 平均成功率: {data['avg_success']:.1f}%")

if __name__ == "__main__":
    update_dashboard()
