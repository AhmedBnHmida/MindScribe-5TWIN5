"""
Image analysis pipeline using Hugging Face models.
"""
import os
import logging
import torch
from PIL import Image
from transformers import (
    pipeline,
    ViTFeatureExtractor,
    ViTForImageClassification,
    VisionEncoderDecoderModel,
    AutoTokenizer,
    AutoProcessor
)

# Configure logging
logger = logging.getLogger(__name__)

# Global variables to store loaded models
image_captioning_model = None
image_captioning_feature_extractor = None
image_captioning_tokenizer = None
scene_processor = None
scene_model = None

def load_models():
    """
    Load all image analysis models.
    This function should be called once during application startup.
    """
    global image_captioning_model, image_captioning_feature_extractor, image_captioning_tokenizer
    global scene_processor, scene_model
    
    logger.info("Loading image analysis models...")
    
    # Determine device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")
    
    try:
        # Image captioning model
        image_captioning_model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
        image_captioning_feature_extractor = ViTFeatureExtractor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
        image_captioning_tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
        
        # Set special tokens
        image_captioning_tokenizer.pad_token = image_captioning_tokenizer.eos_token
        
        # Set generation parameters
        image_captioning_model.config.decoder_start_token_id = image_captioning_tokenizer.bos_token_id
        image_captioning_model.config.eos_token_id = image_captioning_tokenizer.eos_token_id
        image_captioning_model.config.pad_token_id = image_captioning_tokenizer.pad_token_id
        image_captioning_model.config.max_length = 40
        
        # Move model to appropriate device
        image_captioning_model = image_captioning_model.to(device)
        logger.info("Image captioning model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load image captioning model: {e}")
    
    try:
        # Image scene classification model
        scene_processor = AutoProcessor.from_pretrained("google/vit-base-patch16-224")
        scene_model = ViTForImageClassification.from_pretrained("google/vit-base-patch16-224")
        scene_model = scene_model.to(device)
        logger.info("Image scene classification model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load image scene classification model: {e}")


def caption_image(image_path):
    """
    Generate a caption for an image.
    
    Args:
        image_path (str): The path to the image
        
    Returns:
        str: The caption
    """
    if not image_path or not image_captioning_model:
        return ""
    
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return ""
        
        # Open image
        image = Image.open(image_path).convert("RGB")
        
        # Determine device
        device = next(image_captioning_model.parameters()).device
        
        # Process image
        pixel_values = image_captioning_feature_extractor(image, return_tensors="pt").pixel_values.to(device)
        
        # Generate caption
        output_ids = image_captioning_model.generate(pixel_values, max_length=40)
        
        # Decode caption
        caption = image_captioning_tokenizer.decode(output_ids[0], skip_special_tokens=True)
        
        return caption
    except Exception as e:
        logger.error(f"Error captioning image: {e}")
        return ""


def classify_image_scene(image_path):
    """
    Classify the scene in an image.
    
    Args:
        image_path (str): The path to the image
        
    Returns:
        str: The scene classification
    """
    if not image_path or not scene_model:
        return ""
    
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return ""
        
        # Open image
        image = Image.open(image_path).convert("RGB")
        
        # Determine device
        device = next(scene_model.parameters()).device
        
        # Process image
        inputs = scene_processor(images=image, return_tensors="pt").to(device)
        
        # Generate prediction
        with torch.no_grad():
            outputs = scene_model(**inputs)
        
        # Get predicted class
        logits = outputs.logits
        predicted_class_idx = logits.argmax(-1).item()
        
        # Get class label
        label = scene_model.config.id2label[predicted_class_idx]
        
        return label
    except Exception as e:
        logger.error(f"Error classifying image scene: {e}")
        return ""

