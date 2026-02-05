import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

# ================= 配置区域 =================
MAIL_USER = os.environ.get("MAIL_USER")
MAIL_PASS = os.environ.get("MAIL_PASS")
QWEATHER_KEY = os.environ.get("QWEATHER_KEY") 

# ⚠️⚠️⚠️ 请在这里填你自己的 QQ 号！不要填我的测试号！
RECEIVERS = ["2387993145@qq.com"]  

LOCATION_ID = "101270101" # 成都

# 你的专属 API Host
API_HOST = "https://pv6tuq6kxt.re.qweatherapi.com"
# ===========================================

def get_weather_data():
    print("📡 正在调用和风天气 API...")
    if not QWEATHER_KEY:
        print("❌ 错误：未找到 QWEATHER_KEY")
        return None

    # 拼接 URL
    url_now = f"{API_HOST}/v7/weather/now?location={LOCATION_ID}&key={QWEATHER_KEY}"
    url_daily = f"{API_HOST}/v7/weather/3d?location={LOCATION_ID}&key={QWEATHER_KEY}"
    url_indices = f"{API_HOST}/v7/indices/1d?location={LOCATION_ID}&key={QWEATHER_KEY}&type=1,3,5"

    try:
        # 1. 获取实时天气
        resp_now = requests.get(url_now).json()
        if resp_now.get('code') != '200':
            print(f"❌ 实时天气请求失败: {resp_now}")
            return None
            
        # 2. 获取预报
        resp_daily = requests.get(url_daily).json()
        if resp_daily.get('code') != '200':
            print(f"❌ 预报请求失败: {resp_daily}")
            return None
            
        # 3. 获取指数
        resp_indices = requests.get(url_indices).json()
        if resp_indices.get('code') != '200':
            print(f"❌ 指数请求失败: {resp_indices}")
            return None

        # 解析数据
        now = resp_now['now']
        daily = resp_daily['daily'][0]
        indices = resp_indices['daily']

        suggestion_cloth = "N/A"
        suggestion_uv = "N/A"
        suggestion_sport = "N/A"
        for item in indices:
            if item['type'] == '3': suggestion_cloth = item['text']
            elif item['type'] == '5': suggestion_uv = item['category']
            elif item['type'] == '1': suggestion_sport = item['text']

        # 组装 HTML
        html_content = f"""
        <div style="font-family: '微软雅黑', sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.05);">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; text-align: center; color: white;">
                <h2 style="margin: 0; font-size: 24px;">📅 成都天气日报</h2>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">{daily['fxDate']} (今天)</p>
            </div>
            <div style="padding: 25px;">
                <div style="text-align: center; margin-bottom: 25px;">
                    <span style="font-size: 48px; font-weight: bold; color: #333;">{now['temp']}°</span>
                    <span style="font-size: 20px; color: #666; margin-left: 10px;">{now['text']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <div style="text-align: center; flex: 1;">
                        <div style="font-size: 12px; color: #888;">最高/最低</div>
                        <div style="font-weight: bold; color: #333;">{daily['tempMin']}° ~ {daily['tempMax']}°</div>
                    </div>
                    <div style="text-align: center; flex: 1; border-left: 1px solid #ddd;">
                        <div style="font-size: 12px; color: #888;">湿度</div>
                        <div style="font-weight: bold; color: #333;">{now['humidity']}%</div>
                    </div>
                    <div style="text-align: center; flex: 1; border-left: 1px solid #ddd;">
                        <div style="font-size: 12px; color: #888;">风力</div>
                        <div style="font-weight: bold; color: #333;">{now['windScale']}级</div>
                    </div>
                </div>
                <h3 style="font-size: 16px; border-left: 4px solid #764ba2; padding-left: 10px; margin-bottom: 15px;">💡 生活指数</h3>
                <div style="margin-bottom: 10px;"><strong style="color: #555;">👕 穿衣：</strong>{suggestion_cloth}</div>
                <div style="margin-bottom: 10px;"><strong style="color: #555;">☀️ 紫外线：</strong>{suggestion_uv}</div>
                <div style="margin-bottom: 10px;"><strong style="color: #555;">🏃 运动：</strong>{suggestion_sport}</div>
                <div style="margin-top: 20px; font-size: 13px; color: #888; text-align: center; border-top: 1px dashed #eee; padding-top: 10px;">
                    🌅 日出 {daily['sunrise']} | 🌇 日落 {daily['sunset']}
                </div>
            </div>
            <div style="background-color: #f0f2f5; padding: 10px; text-align: center; font-size: 12px; color: #999;">
                数据来源：和风天气 API
            </div>
        </div>
        """
        return html_content

    except Exception as e:
        print(f"❌ 发生未知错误: {e}")
        return None

def send_email(content):
    print("🚀 正在连接 QQ 邮箱服务器...")
    if not MAIL_USER or not MAIL_PASS:
        print("❌ 错误：未找到邮箱账号或密码")
        return
    msg = MIMEText(content, 'html', 'utf-8')
    msg['From'] = formataddr(("天气小助手", MAIL_USER))
    msg['To'] = ",".join(RECEIVERS)
    msg['Subject'] = Header('早安！今日天气详报 ☀️', 'utf-8')
    try:
        server = smtplib.SMTP_SSL('smtp.qq.com', 465)
        server.login(MAIL_USER, MAIL_PASS)
        server.sendmail(MAIL_USER, RECEIVERS, msg.as_string())
        server.quit()
        print("✅ 邮件发送成功！")
    except Exception as e:
        print(f"❌ 发送失败: {e}")

if __name__ == "__main__":
    html = get_weather_data()
    if html:
        send_email(html)
