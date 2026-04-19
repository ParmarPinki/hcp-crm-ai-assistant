from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings
from app.db.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title='AI-First CRM HCP Module', version='1.0.0')

origins = [origin.strip() for origin in settings.cors_origins.split(',') if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(router)


@app.get('/health')
def health_check():
    return {'status': 'ok'}
