from pathlib import Path
from typing import List
import mimetypes


class FileHandler:
    """Utilitários para manipulação de arquivos"""
    
    SUPPORTED_FORMATS = {".pdf", ".png", ".jpg", ".jpeg"}
    
    @staticmethod
    def is_supported(file_path: str) -> bool:
        """Verifica se o formato do arquivo é suportado"""
        return Path(file_path).suffix.lower() in FileHandler.SUPPORTED_FORMATS
    
    @staticmethod
    def get_files_from_directory(directory: str, recursive: bool = False) -> List[str]:
        """Lista arquivos suportados em um diretório"""
        dir_path = Path(directory)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"Diretório não encontrado: {directory}")
        
        pattern = "**/*" if recursive else "*"
        files = []
        
        for file_path in dir_path.glob(pattern):
            if file_path.is_file() and FileHandler.is_supported(str(file_path)):
                files.append(str(file_path))
        
        return files
    
    @staticmethod
    def validate_file(file_path: str, max_size: int = 5242880) -> bool:
        """Valida arquivo (existência, formato, tamanho)"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        if not FileHandler.is_supported(file_path):
            raise ValueError(f"Formato não suportado: {path.suffix}")
        
        if path.stat().st_size > max_size:
            raise ValueError(f"Arquivo muito grande. Máximo: {max_size} bytes")
        
        return True
