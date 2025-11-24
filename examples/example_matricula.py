#!/usr/bin/env python3
"""
Exemplo específico para processamento de matrículas de imóveis
"""

from config.settings import settings
from src.orchestrator import DocumentPipeline
from src.utils import setup_logger


def process_matricula():
    """Processa uma matrícula de imóvel com validações específicas"""
    
    logger = setup_logger()
    
    pipeline = DocumentPipeline(
        ocr_model_id=settings.ocr_model_id,
        validation_model_id=settings.validation_model_id,
        embedding_model_id=settings.embedding_model_id,
        knowledge_base_path=settings.knowledge_base_path,
        output_path=settings.output_path,
        region=settings.aws_region
    )
    
    # Prompt específico para matrícula
    matricula_prompt = """
    Analise esta matrícula de imóvel e extraia as seguintes informações em formato JSON:
    
    {
        "numero_matricula": "número da matrícula",
        "livro": "número do livro",
        "folha": "número da folha",
        "cartorio": "nome do cartório e comarca",
        "data_abertura": "data de abertura da matrícula",
        
        "imovel": {
            "tipo": "tipo do imóvel (terreno, casa, apartamento, etc)",
            "endereco_completo": "endereço completo",
            "area_terreno": "área do terreno em m²",
            "area_construida": "área construída em m²",
            "inscricao_municipal": "número da inscrição municipal/IPTU",
            "confrontacoes": "descrição das confrontações"
        },
        
        "proprietario_atual": {
            "nome": "nome completo",
            "cpf_cnpj": "CPF ou CNPJ",
            "estado_civil": "estado civil",
            "regime_bens": "regime de bens se casado"
        },
        
        "registros": [
            {
                "numero": "R.1, R.2, etc",
                "data": "data do registro",
                "forma_aquisicao": "compra e venda, doação, etc",
                "valor": "valor da transação",
                "titulo_origem": "escritura pública, etc"
            }
        ],
        
        "onus_gravames": [
            {
                "numero": "AV.1, AV.2, etc",
                "tipo": "hipoteca, penhora, etc",
                "credor": "nome do credor",
                "valor": "valor do ônus",
                "data": "data da averbação",
                "status": "ativo ou cancelado"
            }
        ],
        
        "averbacoes": [
            {
                "numero": "AV.X",
                "tipo": "tipo da averbação",
                "data": "data",
                "descricao": "descrição"
            }
        ]
    }
    
    Extraia todos os dados visíveis no documento.
    """
    
    # Processa a matrícula
    result = pipeline.process_document(
        "./examples/matricula_imovel.pdf",
        custom_prompt=matricula_prompt
    )
    
    # Exibe resultado detalhado
    print("\n" + "="*70)
    print("ANÁLISE DE MATRÍCULA DE IMÓVEL")
    print("="*70)
    
    if result['status'] == 'success':
        validation = result['result']['validation']
        
        print(f"\n📋 Status: {'✅ VÁLIDA' if validation.get('is_valid') else '❌ INVÁLIDA'}")
        print(f"🎯 Confiança: {validation.get('confidence', 0)*100:.1f}%")
        
        # Validação especializada
        if 'specialized_validation' in validation:
            spec = validation['specialized_validation']
            
            print(f"\n📄 Matrícula Nº: {spec.get('matricula_number', 'N/A')}")
            print(f"📝 Registros encontrados: {', '.join(spec.get('registros', []))}")
            print(f"📌 Averbações encontradas: {', '.join(spec.get('averbacoes', []))}")
            
            if spec.get('area', {}).get('valid'):
                print(f"📐 Área: {spec['area']['area']} {spec['area']['unit']}")
            
            if spec.get('has_onus'):
                print("\n⚠️  ATENÇÃO: IMÓVEL COM ÔNUS ATIVOS!")
            
            if spec.get('valid_cpfs'):
                print(f"\n👤 CPFs válidos: {', '.join(spec['valid_cpfs'])}")
            
            if spec.get('valid_cnpjs'):
                print(f"\n🏢 CNPJs válidos: {', '.join(spec['valid_cnpjs'])}")
        
        # Problemas encontrados
        if validation.get('issues'):
            print("\n❌ PROBLEMAS ENCONTRADOS:")
            for issue in validation['issues']:
                print(f"   • {issue}")
        
        # Avisos
        if validation.get('warnings'):
            print("\n⚠️  AVISOS:")
            for warning in validation['warnings']:
                print(f"   • {warning}")
        
        # Recomendações
        if validation.get('recommendations'):
            print("\n💡 RECOMENDAÇÕES:")
            for rec in validation['recommendations']:
                print(f"   • {rec}")
        
        # Campos extraídos
        if validation.get('extracted_fields'):
            print("\n📊 CAMPOS EXTRAÍDOS:")
            import json
            print(json.dumps(validation['extracted_fields'], indent=2, ensure_ascii=False))
    
    else:
        print(f"\n❌ Erro: {result.get('error')}")
    
    print("\n" + "="*70)


def validate_multiple_matriculas():
    """Valida múltiplas matrículas em lote"""
    
    logger = setup_logger()
    
    pipeline = DocumentPipeline(
        ocr_model_id=settings.ocr_model_id,
        validation_model_id=settings.validation_model_id,
        embedding_model_id=settings.embedding_model_id,
        knowledge_base_path=settings.knowledge_base_path,
        output_path=settings.output_path
    )
    
    matriculas = [
        "./examples/matricula1.pdf",
        "./examples/matricula2.pdf",
        "./examples/matricula3.pdf"
    ]
    
    results = pipeline.process_batch(matriculas)
    
    print("\n" + "="*70)
    print("RESUMO DO PROCESSAMENTO EM LOTE")
    print("="*70)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['document_path']}")
        
        if result['status'] == 'success':
            validation = result['result']['validation']
            status = "✅ VÁLIDA" if validation.get('is_valid') else "❌ INVÁLIDA"
            
            print(f"   Status: {status}")
            print(f"   Confiança: {validation.get('confidence', 0)*100:.1f}%")
            
            if validation.get('specialized_validation', {}).get('has_onus'):
                print("   ⚠️  ATENÇÃO: Possui ônus ativos")
            
            if validation.get('issues'):
                print(f"   Problemas: {len(validation['issues'])}")
        else:
            print(f"   ❌ Erro: {result.get('error')}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    print("Escolha uma opção:")
    print("1. Processar uma matrícula")
    print("2. Processar múltiplas matrículas")
    
    choice = input("\nOpção: ")
    
    if choice == "1":
        process_matricula()
    elif choice == "2":
        validate_multiple_matriculas()
    else:
        print("Opção inválida")
