#!/usr/bin/env python3
"""
Exemplos de uso do sistema de OCR com Bedrock
"""

from config.settings import settings
from src.orchestrator import DocumentPipeline
from src.utils import setup_logger


def example_single_document():
    """Exemplo: processar um único documento"""
    
    logger = setup_logger()
    
    pipeline = DocumentPipeline(
        ocr_model_id=settings.ocr_model_id,
        validation_model_id=settings.validation_model_id,
        embedding_model_id=settings.embedding_model_id,
        knowledge_base_path=settings.knowledge_base_path,
        output_path=settings.output_path,
        region=settings.aws_region
    )
    
    # Processa documento
    result = pipeline.process_document("./examples/sample_document.jpg")
    
    print("Resultado:", result)


def example_custom_prompt():
    """Exemplo: usar prompt customizado para extração"""
    
    pipeline = DocumentPipeline(
        ocr_model_id=settings.ocr_model_id,
        validation_model_id=settings.validation_model_id,
        embedding_model_id=settings.embedding_model_id,
        knowledge_base_path=settings.knowledge_base_path,
        output_path=settings.output_path
    )
    
    custom_prompt = """
    Extraia as seguintes informações deste documento:
    1. Número do documento
    2. Nome completo
    3. Data de nascimento
    4. CPF
    5. Endereço completo
    
    Retorne em formato JSON.
    """
    
    result = pipeline.process_document(
        "./examples/sample_rg.jpg",
        custom_prompt=custom_prompt
    )
    
    print("Resultado:", result)


def example_batch_processing():
    """Exemplo: processar múltiplos documentos"""
    
    pipeline = DocumentPipeline(
        ocr_model_id=settings.ocr_model_id,
        validation_model_id=settings.validation_model_id,
        embedding_model_id=settings.embedding_model_id,
        knowledge_base_path=settings.knowledge_base_path,
        output_path=settings.output_path
    )
    
    documents = [
        "./examples/doc1.jpg",
        "./examples/doc2.jpg",
        "./examples/doc3.pdf"
    ]
    
    results = pipeline.process_batch(documents)
    
    for result in results:
        print(f"Documento: {result['document_path']}")
        print(f"Status: {result['status']}")
        print("-" * 50)


if __name__ == "__main__":
    print("Escolha um exemplo:")
    print("1. Processar documento único")
    print("2. Usar prompt customizado")
    print("3. Processar em lote")
    
    choice = input("Opção: ")
    
    if choice == "1":
        example_single_document()
    elif choice == "2":
        example_custom_prompt()
    elif choice == "3":
        example_batch_processing()
    else:
        print("Opção inválida")
