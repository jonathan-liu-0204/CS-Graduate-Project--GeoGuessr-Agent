from PIL import ImageGrab
import colorama
from torchvision import transforms
import torch
import time
import keyboard

SCREEN = (500, 325, 1500, 775)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
colorama.init()

model_path, label_path = 'models/final.pth', 'labels/world.txt'  # Your Model / Label Location
num_classes = 66                                                 # Number of Classes
test_count = 0
history = [ 0.0 ] * num_classes
best = [ 0.0, "CountryName"]
labels = []
yes = ['Y', 'y']

class bcolors:
    PERFECT_BACK = '\033[42m'
    GREAT_BACK = '\033[44m'
    GOOD_BACK = '\033[43m'
    BAD_BACK = '\033[100m'
    NORMAL_BACK = '\033[47m'
    SUMMARY_BACK = '\033[41m'
    PERFECT = '\033[92m'
    GREAT = '\033[94m'
    GOOD = '\033[93m'
    BAD = '\033[90m'
    SUMMARY = '\033[91m'
    ENDC = '\033[0m'    

def model_loading(model_path):
    # model = models.vgg11_bn(pretrained=False)
    # num_ftrs = model.classifier[6].in_features
    # model.classifier[6] = nn.Linear(num_ftrs, num_classes)
    # model.load_state_dict(torch.load(model_path))
    model = torch.load(model_path)
    model = model.to(device)
    return model

def data_preprocessing(image):
    preprocess = transforms.Compose([
        transforms.Resize(224),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    return torch.unsqueeze(preprocess(image), 0)

def predicting(model, image):
    model.eval()
    image = image.to(device)
    out = model(image)
    
    percentage = torch.nn.functional.softmax(out, dim=1)[0] * 100
    _, index = torch.max(out, 1)
    _, indices = torch.sort(out, descending=True)

    if percentage[index[0]].item() > best[0]:
        best[0] = percentage[index[0]].item()
        best[1] = labels[index[0]]

    if percentage[index[0]].item() > 90:
        print(f'{bcolors.PERFECT_BACK} PERFECT {bcolors.ENDC}', end =" ")
    elif percentage[index[0]].item() > 80:
        print(f'{bcolors.GREAT_BACK}  GREAT  {bcolors.ENDC}', end =" ")
    elif percentage[index[0]].item() > 70:
        print(f'{bcolors.GOOD_BACK}  GOOD   {bcolors.ENDC}', end =" ")
    elif percentage[index[0]].item() < 40:
        print(f'{bcolors.BAD_BACK}   BAD   {bcolors.ENDC}', end =" ")
    else:
        print(f'{bcolors.NORMAL_BACK}         {bcolors.ENDC}', end =" ")

    for idx in indices[0][:3]:
        if(percentage[idx].item() > 90):
            print(f'{bcolors.PERFECT}{labels[idx]} ({round(percentage[idx].item(), 2)}) {bcolors.ENDC}', end =" ")
        elif(percentage[idx].item() > 80):
            print(f'{bcolors.GREAT}{labels[idx]} ({round(percentage[idx].item(), 2)}) {bcolors.ENDC}', end =" ")
        elif(percentage[idx].item() > 70):
            print(f'{bcolors.GOOD}{labels[idx]} ({round(percentage[idx].item(), 2)}) {bcolors.ENDC}', end =" ")
        elif(percentage[idx].item() < 40):
            print(f'{bcolors.BAD}{labels[idx]} ({round(percentage[idx].item(), 2)}) {bcolors.ENDC}', end =" ")
        else:
            print(f'{labels[idx]} ({round(percentage[idx].item(), 2)})', end =" ")
        
        history[idx.item()] += percentage[idx].item()    
    print()

def summary():
    print()
    print(f'{bcolors.SUMMARY_BACK} SUMMARY {bcolors.ENDC}', end =" ")
    for _ in range(3):
        index_max = max(range(len(history)), key=history.__getitem__)
        print(f'{bcolors.SUMMARY}{labels[index_max]}{bcolors.ENDC}', end ="  ")
        history[index_max] = 0.0
    print(f'ranked since checkpoint with single best result {round(best[0], 2)}% in {best[1]}')
    print()

def initialize():
    return 0, [ 0.0 ] * num_classes, [ 0.0, "CountryName"]

if __name__ == '__main__':
    target_model = model_loading(model_path)
    img = ImageGrab.grab(bbox=SCREEN)
    img.show()
    if input("Check the image and press [Y/y] to start, others to quit: ") not in yes:
        exit(0)

    with open(label_path) as f:
        labels = [line.strip() for line in f.readlines()]

    while True:
        if keyboard.is_pressed('e'):
            img = ImageGrab.grab(bbox=SCREEN)
            img = img.convert('RGB')
            image = data_preprocessing(img)
            predicting(target_model, image)
            time.sleep(0.5)
            test_count += 1
        elif keyboard.is_pressed('t'):
            summary()         
            test_count, history, best = initialize()
            time.sleep(0.5)
        elif keyboard.is_pressed('q'):
            exit(0)
