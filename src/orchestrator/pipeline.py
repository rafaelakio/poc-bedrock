import logging
from pathlib import Path
from typing import Dict, Any, List
import json
from datetime import datetime

from ..ocr import BedrockOCR
from ..rag import KnowledgeBase, DocumentValidator


class DocumentPipeline:
    """Orquestra o pipeline completo de OCR e validação"""
    
    def __init__(
        self,
        ocr_model_id: str,
        validation_model_id: str,
        embedding_model_id: str,
        knowledge_base_path: str,
        output_path: str = "./output",
        region: str = "us-east-1"
    ):
        self.logger = logging.getLogger(__name__)
        
        # Inicializa componentes
        self.ocr = BedrockOCR(model_id=ocr_model_id, region=region)
        self.knowledge_base = KnowledgeBase(
            knowledge_path=knowledge_base_path,
            embedding_model_id=embedding_model_id,
            region=region
        )
        self.validator = DocumentValidator(
            knowledge_base=self.knowledge_base,
            model_id=validation_model_id,
            region=region
        )
        
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
    
    def process_document(self, document_path: str, custom_prompt: str = None) -> Dict[str, Any]:
        """Processa um documento completo: OCR + Validação"""
        
        self.logger.info(f"Processando documento: {document_path}")
        
        try:
            # Etapa 1: OCR
            self.logger.info("Executando OCR...")
            extracted_data = self.ocr.extract_from_image(document_path, custom_prompt)
            
            # Etapa 2: Validação com RAG
            self.logger.info("Validando com base de conhecimento...")
            validation_result = self.validator.validate(extracted_data)
            
            # Etapa 3: Salva resultado
            result = {
                "timestamp": datetime.now().isoformat(),
                "document_path": document_path,
                "status": "success",
                "result": validation_result
            }
            
            self._save_result(document_path, result)
            
            self.logger.info("Processamento concluído com sucesso")
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao processar documento: {str(e)}")
            error_result = {
                "timestamp": datetime.now().isoformat(),
                "document_path": document_path,
                "status": "error",
                "error": str(e)
            }
            self._save_result(document_path, error_result)
            return error_result
    
    def process_batch(self, document_paths: List[str]) -> List[Dict[str, Any]]:
        """Processa múltiplos documentos"""
        results = []
        
        for doc_path in document_paths:
            result = self.process_document(doc_path)
            results.append(result)
        
        return results
    
    def _save_result(self, document_path: str, result: Dict[str, Any]):
        """Salva resultado do processamento"""
        doc_name = Path(document_path).stem
        output_file = self.output_path / f"{doc_name}_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Resultado salvo em: {output_file}")
