import re
from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, declared_attr, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func

from app.conf.config import settings

from .i18n import Translatable as BaseTranslatable

metadata = sa.MetaData()


class UnMapped:
    __allow_unmapped__ = True


PlainBase = declarative_base(metadata=metadata, cls=UnMapped)


class Base(PlainBase):
    __name__: str
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        pattern = re.compile(r'(?<!^)(?=[A-Z])')
        return pattern.sub('_', cls.__name__).lower()


class SlugBase(Base):
    __abstract__ = True
    slug: Mapped[str] = mapped_column(sa.String(255), unique=True, index=True, nullable=False)


class CreationModificationDateBase(Base):
    __abstract__ = True
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True), onupdate=func.now(),
        nullable=True
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True))


class PublishableModelBase(Base):
    __abstract__ = True

    publication_date: Mapped[Optional[datetime]] = mapped_column(sa.DateTime, nullable=True)
    is_published: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)

    @hybrid_property
    def is_visible(self) -> bool:
        return self.is_published and (
                self.publication_date is None
                or self.publication_date <= datetime.today()
        )


class SeoModelBase(Base):
    __abstract__ = True
    seo_title: Mapped[str] = mapped_column('seo_title', sa.String(255), default='')
    seo_description: Mapped[str] = mapped_column('seo_description', sa.String(255), default='')
    seo_keywords: Mapped[str] = mapped_column('seo_keywords', sa.String(500), default='')
