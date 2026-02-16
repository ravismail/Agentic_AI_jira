# Configuration
import os

# Jira Configuration
JIRA_URL = "https://ravikanthmasanal.atlassian.net"
JIRA_API_TOKEN = ""
JIRA_EMAIL = "ravikanth.masanal@gmail.com"

# Confluence Configuration
CONFLUENCE_PAGE_URL = "https://ravikanthmasanal.atlassian.net/wiki/spaces/~7120208d0b443ee4af464889146a4138af33f3/pages/393218/2026-02-06+Meeting+notes"

# LLM Configuration
# Options: 'ollama', 'openai'
LLM_PROVIDER = "openai" 

# Ollama Settings
OLLAMA_MODEL = "llama3"
OLLAMA_BASE_URL = "http://localhost:11434"

# OpenAI Settings
OPENAI_API_KEY = ""
OPENAI_MODEL = "gpt-4o"

# You can override these with environment variables if needed
if os.getenv("JIRA_API_TOKEN"):
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
if os.getenv("OPENAI_API_KEY"):
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
