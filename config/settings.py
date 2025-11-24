from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # AWS
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    
    # Bedrock Models
    ocr_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    embedding_model_id: str = "amazon.titan-embed-text-v1"
    validation_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    # Application
    max_image_size: int = 5242880  # 5MB
    knowledge_base_path: str = "./knowledge_base"
    output_path: str = "./output"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
