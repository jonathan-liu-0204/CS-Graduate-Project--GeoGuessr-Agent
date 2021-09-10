import random
import requests
import json
from PIL import Image
from io import BytesIO

size, fov, heading, pitch, key = "600x300", "90", "180", "0", "API-KEY" # 設定 Google Street View 當中的 URL 參數 (API KEY 需註冊)

username = "USER-NAME" # 設定"依經緯度傳換為國家"網站上的帳號名稱 (需註冊)

imgCount = 1 # 設定需要找到多少張合法經緯度位置的圖片

currentCount = 0 # 目前已找到多少張圖片

def downloadImg():
    lat, lng = (random.random() * 90) - 90,  (random.random() * 180) - 180 # 隨機數產生經緯度
    lat, lng = 46.414382, 10.013988 # 暫時以確定值代替以節省 API 用量
    location = str(lat) + ',' + str(lng)
    viewUrl = "https://maps.googleapis.com/maps/api/streetview?size=" + size + "&location=" + location + "&fov=" + fov + "&heading="+ heading + "&pitch=" + pitch + "&key=" + key + "&return_error_code=true"
    viewRresponse = requests.get(viewUrl)
    if viewRresponse.status_code == 200: # 回傳值為200代表合法經緯度，若為404則為非法
        img = Image.open(BytesIO(viewRresponse.content)) # 轉成 img 供以後做處理 (直接匯入 model 或先存在本機上)
        img.save("./images/" + str(currentCount) + ".jpg") # 以儲存在 images 資料夾做範例 (需新建一個 images/)
        countryUrl = "http://api.geonames.org/countryCodeJSON?lat=" + str(round(lat, 2)) + "&lng=" + str(round(lng, 2)) + "&username=" + username
        countryResponse = requests.get(countryUrl)
        countryDetail = json.loads(countryResponse.text) # 將回傳的 json 格式檔讀入
        print(f'Location: {tuple((lat, lng))}\tCountry: {countryDetail["countryName"]}') # 印出其經緯度及對應的國家名稱 (供未來作為 ground truth)
        return True
    return False

if __name__ == '__main__':
    while True:
        if(downloadImg()): currentCount += 1 # 回傳為 True 代表找到圖片
        if(currentCount == imgCount): break # 若以找到圖片數已達到一開始所要求數量則停止
