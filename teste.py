from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import config

engine = create_engine(config.conexao_banco)

with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM game"))
    print(result.scalar())
