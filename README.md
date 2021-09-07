# GeoGuessr Agent

## Table of Contents
- [GeoGuessr Agent](#geoguessr-agent)
  - [Table of Contents](#table-of-contents)
  - [Timeline](#timeline)
  - [Data Preparation](#data-preparation)
    - [Google Street View API](#google-street-view-api)
    - [Convert to Country](#convert-to-country)
  - [Model Selection](#model-selection)
  - [Training Process](#training-process)
  - [Result](#result)

## Timeline
- 預計結案時間：2021-12-31
- 採每周Metting模式
- 時間規劃表
  - 找DATA
    - 預計花費時長:1個月
    - 預計方法
  - 選擇、修改和優化 Model
    - 預計花費時長:2個月
  - 結案報告
    - 預計花費時長:1週
  - 彈性時間(三週)


## Data Preparation

### Google Street View API

- API Introduction
  - [Street View Static API Overview](https://developers.google.com/maps/documentation/streetview/overview)
  - The Street View Static API lets you embed a static (non-interactive) Street View panorama or thumbnail into your web page, without the use of JavaScript. The viewport is defined with URL parameters sent through a standard HTTP request, and is returned as a static image.

- URL Parameters
  - example `https://maps.googleapis.com/maps/api/streetview?parameters`
  - size of image `size=400x400`
  - latitude and longitude`location=40.457375,-80.009353`
  - field of view `fov=50`
  - heading direcrtion `heading=180`
  - elevation angle `pitch=0`
  - api key `key=YOUR-API-KEY`

### Convert to Country

- API Introduction
  - [GeoNames Website](http://www.geonames.org/export/)
  - Returns the country name for the given latitude and longitude

- URL Parameters
  - example `http://api.geonames.org/countryCodeJSON?lat=49.03&lng=10.2&username=demo`

## Model Selection

## Training Process

## Result








