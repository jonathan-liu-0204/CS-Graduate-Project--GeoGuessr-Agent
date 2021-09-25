# GeoGuessr Agent

## Table of Contents
- [GeoGuessr Agent](#geoguessr-agent)
  - [Table of Contents](#table-of-contents)
  - [Timeline](#timeline)
  - [Data Preparation](#data-preparation)
    - [Google Street View API](#google-street-view-api)
    - [Convert to Country](#convert-to-country)
  - [Model Selection](#model-selection)
    - [Finetuning Torchvision Models](#finetuning-torchvision-models)
    - [Number of Models](#number-of-models)
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
  - List of qualified countries (75)
    - Asia (19) `Russia` `Japan` `South Korea` `Taiwan` `Singapore` `Malaysia` `Thailand` `Indonesia` `Philippines` `Israel` `Cambodia` `Sri Lanka` `Vietnam` `Mongolia` `Bhutan` `Bangladesh` `India` `Kyrgyzstan` `UAE`
    - Europe (35) `UK` `Ireland` `Iceland` `Spain` `Portugal` `Germany` `France` `Netherlands` `Denmark` `Belgium` `Italy` `Switzerland` `Luxembourg` `Poland` `Czechia` `Estonia` `Latvia` `Lithuania` `Austria` `Hungary` `Slovakia` `Slovenia` `Norway` `Sweden` `Finland` `Serbia` `Romania` `Bulgaria` `Croatia` `Greece` `Turkey` `Ukraine` `Albania` `Montenegro` `North Macedonia`
    - North America (3)  `USA` `Canada` `Mexico`
    - South America (8) `Brazil` `Argentina` `Chile` `Uruguay` `Peru` `Ecuador` `Colombia` `Bolivia`
    - Africa (8) `South Africa` `Botswana` `Kenya` `Ghana` `Senegal` `Nigeria` `Lesotho` `Eswatini`
    - Oceania (2) `Australia` `New Zealand`

### Convert to Country

- API Introduction
  - [GeoNames Website](http://www.geonames.org/export/)
  - *Returns the country name for the given latitude and longitude*

- URL Parameters
  - example `http://api.geonames.org/countryCodeJSON?lat=49.03&lng=10.2&username=demo`

## Model Selection

### Finetuning Torchvision Models

- Source Code
  - [Pytorch Tutorial](https://pytorch.org/tutorials/beginner/finetuning_torchvision_models_tutorial.html)

### Number of Models

- 橫向拓展
  - 將一個地點用多張圖片代表而非一張，例如四個方位各取一張照片
- 縱向拓展
  - 將分類分層，例如先區分出七大洲再去尋找國家

## Training Process

## Result
