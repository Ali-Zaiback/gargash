from datetime import datetime, UTC
import random
import re
from typing import Dict, Any

class MockAIService:
    """Mock service for AI-powered call analysis used in testing."""
    
    def __init__(self):
        self.model_patterns = {
            'e-class': r'e-?class|e class',
            'g-class': r'g-?class|g class',
            'eqe': r'eqe|electric',
            'cla': r'cla',
            'amg': r'amg',
            's-class': r's-?class|s class',
            'c-class': r'c-?class|c class',
            'glc': r'glc'
        }
        
        self.model_analysis = {
            'amg': {
                'agent_performance_score': 96.0,
                'customer_interest_score': 98.0,
                'customer_description': 'AMG enthusiast',
                'customer_preferences': 'AMG, performance, customization, test drive',
                'test_drive_readiness': 97.0,
                'agent_issues': 'No issues'
            },
            'e-class': {
                'agent_performance_score': 92.0,
                'customer_interest_score': 95.0,
                'customer_description': 'Very interested in E-Class',
                'customer_preferences': 'E-Class, AMG, MBUX, test drive, colors, interior options',
                'test_drive_readiness': 98.0,
                'agent_issues': 'No issues'
            },
            'g-class': {
                'agent_performance_score': 91.0,
                'customer_interest_score': 93.0,
                'customer_description': 'Luxury SUV customer',
                'customer_preferences': 'G-Class, AMG, customization, showroom',
                'test_drive_readiness': 95.0,
                'agent_issues': 'No issues'
            },
            'eqe': {
                'agent_performance_score': 90.0,
                'customer_interest_score': 92.0,
                'customer_description': 'Interested in electric vehicles',
                'customer_preferences': 'EQE, electric, charging, MBUX Hyperscreen',
                'test_drive_readiness': 90.0,
                'agent_issues': 'No issues'
            },
            'cla': {
                'agent_performance_score': 89.0,
                'customer_interest_score': 91.0,
                'customer_description': 'Entry-level luxury customer',
                'customer_preferences': 'CLA, compact luxury, style',
                'test_drive_readiness': 88.0,
                'agent_issues': 'No issues'
            },
            's-class': {
                'agent_performance_score': 94.0,
                'customer_interest_score': 96.0,
                'customer_description': 'Premium luxury customer',
                'customer_preferences': 'S-Class, luxury, comfort, technology',
                'test_drive_readiness': 96.0,
                'agent_issues': 'No issues'
            },
            'c-class': {
                'agent_performance_score': 88.0,
                'customer_interest_score': 87.0,
                'customer_description': 'Mid-range luxury customer',
                'customer_preferences': 'C-Class, value, performance',
                'test_drive_readiness': 85.0,
                'agent_issues': 'No issues'
            },
            'glc': {
                'agent_performance_score': 87.0,
                'customer_interest_score': 86.0,
                'customer_description': 'SUV customer',
                'customer_preferences': 'GLC, SUV, practicality',
                'test_drive_readiness': 84.0,
                'agent_issues': 'No issues'
            }
        }
        
        self.scenario_patterns = {
            'pre-owned': {
                'agent_performance_score': 93.0,
                'customer_interest_score': 90.0,
                'customer_description': 'Interested in pre-owned vehicles',
                'customer_preferences': 'pre-owned, warranty, service package',
                'test_drive_readiness': 85.0,
                'agent_issues': 'No issues'
            },
            'service': {
                'agent_performance_score': 87.0,
                'customer_interest_score': 75.0,
                'customer_description': 'Service inquiry',
                'customer_preferences': 'service, maintenance, pickup',
                'test_drive_readiness': 60.0,
                'agent_issues': 'No issues'
            },
            'showroom': {
                'agent_performance_score': 95.0,
                'customer_interest_score': 97.0,
                'customer_description': 'Showroom visitor',
                'customer_preferences': 'showroom, viewing, test drive',
                'test_drive_readiness': 99.0,
                'agent_issues': 'No issues'
            },
            'price': {
                'agent_performance_score': 88.0,
                'customer_interest_score': 85.0,
                'customer_description': 'Price-sensitive customer',
                'customer_preferences': 'financing, trade-in, value',
                'test_drive_readiness': 80.0,
                'agent_issues': 'No issues'
            },
            'test_drive': {
                'agent_performance_score': 90.0,
                'customer_interest_score': 90.0,
                'customer_description': 'Test drive inquiry',
                'customer_preferences': 'test drive, experience, performance',
                'test_drive_readiness': 95.0,
                'agent_issues': 'No issues'
            }
        }

    def analyze_call(self, transcript: str) -> Dict[str, Any]:
        """
        Analyze a call transcript and return metrics.
        This is a mock implementation for testing.
        
        Args:
            transcript: The call transcript text
            
        Returns:
            Dict containing analysis results
            
        Raises:
            ValueError: If transcript is empty
        """
        if not transcript or not transcript.strip():
            raise ValueError("Transcript cannot be empty")

        transcript_lower = transcript.lower()
        
        # Check for model-specific analysis
        for model, pattern in self.model_patterns.items():
            if re.search(pattern, transcript_lower):
                return self.model_analysis[model]
        
        # Check for scenario-specific analysis
        for scenario, pattern in self.scenario_patterns.items():
            if scenario in transcript_lower or (scenario == 'price' and 'negotiation' in transcript_lower):
                return pattern
        
        # Default analysis for general inquiries
        return {
            'agent_performance_score': random.uniform(70, 95),
            'customer_interest_score': random.uniform(60, 90),
            'customer_description': 'General inquiry',
            'customer_preferences': 'Luxury vehicles',
            'test_drive_readiness': random.uniform(50, 100),
            'agent_issues': 'No issues'
        } 