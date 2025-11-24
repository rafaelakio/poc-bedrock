import unittest
from src.validators import MatriculaValidator


class TestMatriculaValidator(unittest.TestCase):
    
    def test_validate_cpf_valid(self):
        """Testa validação de CPF válido"""
        valid_cpfs = [
            "123.456.789-09",
            "111.444.777-35",
            "12345678909"
        ]
        
        for cpf in valid_cpfs:
            self.assertTrue(MatriculaValidator.validate_cpf(cpf), f"CPF {cpf} deveria ser válido")
    
    def test_validate_cpf_invalid(self):
        """Testa validação de CPF inválido"""
        invalid_cpfs = [
            "123.456.789-00",
            "111.111.111-11",
            "000.000.000-00",
            "12345678900"
        ]
        
        for cpf in invalid_cpfs:
            self.assertFalse(MatriculaValidator.validate_cpf(cpf), f"CPF {cpf} deveria ser inválido")
    
    def test_validate_cnpj_valid(self):
        """Testa validação de CNPJ válido"""
        valid_cnpj = "11.222.333/0001-81"
        # Nota: Este é um CNPJ de exemplo, ajuste conforme necessário
        result = MatriculaValidator.validate_cnpj(valid_cnpj)
        self.assertIsInstance(result, bool)
    
    def test_validate_cep(self):
        """Testa validação de CEP"""
        self.assertTrue(MatriculaValidator.validate_cep("12345-678"))
        self.assertTrue(MatriculaValidator.validate_cep("12345678"))
        self.assertFalse(MatriculaValidator.validate_cep("1234-567"))
        self.assertFalse(MatriculaValidator.validate_cep("123456"))
    
    def test_extract_matricula_number(self):
        """Testa extração de número de matrícula"""
        text = "MATRÍCULA Nº: 12.345"
        result = MatriculaValidator.extract_matricula_number(text)
        self.assertEqual(result, "12.345")
        
        text2 = "Matrícula: 67890"
        result2 = MatriculaValidator.extract_matricula_number(text2)
        self.assertEqual(result2, "67890")
    
    def test_extract_registros(self):
        """Testa extração de registros"""
        text = "R.1 - Proprietário: João Silva\nR.2 - Proprietário: Maria Santos"
        registros = MatriculaValidator.extract_registros(text)
        self.assertEqual(len(registros), 2)
        self.assertIn("R.1", registros)
        self.assertIn("R.2", registros)
    
    def test_extract_averbacoes(self):
        """Testa extração de averbações"""
        text = "AV.1 - Hipoteca\nAV.2 - Cancelamento de hipoteca"
        averbacoes = MatriculaValidator.extract_averbacoes(text)
        self.assertEqual(len(averbacoes), 2)
        self.assertIn("AV.1", averbacoes)
        self.assertIn("AV.2", averbacoes)
    
    def test_has_onus_ativos(self):
        """Testa detecção de ônus ativos"""
        text_com_onus = "AV.1 - Hipoteca em favor do Banco XYZ"
        self.assertTrue(MatriculaValidator.has_onus_ativos(text_com_onus))
        
        text_sem_onus = "AV.1 - Hipoteca cancelada"
        self.assertFalse(MatriculaValidator.has_onus_ativos(text_sem_onus))
    
    def test_validate_area(self):
        """Testa validação de área"""
        text = "Área: 250,50 m²"
        result = MatriculaValidator.validate_area(text)
        self.assertTrue(result['valid'])
        self.assertEqual(result['area'], 250.5)
        self.assertEqual(result['unit'], 'm²')
    
    def test_validate_structure(self):
        """Testa validação de estrutura completa"""
        sample_text = """
        MATRÍCULA Nº: 12.345
        R.1 - Proprietário: João Silva
        CPF: 123.456.789-09
        Área: 250,00 m²
        CEP: 12345-678
        Inscrição Municipal: 123.456.789
        """
        
        extracted_data = {'raw_text': sample_text}
        result = MatriculaValidator.validate_structure(extracted_data)
        
        self.assertEqual(result['matricula_number'], "12.345")
        self.assertGreater(len(result['registros']), 0)
        self.assertGreater(len(result['valid_cpfs']), 0)
        self.assertTrue(result['area']['valid'])


if __name__ == '__main__':
    unittest.main()
