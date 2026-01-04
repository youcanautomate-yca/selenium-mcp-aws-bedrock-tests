#!/usr/bin/env python
"""Bedrock-Driven MCP Browser Automation

This script sends prompts to AWS Bedrock, which analyzes them and uses
MCP server tools to execute browser automation tasks.
"""

import os
import sys
import json
import argparse
import re
import asyncio
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import httpx
from src.bedrock import BedrockClient


class BedrockMCPBrowserAutomation:
    """Execute browser automation via Bedrock + MCP"""
    
    def __init__(self, mcp_server_url: str = "http://localhost:8000"):
        """Initialize automation engine
        
        Args:
            mcp_server_url: URL of the MCP server
        """
        self.mcp_server_url = mcp_server_url.rstrip('/')
        self.bedrock = BedrockClient()
        self.conversation_history = []
        self.max_iterations = 20
        
        # Available MCP tools for browser automation
        # MCP Selenium tools (from angiejones/mcp-selenium in SSE mode)
        self.mcp_tools = {
            "start_browser": {
                "description": "Launches a browser session",
                "params": {"browser": "chrome|firefox", "options": {"headless": "boolean", "arguments": "array"}}
            },
            "close_session": {
                "description": "Closes the current browser session and cleans up resources",
                "params": {}
            },
            "navigate": {
                "description": "Navigates to a URL",
                "params": {"url": "string"}
            },
            "find_element": {
                "description": "Finds an element on the page using locator strategy",
                "params": {"by": "id|css|xpath|name|tag|class", "value": "string", "timeout": "integer (milliseconds, default 10000)"}
            },
            "click_element": {
                "description": "Clicks an element",
                "params": {"by": "id|css|xpath|name|tag|class", "value": "string", "timeout": "integer (default 10000)"}
            },
            "send_keys": {
                "description": "Sends keys to an element (typing text)",
                "params": {"by": "id|css|xpath|name|tag|class", "value": "string", "text": "string", "timeout": "integer"}
            },
            "get_element_text": {
                "description": "Gets the text content of an element",
                "params": {"by": "id|css|xpath|name|tag|class", "value": "string", "timeout": "integer"}
            },
            "hover": {
                "description": "Moves the mouse to hover over an element",
                "params": {"by": "id|css|xpath|name|tag|class", "value": "string", "timeout": "integer"}
            },
            "double_click": {
                "description": "Performs a double click on an element",
                "params": {"by": "id|css|xpath|name|tag|class", "value": "string", "timeout": "integer"}
            },
            "right_click": {
                "description": "Performs a right click (context click) on an element",
                "params": {"by": "id|css|xpath|name|tag|class", "value": "string", "timeout": "integer"}
            },
            "press_key": {
                "description": "Simulates pressing a keyboard key",
                "params": {"key": "string (e.g., 'Enter', 'Tab', 'a')"}
            },
            "drag_and_drop": {
                "description": "Drags an element and drops it onto another element",
                "params": {"by": "id|css|xpath|name|tag|class", "value": "string", "targetBy": "id|css|xpath|name|tag|class", "targetValue": "string", "timeout": "integer"}
            },
            "upload_file": {
                "description": "Uploads a file using a file input element",
                "params": {"by": "id|css|xpath|name|tag|class", "value": "string", "filePath": "string (absolute path)", "timeout": "integer"}
            },
            "take_screenshot": {
                "description": "Captures a screenshot of the current page",
                "params": {"outputPath": "string (optional)"}
            }
        }
    
    async def call_mcp_tool(self, tool_name: str, **kwargs) -> str:
        """Call a tool on the MCP server using JSON-RPC protocol
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Send to /call endpoint with tool_name format
                payload = {
                    "tool_name": tool_name,
                    "parameters": kwargs
                }
                
                response = await client.post(
                    f"{self.mcp_server_url}/call",
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        if isinstance(result, dict):
                            # Extract the actual result from MCP response
                            if "result" in result:
                                content = result["result"]
                                if isinstance(content, dict) and "content" in content:
                                    # Extract text from content array
                                    for item in content["content"]:
                                        if isinstance(item, dict) and "text" in item:
                                            return item["text"]
                                    return json.dumps(content)
                                elif isinstance(content, dict):
                                    if "message" in content:
                                        return content.get("message", "Tool executed")
                                    return json.dumps(content)
                                return str(content)
                            elif "error" in result:
                                return f"Error: {result['error'].get('message', str(result['error']))}"
                            return json.dumps(result)
                        return str(result)
                    except:
                        return response.text
                else:
                    return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error calling tool: {str(e)}"
    
    def build_system_prompt(self) -> str:
        """Build system prompt for Bedrock with tool context
        
        Returns:
            System prompt string
        """
        tools_desc = "Available Browser Automation Tools:\n\n"
        for tool_name, tool_info in self.mcp_tools.items():
            tools_desc += f"- {tool_name}: {tool_info['description']}\n"
            if "params" in tool_info:
                tools_desc += f"  Parameters: {json.dumps(tool_info['params'])}\n"
            tools_desc += "\n"
        
        return f"""You are an intelligent browser automation assistant with access to MCP Selenium tools for precise browser automation.
