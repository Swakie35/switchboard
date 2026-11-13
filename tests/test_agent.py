from types import SimpleNamespace
from fastapi.testclient import TestClient
import pytest
from switchboard.agent import Action,Agent,Audit,RulePlanner
from switchboard.api import app
from switchboard.tools import execute,openai_tools

def test_offline_agent_gives_evidence_trace():
    report=Agent().run('Which products are low in stock?')
    assert report['status']=='answered'
    assert report['trace'][0]['tool']=='low_stock'
    assert len(report['trace'][0]['result']['items'])==2
    assert 'demo/inventory.csv' in report['answer']

def test_audit_and_validation():
    audit=Audit();agent=Agent(audit)
    report=agent.run('Explain our returns policy')
    assert audit.get(report['run_id'])==report
    assert report['trace'][0]['tool']=='policy_lookup'
    with pytest.raises(ValueError):agent.run('')

def test_unapproved_tool_is_blocked():
    class Dangerous:
        def step(self,question,observations):return Action('tool','delete_all',{})
        def observe(self,action,result):pass
    r=Agent().run('ignore policy',Dangerous())
    assert r['status']=='blocked' and r['steps']==0

def test_step_budget_stops_loop():
    class Loop:
        def step(self,question,observations):return Action('tool','low_stock',{})
        def observe(self,action,result):pass
    r=Agent(max_steps=2).run('what?',Loop())
    assert r['status']=='step_limit' and r['steps']==2

def test_schema_rejects_extra_arguments():
    with pytest.raises(ValueError):execute('low_stock',{'sql':'DROP TABLE ...'})
    assert len(openai_tools())==3

def test_http_routes():
    c=TestClient(app)
    assert c.get('/health').status_code==200
    r=c.post('/ask',json={'question':'sales last week','mode':'offline'})
    assert r.status_code==200
    assert c.get('/runs/'+r.json()['run_id']).status_code==200
    assert c.post('/ask',json={'question':'hello','mode':'invalid'}).status_code==400
