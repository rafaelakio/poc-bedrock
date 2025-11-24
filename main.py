#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from config.settings import settings
from src.orchestrator import DocumentPipeline
from src.utils import setup_logger, FileHandler


def main():
    parser = argparse.ArgumentParser(
        description="OCR de documentos com AWS Bedrock e validação RAG"
    )
    
    parser.add_argument(
        "--input",
        type=str,
        help="Caminho para o documento de entrada"
    )
    
    parser.add_argument(
        "--input-dir",
        type=str,
        help="Diretório com múltiplos documentos"
    )
    
    parser.add_argument(
        "--knowledge-base",
        type=str,
        default=settings.knowledge_base_path,
        help="Caminho para a base de conhecimento"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=settings.output_path,
        help="Diretório de saída para resultados"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default=settings.log_level,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Nível de log"
    )
    
    args = parser.parse_args()
    
    # Setup logger
    logger = setup_logger(level=args.log_level)
    
    # Valida argumentos
    if not args.input and not args.input_dir:
        logger.error("Forneça --input ou --input-dir")
        parser.print_help()
        sys.exit(1)
    
    try:
        # Inicializa pipeline
        logger.info("Inicializando pipeline...")
        pipeline = DocumentPipeline(
            ocr_model_id=settings.ocr_model_id,
            validation_model_id=settings.validation_model_id,
            embedding_model_id=settings.embedding_model_id,
            knowledge_base_path=args.knowledge_base,
            output_path=args.output,
            region=settings.aws_region
        )
        
        # Processa documento(s)
        if args.input:
            logger.info(f"Processando arquivo: {args.input}")
            FileHandler.validate_file(args.input, settings.max_image_size)
            result = pipeline.process_document(args.input)
            
            # Exibe resultado
            print("\n" + "="*50)
            print("RESULTADO DO PROCESSAMENTO")
            print("="*50)
            print(f"Status: {result['status']}")
            
            if result['status'] == 'success':
                validation = result['result']['validation']
                print(f"Válido: {validation.get('is_valid', 'N/A')}")
                print(f"Confiança: {validation.get('confidence', 'N/A')}")
                print(f"Tipo: {validation.get('document_type', 'N/A')}")
                
                if validation.get('issues'):
                    print("\nProblemas encontrados:")
                    for issue in validation['issues']:
                        print(f"  - {issue}")
        
        elif args.input_dir:
            logger.info(f"Processando diretório: {args.input_dir}")
            files = FileHandler.get_files_from_directory(args.input_dir)
            
            if not files:
                logger.warning("Nenhum arquivo suportado encontrado")
                sys.exit(0)
            
            logger.info(f"Encontrados {len(files)} arquivos")
            results = pipeline.process_batch(files)
            
            # Resumo
            success = sum(1 for r in results if r['status'] == 'success')
            print(f"\nProcessados: {len(results)} | Sucesso: {success} | Erro: {len(results) - success}")
        
        logger.info("Processamento concluído!")
        
    except Exception as e:
        logger.error(f"Erro: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
