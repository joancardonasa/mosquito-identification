import pytest
from app.ai_classifier import AIClassifier
from PIL import Image

class TestAIClassifier:
    def test_classify_returns_valid_species(self, tmp_path):
        dummy_image = tmp_path/"mosquito.jpg"

        img = Image.new("RGB", (1, 1), color="white")
        img.save(dummy_image)

        classifier = AIClassifier()
        result = classifier.classify(str(dummy_image))

        assert result in AIClassifier.SPECIES
