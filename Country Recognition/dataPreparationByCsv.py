import random, time, os
import requests, json
from PIL import Image
from io import BytesIO
import csv

size, fov, heading, pitch = "600x300", "90", "0", "0" # 設定 Google Street View 當中的 URL 參數 (圖片呈現格式)

imageKey, checkKey = "YOUR-API-KEY", "YOUR-API-KEY" # 將 Key 分兩支以確認 checkKey 不會消耗使用量

username = "USER-NAME" # 設定"依經緯度傳換為國家"網站上的帳號名稱 (需註冊)

currentCount = 0 # 目前已找到多少張圖片

imgCount, targetCountry, usage, latRange, latMin, lngRange, lngMin = [], [], [], [], [], [], []

def downloadImg(imgCount, targetCountry, usage, latRange, latMin, lngRange, lngMin):
    lat, lng = (random.random() * latRange) + latMin,  (random.random() * lngRange) + lngMin # 隨機數產生經緯度(在目標國家範圍下)
    location = str(lat) + ',' + str(lng)
    checkUrl = "https://maps.googleapis.com/maps/api/streetview/metadata?location=" + location + "&key=" + checkKey
    viewUrl = "https://maps.googleapis.com/maps/api/streetview?size=" + size + "&location=" + location + "&fov=" + fov + "&heading="+ heading + "&pitch=" + pitch + "&key=" + imageKey + "&return_error_code=true"
    checkRresponse = requests.get(checkUrl)
    checkDetail = json.loads(checkRresponse.text)
    if checkDetail["status"] == "OK": # 回傳值為OK代表合法經緯度，若為REQUEST_DENIED or ZERO_RESULTS則為非法
        countryUrl = "http://api.geonames.org/countryCodeJSON?lat=" + str(round(lat, 3)) + "&lng=" + str(round(lng, 3)) + "&username=" + username
        countryResponse = requests.get(countryUrl)
        countryDetail = json.loads(countryResponse.text) # 將回傳的 json 格式檔讀入
        if(countryResponse.text.find('no country code found') != -1):
            return False # 此部分情況是合法的經緯度但並非我們的目標國家
        if(countryDetail["countryName"] == targetCountry): # 若此合法經緯度位於我們設定的目標國家
            viewRresponse = requests.get(viewUrl)
            img = Image.open(BytesIO(viewRresponse.content)) # 轉成 img 供以後做處理
            img.save("./generated/images/" + usage + "/" + countryDetail["countryName"] + '/' + location + ".jpg") # 將圖片儲存在路徑 'generated/images/{country}/'
            print(f'Number: {currentCount+1}/{imgCount}\tLocation: {tuple((lat, lng))}\tCountry: {countryDetail["countryName"]}') # 印出其經緯度及對應的國家名稱 (供未來作為 ground truth)
            return True # 此部分情況是合法的經緯度且位於我們的目標國家
        return False # 此部分情況是合法的經緯度但並非我們的目標國家
    return False # 此部分情況是非法的經緯度


def readFromCsv():
    with open('dataPreparation.csv', newline='') as csvfile:
        rows = csv.DictReader(csvfile)
        for row in rows:
            imgCount.append(int(row['imgCount']))
            targetCountry.append(row['targetCountry'])
            usage.append(row['usage'])
            latRange.append(int(row['latRange']))
            latMin.append(int(row['latMin']))
            lngRange.append(int(row['lngRange']))
            lngMin.append(int(row['lngMin']))


if __name__ == '__main__':
    
    readFromCsv()

    if not os.path.exists('generated/'):
        os.mkdir('generated/') # 產生 generated 及 images 資料夾
        os.mkdir('generated/images/')
        os.mkdir('generated/images/train/')
        os.mkdir('generated/images/val/')
    
    for i in range(len(targetCountry)):
        if not os.path.exists('generated/images/train/'+targetCountry[i]+'/'): # 檢查train資料夾是否存在
            os.mkdir('generated/images/train/'+targetCountry[i]+'/')
        if not os.path.exists('generated/images/val/'+targetCountry[i]+'/'): # 檢查val資料夾是否存在
            os.mkdir('generated/images/val/'+targetCountry[i]+'/')

        if username == "lawrence0215":
            username = "tempsecondary"
            print("Now Username: ", username)
        elif username == "tempsecondary":
            username = "lawrence0215"
            print("Now Username: ", username)

        currentCount = 0
        start = time.time()
        while True:
            if(downloadImg(imgCount[i], targetCountry[i], usage[i], latRange[i], latMin[i], lngRange[i], lngMin[i])): currentCount += 1 # 回傳為 True 代表找到圖片
            if(currentCount == imgCount[i]): break # 若以找到圖片數已達到一開始所要求數量則停止
        end = time.time()

        print(f'Download {imgCount[i]} image(s) in {round(end-start, 3)} sec(s)')
  