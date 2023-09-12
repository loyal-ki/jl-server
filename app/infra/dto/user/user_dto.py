import datetime
import time

from sqlalchemy import CHAR, Boolean, Column, Date, ForeignKey, String
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.entities.user.user_entity import UserEntity
from app.infra.dto.user.sex_dto import SexDTO


class UserDTO(Base):
    __tablename__ = "users"

    id: int | Column = Column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=True
    )
    user_code: str | Column = Column(
        String(36), index=True, unique=True, nullable=True
    )
    email: str | Column = Column(
        String(100), index=True, unique=True, nullable=True
    )
    phone: str | Column = Column(
        String(15), index=True, unique=True, nullable=True
    )
    hashed_password: str | Column = Column(
        String(100), unique=True, nullable=True
    )
    is_email_verified: bool | Column = Column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    is_phone_verified: bool | Column = Column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    is_active: bool | Column = Column(
        Boolean, nullable=False, default=True, server_default="1"
    )
    name: str | Column = Column(String(50), nullable=True)
    sex_code: str | Column = Column(CHAR(1), ForeignKey("sex.code"))
    birthday: datetime.date | Column = Column(Date, nullable=True)

    facebook_id: str | Column = Column(String(50), nullable=True)
    facebook_access_token: str | Column = Column(String(255), nullable=True)
    facebook_username: str | Column = Column(String(50), nullable=True)

    google_id: str | Column = Column(String(50), nullable=True)
    google_access_token: str | Column = Column(String(255), nullable=True)
    google_username: str | Column = Column(String(50), nullable=True)

    created_at: int | Column = Column(BIGINT, default=int(time.time()))
    updated_at: int | Column = Column(
        BIGINT, default=int(time.time()), onupdate=int(time.time())
    )
    deleted_at: int | Column = Column(BIGINT, nullable=True)

    sex: SexDTO = relationship("SexDTO", lazy="joined")

    def to_entity(self) -> UserEntity:
        return UserEntity(
            id=self.id,
            user_code=self.user_code,
            email=self.email,
            phone=self.phone,
            hashed_password=self.hashed_password,
            is_email_verified=self.is_email_verified,
            is_phone_verified=self.is_phone_verified,
            is_active=self.is_active,
            name=self.name,
            sex_code=self.sex.code,
            birthday=self.birthday,
            facebook_id=self.facebook_id,
            facebook_access_token=self.facebook_access_token,
            facebook_username=self.facebook_username,
            google_id=self.google_id,
            google_access_token=self.google_access_token,
            google_username=self.google_username,
            created_at=datetime.datetime.fromtimestamp(self.created_at),
            updated_at=datetime.datetime.fromtimestamp(self.updated_at),
            deleted_at=datetime.datetime.fromtimestamp(self.deleted_at)
            if self.deleted_at
            else None,
        )

    def set_from_entity(self, user: UserEntity):
        self.user_code = user.user_code
        self.email = user.email
        self.phone = user.phone
        self.hashed_password = user.hashed_password
        self.is_email_verified = user.is_email_verified
        self.is_phone_verified = user.is_phone_verified
        self.is_active = user.is_active
        self.name = user.name
        self.sex_code = user.sex_code
        self.birthday = user.birthday
        self.facebook_id = user.facebook_id
        self.facebook_access_token = user.facebook_access_token
        self.facebook_username = user.facebook_username
        self.google_id = user.google_id
        self.google_access_token = user.google_access_token
        self.google_username = user.google_username

        self.deleted_at = (
            user.deleted_at.timestamp() if user.deleted_at else None
        )

    @classmethod
    def from_entity(cls, user: UserEntity) -> "UserDTO":
        dto = UserDTO(
            id=user.id,
            user_code=user.user_code,
            email=user.email,
            phone=user.phone,
            hashed_password=user.hashed_password,
            is_email_verified=user.is_email_verified,
            is_phone_verified=user.is_phone_verified,
            is_active=user.is_active,
            name=user.name,
            sex_code=user.sex_code,
            birthday=user.birthday,
            facebook_id=user.facebook_id,
            facebook_access_token=user.facebook_access_token,
            facebook_username=user.facebook_username,
            google_id=user.google_id,
            google_access_token=user.google_access_token,
            google_username=user.google_username,
            created_at=time.mktime(user.created_at.timetuple())
            if user.created_at
            else None,
            updated_at=time.mktime(user.updated_at.timetuple())
            if user.updated_at
            else None,
            deleted_at=time.mktime(user.deleted_at.timetuple())
            if user.deleted_at
            else None,
        )
        return dto
