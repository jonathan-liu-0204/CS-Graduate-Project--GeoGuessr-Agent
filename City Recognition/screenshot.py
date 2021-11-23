from PIL import ImageGrab
import keyboard, os, time

SCREEN = (500, 325, 1500, 775)

countryName = "Taiwan"
cityName = "Taipei"
usage = "train"
imageCount = 1

if __name__ == '__main__':
    if not os.path.exists('generated/cities/' + usage + '/' + countryName):
        os.mkdir('generated/cities/' + usage + '/' + countryName)
    while True:
        if keyboard.is_pressed('c'):
            img = ImageGrab.grab(bbox=SCREEN)
            img = img.convert('RGB')
            savePath = 'generated/cities/' + usage + '/' + countryName + '/' + cityName + '-' + str(imageCount) + '.jpg'
            img.save(savePath)
            print(f'Image {imageCount} saved in {countryName}, {cityName}')
            imageCount += 1
            time.sleep(1)
        elif keyboard.is_pressed('q'):
            print(f'Total image count {imageCount-1} in {countryName}, {cityName}')
            break

