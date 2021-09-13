import random, time, os
import requests, json
from PIL import Image
from io import BytesIO

size, fov, heading, pitch = "600x300", "90", "0", "0" # 設定 Google Street View 當中的 URL 參數 (圖片呈現格式)

imageKey, checkKey = "YOUR-API-KEY", "YOUR-API-KEY" # 將 Key 分兩支以確認 checkKey 不會消耗使用量

username = "USER-NAME" # 設定"依經緯度傳換為國家"網站上的帳號名稱 (需註冊)

imgCount = 3 # 設定需要找到多少張合法經緯度位置的圖片

currentCount = 0 # 目前已找到多少張圖片

def downloadImg():
    lat, lng = (random.random() * 180) - 90,  (random.random() * 360) - 180 # 隨機數產生經緯度
    location = str(lat) + ',' + str(lng)
    checkUrl = "https://maps.googleapis.com/maps/api/streetview/metadata?location=" + location + "&key=" + checkKey
    viewUrl = "https://maps.googleapis.com/maps/api/streetview?size=" + size + "&location=" + location + "&fov=" + fov + "&heading="+ heading + "&pitch=" + pitch + "&key=" + imageKey + "&return_error_code=true"
    checkRresponse = requests.get(checkUrl)
    checkDetail = json.loads(checkRresponse.text)
    if checkDetail["status"] == "OK": # 回傳值為OK代表合法經緯度，若為REQUEST_DENIED or ZERO_RESULTS則為非法
        viewRresponse = requests.get(viewUrl)
        img = Image.open(BytesIO(viewRresponse.content)) # 轉成 img 供以後做處理 (直接匯入 model 或先存在本機上)
        img.save("./generated/images/image-" + str(currentCount) + ".jpg") # 以儲存在 images 資料夾做範例 (需新建一個 images/)
        countryUrl = "http://api.geonames.org/countryCodeJSON?lat=" + str(round(lat, 2)) + "&lng=" + str(round(lng, 2)) + "&username=" + username
        countryResponse = requests.get(countryUrl)
        countryDetail = json.loads(countryResponse.text) # 將回傳的 json 格式檔讀入
        print(f'Location: {tuple((lat, lng))}\tCountry: {countryDetail["countryName"]}') # 印出其經緯度及對應的國家名稱 (供未來作為 ground truth)
        return True
    return False

if __name__ == '__main__':
    if not os.path.exists('generated/'):
        os.mkdir('generated/') # 產生 generated 及 images 資料夾
        os.mkdir('generated/images/')

    start = time.time()
    while True:
        if(downloadImg()): currentCount += 1 # 回傳為 True 代表找到圖片
        if(currentCount == imgCount): break # 若以找到圖片數已達到一開始所要求數量則停止
    end = time.time()

    print(f'Download {imgCount} image(s) in {round(end-start, 3)} sec(s)')
