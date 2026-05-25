#!/usr/bin/env python3
"""
proxy.py — Flask backend for AI analysis API.
Runs on port 8082.
Supports 5 AI models:
  - kimi    (月之暗面 Kimi)
  - zhipu  (智谱 AI)
  - qianfan (百度千帆)
  - aliyun  (阿里云百炼)
  - deepseek (DeepSeek)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import requests
import datetime

app = Flask(__name__)
CORS(app, origins=['http://localhost:8081', 'http://127.0.0.1:8081'])

# ============================================================
# Load API Keys from config.env (same directory as proxy.py)
# Priority: environment variable > config.env file
# ============================================================
_CONFIG_ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.env')

def _load_config_env():
    """Load KEY=VALUE pairs from config.env, skip blank/comment lines."""
    if not os.path.exists(_CONFIG_ENV_PATH):
        return
    with open(_CONFIG_ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, _, val = line.partition('=')
                key = key.strip()
                val = val.strip()
                # Only set if env var not already defined AND value is non-empty
                if key and val and not os.environ.get(key):
                    os.environ[key] = val

_load_config_env()
print(f'[config] Loaded keys from {_CONFIG_ENV_PATH}')
for k in ['KIMI_API_KEY', 'ZHIPU_API_KEY', 'QIANFAN_API_KEY', 'ALIYUN_API_KEY', 'DEEPSEEK_API_KEY']:
    status = 'SET' if os.environ.get(k, '').strip() else 'NOT SET'
    print(f'  {k}: {status}')

# ============================================================
# AI API Config
# ============================================================
def _get_ai_config():
    """Build AI config dynamically so API keys are read at request time."""
    return {
        'kimi': {
            'url': 'https://api.moonshot.cn/v1/chat/completions',
            'model': 'moonshot-v1-8k',
            'headers': {
                'Authorization': 'Bearer ' + os.environ.get('KIMI_API_KEY', ''),
                'Content-Type': 'application/json',
            }
        },
        'zhipu': {
            'url': 'https://open.bigmodel.cn/api/paas/v4/chat/completions',
            'model': 'glm-4-flash',
            'headers': {
                'Authorization': 'Bearer ' + os.environ.get('ZHIPU_API_KEY', ''),
                'Content-Type': 'application/json',
            }
        },
        'qianfan': {
            'url': 'https://qianfan.baidubce.com/v2/chat/completions',
            'model': 'ernie-4.0-turbo-8k',
            'headers': {
                'Authorization': 'Bearer ' + os.environ.get('QIANFAN_API_KEY', ''),
                'Content-Type': 'application/json',
            }
        },
        'aliyun': {
            'url': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
            'model': 'qwen-turbo',
            'headers': {
                'Authorization': 'Bearer ' + os.environ.get('ALIYUN_API_KEY', ''),
                'Content-Type': 'application/json',
            }
        },
        'deepseek': {
            'url': 'https://api.deepseek.com/chat/completions',
            'model': 'deepseek-chat',
            'headers': {
                'Authorization': 'Bearer ' + os.environ.get('DEEPSEEK_API_KEY', ''),
                'Content-Type': 'application/json',
            }
        },
    }

AI_CONFIG = _get_ai_config()

# Prompt template for channel data analysis
ANALYSIS_PROMPT = """你是一位资深渠道运营分析专家。
以下是当前渠道数据看板的核心指标，请做深度分析并给出可落地的优化建议。

## 核心数据
- 总订单量：{total_orders}
- 平均上门率：{avg_arrival}%
- 平均成功率：{avg_success}%
- 取消率：{avg_cancel}%

## TOP 渠道（按订单量）
{top_channels}

## TOP 城市
{top_cities}

## 行业分布
{top_industries}

## 取消原因 TOP3
{cancel_reasons}

## 语音标记关键指标
- 不服务品类率：{voice_bupinlei}%
- 无维修需求率：{voice_wuxuqiugou}%
- 标记已下单率：{voice_yixiadan}%
- 啄木鸟转单率：{voice_zhuomuniao}%

