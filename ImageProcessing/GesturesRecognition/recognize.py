import torch
import numpy as np
import torchvision.transforms.functional as F
from PIL import Image
from torchvision import transforms
from torchvision.utils import save_image
from os import listdir
from dataclasses import dataclass
import cv2

from .architecture import Net


LANDMARKS_LINKS = {
    0: [1, 5, 17],
    1: [2],
    2: [3],
    3: [4],
    5: [6, 9],
    6: [7],
    7: [8],
    9: [10, 13],
    10: [11],
    11: [12],
    13: [14, 17],
    14: [15],
    15: [16],
    17: [18],
    18: [19],
    19: [20]
}
GESTURES = {
    0: 'finger',
    1: 'fist',
    2: 'palm',
    3: 'peace'
}


@dataclass
class ImageShape:
    x: int
    y: int

    def __iter__(self):
        yield self.x
        yield self.y


class Recognizer:
	transform = transforms.Compose([
		transforms.ToTensor(),
		transforms.Normalize(mean=[0.5], std=[0.5])
	])
	device = "cuda" if torch.cuda.is_available() else "cpu"
	OUTPUT_SHAPE = ImageShape(28, 28)

	def __init__(self):
		self._load_model()
	
	def recognize_gesture(self, landmarks) -> Image:
		image = self._convert_to_image(landmarks)
		image = self.transform(image)
		image = image.unsqueeze(0).to(self.device)
		if torch.cuda.is_available():
			self.model.cuda()
		result = self.model(image)
		probability = torch.softmax(result.squeeze(), dim=0)
		gesture = probability.argmax()
		return GESTURES[gesture.item()]
	
	def _convert_to_image(self, landmarks):
		x = [landmark.x for landmark in landmarks.hand_landmarks[0]]
		y = [landmark.y for landmark in landmarks.hand_landmarks[0]]
		min_x = min(x)
		max_x = max(x)
		min_y = min(y)
		max_y = max(y)
		x_norm = [int((value - min_x) / (max_x - min_x) * (self.OUTPUT_SHAPE.x - 1)) for value in x]
		y_norm = [int((value - min_y) / (max_y - min_y) * (self.OUTPUT_SHAPE.y - 1)) for value in y]

		blank_img = np.zeros(tuple(self.OUTPUT_SHAPE), np.uint8)
		for idx_from, target in LANDMARKS_LINKS.items():
			for idx_to in target:
				blank_img = cv2.line(blank_img, (x_norm[idx_from], y_norm[idx_from]), (x_norm[idx_to], y_norm[idx_to]), (255, 255, 255), 1)
		return blank_img
	
	def _load_model(self) -> None:
		path = 'ImageProcessing/GesturesRecognition/models/hand_recognition_model.pth.tar'
		model = Net(input_shape=1,
			  hidden_units=10,
			  output_shape=4)
		model.load_state_dict(torch.load(path))
		model.eval()
		self.model = model
		