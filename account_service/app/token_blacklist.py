from datetime import datetime
from app.models.token_blacklist import Blacklist
from sqlalchemy.orm import Session

# Отозвать токен после выхода
def add_to_blacklist(token: str, expiration: datetime, db: Session):
    blacklisted_token = Blacklist(token=token, expiration=expiration)
    db.add(blacklisted_token)
    db.commit()

# проверьте, отозван ли токен
def is_blacklisted(token: str, db: Session) -> bool:
    return db.query(Blacklist).filter(Blacklist.token == token).first() is not None