YOU MUST FOLLOW EXACT INSTRUCTIONS - DO NOT DEVIATE OR MODIFY USER REQUESTS.
COMPLETE ALL STEPS - Execute every step in the user's instructions before providing a summary.

{tools_desc}

CRITICAL RULES:
1. FOLLOW EXACT VALUES: Use the EXACT search terms, URLs, and values the user specifies. Never substitute or change them.
2. COMPLETE ALL STEPS: Execute EVERY numbered step in the user's instructions. Do not skip steps or stop early.
3. PRESERVE CONTEXT: Remember and use exact text from the original instructions throughout the entire session.
4. ONE TOOL PER RESPONSE: Generate EXACTLY one JSON block per response.
5. EXACT JSON FORMAT: 
{{
    "action": "use_tool",
    "tool_name": "tool_name_here",
    "parameters": {{"param1": "value1", "param2": "value2"}}
}}
6. ERROR RECOVERY: If a tool fails, analyze the error and try:
   - Alternative locator strategies (id, css, xpath, name, tag, class)
   - Different timeout values
   - Alternative methods to achieve the goal
7. INTELLIGENT ELEMENT FINDING:
   - Use find_element to discover elements before interacting with them
   - For "first item" or "first product": try common patterns like:
     * CSS selector: ".product:first-child" or "[data-component-type='s-search-result']:first-of-type"
     * XPath: "//div[@data-component-type='s-search-result'][1]" or "(//*[@class='s-result-item'])[1]"
     * Common Amazon: "div[data-component-type='s-search-result'] a.a-link-normal:first-of-type"
   - Try locators in this order: id → name → css → xpath
   - Default timeout is 10000ms; increase for slow-loading pages

EXECUTION RULES:
- Execute each step one at a time in order
- Track your progress through the numbered steps EXPLICITLY
- Before moving to a new step, confirm the previous step is complete
- When a step says "Wait for X to load/appear": use find_element with an appropriate timeout
- When a step says "Click on X": find the element, then click it
- When a step says "Enter text": use send_keys with the exact text specified
- If a tool fails with an error, try alternative approaches, but CONTINUE attempting to complete the step
- ONLY provide a final summary when ALL numbered steps have been executed successfully
- Never skip steps just because something is difficult - persist and try alternatives
- DO NOT DECLARE TASK COMPLETE after reaching search results - search results are typically step 4, not the last step
- Count the total numbered steps and ensure you complete ALL of them

STEP COMPLETION TRACKING:
- At the start, count the total number of steps in the instructions
- After each step, state clearly: "Step X/Y complete" or "Completed step X of Y"
- Do NOT stop until you reach "Step X/Y complete" where X = Y (last step)

SPECIFIC GUIDANCE FOR AMAZON:
- Search bar: id="twotabsearchtextbox"
- Search submit button: id="nav-search-submit-button"
- First search result product: Look for first element with class containing "s-result" or data-component-type="s-search-result"
- Product title on results page: h2 or span with class "a-size-base"
- After getting search results, CONTINUE with remaining steps (clicking product, getting title, etc.)

