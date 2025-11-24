import boto3
import json
from pathlib import Path
from typing import List, Dict, Any
import numpy as np


class KnowledgeBase:
    """Gerencia a base de conhecimento para validação de documentos"""
    
    def __init__(self, knowledge_path: str, embedding_model_id: str, region: str = "us-east-1"):
        self.knowledge_path = Path(knowledge_path)
        self.embedding_model_id = embedding_model_id
        self.client = boto3.client("bedrock-runtime", region_name=region)
        self.documents = []
        self.embeddings = []
        
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Carrega documentos da base de conhecimento"""
        if not self.knowledge_path.exists():
            self.knowledge_path.mkdir(parents=True, exist_ok=True)
            return
        
        for file_path in self.knowledge_path.glob("*.txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.documents.append({
                    "filename": file_path.name,
                    "content": content
                })
    
    def add_document(self, content: str, metadata: Dict[str, Any] = None):
        """Adiciona documento à base de conhecimento"""
        doc = {
            "content": content,
            "metadata": metadata or {}
        }
        self.documents.append(doc)
    
    def get_embedding(self, text: str) -> List[float]:
        """Gera embedding usando Bedrock"""
        body = json.dumps({"inputText": text})
        
        response = self.client.invoke_model(
            modelId=self.embedding_model_id,
            body=body
        )
        
        result = json.loads(response["body"].read())
        return result["embedding"]
    
    def search_similar(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Busca documentos similares usando embeddings"""
        if not self.documents:
            return []
        
        query_embedding = self.get_embedding(query)
        
        # Gera embeddings dos documentos se ainda não existem
        if not self.embeddings:
            for doc in self.documents:
                emb = self.get_embedding(doc["content"])
                self.embeddings.append(emb)
        
        # Calcula similaridade
        similarities = []
        for i, doc_emb in enumerate(self.embeddings):
            similarity = self._cosine_similarity(query_embedding, doc_emb)
            similarities.append((i, similarity))
        
        # Ordena e retorna top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for idx, score in similarities[:top_k]:
            results.append({
                "document": self.documents[idx],
                "score": score
            })
        
        return results
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcula similaridade de cosseno entre dois vetores"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
