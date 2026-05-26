#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉机器人 Webhook 推送模块
使用方法：
1. 在钉钉群中添加自定义机器人
2. 设置关键词（如：数据报告）
3. 将关键词填入 KEYWORD 配置项
"""

import requests
import json
import re
from datetime import datetime

# =================== 配置区域 ===================
# 钉钉 Webhook URL
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=df13aa097a7a62a2169522961ac05246e51c163c7aee21984cd5fcdb353065f1"

# 自定义关键词（必须与钉钉机器人设置的关键词一致）
KEYWORD = "渠道数据分析监控"

# ==========================================

def get_data_summary():
    """从 data.js 读取数据摘要"""
    try:
        with open("data.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 提取数据
        channels = re.search(r'var CHANNELS = \[(.*?)\];', content, re.DOTALL)
        if channels:
            orders = re.findall(r'"orders":\s*(\d+)', channels.group(1))
            types = re.findall(r'"channelType":\s*"([^"]+)"', channels.group(1))
            total = sum(int(o) for o in orders)
            new_orders = sum(int(o) for o, t in zip(orders, types) if t == '新渠道')
            old_orders = sum(int(o) for o, t in zip(orders, types) if t != '新渠道')
            
            return {
                "total_orders": total,
                "total_channels": 213,
                "active_channels": len(orders),
                "active_rate": round(len(orders) / 213 * 100, 1),
                "new_orders": new_orders,
                "old_orders": old_orders
            }
    except Exception as e:
        print(f"读取数据失败: {e}")
    
    return {
        "total_orders": 0,
        "total_channels": 0,
        "active_channels": 0,
        "active_rate": 0,
        "new_orders": 0,
        "old_orders": 0
    }

def send_dingtalk_message(message, msg_type="text"):
    """
    发送钉钉消息
    
    Args:
        message: 消息内容
        msg_type: 消息类型 (text/markdown/link)
    """
    headers = {"Content-Type": "application/json"}
    
    if msg_type == "text":
        data = {
            "msgtype": "text",
            "text": {
                "content": f"{KEYWORD} {message}"
            }
        }
    elif msg_type == "markdown":
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": f"{KEYWORD} - {message.get('title', '报告')}",
                "text": message.get("text", "")
            }
        }
    elif msg_type == "link":
        data = {
            "msgtype": "link",
            "link": message
        }
    
    try:
        response = requests.post(DINGTALK_WEBHOOK, headers=headers, data=json.dumps(data))
        result = response.json()
        if result.get("errcode") == 0:
            print("✅ 钉钉消息推送成功")
            return True
        else:
            print(f"❌ 推送失败: {result.get('errmsg')}")
            return False
    except Exception as e:
        print(f"❌ 推送异常: {str(e)}")
        return False

def send_dashboard_report():
    """发送看板数据报告到钉钉"""
    data_summary = get_data_summary()
    
    title = f"{KEYWORD} - 渠道数据看板报告"
    text = f"""### {title}

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

**📈 总单量**: {data_summary['total_orders']:,}

**🏢 合作渠道**: {data_summary['total_channels']}家

**✅ 产单渠道**: {data_summary['active_channels']}家

**📊 产单率**: {data_summary['active_rate']}%

---

**🆕 新渠道单量**: {data_summary['new_orders']:,}

**🏠 老渠道单量**: {data_summary['old_orders']:,}

---

🔗 [查看完整看板](https://AmengYull.github.io/channel-dashboard/dashboard.html)
"""
    
    message = {
        "title": title,
        "text": text
    }
    
    return send_dingtalk_message(message, msg_type="markdown")

def send_simple_message(content):
    """发送简单文本消息"""
    return send_dingtalk_message(content, msg_type="text")

if __name__ == "__main__":
    print("=" * 50)
    print("📤 钉钉推送工具")
    print("=" * 50)
    print(f"\n关键词: {KEYWORD}")
    print("\n正在推送数据报告到钉钉...\n")
    
    send_dashboard_report()
    
    print("\n" + "=" * 50)
