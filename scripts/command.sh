#!/bin/bash

# General usage pattern:
#docker exec -it the-architect python main.py "YOUR_COMMAND_HERE"

# Concrete Example:
#docker exec -it the-architect python main.py "Research best practices for sanitizing sqlite file uploads and log the result to output/sec_brief.txt"

# How to Target a Specific Agent via Terminal
#docker exec -it the-architect python main.py --agent coder "Write a database migration script"

# Targeting a Specific Agent (e.g., the Coder):
#docker exec -it the-architect python main.py --agent coder "Implement a secure token validation method in auth.py"

# Use code with caution.Targeting the Researcher:
#docker exec -it the-architect python main.py --agent researcher "Find the latest CVE patches released for SQLite in 2026"

# Use code with caution.Global Fallback (Legacy Mode):
#docker exec -it the-architect python main.py "Standard mission instruction"





