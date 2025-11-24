import re
from typing import Dict, Any, List
from datetime import datetime


class MatriculaValidator:
    """Validador especializado para matrículas de imóveis"""
    
    @staticmethod
    def validate_cpf(cpf: str) -> bool:
        """Valida CPF brasileiro"""
        cpf = re.sub(r'\D', '', cpf)
        
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False
        
        # Valida primeiro dígito
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digito1 = (soma * 10 % 11) % 10
        
        if int(cpf[9]) != digito1:
            return False
        
        # Valida segundo dígito
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digito2 = (soma * 10 % 11) % 10
        
        return int(cpf[10]) == digito2
    
    @staticmethod
    def validate_cnpj(cnpj: str) -> bool:
        """Valida CNPJ brasileiro"""
        cnpj = re.sub(r'\D', '', cnpj)
        
        if len(cnpj) != 14:
            return False
        
        # Valida primeiro dígito
        multiplicadores1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj[i]) * multiplicadores1[i] for i in range(12))
        digito1 = 0 if soma % 11 < 2 else 11 - (soma % 11)
        
        if int(cnpj[12]) != digito1:
            return False
        
        # Valida segundo dígito
        multiplicadores2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj[i]) * multiplicadores2[i] for i in range(13))
        digito2 = 0 if soma % 11 < 2 else 11 - (soma % 11)
        
        return int(cnpj[13]) == digito2
    
    @staticmethod
    def validate_cep(cep: str) -> bool:
        """Valida formato de CEP"""
        cep = re.sub(r'\D', '', cep)
        return len(cep) == 8
    
    @staticmethod
    def extract_matricula_number(text: str) -> str:
        """Extrai número da matrícula"""
        patterns = [
            r'MATRÍCULA\s*N[ºª°]?\s*:?\s*(\d+[\.\d]*)',
            r'MATRICULA\s*N[ºª°]?\s*:?\s*(\d+[\.\d]*)',
            r'Matrícula\s*:?\s*(\d+[\.\d]*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def extract_registros(text: str) -> List[str]:
        """Extrai registros (R.1, R.2, etc)"""
        pattern = r'R\.\d+'
        return re.findall(pattern, text)
    
    @staticmethod
    def extract_averbacoes(text: str) -> List[str]:
        """Extrai averbações (AV.1, AV.2, etc)"""
        pattern = r'AV\.\d+'
        return re.findall(pattern, text)
    
    @staticmethod
    def has_onus_ativos(text: str) -> bool:
        """Verifica se há ônus ativos"""
        onus_keywords = [
            'hipoteca',
            'penhora',
            'arresto',
            'alienação fiduciária',
            'usufruto'
        ]
        
        text_lower = text.lower()
        
        for keyword in onus_keywords:
            if keyword in text_lower:
                # Verifica se não está cancelado
                if 'cancelad' not in text_lower[max(0, text_lower.find(keyword)-100):text_lower.find(keyword)+100]:
                    return True
        
        return False
    
    @staticmethod
    def validate_area(area_text: str) -> Dict[str, Any]:
        """Valida área do imóvel"""
        pattern = r'(\d+[,\.]?\d*)\s*m[²2]'
        match = re.search(pattern, area_text)
        
        if match:
            area = float(match.group(1).replace(',', '.'))
            return {
                'valid': area > 0,
                'area': area,
                'unit': 'm²'
            }
        
        return {'valid': False, 'area': None, 'unit': None}
    
    @staticmethod
    def validate_structure(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida estrutura completa da matrícula"""
        text = extracted_data.get('raw_text', '')
        
        issues = []
        warnings = []
        
        # Valida número da matrícula
        matricula_num = MatriculaValidator.extract_matricula_number(text)
        if not matricula_num:
            issues.append("Número da matrícula não encontrado")
        
        # Valida registros
        registros = MatriculaValidator.extract_registros(text)
        if not registros:
            issues.append("Nenhum registro de propriedade encontrado (R.1, R.2, etc)")
        
        # Verifica ônus
        if MatriculaValidator.has_onus_ativos(text):
            warnings.append("⚠️ ATENÇÃO: Imóvel possui ônus ativos (hipoteca, penhora, etc)")
        
        # Valida CPF/CNPJ
        cpf_matches = re.findall(r'\d{3}\.\d{3}\.\d{3}-\d{2}', text)
        cnpj_matches = re.findall(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', text)
        
        valid_cpfs = [cpf for cpf in cpf_matches if MatriculaValidator.validate_cpf(cpf)]
        valid_cnpjs = [cnpj for cnpj in cnpj_matches if MatriculaValidator.validate_cnpj(cnpj)]
        
        if not valid_cpfs and not valid_cnpjs:
            issues.append("CPF/CNPJ do proprietário não encontrado ou inválido")
        
        # Valida CEP
        cep_matches = re.findall(r'\d{5}-?\d{3}', text)
        if not cep_matches:
            warnings.append("CEP não encontrado no endereço")
        
        # Valida área
        area_info = MatriculaValidator.validate_area(text)
        if not area_info['valid']:
            issues.append("Área do imóvel não encontrada ou inválida")
        
        # Verifica inscrição municipal
        if not re.search(r'inscri[çc][ãa]o\s+municipal', text, re.IGNORECASE):
            warnings.append("Inscrição municipal (IPTU) não encontrada")
        
        return {
            'matricula_number': matricula_num,
            'registros': registros,
            'averbacoes': MatriculaValidator.extract_averbacoes(text),
            'has_onus': MatriculaValidator.has_onus_ativos(text),
            'area': area_info,
            'valid_cpfs': valid_cpfs,
            'valid_cnpjs': valid_cnpjs,
            'issues': issues,
            'warnings': warnings,
            'is_valid': len(issues) == 0
        }
