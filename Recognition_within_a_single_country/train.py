import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler
import numpy as np
import pandas as pd
import seaborn as sns
import torchvision
from torchvision import datasets, models, transforms
import matplotlib.pyplot as plt
import time
import os
import copy

############## TENSORBOARD ##############
from torch.utils.tensorboard import SummaryWriter

exp_name = "1011 US Area 1to4 2-1"                # 設定實驗名稱 (可簡單用代碼，詳細可見 comparison.xlsx) ex.實驗組別/實驗編號
data_dir = "generated/images"   # 設定圖片資料夾位置
model_name = "vgg"              # 選擇 Models (非正式名稱)
num_classes = 8                 # 設定共有多少類別 (手動)
batch_size = 8                  # 取決於擁有多少記憶體
max_epochs = 100                 # 設定訓練過程最大 Epochs 上限
target_acc = 0.7                # 設定目標正確率
feature_extract = False         # 這裡固定為 False (表示去訓練整個 Model)

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
writer = SummaryWriter('runs/' + exp_name)

confusion_matrix = [[0] * num_classes for i in range(num_classes)]                              ## add: confustion matrix

def train_model(model, dataloaders, criterion, optimizer, scheduler, num_epochs, is_inception):
    since = time.time()
    
    val_acc_history = []
    best_model_wts = copy.deepcopy(model.state_dict())
    best_train_acc = 0.0
    best_val_acc = 0.0
    top3_best_train_acc = 0.0
    top3_best_val_acc = 0.0

    for epoch in range(num_epochs):
        print(f'Epoch: {epoch+1}')
        print('-' * 15)

        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
            else:
                model.eval()
            
            running_loss = 0.0
            running_corrects = 0
            top3_running_corrects = 0                                                           ## add: top 3 accuracy

            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == 'train'):
                    if is_inception and phase == 'train':
                        outputs, aux_outputs = model(inputs)
                        loss1 = criterion(outputs, labels)
                        loss2 = criterion(aux_outputs, labels)
                        loss = loss1 + 0.4 * loss2
                    else:
                        outputs = model(inputs)
                        loss = criterion(outputs, labels)
                    
                    _, preds = torch.max(outputs, 1)
                    _, top3_preds = torch.topk(outputs, 3, 1)                                   ## add: top 3 accuracy

                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)
                top3_labels = labels.data.reshape(labels.data.shape[0], 1)                      ## add: top 3 accuracy
                top3_running_corrects += torch.sum(top3_labels == top3_preds)                   ## add: top 3 accuracy
                
                if (epoch == num_epochs-1 and phase == 'val'):                                  ## add: confustion matrix
                    for batch_index in range(labels.data.shape[0]):
                        confusion_matrix[labels.data[batch_index].item()][preds[batch_index].item()] += 1

            if phase == 'train':
                scheduler.step()

            epoch_loss = running_loss / len(dataloaders[phase].dataset)
            epoch_acc = running_corrects.double() / len(dataloaders[phase].dataset)
            top3_epoch_acc = top3_running_corrects.double() / len(dataloaders[phase].dataset)   ## add: top 3 accuracy

            print('{}\tLoss: {:.4f}\tAcc: {:.4f}\tTop 3 Acc: {:.4f}'.format(phase.upper(), epoch_loss, epoch_acc, top3_epoch_acc))
            
            if phase == 'train':
                writer.add_scalar('Training Loss', epoch_loss, epoch)
                writer.add_scalar('Training Acc', epoch_acc, epoch)
                writer.add_scalar('Top 3 Training Acc', top3_epoch_acc, epoch)                  ## add: top 3 accuracy
            else:
                writer.add_scalar('Validation Loss', epoch_loss, epoch)
                writer.add_scalar('Validation Acc', epoch_acc, epoch)
                writer.add_scalar('Top 3 Validation Acc', top3_epoch_acc, epoch)                ## add: top 3 accuracy

            if phase == 'train' and epoch_acc > best_train_acc:
                best_train_acc = epoch_acc
                #best_model_wts = copy.deepcopy(model.state_dict())
            if phase == 'val' and epoch_acc > best_val_acc:
                best_val_acc = epoch_acc
                best_model_wts = copy.deepcopy(model.state_dict())
            if phase == 'train' and top3_epoch_acc > top3_best_train_acc:
                top3_best_train_acc = top3_epoch_acc
                #best_model_wts = copy.deepcopy(model.state_dict())
            if phase == 'val' and top3_epoch_acc > top3_best_val_acc:
                top3_best_val_acc = top3_epoch_acc
                #best_model_wts = copy.deepcopy(model.state_dict())
            if phase == 'val':
                val_acc_history.append(epoch_acc)
        
        print()
        if(best_val_acc >= target_acc):
            break
    
    time_elapsed = time.time() - since
    print('Training complete in {:.0f}m {:.0f}s'.format(time_elapsed // 60, time_elapsed % 60))
    print(f'Best Train Acc: {best_train_acc}')
    print(f'Best Val Acc: {best_val_acc}')
    print(f'Top 3 Best Train Acc: {top3_best_train_acc}')
    print(f'Top 3 Best Val Acc: {top3_best_val_acc}')
    print()

    model.load_state_dict(best_model_wts)
    return model, val_acc_history

# Notice that inception_v3 requires the input size to be (299,299), whereas all of the other models expect (224,224).
def initialize_model(model_name, num_classes, feature_extract, use_pretrained=False):
    model_ft, input_size = None, 0

    if model_name == 'resnet': # Example: Resnet18
        model_ft = models.resnet18(pretrained=use_pretrained)
        set_parameter_requires_grad(model_ft, feature_extract)
        num_ftrs = model_ft.fc.in_features
        model_ft.fc = nn.Linear(num_ftrs, num_classes)
        input_size = 224

    elif model_name == 'alexnet':
        model_ft = models.alexnet(pretrained=use_pretrained)
        set_parameter_requires_grad(model_ft, feature_extract)
        num_ftrs = model_ft.classifier[6].in_features
        model_ft.classifier[6] = nn.Linear(num_ftrs,num_classes)
        input_size = 224

    elif model_name == 'vgg': # Example: VGG-11
        model_ft = models.vgg11_bn(pretrained=use_pretrained)
        set_parameter_requires_grad(model_ft, feature_extract)
        num_ftrs = model_ft.classifier[6].in_features
        model_ft.classifier[6] = nn.Linear(num_ftrs,num_classes)
        input_size = 224

    elif model_name == 'squeezenet': # Example: Version 1.0
        model_ft = models.squeezenet1_0(pretrained=use_pretrained)
        set_parameter_requires_grad(model_ft, feature_extract)
        model_ft.classifier[1] = nn.Conv2d(512, num_classes, kernel_size=(1,1), stride=(1,1))
        model_ft.num_classes = num_classes
        input_size = 224

    elif model_name == 'densenet': # Example: Densenet-121
        model_ft = models.densenet121(pretrained=use_pretrained)
        set_parameter_requires_grad(model_ft, feature_extract)
        num_ftrs = model_ft.classifier.in_features
        model_ft.classifier = nn.Linear(num_ftrs, num_classes)
        input_size = 224

    else:
        print("Invalid Model Name......")
        exit()

    return model_ft, input_size

# If transfer learning...
def set_parameter_requires_grad(model, feature_extracting):
    if feature_extracting:
        for param in model.parameters():
            param.requires_grad = False

##### Initialize and Reshape the Networks #####
model_ft, input_size = initialize_model(model_name, num_classes, feature_extract, use_pretrained=True)
print(model_ft)

########## Load Data From Directory ##########
data_transforms = {
    # Notice, the models were pretrained with the hard-coded normalization values
    'train': transforms.Compose([
        transforms.RandomResizedCrop(input_size),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'val': transforms.Compose([
        transforms.Resize(input_size),
        transforms.CenterCrop(input_size),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
}

print("Initializing Datasets and Dataloaders...")

image_datasets = {x: datasets.ImageFolder(os.path.join(data_dir, x), data_transforms[x]) for x in ['train', 'val']}
dataloaders_dict = {x: torch.utils.data.DataLoader(image_datasets[x], batch_size=batch_size, shuffle=True, num_workers=0) for x in ['train', 'val']}
class_names = image_datasets['train'].classes

print(f'Class Names: {class_names} on Device: {device}')

#### Create the Optimizer and Loss Function ####
model_ft = model_ft.to(device)
params_to_update = model_ft.parameters()

optimizer_ft = optim.SGD(params_to_update, lr=0.005, momentum=0.9)
criterion = nn.CrossEntropyLoss()

###### Run Training and Validation Step ######
step_lr_scheduler = lr_scheduler.StepLR(optimizer_ft, step_size=5, gamma=0.5)
model_ft, history = train_model(model_ft, dataloaders_dict, criterion, optimizer_ft, step_lr_scheduler, num_epochs=max_epochs, is_inception=False)

# ########### Saving The Model ###########
save_path = 'models/area1to4/' + '2-1.pth'
torch.save(model_ft, save_path)

######### Show Confusion Matrix #########
for i in range(len(class_names)):
    total_val_amount = np.sum(confusion_matrix[i])
    for j in range(len(class_names)):
        confusion_matrix[i][j] = confusion_matrix[i][j] / total_val_amount
df_cm = pd.DataFrame(confusion_matrix, class_names, class_names)
plt.figure(figsize=(21,14))
sns.heatmap(df_cm, annot=True, fmt=".2f", cmap='BuGn')
plt.xlabel("Prediction", fontsize=18)
plt.ylabel("Ground Truth", fontsize=18)
fig_name = exp_name.replace('/', '-')
plt.savefig('figures/' + fig_name + '.png')
img = Image.open('figures/' + fig_name + '.png')
img.show()