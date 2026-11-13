import argparse
import json
from .agent import Agent,RulePlanner
from .openai_planner import OpenAIPlanner
p=argparse.ArgumentParser(description='Read-only, step-bounded tool-calling demonstration')
p.add_argument('--question',default='Which items are below their reorder point?')
p.add_argument('--mode',choices=['offline','llm'],default='offline')
a=p.parse_args()
planner=RulePlanner() if a.mode=='offline' else OpenAIPlanner()
print(json.dumps(Agent().run(a.question,planner),indent=2))
