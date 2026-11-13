from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from .agent import Agent,Audit,RulePlanner
from .openai_planner import OpenAIPlanner

app=FastAPI(title='Switchboard',version='0.1.0')
agent=Agent(Audit('switchboard.sqlite'),max_steps=3)
class Question(BaseModel):
    question:str=Field(min_length=1,max_length=1000)
    mode:str='offline'
@app.get('/health')
def health():return {'status':'ok'}
@app.post('/ask')
def ask(body:Question):
    if body.mode not in ('offline','llm'):raise HTTPException(400,'mode must be offline or llm')
    try:
        planner=RulePlanner() if body.mode=='offline' else OpenAIPlanner()
        return agent.run(body.question,planner)
    except ValueError as ex:raise HTTPException(400,str(ex))
@app.get('/runs/{run_id}')
def get_run(run_id:str):
    result=agent.audit.get(run_id)
    if result is None:raise HTTPException(404,'Run not found')
    return result
