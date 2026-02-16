import requests
import streamlit as st
import urllib.parse

class WCA_OAuth:
    def __init__(self):
        # ⚠️ 請把你在 WCA 申請到的 ID 和 Secret 填入這裡
        # 未來正式上線建議放在 st.secrets 裡比較安全
        self.CLIENT_ID = "你的_Client_ID_貼在這裡"
        self.CLIENT_SECRET = "你的_Client_Secret_貼在這裡"
        
        # 必須跟你在 WCA 後台設定的一模一樣 (少一個斜線都不行)
        self.REDIRECT_URI = "http://localhost:8501" 
        
        self.AUTH_URL = "https://www.worldcubeassociation.org/oauth/authorize"
        self.TOKEN_URL = "https://www.worldcubeassociation.org/oauth/token"
        self.USER_INFO_URL = "https://www.worldcubeassociation.org/api/v0/me"

    def get_login_url(self):
        """產生讓使用者點擊的登入連結"""
        params = {
            "client_id": self.CLIENT_ID,
            "redirect_uri": self.REDIRECT_URI,
            "response_type": "code",
            "scope": "public"
        }
        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"

    def exchange_code_for_token(self, code):
        """拿 WCA 給的 code 去換取 Access Token (數位身分證)"""
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET,
            "redirect_uri": self.REDIRECT_URI,
        }
        try:
            resp = requests.post(self.TOKEN_URL, data=payload)
            if resp.status_code == 200:
                return resp.json().get("access_token")
            else:
                st.error(f"換取 Token 失敗: {resp.text}")
                return None
        except Exception as e:
            st.error(f"連線錯誤: {e}")
            return None

    def get_user_info(self, access_token):
        """拿 Token 去問 WCA 這位使用者是誰"""
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            resp = requests.get(self.USER_INFO_URL, headers=headers)
            if resp.status_code == 200:
                return resp.json().get("me") # 這裡面會有 wca_id, name, avatar 等等
            return None
        except:
            return None