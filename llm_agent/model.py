"""
Model loading and inference for language models with tool use capabilities.
"""

import os
from typing import Dict, List, Optional, Any, Union
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from loguru import logger

DEFAULT_MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"

class LLMModel:
    """Handles loading and inference for language models with tools."""
    
    def __init__(self, 
                 model_id: str = None,
                 device: str = "cuda" if torch.cuda.is_available() else "cpu",
                 max_new_tokens: int = 1024,
                 temperature: float = 0.1):
        """
        Initialize the language model.
        
        Args:
            model_id: HuggingFace model ID or path to local model
            device: Device to run the model on ("cuda", "cpu")
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
        """
        self.model_id = model_id or os.environ.get("MODEL_PATH", DEFAULT_MODEL_ID)
        self.device = device
        self.max_new_tokens = int(os.environ.get("MAX_NEW_TOKENS", max_new_tokens))
        self.temperature = temperature
        
        # Get HuggingFace token from environment if available
        hf_token = os.environ.get("HUGGINGFACE_TOKEN")
        logger.info(f"Loading model {self.model_id} on {self.device}")
        
        # Pass token to tokenizer and model loaders if available
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_id,
            token=hf_token
        )
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            token=hf_token,
            torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )
        logger.info(f"Model loaded successfully")
        
        self.generation_pipeline = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=self.max_new_tokens,
            temperature=self.temperature,
            top_p=0.95,
            do_sample=temperature > 0,
            pad_token_id=self.tokenizer.eos_token_id
        )
    
    def generate(self, prompt: str) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text
        """
        logger.debug(f"Generating with prompt:\n{prompt}")
        result = self.generation_pipeline(prompt)[0]['generated_text']
        
        # Extract only the newly generated content
        if result.startswith(prompt):
            result = result[len(prompt):]
            
        logger.debug(f"Generated text:\n{result}")
        return result.strip()
        
    def generate_with_tools(self, prompt: str) -> Dict[str, Any]:
        """
        Generate text that may include tool calls.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Dict with generated text and detected tool calls
        """
        raw_output = self.generate(prompt)
        
        # This would be expanded in the agent module to parse the tool calls
        return {
            "output": raw_output,
            "tool_calls": self._extract_tool_calls(raw_output)
        }
    
    def _extract_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        """
        Simple extraction of potential tool calls from text.
        This is a placeholder - the full implementation would be in the agent module.
        
        Args:
            text: Generated text to extract tool calls from
            
        Returns:
            List of extracted tool calls
        """
        # Placeholder - will be implemented in agent.py
        return [] 