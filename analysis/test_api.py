"""
Script to test the analysis API endpoint.
"""
import requests
import json
import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up the API endpoint URL
API_URL = 'http://localhost:8000/api/analyse/'

def test_text_analysis():
    """
    Test text analysis.
    """
    print("\n=== Testing Text Analysis ===")
    
    # Sample text in French
    data = {
        'text': "Aujourd'hui, j'ai eu une réunion très productive avec mon équipe. Nous avons discuté de nouveaux projets et j'ai proposé des idées qui ont été bien reçues. Je me sens motivé et enthousiaste pour la suite."
    }
    
    try:
        # Send the request
        response = requests.post(API_URL, data=data)
        
        # Check the response
        if response.status_code == 200:
            result = response.json()
            print("Analysis successful!")
            print(f"Sentiment: {result.get('sentiment')}")
            print(f"Emotion Score: {result.get('emotion_score')}")
            print(f"Keywords: {', '.join(result.get('keywords', []))}")
            print(f"Topics: {', '.join(result.get('topics', []))}")
            print(f"Summary: {result.get('summary')}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"Error: {e}")

def test_image_analysis():
    """
    Test image analysis.
    """
    print("\n=== Testing Image Analysis ===")
    
    # Path to a sample image
    image_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'img', 'brain-1.png')
    
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return
    
    try:
        # Prepare the files
        files = {
            'image_file': open(image_path, 'rb')
        }
        
        # Send the request
        response = requests.post(API_URL, files=files)
        
        # Check the response
        if response.status_code == 200:
            result = response.json()
            print("Analysis successful!")
            print(f"Image Caption: {result.get('image_caption')}")
            print(f"Image Scene: {result.get('image_scene')}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the file
        if 'files' in locals() and 'image_file' in files:
            files['image_file'].close()

def test_multimodal_analysis():
    """
    Test multimodal analysis (text + image).
    """
    print("\n=== Testing Multimodal Analysis ===")
    
    # Path to a sample image
    image_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'img', 'brain-1.png')
    
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return
    
    try:
        # Prepare the files and data
        files = {
            'image_file': open(image_path, 'rb')
        }
        
        data = {
            'text': "J'ai passé la journée à travailler sur un projet d'intelligence artificielle. C'est fascinant de voir comment les modèles peuvent analyser différents types de données."
        }
        
        # Send the request
        response = requests.post(API_URL, data=data, files=files)
        
        # Check the response
        if response.status_code == 200:
            result = response.json()
            print("Analysis successful!")
            print(f"Sentiment: {result.get('sentiment')}")
            print(f"Emotion Score: {result.get('emotion_score')}")
            print(f"Keywords: {', '.join(result.get('keywords', []))}")
            print(f"Topics: {', '.join(result.get('topics', []))}")
            print(f"Summary: {result.get('summary')}")
            print(f"Image Caption: {result.get('image_caption')}")
            print(f"Image Scene: {result.get('image_scene')}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the file
        if 'files' in locals() and 'image_file' in files:
            files['image_file'].close()

if __name__ == "__main__":
    print("Testing the Analysis API...")
    
    # Test text analysis
    test_text_analysis()
    
    # Test image analysis
    test_image_analysis()
    
    # Test multimodal analysis
    test_multimodal_analysis()

