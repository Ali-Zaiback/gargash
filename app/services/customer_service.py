from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, OperationalError
from app.models import Customer
from app.schemas import CustomerCreate, CustomerUpdate

class CustomerService:
    """Service for managing customers."""
    
    def __init__(self, db: Session):
        self.db = db

    def create_customer(self, customer: CustomerCreate) -> Customer:
        """Create a new customer."""
        try:
            # Check for existing customer with same email
            existing_email = self.db.query(Customer).filter(Customer.email == customer.email).first()
            if existing_email:
                raise HTTPException(status_code=400, detail="Email already registered")

            # Check for existing customer with same phone
            existing_phone = self.db.query(Customer).filter(Customer.phone_number == customer.phone_number).first()
            if existing_phone:
                raise HTTPException(status_code=400, detail="Phone number already registered")

            db_customer = Customer(
                name=customer.name,
                email=customer.email,
                phone_number=customer.phone_number
            )
            self.db.add(db_customer)
            self.db.commit()
            self.db.refresh(db_customer)
            return db_customer

        except HTTPException:
            self.db.rollback()
            raise
        except OperationalError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error")
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def get_customers(self, skip: int = 0, limit: int = 100):
        """Get filtered list of customers."""
        return self.db.query(Customer).offset(skip).limit(limit).all()

    def get_customer(self, customer_id: int) -> Customer:
        """Get a specific customer."""
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def update_customer(self, customer_id: int, customer: CustomerUpdate) -> Customer:
        """Update a customer."""
        try:
            db_customer = self.get_customer(customer_id)
            if not db_customer:
                raise HTTPException(status_code=404, detail="Customer not found")

            # Check for existing customer with same email if email is being updated
            if customer.email and customer.email != db_customer.email:
                existing_email = self.db.query(Customer).filter(Customer.email == customer.email).first()
                if existing_email:
                    raise HTTPException(status_code=400, detail="Email already registered")

            # Check for existing customer with same phone if phone is being updated
            if customer.phone_number and customer.phone_number != db_customer.phone_number:
                existing_phone = self.db.query(Customer).filter(Customer.phone_number == customer.phone_number).first()
                if existing_phone:
                    raise HTTPException(status_code=400, detail="Phone number already registered")

            for key, value in customer.dict(exclude_unset=True).items():
                setattr(db_customer, key, value)

            self.db.commit()
            self.db.refresh(db_customer)
            return db_customer

        except HTTPException:
            self.db.rollback()
            raise
        except OperationalError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error")
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def delete_customer(self, customer_id: int) -> bool:
        """Delete a customer."""
        db_customer = self.get_customer(customer_id)
        if not db_customer:
            return False
            
        self.db.delete(db_customer)
        self.db.commit()
        return True 