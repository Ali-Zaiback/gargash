from datetime import datetime, UTC, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Call, Agent, Customer
from app.schemas import CallCreate
from app.services.ai_service import AIService
import time
from sqlalchemy.exc import OperationalError

class CallService:
    """Service for managing call records and analysis."""
    
    def __init__(self, db: Session, ai_service=None):
        """Initialize the call service with database session and optional AI service."""
        self.db = db
        self.ai_service = ai_service

    def create_call(self, call: CallCreate) -> Call:
        """Create a new call record with AI analysis."""
        try:
            # Create the call record
            db_call = Call(
                customer_id=call.customer_id,
                agent_id=call.agent_id,
                transcript=call.transcript,
                call_date=call.call_date
            )
            
            # If AI service is available, perform analysis
            if self.ai_service:
                try:
                    analysis = self.ai_service.analyze_call(call.transcript)
                    
                    # Update call with analysis results
                    db_call.agent_performance_score = analysis["agent_performance_score"]
                    db_call.agent_issues = analysis["agent_issues"]
                    db_call.customer_interest_score = analysis["customer_interest_score"]
                    db_call.customer_description = analysis["customer_description"]
                    db_call.customer_preferences = analysis["customer_preferences"]
                    db_call.test_drive_readiness = analysis["test_drive_readiness"]
                    db_call.analysis_results = analysis["analysis_results"]
                except Exception as e:
                    print(f"AI analysis failed: {str(e)}")
                    # Continue without analysis results
            
            # Save the call record with retry logic for database locks
            max_retries = 3
            retry_delay = 1  # seconds
            
            for attempt in range(max_retries):
                try:
                    self.db.add(db_call)
                    self.db.commit()
                    self.db.refresh(db_call)
                    
                    # If AI analysis was successful, update agent metrics
                    if self.ai_service and hasattr(db_call, 'agent_performance_score'):
                        self._update_agent_metrics(call.agent_id)
                    
                    return db_call
                except OperationalError as e:
                    if "database is locked" in str(e) and attempt < max_retries - 1:
                        print(f"Database locked, attempt {attempt + 1} of {max_retries}. Retrying...")
                        self.db.rollback()
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create call: {str(e)}")

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