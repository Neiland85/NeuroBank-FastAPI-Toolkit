from mangum import Mangum
from app.main import app

# Handler para AWS Lambda
lambda_handler = Mangum(app)