Remember: Your role is to execute user instructions COMPLETELY and precisely. Do not stop until EVERY step is done."""
    
    async def execute_prompt(self, user_prompt: str, verbose: bool = True) -> str:
        """Execute a browser automation prompt using context-driven while loop
        
        Args:
            user_prompt: The automation task description
            verbose: Print detailed output
            
        Returns:
            Final result/summary
        """
        system_prompt = self.build_system_prompt()
        self.conversation_history = []
        iteration = 0
        
        # Count the number of steps in the prompt
        step_count = len([line for line in user_prompt.split('\n') if line.strip() and line.strip()[0].isdigit() and '.' in line.strip()[:3]])
        
        # Add initial user prompt to conversation
        self.conversation_history.append({
            "role": "user",
            "content": user_prompt
        })
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"STARTING BEDROCK-DRIVEN AUTOMATION")
            print('='*70)
            print(f"📋 Total Steps to Complete: {step_count}")
            print(f"Initial Prompt: {user_prompt[:100]}...\n")
        
        # Main execution loop - continues until task completion
        while True:
            iteration += 1
            
            if verbose:
                print(f"\n{'='*70}")
                print(f"ITERATION {iteration}")
                print('='*70)
                print(f"Context History: {len(self.conversation_history)} messages")
            
            # Call Bedrock with full conversation context
            if verbose:
                print("📞 Calling AWS Bedrock with current context...")
            
            response_text = await self._call_bedrock(system_prompt)
            
            if verbose:
                print(f"\n🤖 Bedrock Response:\n{response_text}\n")
            
            # Add assistant response to history for context
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
            
            # Extract and execute tools in a loop until no more tools or task complete
            tool_iteration = 0
            while True:
                tool_iteration += 1
                
                # Check for tool usages in current response
                tool_usages = self._extract_all_tool_usage(response_text)
                
                if verbose:
                    print(f"📊 Extracted {len(tool_usages)} tools from current response")
                
                if not tool_usages:
                    # No tools in response = task complete
                    if verbose:
                        print("\n✅ No more tools to execute - Task complete!")
                    return response_text
                
                # Execute all tools from this response
                all_results = []
                has_errors = False
                
                for tool_usage in tool_usages:
                    tool_name = tool_usage.get("tool_name")
                    parameters = tool_usage.get("parameters", {})
                    
                    if verbose:
                        print(f"\n🔧 Executing tool: {tool_name}")
                        print(f"   Parameters: {json.dumps(parameters, indent=2)}")
                    
                    # Execute the tool
                    tool_result = await self.call_mcp_tool(tool_name, **parameters)
                    
                    # Check if result is an error
                    is_error = isinstance(tool_result, str) and ("error" in tool_result.lower() or "failed" in tool_result.lower())
                    
                    if verbose:
                        if is_error:
                            print(f"   ⚠️  Error: {tool_result}")
                        else:
                            print(f"   ✓ Success: {str(tool_result)[:150]}")
                    
                    all_results.append({
                        "tool": tool_name,
                        "result": tool_result,
                        "error": is_error
                    })
                    
                    if is_error:
                        has_errors = True
                
                # Build results summary
                results_summary = "\n".join([
                    f"{'❌' if r['error'] else '✓'} {r['tool']}: {r['result']}"
                    for r in all_results
                ])
                
                if verbose:
                    print(f"\n📨 Tool Results Summary:")
                    print(results_summary)
                
                # Send results BACK to Bedrock as context for next decision
                if has_errors:
                    # Errors occurred - ask Bedrock for recovery
                    feedback = f"""⚠️  TOOL EXECUTION ERRORS DETECTED:

{results_summary}

Please analyze these errors and provide recovery actions:
1. For each failed tool, suggest alternative selectors or approaches
2. Try different locator strategies (CSS_SELECTOR, XPATH, ID, CLASS_NAME, NAME)
3. Check if page structure differs from expected
4. Propose the next action to handle these failures and continue toward the goal"""
                    
                    if verbose:
                        print(f"\n🔄 Sending error context to Bedrock for recovery analysis...")
                else:
                    # All tools succeeded
                    feedback = f"""✓ TOOL EXECUTION SUCCESSFUL:

{results_summary}

