import os
import google.generativeai as genai
from typing import Dict, Any
import json
import re

class AIService:
    """Service for AI-powered call analysis."""
    
    def __init__(self):
        """Initialize the AI service with Gemini API."""
        try:
            genai.configure(api_key="AIzaSyBWolI6Em5ce-Lt_KUUoW4rgx4jY615P0c")
            
            # List available models for debugging
            models = genai.list_models()
            print("Available models:", [model.name for model in models])
            
            # Use the correct model name
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
            print("Model initialized successfully: gemini-1.5-flash-latest")
        except Exception as e:
            print(f"Error initializing AI service: {str(e)}")
            raise

    def analyze_call(self, transcript: str) -> dict:
        """Analyze a call transcript and return insights."""
        # This is a mock implementation. In a real system, this would call an AI service.
        return {
            "agent_performance_score": 85.0,
            "agent_issues": "No issues",
            "customer_interest_score": 90.0,
            "customer_description": "Very interested in E-Class",
            "customer_preferences": "Luxury sedan, AMG package",
            "test_drive_readiness": 95.0
        }

    def analyze_call_real(self, transcript: str) -> Dict[str, Any]:
        """Analyze a call transcript using Gemini AI."""
        prompt = f"""Analyze this call transcript and provide a structured analysis in JSON format with the following fields:
        {{
            "agent_performance": {{
                "score": float,  # 0-1 score
                "issues": [string]  # List of issues identified
            }},
            "customer_analysis": {{
                "interest_score": float,  # 0-1 score
                "description": string,  # Brief description of customer
                "preferences": string  # Customer preferences identified
            }},
            "test_drive": {{
                "readiness_score": float  # 0-1 score
            }}
        }}

        Transcript: {transcript}"""

        try:
            print("Sending request to Gemini API...")
            response = self.model.generate_content(prompt)
            print("Received response from Gemini API")
            print("\nRaw response from Gemini:")
            print("=" * 50)
            print(response.text)
            print("=" * 50)
            
            # Extract JSON from the response, handling markdown code blocks
            response_text = response.text
            json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', response_text)
            if json_match:
                response_text = json_match.group(1)
                print("\nExtracted JSON:")
                print("=" * 50)
                print(response_text)
                print("=" * 50)
            
            # Try to parse the response as JSON
            try:
                analysis = json.loads(response_text)
                print("\nParsed JSON:")
                print("=" * 50)
                print(json.dumps(analysis, indent=2))
                print("=" * 50)
            except json.JSONDecodeError:
                print("Failed to parse response as JSON. Raw response:", response_text)
                raise ValueError("Invalid JSON response from AI model")
            
            # Ensure all required fields are present with default values if missing
            agent_performance = analysis.get("agent_performance", {})
            customer_analysis = analysis.get("customer_analysis", {})
            test_drive = analysis.get("test_drive", {})
            
            result = {
                "agent_performance_score": float(agent_performance.get("score", 0.0)),
                "agent_issues": ", ".join(agent_performance.get("issues", [])),
                "customer_interest_score": float(customer_analysis.get("interest_score", 0.0)),
                "customer_description": str(customer_analysis.get("description", "")),
                "customer_preferences": str(customer_analysis.get("preferences", "")),
                "test_drive_readiness": float(test_drive.get("readiness_score", 0.0)),
                "analysis_results": analysis
            }
            
            print("\nFinal processed result:")
            print("=" * 50)
            print(json.dumps(result, indent=2))
            print("=" * 50)
            
            return result
        except Exception as e:
            print(f"Error in analyze_call: {str(e)}")
            print(f"Error type: {type(e)}")
            print(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No details available'}")
            raise ValueError(f"Analysis failed: {str(e)}") 