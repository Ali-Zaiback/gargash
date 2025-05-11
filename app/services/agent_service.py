from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, OperationalError
from app.models import Agent, Call
from app.schemas import AgentCreate, AgentUpdate, AgentPerformance
from datetime import datetime, UTC, timedelta
import logging

class AgentService:
    """Service for managing agents."""
    
    def __init__(self, db: Session):
        self.db = db

    def create_agent(self, agent: AgentCreate) -> Agent:
        """Create a new agent."""
        try:
            # Check for existing agent with same email
            existing_email = self.db.query(Agent).filter(Agent.email == agent.email).first()
            if existing_email:
                raise HTTPException(status_code=400, detail="Email already registered")

            db_agent = Agent(
                name=agent.name,
                employee_id=agent.employee_id,
                email=agent.email,
                phone_number=agent.phone_number,
                specialization=agent.specialization,
                total_calls_handled=0,
                average_performance_score=0.0,
                created_at=datetime.now(UTC),
                is_active=True
            )
            self.db.add(db_agent)
            self.db.commit()
            self.db.refresh(db_agent)
            return db_agent

        except HTTPException:
            self.db.rollback()
            raise
        except OperationalError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error")
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def get_agents(self, skip: int = 0, limit: int = 100):
        """Get filtered list of agents."""
        return self.db.query(Agent).offset(skip).limit(limit).all()

    def get_agent(self, agent_id: int) -> Agent:
        """Get a specific agent."""
        return self.db.query(Agent).filter(Agent.id == agent_id).first()

    def update_agent(self, agent_id: int, agent: AgentUpdate) -> Agent:
        """Update an agent."""
        try:
            db_agent = self.get_agent(agent_id)
            if not db_agent:
                raise HTTPException(status_code=404, detail="Agent not found")

            # Check for existing agent with same email if email is being updated
            if agent.email and agent.email != db_agent.email:
                existing_email = self.db.query(Agent).filter(Agent.email == agent.email).first()
                if existing_email:
                    raise HTTPException(status_code=400, detail="Email already registered")

            for key, value in agent.dict(exclude_unset=True).items():
                setattr(db_agent, key, value)

            self.db.commit()
            self.db.refresh(db_agent)
            return db_agent

        except HTTPException:
            self.db.rollback()
            raise
        except OperationalError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error")
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def delete_agent(self, agent_id: int) -> bool:
        """Delete an agent."""
        db_agent = self.get_agent(agent_id)
        if not db_agent:
            return False
            
        self.db.delete(db_agent)
        self.db.commit()
        return True

    def calculate_performance(self, agent_id: int) -> AgentPerformance:
        """Calculate agent performance metrics."""
        try:
            logging.error(f"calculate_performance input: agent_id={agent_id}")
            agent = self.get_agent(agent_id)
            if not agent:
                logging.error("Agent not found")
                raise HTTPException(status_code=404, detail="Agent not found")

            # Get recent calls (last 30 days)
            cutoff_date = datetime.now(UTC) - timedelta(days=30)
            recent_calls = self.db.query(Call).filter(
                Call.agent_id == agent_id,
                Call.call_date >= cutoff_date
            ).all()
            logging.error(f"Recent calls: {recent_calls}")

            # Calculate metrics
            total_calls = len(recent_calls)
            if total_calls == 0:
                logging.error("No recent calls found")
                return AgentPerformance(
                    agent_id=agent_id,
                    agent_name=agent.name,
                    total_calls_handled=0,
                    average_performance_score=0.0,
                    average_customer_interest=0.0,
                    average_test_drive_readiness=0.0,
                    agent_issues=[],
                    specialization=agent.specialization,
                    is_active=True
                )

            # Calculate averages and issues
            valid_scores = [call.agent_performance_score for call in recent_calls if call.agent_performance_score is not None]
            avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
            valid_interest = [call.customer_interest_score for call in recent_calls if call.customer_interest_score is not None]
            avg_interest = sum(valid_interest) / len(valid_interest) if valid_interest else 0.0
            valid_readiness = [call.test_drive_readiness for call in recent_calls if call.test_drive_readiness is not None]
            avg_readiness = sum(valid_readiness) / len(valid_readiness) if valid_readiness else 0.0
            issues = []
            for call in recent_calls:
                if call.agent_issues:
                    issues.extend([i.strip() for i in str(call.agent_issues).split(",") if i.strip()])
            issues = list(set(issues))
            logging.error(f"valid_scores: {valid_scores}, avg_score: {avg_score}, avg_interest: {avg_interest}, avg_readiness: {avg_readiness}, issues: {issues}")

            return AgentPerformance(
                agent_id=agent_id,
                agent_name=agent.name,
                total_calls_handled=total_calls,
                average_performance_score=avg_score,
                average_customer_interest=avg_interest,
                average_test_drive_readiness=avg_readiness,
                agent_issues=issues,
                specialization=agent.specialization,
                is_active=True
            )

        except HTTPException:
            raise
        except OperationalError as e:
            logging.error(f"OperationalError in calculate_performance: {e}")
            raise HTTPException(status_code=500, detail="Database error")
        except Exception as e:
            logging.error(f"Unhandled exception in calculate_performance: {e}")
            raise HTTPException(status_code=500, detail=str(e)) 