All tools executed successfully. Analyze the results and:
1. Determine if more steps are needed to complete the task
2. If yes, provide the next tool call
3. If no, provide a final summary of what was accomplished"""
                    
                    if verbose:
                        print(f"\n🔄 Sending success context to Bedrock for next steps...")
                
                # Add results to conversation history
                self.conversation_history.append({
                    "role": "user",
                    "content": feedback
                })
                
                # Call Bedrock AGAIN with the context of tool results
                if verbose:
                    print("📞 Calling AWS Bedrock with tool results context...")
                
                response_text = await self._call_bedrock(system_prompt)
                
                if verbose:
                    print(f"\n🤖 Bedrock's Response to Tool Results:\n{response_text}\n")
                
                # Add Bedrock's response to history for continuity
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response_text
                })
                
                # Loop back to check for more tools in Bedrock's new response
                # The while True loop will continue here
        
        # Max iterations reached
        if verbose:
            print(f"\n⚠️  Max iterations ({self.max_iterations}) reached.")
        return response_text
        
        return "⏱️ Max iterations reached. Could not complete the task."
    
    async def _call_bedrock(self, system_prompt: str) -> str:
        """Call Bedrock API with conversation history
        
        Args:
            system_prompt: System prompt for Bedrock
            
        Returns:
            Bedrock response
        """
        try:
            # Always keep the first message (original prompt) + last 9 messages for context
            if len(self.conversation_history) > 10:
                messages = [self.conversation_history[0]] + self.conversation_history[-9:]
            else:
                messages = self.conversation_history
            
            response = self.bedrock.client.converse(
                modelId=self.bedrock.model_id,
                system=[{"text": system_prompt}],
                messages=[
                    {
                        "role": msg["role"],
                        "content": [{"text": msg["content"]}]
                    }
                    for msg in messages
                ],
                inferenceConfig={
                    "maxTokens": 2048,
                    "temperature": 0.5
                }
            )
            
            if "output" in response and "message" in response["output"]:
                if "content" in response["output"]["message"]:
                    content = response["output"]["message"]["content"]
                    if len(content) > 0 and "text" in content[0]:
                        return content[0]["text"]
            
            return "No response from Bedrock"
            
        except Exception as e:
            return f"Error calling Bedrock: {str(e)}"
    
    def _extract_all_tool_usage(self, response_text: str) -> List[Dict[str, Any]]:
        """Extract ALL tool usage requests from Bedrock response
        
        Args:
            response_text: Response from Bedrock
            
        Returns:
            List of tool usage dictionaries
        """
        tools_list = []
        
        # Find all JSON objects in the response
        # Strategy: find all { and } pairs, then try to parse them
        depth = 0
        start = -1
        
        for i, char in enumerate(response_text):
            if char == '{':
                if depth == 0:
                    start = i
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0 and start != -1:
                    json_str = response_text[start:i+1]
                    try:
                        obj = json.loads(json_str)
                        if obj.get("action") == "use_tool" and obj.get("tool_name"):
                            tools_list.append(obj)
                    except (json.JSONDecodeError, ValueError):
                        # Not valid JSON, skip
                        pass
                    start = -1
        
        return tools_list
    
    def _extract_tool_usage(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extract FIRST tool usage request from Bedrock response
        
        Args:
            response_text: Response from Bedrock
            
        Returns:
            First tool usage dictionary or None
        """
        tools_list = self._extract_all_tool_usage(response_text)
        return tools_list[0] if tools_list else None


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Execute browser automation via Bedrock + MCP"
    )
    
    parser.add_argument(
        "--prompt",
        type=str,
        help="Browser automation task prompt"
    )
    
    parser.add_argument(
        "--prompt-file",
        type=str,
        help="File containing the automation prompt"
    )
    
    parser.add_argument(
        "--mcp-server",
        type=str,
        default="http://localhost:8000",
        help="MCP server URL (default: http://localhost:8000)"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress verbose output"
    )
    
    args = parser.parse_args()
    
    load_dotenv()
    
    # Get prompt from file or command line
    prompt = None
    
    if args.prompt_file:
        if not os.path.exists(args.prompt_file):
            print(f"❌ Prompt file not found: {args.prompt_file}")
            return 1
        
        with open(args.prompt_file, 'r') as f:
            prompt = f.read().strip()
            if not args.quiet:
                print(f"📄 Loaded prompt from: {args.prompt_file}")
    
    elif args.prompt:
        prompt = args.prompt
    
    else:
        print("❌ Please provide either --prompt or --prompt-file")
        parser.print_help()
        return 1
    
    # Create automation engine
    automation = BedrockMCPBrowserAutomation(mcp_server_url=args.mcp_server)
    
    if not args.quiet:
        print("=" * 70)
        print("BEDROCK-DRIVEN MCP BROWSER AUTOMATION")
        print("=" * 70)
        print(f"MCP Server: {args.mcp_server}")
        print(f"Bedrock Model: {automation.bedrock.model_id}")
        print(f"AWS Region: {automation.bedrock.region_name}")
        print("=" * 70)
        print(f"\nPrompt:\n{prompt}\n")
    
    try:
        # Execute the prompt
        result = await automation.execute_prompt(prompt, verbose=not args.quiet)
        
        if not args.quiet:
            print("\n" + "=" * 70)
            print("FINAL RESULT")
            print("=" * 70)
        
        print(result)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import asyncio
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
