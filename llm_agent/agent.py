"""
Core agent functionality for LLM Tool Agent.
"""

import json
import re
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from loguru import logger

from .model import LLMModel
from .prompts import create_full_prompt

# Regular expressions for parsing ReAct format
THINKING_PATTERN = r"THINKING:\s*(.*?)(?=ACTION:|FINAL_ANSWER:|$)"
ACTION_PATTERN = r"ACTION:\s*(.*?)(?=ACTION_INPUT:|$)"
ACTION_INPUT_PATTERN = r"ACTION_INPUT:\s*(.*?)(?=OBSERVATION:|$)"
OBSERVATION_PATTERN = r"OBSERVATION:\s*(.*?)(?=THINKING:|ACTION:|FINAL_ANSWER:|$)"
FINAL_ANSWER_PATTERN = r"FINAL_ANSWER:\s*(.*?)(?=$)"


class ToolAgent:
    """
    Agent that uses language models with ReAct-style tool use capabilities.
    """
    
    def __init__(self, model: Optional[LLMModel] = None):
        """
        Initialize the tool agent.
        
        Args:
            model: Optional LLMModel instance (will create one if not provided)
        """
        self.model = model or LLMModel()
        self.tools: Dict[str, Callable] = {}
        self.tool_definitions: List[Dict[str, Any]] = []
    
    def register_tool(self, 
                     name: str, 
                     func: Callable, 
                     description: str, 
                     parameters: Dict[str, Dict[str, Any]],
                     output_description: str):
        """
        Register a tool with the agent.
        
        Args:
            name: Tool name
            func: Function to call when the tool is used
            description: Tool description
            parameters: Parameter definitions for the tool
            output_description: Description of the tool's output
        """
        self.tools[name] = func
        self.tool_definitions.append({
            "name": name,
            "description": description,
            "parameters": parameters,
            "output": output_description
        })
        logger.info(f"Registered tool: {name}")
    
    def parse_react_output(self, text: str) -> Dict[str, Any]:
        """
        Parse ReAct-formatted text to extract thinking, actions, and final answer.
        
        Args:
            text: ReAct-formatted text output from the model
            
        Returns:
            Dictionary with parsed components
        """
        result = {
            "thinking": [],
            "actions": [],
            "final_answer": None,
            "raw_output": text
        }
        
        # Extract thinking steps
        thinking_matches = re.finditer(THINKING_PATTERN, text, re.DOTALL)
        for match in thinking_matches:
            if match.group(1).strip():
                result["thinking"].append(match.group(1).strip())
        
        # Extract actions and their inputs
        action_matches = list(re.finditer(ACTION_PATTERN, text, re.DOTALL))
        action_input_matches = list(re.finditer(ACTION_INPUT_PATTERN, text, re.DOTALL))
        observation_matches = list(re.finditer(OBSERVATION_PATTERN, text, re.DOTALL))
        
        for i, action_match in enumerate(action_matches):
            action = action_match.group(1).strip()
            
            # Try to find the corresponding input
            action_input = None
            if i < len(action_input_matches):
                action_input_text = action_input_matches[i].group(1).strip()
                try:
                    # Try to parse as JSON
                    action_input = json.loads(action_input_text)
                except json.JSONDecodeError:
                    # If not valid JSON, use as raw text
                    action_input = action_input_text
            
            # Try to find the corresponding observation
            observation = None
            if i < len(observation_matches):
                observation = observation_matches[i].group(1).strip()
            
            result["actions"].append({
                "tool": action,
                "input": action_input,
                "observation": observation
            })
        
        # Extract final answer
        final_answer_match = re.search(FINAL_ANSWER_PATTERN, text, re.DOTALL)
        if final_answer_match:
            result["final_answer"] = final_answer_match.group(1).strip()
        
        return result
    
    def execute_tools(self, parsed_output: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """
        Execute the tools specified in the parsed output.
        
        Args:
            parsed_output: Output from parse_react_output
            
        Returns:
            Updated parsed output and continuation prompt
        """
        continuation_text = ""
        
        for i, action in enumerate(parsed_output["actions"]):
            tool_name = action["tool"]
            tool_input = action["input"]
            
            # Skip if this action already has an observation
            if action["observation"] is not None:
                continue
            
            # Check if tool exists
            if tool_name not in self.tools:
                observation = f"Error: Tool '{tool_name}' not found. Available tools: {', '.join(self.tools.keys())}"
            else:
                try:
                    # Execute the tool
                    tool_func = self.tools[tool_name]
                    observation = tool_func(tool_input)
                    parsed_output["actions"][i]["observation"] = observation
                except Exception as e:
                    observation = f"Error executing tool '{tool_name}': {str(e)}"
                    parsed_output["actions"][i]["observation"] = observation
            
            # Add to continuation text for the next model call
            continuation_text += f"ACTION: {tool_name}\n"
            continuation_text += f"ACTION_INPUT: {json.dumps(tool_input, ensure_ascii=False)}\n"
            continuation_text += f"OBSERVATION: {observation}\n"
            
            # We only execute the first tool without an observation
            break
        
        return parsed_output, continuation_text
    
    def run(self, 
           query: str, 
           conversation_history: Optional[List[Dict[str, str]]] = None,
           examples: Optional[List[Dict[str, str]]] = None,
           max_iterations: int = 10) -> Dict[str, Any]:
        """
        Run the agent with a query.
        
        Args:
            query: User query
            conversation_history: Optional conversation history
            examples: Optional few-shot examples
            max_iterations: Maximum number of tool execution iterations
            
        Returns:
            Result dictionary with thinking steps, actions, and final answer
        """
        logger.info(f"Running agent with query: {query}")
        
        prompt = create_full_prompt(
            query=query,
            tools=self.tool_definitions,
            examples=examples,
            conversation_history=conversation_history
        )
        
        # First model call to get initial response
        response = self.model.generate(prompt)
        parsed = self.parse_react_output(response)
        
        # Iterate until we have a final answer or reach max iterations
        iterations = 0
        while (not parsed["final_answer"] and 
               iterations < max_iterations and 
               any(action["observation"] is None for action in parsed["actions"])):
            
            # Execute tools
            parsed, continuation = self.execute_tools(parsed)
            
            if not continuation:
                # No more tools to execute
                break
            
            # Continue with the model
            next_prompt = prompt + response + "\n" + continuation
            next_response = self.model.generate(next_prompt)
            
            # Add the new response to the existing one
            response += "\n" + continuation + next_response
            parsed = self.parse_react_output(response)
            
            iterations += 1
            logger.debug(f"Completed iteration {iterations}")
        
        result = {
            "query": query,
            "thinking": parsed["thinking"],
            "actions": parsed["actions"],
            "final_answer": parsed["final_answer"],
            "raw_output": parsed["raw_output"]
        }
        
        logger.info(f"Agent run completed with {len(parsed['actions'])} tool calls")
        return result 