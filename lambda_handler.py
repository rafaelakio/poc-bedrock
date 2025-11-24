import json
import boto3
import os
from urllib.parse import unquote_plus
from src.orchestrator import DocumentPipeline
from src.utils import setup_logger


s3_client = boto3.client('s3')
logger = setup_logger()


def handler(event, context):
    """
    Lambda handler para processar documentos do S3
    """
    
    try:
        # Extrai informações do evento S3
        if 'Records' in event:
            # Evento S3
            record = event['Records'][0]
            bucket = record['s3']['bucket']['name']
            key = unquote_plus(record['s3']['object']['key'])
            
            logger.info(f"Processando arquivo: s3://{bucket}/{key}")
            
            # Download do arquivo
            local_path = f"/tmp/{os.path.basename(key)}"
            s3_client.download_file(bucket, key, local_path)
            
        elif 'body' in event:
            # Evento API Gateway
            body = json.loads(event['body'])
            bucket = body.get('bucket')
            key = body.get('key')
            
            if not bucket or not key:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'bucket and key are required'})
                }
            
            local_path = f"/tmp/{os.path.basename(key)}"
            s3_client.download_file(bucket, key, local_path)
        
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid event format'})
            }
        
        # Inicializa pipeline
        pipeline = DocumentPipeline(
            ocr_model_id=os.environ['OCR_MODEL_ID'],
            validation_model_id=os.environ['VALIDATION_MODEL_ID'],
            embedding_model_id=os.environ['EMBEDDING_MODEL_ID'],
            knowledge_base_path='/tmp/knowledge_base',
            output_path='/tmp/output'
        )
        
        # Download da base de conhecimento
        knowledge_bucket = os.environ['KNOWLEDGE_BUCKET']
        download_knowledge_base(knowledge_bucket, '/tmp/knowledge_base')
        
        # Processa documento
        result = pipeline.process_document(local_path)
        
        # Upload do resultado para S3
        output_bucket = os.environ['OUTPUT_BUCKET']
        output_key = f"results/{os.path.basename(key)}.json"
        
        s3_client.put_object(
            Bucket=output_bucket,
            Key=output_key,
            Body=json.dumps(result, ensure_ascii=False, indent=2),
            ContentType='application/json'
        )
        
        logger.info(f"Resultado salvo em: s3://{output_bucket}/{output_key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Document processed successfully',
                'result_location': f"s3://{output_bucket}/{output_key}",
                'validation': result.get('result', {}).get('validation', {})
            })
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar documento: {str(e)}", exc_info=True)
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }


def download_knowledge_base(bucket, local_path):
    """Download da base de conhecimento do S3"""
    os.makedirs(local_path, exist_ok=True)
    
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket)
    
    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                key = obj['Key']
                local_file = os.path.join(local_path, os.path.basename(key))
                s3_client.download_file(bucket, key, local_file)
                logger.info(f"Downloaded: {key}")
