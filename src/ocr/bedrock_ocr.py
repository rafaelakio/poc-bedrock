import boto3
import base64
import json
from typing import Dict, Any, Optional
from pathlib import Path
from PIL import Image
import io


class BedrockOCR:
    """Cliente para OCR usando AWS Bedrock com modelos multimodais"""
    
    def __init__(self, model_id: str, region: str = "us-east-1"):
        self.model_id = model_id
        self.client = boto3.client("bedrock-runtime", region_name=region)
    
    def extract_from_image(self, image_path: str, prompt: Optional[str] = None) -> Dict[str, Any]:
        """Extrai texto e dados estruturados de uma imagem"""
        
        image_data = self._load_image(image_path)
        
        if prompt is None:
            prompt = """Analise este documento e extraia todas as informações relevantes.
            Retorne os dados em formato JSON estruturado com os seguintes campos quando aplicável:
            - tipo_documento
            - numero_documento
            - data_emissao
            - dados_pessoais (nome, cpf, rg, etc)
            - valores_monetarios
            - datas_importantes
            - texto_completo
            """
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        result = json.loads(response["body"].read())
        extracted_text = result["content"][0]["text"]
        
        return {
            "raw_text": extracted_text,
            "model_id": self.model_id,
            "source": image_path
        }
    
    def _load_image(self, image_path: str) -> str:
        """Carrega e converte imagem para base64"""
        with Image.open(image_path) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=95)
            image_bytes = buffer.getvalue()
            
            return base64.b64encode(image_bytes).decode("utf-8")
