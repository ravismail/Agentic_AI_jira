from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
import config
import os

# Data structure for output
class JiraStory(BaseModel):
    summary: str = Field(description="The validation summary of the story")
    description: str = Field(description="Detailed description of the story")
    acceptance_criteria: List[str] = Field(description="List of acceptance criteria")

class StoryList(BaseModel):
    stories: List[JiraStory] = Field(description="List of extracted Jira stories")

class LLMProcessor:
    def __init__(self, provider=None, model_name=None):
        self.provider = provider or config.LLM_PROVIDER
        self.model = model_name
        
        if self.provider == 'openai':
            api_key = config.OPENAI_API_KEY
            if not api_key:
                print("Warning: OPENAI_API_KEY not found in config.")
            self.model = self.model or config.OPENAI_MODEL
            self.llm = ChatOpenAI(model=self.model, api_key=api_key)
            print(f"Initialized OpenAI with model: {self.model}")
        else:
            # Default to Ollama
            self.model = self.model or config.OLLAMA_MODEL
            try:
                self.llm = OllamaLLM(model=self.model, base_url=config.OLLAMA_BASE_URL)
            except Exception:
                self.llm = OllamaLLM(model=self.model)
            print(f"Initialized Ollama with model: {self.model}")
        
        self.parser = JsonOutputParser(pydantic_object=StoryList)
        
        template = """
        You are an expert Agile Product Owner. Your task is to analyze meeting minutes or project documentation and extract actionable user stories for Jira.
        
        For each story, provide:
        1. A concise Summary.
        2. A detailed Description explaining the 'Why', 'What', and 'Who'.
        3. A list of Acceptance Criteria that must be met.
        
        Return the result as a JSON object with a list of stories.
        
        Meeting Minutes / Content:
        {content}
        
        {format_instructions}
        """
        
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["content"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        
        # Create a simple chain that returns the raw string first
        self.chain = self.prompt | self.llm

    def generate_stories(self, content):
        """Generates Jira stories from text content."""
        print("Analyzing content with LLM...")
        try:
            # 1. Get raw response
            response = self.chain.invoke({"content": content})
            
            # Handle AIMessage object (OpenAI) vs String (Ollama sometimes)
            if hasattr(response, 'content'):
                clean_response = response.content
            else:
                clean_response = str(response)
            
            # 2. Clean response (remove markdown fences if present)
            clean_response = clean_response.strip()
            # Remove markdown code blocks
            if "```json" in clean_response:
                clean_response = clean_response.split("```json")[1].split("```")[0]
            elif "```" in clean_response:
                clean_response = clean_response.split("```")[1].split("```")[0]
            
            # Find the first '{' and the last '}'
            start_idx = clean_response.find('{')
            end_idx = clean_response.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                clean_response = clean_response[start_idx:end_idx+1]
            
            clean_response = clean_response.strip()

            # 3. Parse
            parsed = self.parser.parse(clean_response)
            return parsed.get('stories', [])
            
        except Exception as e:
            print(f"\nError generating stories: {e}")
            print("\n--- RAW LLM RESPONSE ---")
            # If response variable exists, print it
            if 'response' in locals():
                print(response)
            else:
                print("No response received.")
            print("------------------------\n")
            return []

if __name__ == "__main__":
    pass
