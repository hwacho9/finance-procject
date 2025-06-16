from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic, Type, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """Base repository class with common CRUD operations"""

    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model

    def get(self, id: Any) -> Optional[ModelType]:
        """Get a single record by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, *, skip: int = 0, limit: int = 100, **filters
    ) -> List[ModelType]:
        """Get multiple records with optional filtering"""
        query = self.db.query(self.model)

        # Apply filters
        for field, value in filters.items():
            if hasattr(self.model, field) and value is not None:
                query = query.filter(getattr(self.model, field) == value)

        return query.offset(skip).limit(limit).all()

    def create(self, *, obj_in: CreateSchemaType, **kwargs) -> ModelType:
        """Create a new record"""
        obj_in_data = obj_in.dict() if hasattr(obj_in, "dict") else obj_in
        obj_in_data.update(kwargs)
        db_obj = self.model(**obj_in_data)

        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(
        self, *, db_obj: ModelType, obj_in: UpdateSchemaType, **kwargs
    ) -> ModelType:
        """Update an existing record"""
        obj_data = (
            obj_in.dict(exclude_unset=True) if hasattr(obj_in, "dict") else obj_in
        )
        obj_data.update(kwargs)

        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, *, id: Any) -> bool:
        """Delete a record by ID"""
        obj = self.get(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False

    def count(self, **filters) -> int:
        """Count records with optional filtering"""
        query = self.db.query(self.model)

        # Apply filters
        for field, value in filters.items():
            if hasattr(self.model, field) and value is not None:
                query = query.filter(getattr(self.model, field) == value)

        return query.count()

    def exists(self, **filters) -> bool:
        """Check if record exists with given filters"""
        query = self.db.query(self.model)

        # Apply filters
        for field, value in filters.items():
            if hasattr(self.model, field) and value is not None:
                query = query.filter(getattr(self.model, field) == value)

        return query.first() is not None
