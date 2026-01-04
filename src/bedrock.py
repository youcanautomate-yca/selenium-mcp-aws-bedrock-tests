"""AWS Bedrock integration for AI-powered test automation"""

import boto3
import json
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BedrockClient:
    """Client for interacting with AWS Bedrock AI models"""

    def __init__(self, region_name: Optional[str] = None, model_id: Optional[str] = None):
        """Initialize Bedrock client
        
        Args:
            region_name: AWS region name. Defaults to environment variable AWS_REGION
            model_id: Bedrock model ID. Defaults to environment variable BEDROCK_MODEL_ID
        """
        self.region_name = region_name or os.getenv("AWS_REGION", "us-west-2")
        self.model_id = model_id or os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-opus-4-5-20251101-v1:0")
        self.client = boto3.client("bedrock-runtime", region_name=self.region_name)

    def invoke_model(self, prompt: str, max_tokens: int = 1024) -> str:
        """Invoke Bedrock model with a prompt
        
        Args:
            prompt: The text prompt to send to the model
            max_tokens: Maximum tokens in the response
            
        Returns:
            The model's response text
        """
        # Use Converse API for Claude 3 and newer models
        if "claude" in self.model_id.lower():
            try:
                response = self.client.converse(
                    modelId=self.model_id,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "text": prompt
                                }
                            ]
                        }
                    ],
                    inferenceConfig={
                        "maxTokens": max_tokens,
                        "temperature": 0.7
                    }
                )
                
                # Extract text from Converse API response
                if "output" in response and "message" in response["output"]:
                    if "content" in response["output"]["message"]:
                        content = response["output"]["message"]["content"]
                        if len(content) > 0 and "text" in content[0]:
                            return content[0]["text"]
                return ""
                
            except Exception as e:
                raise Exception(f"Error invoking model {self.model_id} with Converse API: {str(e)}")
        
        return ""

    def analyze_test_results(self, test_data: Dict[str, Any]) -> str:
        """Analyze test results using Bedrock AI
        
        Args:
            test_data: Dictionary containing test results
            
        Returns:
            AI-generated analysis of the test results
        """
        prompt = f"""Analyze the following test results and provide insights:

{json.dumps(test_data, indent=2)}

Please provide:
1. Summary of test execution
2. Key findings
3. Recommended next steps"""

        return self.invoke_model(prompt)
