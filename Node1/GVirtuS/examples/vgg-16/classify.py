import torch
from torchvision import models, transforms
from PIL import Image

# Load pretrained VGG-16
model = models.vgg16(pretrained=True)
model.eval()

# Define preprocessing (resize, center crop, normalize with ImageNet stats)
preprocess = transforms.Compose([
    transforms.Resize(256),               # Resize smaller edge to 256
    transforms.CenterCrop(224),           # Crop to 224x224
    transforms.ToTensor(),                # Convert PIL Image to tensor
    transforms.Normalize(                 # Normalize using ImageNet mean/std
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225])
])

# Load your image (replace 'your_image.jpg' with your file)
img = Image.open('image.jpg').convert('RGB')

# Preprocess the image
input_tensor = preprocess(img)

# Create a mini-batch as expected by the model (batch size 1)
input_batch = input_tensor.unsqueeze(0)  # shape: [1, 3, 224, 224]

# Run inference
with torch.no_grad():
    output = model(input_batch)

# Get the predicted class index
_, predicted_idx = torch.max(output, 1)

# Load ImageNet labels to map the predicted_idx to human-readable label
# You can download labels from: https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt
with open('imagenet_classes.txt') as f:
    labels = [line.strip() for line in f.readlines()]

print(f'Predicted class: {labels[predicted_idx]}')
