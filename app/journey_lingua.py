import uvicorn

from app.config.config import Config

if __name__ == "__main__":
    uvicorn.run(
        "main:journeyLingua",
        host=Config.SERVER_HOST,
        port=Config.SERVER_PORT,
        reload=True,
        forwarded_allow_ips="*",
    )
