import unittest
from unittest.mock import Mock, patch, MagicMock
from src.ocr import BedrockOCR


class TestBedrockOCR(unittest.TestCase):
    
    def setUp(self):
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        self.region = "us-east-1"
    
    @patch('boto3.client')
    def test_ocr_initialization(self, mock_boto_client):
        """Testa inicialização do OCR"""
        ocr = BedrockOCR(model_id=self.model_id, region=self.region)
        
        self.assertEqual(ocr.model_id, self.model_id)
        mock_boto_client.assert_called_once_with("bedrock-runtime", region_name=self.region)
    
    @patch('boto3.client')
    @patch('PIL.Image.open')
    def test_extract_from_image(self, mock_image_open, mock_boto_client):
        """Testa extração de dados de imagem"""
        # Mock do cliente Bedrock
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        
        # Mock da resposta do Bedrock
        mock_response = {
            "body": MagicMock()
        }
        mock_response["body"].read.return_value = b'{"content": [{"text": "Dados extraídos"}]}'
        mock_client.invoke_model.return_value = mock_response
        
        # Mock da imagem
        mock_img = MagicMock()
        mock_img.mode = "RGB"
        mock_image_open.return_value.__enter__.return_value = mock_img
        
        ocr = BedrockOCR(model_id=self.model_id, region=self.region)
        result = ocr.extract_from_image("test.jpg")
        
        self.assertIn("raw_text", result)
        self.assertEqual(result["model_id"], self.model_id)


if __name__ == '__main__':
    unittest.main()
