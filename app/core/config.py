from dotenv import dotenv_values
config = dotenv_values(".env")
config = {
    "DB_HOST": config.get("DB_HOST", "localhost"),
    "DB_PORT": config.get("DB_PORT", "5432"),
    "DB_NAME": config.get("DB_NAME", "mydatabase"),
    "DB_USER": config.get("DB_USER", "myuser"),
    "DB_PASSWORD": config.get("DB_PASSWORD", "mypassword"),
    "DB_NAME": config.get("DB_NAME", "mydatabase"), 
    "JWT_SECRET": config.get("JWT_SECRET","secret"),
    "ENVIRONMENT": config.get("ENVIRONMENT", "development"),
    "CORS_ORIGINS": config.get("CORS_ORIGINS", "*"),
    "S3_BUCKET_NAME": config.get("S3_BUCKET_NAME", "intellicog-bucket"),
    "S3_REGION_NAME": config.get("S3_REGION_NAME", "us-west-2"),
    "S3_ACCESS_KEY_ID": config.get("S3_ACCESS_KEY_ID", "your-access-key-id"),
    "ACCESS_TOKEN_EXPIRE_MINUTES": int(config.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30)),
    "REFRESH_TOKEN_EXPIRE_MINUTES": int(config.get("REFRESH_TOKEN_EXPIRE_MINUTES", 60)),
    "ALGORITHM": config.get("ALGORITHM", "HS256")
}