请从以下角度分析：
1. **渠道质量诊断**：哪些渠道表现异常？
2. **城市拓展建议**：哪个城市有未开发潜力？
3. **取消原因分析**：怎么降低取消率？
4. **具体的下周行动方案**（3条，可落地）
"""


def build_prompt(data):
    """Build analysis prompt from dashboard data."""
    chs = data.get('channels', [])
    cts = data.get('city', [])
    ind = data.get('industry', [])
    ccl = data.get('cancel', [])
    voc = data.get('voice', {})

    total_orders = sum(c.get('orders', 0) for c in chs[:20])
    avg_arrival = round(sum(c.get('arrivalRate', 0) for c in chs[:20]) / max(len(chs[:20]), 1), 2)
    avg_success = round(sum(c.get('successRate', 0) for c in chs[:20]) / max(len(chs[:20]), 1), 2)
    avg_cancel  = round(sum(c.get('cancelRate', 0) for c in chs[:20]) / max(len(chs[:20]), 1), 2)

    top_ch = '\n'.join([
        f"  - {c['name']}: {c['orders']}单, 上门{c.get('arrivalRate',0)}%, 成功{c.get('successRate',0)}%"
        for c in chs[:5]
    ])
    top_ct = '\n'.join([
        f"  - {c['city']}: {c['orders']}单, 上门{c.get('arrivalRate',0)}%"
        for c in cts[:3]
    ])
    top_in = '\n'.join([
        f"  - {i['industry']}: {i['orders']}单, 上门{i.get('arrivalRate',0)}%"
        for i in ind[:3]
    ])
    top_cl = '\n'.join([
        f"  - {c['name']}: {c['count']}次 ({c.get('rate',0)}%)"
        for c in ccl[:3]
    ])

    prompt = ANALYSIS_PROMPT.format(
        total_orders=total_orders,
        avg_arrival=avg_arrival,
        avg_success=avg_success,
        avg_cancel=avg_cancel,
        top_channels=top_ch,
        top_cities=top_ct,
        top_industries=top_in,
        cancel_reasons=top_cl,
        voice_bupinlei=voc.get('不服务品类率', 0),
        voice_wuxuqiugou=voc.get('无维修需求率', 0),
        voice_yixiadan=voc.get('标记已下单率', 0),
        voice_zhuomuniao=voc.get('啄木鸟转单率', 0),
    )
    return prompt


def call_ai_api(model_key, prompt):
    """Call AI API and return analysis text."""
    # Always reload config dynamically to pick up config.env changes without restart
    cfg = _get_ai_config().get(model_key)
    if not cfg:
        return None, f'不支持的模型: {model_key}'

    # Check API key
    auth_header = cfg['headers']['Authorization']
    if not auth_header or auth_header == 'Bearer ':
        key_name = model_key.upper() + '_API_KEY'
        return None, f'请先在 config.env 中填写 {key_name}（或设置同名环境变量）'

    payload = {
        'model': cfg['model'],
        'messages': [
            {'role': 'system', 'content': '你是资深渠道运营分析专家。'},
            {'role': 'user', 'content': 'prompt'},
        ],
        'temperature': 0.3,
        'max_tokens': 1500,
    }
    # Replace prompt placeholder
    payload['messages'][1]['content'] = prompt

    try:
        resp = requests.post(
            cfg['url'],
            headers=cfg['headers'],
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        result = resp.json()
        # Extract content (handle different response formats)
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            return content, None
        elif 'output' in result:  # Aliyun format
            return result['output']['text'], None
        else:
            return None, f'未知响应格式: {json.dumps(result, ensure_ascii=False)[:200]}'
    except requests.exceptions.Timeout:
        return None, '请求超时（60s），请稍后重试'
    except requests.exceptions.RequestException as e:
        return None, f'API 请求失败: {str(e)[:200]}'
    except Exception as e:
        return None, f'解析响应失败: {str(e)[:200]}'


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'time': datetime.datetime.now().isoformat()})


@app.route('/api/ai-analyze', methods=['POST'])
def ai_analyze():
    """AI 分析接口。
    Request: {model: 'kimi'|'zhipu'|'qianfan'|'aliyun'|'deepseek', data: {...}}
    Response: {success: true, analysis: '...'} or {success: false, error: '...'}
    """
    try:
        body = request.get_json(force=True, silent=True)
        if not body:
            return jsonify({'success': False, 'error': '请求体为空'}), 400

        model = body.get('model', 'kimi')
        data  = body.get('data', {})

        if not data:
            return jsonify({'success': False, 'error': '缺少数据字段 data'}), 400

        prompt = build_prompt(data)
        analysis, err = call_ai_api(model, prompt)

        if err:
            return jsonify({'success': False, 'error': err}), 500

        return jsonify({'success': True, 'analysis': analysis, 'model': model})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai-analyze-stream', methods=['POST'])
def ai_analyze_stream():
    """Streaming version — returns SSE stream."""
    # Could implement later
    return jsonify({'success': False, 'error': '流式接口暂未实现'}), 501


def print_startup_banner():
    cfg = _get_ai_config()
    print('=' * 55)
    print('  AI 分析代理服务  (proxy.py)   Port: 8082')
    print('  Config file:', _CONFIG_ENV_PATH)
    print('  Endpoints:')
    print('    GET  /api/health')
    print('    POST /api/ai-analyze')
    print('  AI 模型配置状态:')
    for k in cfg:
        key = cfg[k]['headers']['Authorization']
        status = '✅ 已配置' if key and key != 'Bearer ' else '❌ 未配置 → 请编辑 config.env'
        print(f'    {k:12s} {status}')
    print('  提示: 修改 config.env 后保存即生效，无需重启')
    print('=' * 55)


if __name__ == '__main__':
    print_startup_banner()
    app.run(host='127.0.0.1', port=8082, debug=True)
