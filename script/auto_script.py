import requests
import os

uname = os.getenv("lv_uname")
upwd = os.getenv("lv_upwd")

data = {"uname": uname, "upwd": upwd, "bushu": ""}

url = "http://127.0.0.1:8000/bushu"
res = requests.post(url=url, data=data).text
print(res)
