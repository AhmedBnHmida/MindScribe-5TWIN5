"""
Tests for the module2_analysis app.
"""
import os
import tempfile
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient

from .models import JournalAnalysis
from .services import analyze_multimodal_content

User = get_user_model()

class AnalysisAPITestCase(TestCase):
    """
    Test case for the analysis API.
    """
    def setUp(self):
        """
        Set up test data.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.api_url = reverse('module2_analysis:api_analyse')
    
    def test_text_analysis(self):
        """
        Test text analysis.
        """
        data = {
            'text': "Aujourd'hui, j'ai eu une réunion très productive avec mon équipe.",
            'user_id': str(self.user.id)
        }
        
        response = self.client.post(self.api_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('sentiment', response.data)
        self.assertIn('keywords', response.data)
        self.assertIn('summary', response.data)
    
    def test_empty_request(self):
        """
        Test that an empty request returns an error.
        """
        response = self.client.post(self.api_url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_audio_analysis(self):
        """
        Test audio analysis with a mock audio file.
        """
        # Create a temporary audio file
        with tempfile.NamedTemporaryFile(suffix='.wav') as temp_file:
            temp_file.write(b'dummy audio content')
            temp_file.seek(0)
            
            # Create a SimpleUploadedFile from the temporary file
            audio_file = SimpleUploadedFile(
                name='test_audio.wav',
                content=temp_file.read(),
                content_type='audio/wav'
            )
            
            # Make the request
            data = {
                'audio_file': audio_file,
                'user_id': str(self.user.id)
            }
            
            response = self.client.post(self.api_url, data, format='multipart')
            
            # Check that the response is valid
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('audio_transcription', response.data)
    
    def test_image_analysis(self):
        """
        Test image analysis with a mock image file.
        """
        # Create a temporary image file
        with tempfile.NamedTemporaryFile(suffix='.jpg') as temp_file:
            temp_file.write(b'dummy image content')
            temp_file.seek(0)
            
            # Create a SimpleUploadedFile from the temporary file
            image_file = SimpleUploadedFile(
                name='test_image.jpg',
                content=temp_file.read(),
                content_type='image/jpeg'
            )
            
            # Make the request
            data = {
                'image_file': image_file,
                'user_id': str(self.user.id)
            }
            
            response = self.client.post(self.api_url, data, format='multipart')
            
            # Check that the response is valid
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('image_caption', response.data)
            self.assertIn('image_scene', response.data)


class AnalysisServiceTestCase(TestCase):
    """
    Test case for the analysis service.
    """
    def test_analyze_text(self):
        """
        Test text analysis service.
        """
        text = "Aujourd'hui, j'ai eu une réunion très productive avec mon équipe."
        
        result = analyze_multimodal_content(text=text)
        
        self.assertIn('sentiment', result)
        self.assertIn('keywords', result)
        self.assertIn('summary', result)
    
    def test_empty_input(self):
        """
        Test that empty input returns default values.
        """
        result = analyze_multimodal_content()
        
        self.assertEqual(result['sentiment'], 'neutre')
        self.assertEqual(result['emotion_score'], 0.5)
        self.assertEqual(result['keywords'], [])
        self.assertEqual(result['summary'], '')

