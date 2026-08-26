import torch
from ultralytics import YOLO
from torchvision import models, transforms
import torch.nn as nn
from PIL import Image
import os

class DetectionAgent:
    def __init__(self, fire_model_path, landslide_model_path):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Load fire/smoke YOLOv8 model
        self.fire_model = YOLO(fire_model_path)

        # Load landslide ResNet18 model
        self.landslide_model = models.resnet18(weights=None)
        self.landslide_model.fc = nn.Linear(self.landslide_model.fc.in_features, 2)
        self.landslide_model.load_state_dict(torch.load(landslide_model_path, map_location=self.device))
        self.landslide_model.to(self.device)
        self.landslide_model.eval()

        self.landslide_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def detect_fire(self, image_path, conf_threshold=0.4):
        """Run fire/smoke detection. Returns list of detections."""
        results = self.fire_model(image_path, conf=conf_threshold, verbose=False)
        detections = []
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                cls_name = self.fire_model.names[cls_id]
                confidence = float(box.conf[0])
                detections.append({"class": cls_name, "confidence": confidence})
        return detections

    def detect_landslide(self, image_path):
        """Run landslide classification. Returns label + confidence."""
        img = Image.open(image_path).convert('RGB')
        img_tensor = self.landslide_transform(img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.landslide_model(img_tensor)
            probs = torch.softmax(output, dim=1)
            pred = torch.argmax(probs, dim=1).item()
            confidence = float(probs[0][pred])

        label = "Landslide" if pred == 1 else "Non-Landslide"
        return {"class": label, "confidence": confidence}

    def analyze(self, image_path, mode="both"):
        """
        Main entry point. mode: 'fire', 'landslide', or 'both'.
        Returns a unified detection report.
        """
        report = {"image": image_path, "detections": {}}

        if mode in ("fire", "both"):
            report["detections"]["fire"] = self.detect_fire(image_path)

        if mode in ("landslide", "both"):
            report["detections"]["landslide"] = self.detect_landslide(image_path)

        return report


if __name__ == "__main__":
    # Quick local test
    agent = DetectionAgent(
        fire_model_path="models/fire_detection/best.pt",
        landslide_model_path="models/landslide_classification/best_model.pt"
    )

    test_image = "bus.jpg"  # reuse your existing test image, or point to any local image
    result = agent.analyze(test_image, mode="both")

    print("Detection Report:")
    print(result)