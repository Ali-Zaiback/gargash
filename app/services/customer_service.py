from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.models import Customer
from app.schemas import CustomerCreate, CustomerUpdate

class CustomerService:
    """Service for managing customers."""
    
    def __init__(self, db: Session):
        self.db = db

    def create_customer(self, customer: CustomerCreate) -> Customer:
        """Create a new customer."""
        try:
            db_customer = Customer(**customer.model_dump())
            self.db.add(db_customer)
            self.db.commit()
            self.db.refresh(db_customer)
            return db_customer
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig)
            if 'email' in error_msg:
                raise HTTPException(status_code=400, detail="Email already registered")
            if 'phone_number' in error_msg:
                raise HTTPException(status_code=400, detail="Phone already registered")
            raise HTTPException(status_code=400, detail="Duplicate entry")

    def get_customers(
        self, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[Customer]:
        """Get filtered list of customers."""
        query = self.db.query(Customer)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Customer.name.ilike(search_term)) |
                (Customer.email.ilike(search_term))
            )
        return query.offset(skip).limit(limit).all()

    def get_customer(self, customer_id: int) -> Optional[Customer]:
        """Get a specific customer."""
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def update_customer(self, customer_id: int, customer: CustomerUpdate) -> Optional[Customer]:
        """Update a customer."""
        db_customer = self.get_customer(customer_id)
        if not db_customer:
            return None
            
        for key, value in customer.model_dump(exclude_unset=True).items():
            setattr(db_customer, key, value)
            
        self.db.commit()
        self.db.refresh(db_customer)
        return db_customer

    def delete_customer(self, customer_id: int) -> bool:
        """Delete a customer."""
        db_customer = self.get_customer(customer_id)
        if not db_customer:
            return False
            
        self.db.delete(db_customer)
        self.db.commit()
        return True 