import random, time, os
import requests, json
from PIL import Image
from io import BytesIO
import csv

size, fov, heading, pitch = "600x300", "90", "0", "0" # 設定 Google Street View 當中的 URL 參數 (圖片呈現格式)

imageKey = ""
checkKey = "" # 將 Key 分兩支以確認 checkKey 不會消耗使用量
StateKey = ""

currentCount = 0 # 目前已找到多少張圖片

imgCount, targetState, usage, latRange, latMin, lngRange, lngMin = [], [], [], [], [], [], []

def downloadImg(imgCount, targetState, usage, latRange, latMin, lngRange, lngMin):
    lat, lng = (random.random() * float(latRange)) + float(latMin),  (random.random() * float(lngRange)) + float(lngMin) # 隨機數產生經緯度(在目標國家範圍下)
    location = str(lat) + ',' + str(lng)
    checkUrl = "https://maps.googleapis.com/maps/api/streetview/metadata?location=" + location + "&key=" + checkKey
    # print(checkUrl)
    viewUrl = "https://maps.googleapis.com/maps/api/streetview?size=" + size + "&location=" + location + "&fov=" + fov + "&heading="+ heading + "&pitch=" + pitch + "&key=" + imageKey + "&return_error_code=true"
    checkRresponse = requests.get(checkUrl)
    checkDetail = json.loads(checkRresponse.text)
    if checkDetail["status"] == "OK": # 回傳值為OK代表合法經緯度，若為REQUEST_DENIED or ZERO_RESULTS則為非法

        StateURL = "https://maps.googleapis.com/maps/api/geocode/json?latlng=" + location + "&key=" + StateKey
        StateChecking = requests.get(StateURL)
        ReturnStateInfo = json.loads(StateChecking.text)
        statecode = ReturnStateInfo["plus_code"]["compound_code"].split(",")

        #print(targetState, " ---> ", statecode[1])
        
        if(StateChecking.text.find('no country code found') != -1):
            return False # 此部分情況是合法的經緯度但並非我們的目標地區
        if(statecode[1] == targetState): # 若此合法經緯度位於我們設定的目標地區
            viewRresponse = requests.get(viewUrl)
            img = Image.open(BytesIO(viewRresponse.content)) # 轉成 img 供以後做處理
            img.save("./generated/images/" + usage + "/" + targetState + '/' + location + ".jpg") # 將圖片儲存在路徑 'generated/images/{state}}/'
            print(f'Number: {currentCount+1}/{imgCount}\tLocation: {tuple((lat, lng))}\tState: {targetState}') # 印出其經緯度及對應的地區名稱 (供未來作為 ground truth)
            writeDetails("Location: " + str(tuple((lat, lng))) + "\tState: " + targetState + "\tUsage: " + usage + '\n', targetState) # 將地理位置存入 .txt
            return True # 此部分情況是合法的經緯度且位於我們的目標地區  
        else:
            print(statecode[1])
            print("NO!! " + location + " NOT IN THE STATE!!!!")     
        return False # 此部分情況是合法的經緯度
    return False # 此部分情況是非法的經緯度

def writeDetails(string, targetState):
    path = 'generated/details/' + targetState + '.txt'
    with open(path, 'a') as file:
        file.write(string)

def readFromCsv():
    with open('dataPreparation.csv', newline='') as csvfile:
        rows = csv.DictReader(csvfile)
        for row in rows:
            imgCount.append(int(row['imgCount']))
            targetState.append(row['targetState'])
            usage.append(row['usage'])
            latRange.append(row['latRange'])
            latMin.append(row['latMin'])
            lngRange.append(row['lngRange'])
            lngMin.append(row['lngMin'])


if __name__ == '__main__':
    
    readFromCsv()

    if not os.path.exists('generated/'):
        os.mkdir('generated/') # 產生 generated 及 images 資料夾
        os.mkdir('generated/images/')
        os.mkdir('generated/details/')
        os.mkdir('generated/images/train/')
        os.mkdir('generated/images/val/')
    
    for i in range(len(targetState)):
        if not os.path.exists('generated/images/train/'+targetState[i]+'/'): # 檢查train資料夾是否存在
            os.mkdir('generated/images/train/'+targetState[i]+'/')
        if not os.path.exists('generated/images/val/'+targetState[i]+'/'): # 檢查val資料夾是否存在
            os.mkdir('generated/images/val/'+targetState[i]+'/')

        currentCount = 0
        start = time.time()
        while True:
            if(downloadImg(imgCount[i], targetState[i], usage[i], latRange[i], latMin[i], lngRange[i], lngMin[i])): currentCount += 1 # 回傳為 True 代表找到圖片
            if(currentCount == imgCount[i]): break # 若以找到圖片數已達到一開始所要求數量則停止
        end = time.time()

        
        print(f'Download {imgCount[i]} image(s) in {round(end-start, 3)} sec(s)')
