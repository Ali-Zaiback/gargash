from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.models import Agent, Call
from app.schemas import AgentCreate, AgentUpdate, AgentPerformance

class AgentService:
    """Service for managing agents."""
    
    def __init__(self, db: Session):
        self.db = db

    def create_agent(self, agent: AgentCreate) -> Agent:
        """Create a new agent."""
        try:
            db_agent = Agent(**agent.model_dump())
            self.db.add(db_agent)
            self.db.commit()
            self.db.refresh(db_agent)
            return db_agent
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig)
            if 'email' in error_msg:
                raise HTTPException(status_code=400, detail="Email already registered")
            if 'phone_number' in error_msg:
                raise HTTPException(status_code=400, detail="Phone already registered")
            if 'employee_id' in error_msg:
                raise HTTPException(status_code=400, detail="Employee ID already registered")
            raise HTTPException(status_code=400, detail="Duplicate entry")

    def get_agents(
        self, 
        skip: int = 0, 
        limit: int = 100,
        min_performance: Optional[float] = None
    ) -> List[Agent]:
        """Get filtered list of agents."""
        query = self.db.query(Agent)
        if min_performance is not None:
            query = query.filter(Agent.average_performance_score >= min_performance)
        return query.offset(skip).limit(limit).all()

    def get_agent(self, agent_id: int) -> Optional[Agent]:
        """Get a specific agent."""
        return self.db.query(Agent).filter(Agent.id == agent_id).first()

    def update_agent(self, agent_id: int, agent: AgentUpdate) -> Optional[Agent]:
        """Update an agent."""
        db_agent = self.get_agent(agent_id)
        if not db_agent:
            return None
            
        for key, value in agent.model_dump(exclude_unset=True).items():
            setattr(db_agent, key, value)
            
        self.db.commit()
        self.db.refresh(db_agent)
        return db_agent

    def delete_agent(self, agent_id: int) -> bool:
        """Delete an agent."""
        db_agent = self.get_agent(agent_id)
        if not db_agent:
            return False
            
        self.db.delete(db_agent)
        self.db.commit()
        return True

    def calculate_performance(self, agent_id: int) -> Optional[AgentPerformance]:
        """Calculate agent performance metrics."""
        agent = self.get_agent(agent_id)
        if not agent:
            return None

        calls = self.db.query(Call).filter(Call.agent_id == agent_id).all()
        if not calls:
            return AgentPerformance(
                agent_id=agent.id,
                agent_name=agent.name,
                total_calls_handled=0,
                average_performance_score=0.0,
                average_customer_interest=0.0,
                average_test_drive_readiness=0.0,
                agent_issues=[],
                specialization=agent.specialization or "",
                is_active=agent.is_active
            )

        return AgentPerformance(
            agent_id=agent.id,
            agent_name=agent.name,
            total_calls_handled=len(calls),
            average_performance_score=sum(c.agent_performance_score for c in calls) / len(calls),
            average_customer_interest=sum(c.customer_interest_score for c in calls) / len(calls),
            average_test_drive_readiness=sum(c.test_drive_readiness for c in calls) / len(calls),
            agent_issues=[c.agent_issues for c in calls if c.agent_issues],
            specialization=agent.specialization or "",
            is_active=agent.is_active
        ) 