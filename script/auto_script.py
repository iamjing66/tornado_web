import requests

data = {"uname": 18235101805, "upwd": "JINGYuhao825", "bushu": ""}

url = "http://127.0.0.1:8000/bushu"
res = requests.post(url=url, data=data).text
print(res)
