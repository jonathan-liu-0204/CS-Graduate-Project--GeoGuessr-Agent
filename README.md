# GeoGuessr Agent

## Table of Contents
- [GeoGuessr Agent](#geoguessr-agent)
  - [Table of Contents](#table-of-contents)
  - [Timeline](#timeline)
  - [Data Preparation](#data-preparation)
    - [Google Street View API](#google-street-view-api)
    - [Convert to Country](#convert-to-country)
    - [Little Widget](#little-widget)
    - [Code Explanation](#code-explanation)
  - [Model Selection](#model-selection)
    - [Finetuning Torchvision Models](#finetuning-torchvision-models)
    - [Model Sample Code](#model-sample-code)
  - [Training Process](#training-process)
  - [Result](#result)

## Timeline
- 預計結案時間：**2021-12-31**
- Meeting 頻率：1次/週
- 時間規劃表
  | Data Preparation | Model Selection | Presentation |
  | :--------------: | :-------------: | :----------: |
  | 1 Month          | 2 Months        | 1 Week       |
- 彈性時間 (三週)

## Data Preparation 

> 先使用 *Street View Image Metadata* 去偵測該位置是否合法(此部分無須消耗 API 使用量)，再利用 *Street View Static API* 去讀取照片，最終再利用 *GeoNames Website* 將其轉換成國家名稱。

### Google Street View API

- API Introduction
  - [Street View Static API Overview](https://developers.google.com/maps/documentation/streetview/overview)
    > *The Street View Static API lets you embed a static (non-interactive) Street View panorama or thumbnail into your web page, without the use of JavaScript. The viewport is defined with URL parameters sent through a standard HTTP request, and is returned as a static image.*
  - [Street View Image Metadata](https://developers.google.com/maps/documentation/streetview/metadata)
    > *The Street View Static API metadata requests provide data about Street View panoramas. Using the metadata, you can find out if a Street View image is available at a given location. Accessing this metadata allows you to customize error behavior in your application.*

- URL Parameters
  - example `https://maps.googleapis.com/maps/api/streetview?parameters`
  - size of image `size=600x400`
  - latitude and longitude `location=40.457375,-80.009353`
  - field of view `fov=90`
  - heading direcrtion `heading=180`
  - elevation angle `pitch=0`
  - api key `key=YOUR-API-KEY`

- Google Street View Coverage
  ![](https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Google_Street_View_coverage.svg/1920px-Google_Street_View_coverage.svg.png)

  - Condition
    - Mostly full coverage (dark blue)
    - Partial converage (light blue)
    - Country size and population 
  - List of qualified countries (65)
    - Asia (11) `Japan` `South Korea` `Singapore` `Malaysia` `Thailand` `Indonesia` `Philippines` `Israel` `Cambodia` `Sri Lanka` `Bangladesh`
    - Europe (34) `UK` `Ireland` `Spain` `Portugal` `Germany` `France` `Netherlands` `Denmark` `Belgium` `Italy` `Switzerland` `Luxembourg` `Poland` `Czechia` `Estonia` `Latvia` `Lithuania` `Austria` `Hungary` `Slovakia` `Slovenia` `Norway` `Sweden` `Finland` `Serbia` `Romania` `Bulgaria` `Croatia` `Greece` `Turkey` `Ukraine` `Albania` `Montenegro` `Russia`
    - North America (2)  `USA` `Canada` 
    - South America (8) `Brazil` `Argentina` `Chile` `Uruguay` `Peru` `Ecuador` `Colombia` `Mexico`
    - Africa (9) `South Africa` `Botswana` `Kenya` `Ghana` `Nigeria` `Lesotho` `Eswatini` `Bolivia`
    - Oceania (2) `Australia` `New Zealand`

### Convert to Country

- API Introduction
  - [GeoNames Website](http://www.geonames.org/export/)
  - *Returns the country name for the given latitude and longitude*

- URL Parameters
  - example `http://api.geonames.org/countryCodeJSON?lat=49.03&lng=10.2&username=demo`

### Little Widget
- [Latitude and Longitude Finder](https://www.latlong.net/)

### Code Explanation
- `dataPreparation.py` 直接在檔案中設定相關資料要求
- `dataPreparationByCsv.py` 將相關要求放置在 `dataPreparation.csv` 並執行連續蒐集

## Model Selection

### Finetuning Torchvision Models

- Source Code
  - [Pytorch Tutorial](https://pytorch.org/tutorials/beginner/finetuning_torchvision_models_tutorial.html)
- Folder Structure
  
  ```
    📦 project
     ┣ 📂generated
     ┃  ┣ 📂images
     ┃  ┃  ┣ 📂train
     ┃  ┃  ┗ 📂val
     ┗  ┗ 📂details
  ```
- Model Choice
  - Resnet
  - Alexnet
  - Densenet
  - Squeezenet
  - VGG
- Notes
  - Tuned Parameters: `Models`, `Data Augmentation`, `Pre-Train`, `Batch Size`, `Learning Rate`, `Decay`...
  - Multiple Models: Continent --> Country
  - Because there are three chances in GeoGuessr Battle Royale, so we decide to also focus on top-3 accuracy (code lines with `## add: top 3 accuracy`)
- Confusion Matrix
  - x-axis: Prediction
  - y-axis: Ground Truth

### Model Sample Code
- Github: bentrevett/pytorch-image-classification
- Link: https://github.com/bentrevett/pytorch-image-classification
- Model Contained:
  - Multilayer Perceptron
  - LeNet
  - AlexNet
  - VGG
  - ResNet

## Training Process
- See More Training Details on [**Google Sheet**](https://docs.google.com/spreadsheets/d/1xkLweQziOTVoZh3IRLCucdoJTCRWPkm7/edit?usp=sharing&ouid=118085605286254605923&rtpof=true&sd=true)

- South America (9)
  - Model `VGG`
  - Accuracy
    - Validation Accuracy `64%`
    - Top-3 Validation Accuracy `87%`
  - Confusion Matrix
- Europe (34)
  - Model `VGG`
  - Accuracy
    - Validation Accuracy `48%`
    - Top-3 Validation Accuracy `73%`
  - Confusion Matrix

## Result

- `agent.py` 使用此檔案進行遊戲輔助
  - press `c` to predict the image
  - press `r` to show the summary
  - press `q` to quit
  - `labels/continent.txt` 表示 label 名稱