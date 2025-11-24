import boto3
import json
from typing import Dict, Any, List
from ..validators.matricula_validator import MatriculaValidator


class DocumentValidator:
    """Valida documentos extraídos usando RAG e Bedrock"""
    
    def __init__(self, knowledge_base, model_id: str, region: str = "us-east-1"):
        self.knowledge_base = knowledge_base
        self.model_id = model_id
        self.client = boto3.client("bedrock-runtime", region_name=region)
        self.matricula_validator = MatriculaValidator()
    
    def validate(self, extracted_data: Dict[str, Any], document_type: str = None) -> Dict[str, Any]:
        """Valida dados extraídos usando a base de conhecimento"""
        
        # Detecta tipo de documento se não especificado
        if not document_type:
            document_type = self._detect_document_type(extracted_data.get('raw_text', ''))
        
        # Validação especializada para matrícula de imóvel
        specialized_validation = None
        if document_type == 'matricula_imovel':
            specialized_validation = self.matricula_validator.validate_structure(extracted_data)
        
        # Busca padrões relevantes na base de conhecimento
        query = f"Padrões e validações para {document_type}: {extracted_data.get('raw_text', '')[:500]}"
        relevant_docs = self.knowledge_base.search_similar(query, top_k=3)
        
        # Monta contexto com documentos relevantes
        context = self._build_context(relevant_docs)
        
        # Valida usando Bedrock
        validation_result = self._validate_with_bedrock(extracted_data, context, document_type)
        
        # Combina validações
        if specialized_validation:
            validation_result['specialized_validation'] = specialized_validation
            validation_result['issues'] = validation_result.get('issues', []) + specialized_validation.get('issues', [])
            validation_result['warnings'] = specialized_validation.get('warnings', [])
        
        return {
            "extracted_data": extracted_data,
            "document_type": document_type,
            "validation": validation_result,
            "relevant_patterns": relevant_docs
        }
    
    def _detect_document_type(self, text: str) -> str:
        """Detecta o tipo de documento baseado no conteúdo"""
        text_lower = text.lower()
        
        # Matrícula de imóvel
        if any(keyword in text_lower for keyword in ['matrícula', 'matricula', 'registro de imóveis', 'cartório']):
            if any(keyword in text_lower for keyword in ['r.1', 'r.2', 'av.1', 'proprietário', 'área']):
                return 'matricula_imovel'
        
        # Outros tipos
        if 'rg' in text_lower or 'registro geral' in text_lower:
            return 'rg'
        if 'cpf' in text_lower and 'receita federal' in text_lower:
            return 'cpf'
        if 'cnh' in text_lower or 'habilitação' in text_lower:
            return 'cnh'
        if 'nota fiscal' in text_lower or 'nf-e' in text_lower:
            return 'nota_fiscal'
        
        return 'documento_generico'
    
    def _build_context(self, relevant_docs: List[Dict[str, Any]]) -> str:
        """Constrói contexto a partir dos documentos relevantes"""
        context_parts = []
        for i, doc_info in enumerate(relevant_docs, 1):
            doc = doc_info["document"]
            score = doc_info["score"]
            context_parts.append(f"Padrão {i} (relevância: {score:.2f}):\n{doc['content']}\n")
        
        return "\n".join(context_parts)
    
    def _validate_with_bedrock(self, extracted_data: Dict[str, Any], context: str, document_type: str) -> Dict[str, Any]:
        """Valida dados usando Bedrock com contexto RAG"""
        
        prompt = f"""Você é um validador de documentos especializado em documentos brasileiros.

TIPO DE DOCUMENTO: {document_type}

CONTEXTO - Padrões conhecidos de documentos:
{context}

DADOS EXTRAÍDOS:
{extracted_data.get('raw_text', '')}

Analise os dados extraídos e valide com base nos padrões fornecidos.
Retorne um JSON com:
- is_valid: boolean indicando se o documento é válido
- confidence: score de confiança (0-1)
- issues: lista de problemas encontrados
- document_type: tipo de documento identificado
- extracted_fields: campos extraídos e validados (estruturado por seção)
- recommendations: recomendações para correção
- warnings: alertas importantes sobre o documento
"""
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        result = json.loads(response["body"].read())
        validation_text = result["content"][0]["text"]
        
        try:
            validation_json = json.loads(validation_text)
        except json.JSONDecodeError:
            validation_json = {
                "is_valid": False,
                "confidence": 0.0,
                "issues": ["Erro ao processar validação"],
                "raw_response": validation_text
            }
        
        return validation_json
