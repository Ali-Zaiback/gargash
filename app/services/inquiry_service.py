from sqlalchemy.orm import Session
from app.models import Customer, Inquiry, InquiryStatus
from app.schemas import InquiryCreate, CustomerCreate, InquiryUpdate, CallCreate
from app.services.customer_service import CustomerService
from app.services.call_service import CallService
from app.services.ai_service import AIService
from fastapi import HTTPException
from datetime import datetime, UTC
from app.database import get_default_ai_agent_id
from sqlalchemy.exc import OperationalError
from pydantic import ValidationError
import logging
import requests

class InquiryService:
    def __init__(self, db: Session):
        self.db = db
        self.customer_service = CustomerService(db)
        self.call_service = CallService(db, AIService())

    def create_inquiry(self, inquiry_data: InquiryCreate) -> Inquiry:
        # First, try to find the customer by phone number
        customer = self.db.query(Customer).filter(
            Customer.phone_number == inquiry_data.phone_number
        ).first()

        # If customer doesn't exist, create a new one
        if not customer:
            customer_data = CustomerCreate(
                name=inquiry_data.name,
                email=inquiry_data.email,
                phone_number=inquiry_data.phone_number
            )
            customer = self.customer_service.create_customer(customer_data)

        # Check if inquiry already exists
        existing_inquiry = self.db.query(Inquiry).filter(
            Inquiry.customer_id == customer.id,
            Inquiry.referral_nr == inquiry_data.referral_nr
        ).first()

        if existing_inquiry:
            return existing_inquiry

        # Create new inquiry
        db_inquiry = Inquiry(
            customer_id=customer.id,
            referral_nr=inquiry_data.referral_nr,
            status=InquiryStatus.CALLING
        )
        
        self.db.add(db_inquiry)
        self.db.commit()
        self.db.refresh(db_inquiry)
        
        # Call external API (bland.ai)
        headers = {
            'Authorization': 'org_5866470eb265da3e5a3fa9cbbd9d493243eb17b08d57dc5357ee4d1bc5d48bf1c68906990e2371be581069',  # TODO: Replace with your actual API key
        }
        data = {
            "phone_number": inquiry_data.phone_number,
            "voice": "June",
            "wait_for_greeting": False,
            "record": True,
            "answered_by_enabled": True,
            "noise_cancellation": False,
            "interruption_threshold": 100,
            "block_interruptions": False,
            "max_duration": 12,
            "model": "base",
            "language": "en",
            "background_track": "none",
            "endpoint": "https://api.bland.ai",
            "voicemail_action": "hangup",
            "pathway_id": "a560e8ab-ce88-440e-a722-308a09d2a9d5",
            "pathway_version": 2,
            "webhook": "https://e9d8-94-206-192-223.ngrok-free.app/inquiries/webhook",
            "metadata": {
                "inquiry_id": db_inquiry.id
            }
        }
        try:
            response = requests.post('https://api.bland.ai/v1/calls', json=data, headers=headers)
            response.raise_for_status()
        except Exception as e:
            print(f"Error calling external API: {e}")
        return db_inquiry 

    def update_inquiry(self, inquiry_id: int, inquiry_update: InquiryUpdate) -> Inquiry:
        """Update an inquiry by ID."""
        try:
            # Find the inquiry by ID
            db_inquiry = self.db.query(Inquiry).filter(Inquiry.id == inquiry_id).first()
            if not db_inquiry:
                raise HTTPException(status_code=404, detail="Inquiry not found")

            # Update inquiry fields
            for field, value in inquiry_update.model_dump(exclude_unset=True).items():
                if field != 'inquiry_id':  # Skip inquiry_id as it's used for lookup
                    setattr(db_inquiry, field, value)

            # If transcript is provided, create a call record
            if inquiry_update.concatenated_transcript:
                # Get the default AI agent ID
                ai_agent_id = get_default_ai_agent_id(self.db)
                if not ai_agent_id:
                    raise HTTPException(status_code=500, detail="Default AI agent not found")

                # Create call record with the concatenated transcript
                call_data = CallCreate(
                    customer_id=db_inquiry.customer_id,
                    agent_id=ai_agent_id,
                    transcript=inquiry_update.concatenated_transcript
                )
                self.call_service.create_call(call_data)

                # Update inquiry status
                db_inquiry.status = InquiryStatus.DEAL

            self.db.commit()
            self.db.refresh(db_inquiry)
            return db_inquiry

        except Exception as e:
            print(f"ali_debug: {e}")
            self.db.rollback()
            raise
        except OperationalError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error")
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e)) 