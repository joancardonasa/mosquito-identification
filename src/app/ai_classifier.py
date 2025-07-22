import random
import numpy as np
from PIL import Image

class MosquitoClassifierModel:
    pass


class AIClassifier:
    SPECIES = ['species1', 'species2', 'species3', 'species4', None]

    def train():
        """
        Process that would change the model's weights, should be stored somewhere like S3
        and brought into cache to classify when needed

        We would need to feed
        """
        pass

    def get_model(model_name: str) -> MosquitoClassifierModel:
        """
        Find model location and bring it in for use
        """
        pass

    def classify(self, photo_location: str = ""):
        img = Image.open(photo_location)
        img_array = np.array(img) # We would use this img_array to perform the actual classification

        # model = get_model("mosquito_classifier_v2.1")
        return random.choice(self.SPECIES)
