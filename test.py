import requests

yolo = "response=requests.get('https://api.github.com/users/dlawlet').json()"
response = None
exec(yolo)
print(response)