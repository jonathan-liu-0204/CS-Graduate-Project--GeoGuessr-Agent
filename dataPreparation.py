import random, time, os
import requests, json
from PIL import Image
from io import BytesIO

size, fov, heading, pitch = "600x300", "90", "0", "0" # 設定 Google Street View 當中的 URL 參數 (圖片呈現格式)

imageKey, checkKey = "AIzaSyCx7BBGzPe1FKawigAXw3qRLspKQkZvCmM", "AIzaSyCr-1jgNuxFhTsLgo9G3GIp3PY1EQS6NDk" # 將 Key 分兩支以確認 checkKey 不會消耗使用量

username = "lawrence0215" # 設定"依經緯度傳換為國家"網站上的帳號名稱 (需註冊)

imgCount = 200 # 設定需要找到多少張合法經緯度位置的圖片 (一次到位，關係到檔案名稱)

currentCount = 0 # 目前已找到多少張圖片

targetCountry = "Latvia" # 設定要尋找的目標國家

usage = 'train' # 可選擇 train 或是 val 代表目前圖片存於哪個資料夾中

def downloadImg(usage='train'):
    lat, lng = (random.random() * 2) + 56,  (random.random() * 7) + 21 # 隨機數產生經緯度(在目標國家範圍下)
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
            writeDetails("Location: " + str(tuple((lat, lng))) + "\tCountry: " + targetCountry + "\tUsage: " + usage + '\n') # 將地理位置存入 .txt
            return True # 此部分情況是合法的經緯度且位於我們的目標國家
        return False # 此部分情況是合法的經緯度但並非我們的目標國家
    return False # 此部分情況是非法的經緯度

def writeDetails(string):
    path = 'generated/details/' + targetCountry + '.txt'
    with open(path, 'a') as file:
        file.write(string)

if __name__ == '__main__':
    if not os.path.exists('generated/'):
        os.mkdir('generated/') # 產生 generated 及 images 資料夾
        os.mkdir('generated/images/')
        os.mkdir('generated/details/')
        os.mkdir('generated/images/train/')
        os.mkdir('generated/images/val/')
    
    if not os.path.exists('generated/images/train/'+targetCountry+'/'): # 檢查train資料夾是否存在
        os.mkdir('generated/images/train/'+targetCountry+'/')
    if not os.path.exists('generated/images/val/'+targetCountry+'/'): # 檢查val資料夾是否存在
        os.mkdir('generated/images/val/'+targetCountry+'/')

    start = time.time()
    while True:
        if(downloadImg(usage)): currentCount += 1 # 回傳為 True 代表找到圖片
        if(currentCount == imgCount): break # 若以找到圖片數已達到一開始所要求數量則停止
    end = time.time()

    print(f'Download {imgCount} image(s) in {round(end-start, 3)} sec(s)')
