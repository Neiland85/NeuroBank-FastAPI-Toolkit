from loguru import logger
import sys, os

def init_logging():
    """
    Configura Loguru para logging estructurado con CloudWatch.
    """
    logger.remove()
    
    # Consola
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level}</level> | {message}"
    )
    
    # CloudWatch (solo si AWS_REGION está configurado)
    if os.getenv("AWS_REGION"):
        try:
            import watchtower
            logger.add(
                watchtower.CloudWatchLogHandler(log_group="neurobank-api"),
                level="INFO",
                serialize=True
            )
            logger.info("CloudWatch logging configured")
        except Exception as e:
            logger.warning(f"Could not configure CloudWatch logging: {e}")
    
    # X-Ray (solo si está en AWS Lambda)
    if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        try:
            from aws_xray_sdk.core import patch_all, xray_recorder
            patch_all()
            xray_recorder.configure(service='NeuroBankAPI')
            logger.info("X-Ray tracing configured")
        except Exception as e:
            logger.warning(f"Could not configure X-Ray: {e}")
