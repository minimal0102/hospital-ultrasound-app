import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import FlexSendMessage
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

app = Flask(__name__)

# 1. 環境變數設定
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')
GROUP_ID = os.environ.get('LINE_GROUP_ID')
ID_SCHEDULE = "1i9jY_xZQDfXCk2eKO6DCCioQdmhpf924BRGqGa_w0fo"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account_key.json", scope)
    return gspread.authorize(creds)

def create_flex_card(title, date_str, shift_data=None):
    """建構精確的 Flex Message 色塊卡片"""
    contents = {
        "type": "bubble",
        "header": {
            "type": "box", "layout": "vertical", "contents": [
                {"type": "text", "text": title, "weight": "bold", "color": "#ffffff", "size": "lg"},
                {"type": "text", "text": f"查詢日期：{date_str}", "color": "#ffffff", "size": "xs"}
            ], "backgroundColor": "#27AE60"
        },
        "body": {"type": "box", "layout": "vertical", "spacing": "sm", "contents": [
            {"type": "text", "text": "🩺 今日值班人員", "weight": "bold", "size": "md", "margin": "md"}
        ]}
    }

    # 內容填充邏輯
    has_content = False
    if shift_data:
        for label, name in shift_data.items():
            if name and str(name).strip() and str(name).lower() != "none":
                has_content = True
                contents["body"]["contents"].append({
                    "type": "box", "layout": "horizontal", "contents": [
                        {"type": "text", "text": label, "size": "xs", "color": "#1976D2", "backgroundColor": "#E3F2FD", "align": "center", "flex": 2, "gravity": "center"},
                        {"type": "text", "text
