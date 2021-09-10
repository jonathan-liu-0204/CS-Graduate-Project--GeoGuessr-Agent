import random
import requests
import json
from PIL import Image
from io import BytesIO

size, fov, heading, pitch, key = "400x400", "50", "180", "0", "API-KEY" # 設定 Google Street View 當中的 URL 參數 (API KEY 需註冊)

username = "USER-NAME" # 設定"依經緯度傳換為國家"網站上的帳號名稱 (需註冊)

imgCount = 2 # 設定需要找到多少張合法經緯度位置的圖片

def downloadImg():
    lat, lng = (random.random() * 90) - 90,  (random.random() * 180) - 180 # 隨機數產生經緯度
    location = str(lat) + ',' + str(lng)
    viewUrl = "https://maps.googleapis.com/maps/api/streetview?size=" + size + "&location=" + location + "&fov=" + fov + "&heading="+ heading + "&pitch=" + pitch + "&key=" + key + "&return_error_code=true"
    viewRresponse = requests.get(viewUrl)
    if viewRresponse.status_code == 200: # 回傳值為200代表合法經緯度，若為404則為非法
        img = Image.open(BytesIO(viewRresponse.content)) # 轉成 img 供以後做處理 (直接匯入 model 或先存在本機上)
        countryUrl = "http://api.geonames.org/countryCodeJSON?lat=" + str(round(lat, 2)) + "&lng=" + str(round(lng, 2)) + "&username=" + username
        countryResponse = requests.get(countryUrl)
        countryDetail = json.loads(countryResponse.text) # 將回傳的 json 格式檔讀入
        print(f'Location: {location}\tCountry: {countryDetail["countryName"]}') # 印出其經緯度及對應的國家名稱 (供未來作為 ground truth)
        return True
    return False

if __name__ == '__main__':
    currentCount = 0
    while True:
        if(downloadImg()): currentCount += 1
        if(currentCount == imgCount): break
