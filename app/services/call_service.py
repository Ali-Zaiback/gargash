from datetime import datetime, UTC, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Call, Agent, Customer
from app.schemas import CallCreate
from app.services.ai_service import AIService
import time
from sqlalchemy.exc import OperationalError
import logging

MAX_TRANSCRIPT_LENGTH = 10000

class CallService:
    """Service for managing call records and analysis."""
    
    def __init__(self, db: Session, ai_service: AIService = None):
        """Initialize the call service with database session and optional AI service."""
        self.db = db
        self.ai_service = ai_service or AIService()

    def create_call(self, call: CallCreate) -> Call:
        """Create a new call record with AI analysis."""
        try:
            # Validate transcript first
            if not call.transcript.strip():
                raise HTTPException(status_code=422, detail="Transcript must not be empty")
            
            if len(call.transcript) > MAX_TRANSCRIPT_LENGTH:
                raise HTTPException(status_code=422, detail="Transcript too long")

            # Verify customer exists
            customer = self.db.query(Customer).filter(Customer.id == call.customer_id).first()
            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found")

            # Verify agent exists
            agent = self.db.query(Agent).filter(Agent.id == call.agent_id).first()
            if not agent:
                raise HTTPException(status_code=404, detail="Agent not found")

            # Create call record
            db_call = Call(
                customer_id=call.customer_id,
                agent_id=call.agent_id,
                transcript=call.transcript,
                call_date=call.call_date
            )

            # Perform AI analysis
            analysis = self.ai_service.analyze_call(call.transcript)
            
            # Update call with analysis results
            db_call.agent_performance_score = analysis.get("agent_performance_score")
            db_call.agent_issues = analysis.get("agent_issues")
            db_call.customer_interest_score = analysis.get("customer_interest_score")
            db_call.customer_description = analysis.get("customer_description")
            db_call.customer_preferences = analysis.get("customer_preferences")
            db_call.test_drive_readiness = analysis.get("test_drive_readiness")
            db_call.analysis_results = analysis

            # Update agent metrics
            agent.total_calls_handled += 1
            agent.average_performance_score = (
                (agent.average_performance_score * (agent.total_calls_handled - 1) +
                 (analysis.get("agent_performance_score") or 0.0)) / agent.total_calls_handled
            )

            self.db.add(db_call)
            self.db.commit()
            self.db.refresh(db_call)
            return db_call
            
        except HTTPException as he:
            self.db.rollback()
            raise
        except OperationalError:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error")
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def get_calls(
        self, 
        skip: int = 0, 
        limit: int = 100,
        customer_id: Optional[int] = None,
        agent_id: Optional[int] = None
    ) -> List[Call]:
        """Get filtered list of calls."""
        query = self.db.query(Call)
        if customer_id:
            query = query.filter(Call.customer_id == customer_id)
        if agent_id:
            query = query.filter(Call.agent_id == agent_id)
        return query.offset(skip).limit(limit).all()

    def get_call(self, call_id: int) -> Optional[Call]:
        """Get a call by ID."""
        return self.db.query(Call).filter(Call.id == call_id).first()

    def get_customer_calls(self, customer_id: int) -> List[Call]:
        """Get all calls for a customer."""
        calls = self.db.query(Call).filter(Call.customer_id == customer_id).all()
        # Ensure all fields have default values
        for call in calls:
            if call.agent_performance_score is None:
                call.agent_performance_score = 0.0
            if call.agent_issues is None:
                call.agent_issues = ""
            if call.customer_interest_score is None:
                call.customer_interest_score = 0.0
            if call.customer_description is None:
                call.customer_description = ""
            if call.customer_preferences is None:
                call.customer_preferences = ""
            if call.test_drive_readiness is None:
                call.test_drive_readiness = 0.0
            if call.analysis_results is None:
                call.analysis_results = {}
        return calls

    def get_agent_calls(self, agent_id: int, days: int = 30) -> List[Call]:
        """Get recent calls for an agent."""
        cutoff_date = datetime.now(UTC) - timedelta(days=days)
        return self.db.query(Call)\
            .filter(Call.agent_id == agent_id)\
            .filter(Call.call_date >= cutoff_date)\
            .all()

    def _update_agent_metrics(self, agent_id: int):
        """Update agent's performance metrics based on recent calls."""
        try:
            agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
            if not agent:
                return

            # Get recent calls (last 30 days)
            recent_calls = self.get_agent_calls(agent_id, days=30)
            if not recent_calls:
                return

            # Calculate new metrics
            total_calls = len(recent_calls)
            # Filter out None values and calculate average
            valid_scores = [call.agent_performance_score for call in recent_calls if call.agent_performance_score is not None]
            avg_performance = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0

            # Update agent record
            agent.total_calls_handled = total_calls
            agent.average_performance_score = avg_performance
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"Failed to update agent metrics: {str(e)}") 