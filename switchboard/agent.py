"""Step-budgeted orchestration with explicit evidence and per-run audit persistence."""
from __future__ import annotations
from dataclasses import dataclass
import json
import sqlite3
from pathlib import Path
import uuid
from .tools import execute

@dataclass(frozen=True)
class Action:
    kind: str   # 'tool' or 'final'
    name: str=''
    args: dict|None=None
    content: str=''
    call_id: str=''

class RulePlanner:
    """Offline planner for demos/tests, NOT a language model."""
    def __init__(self):self.called=False
    def step(self,question,observations):
        if observations:
            last=observations[-1]
            return Action('final',content='From the demonstration data: '+json.dumps(last['result'],sort_keys=True))
        q=question.lower()
        if 'policy' in q or 'returns' in q:
            return Action('tool','policy_lookup',{'topic':'returns' if 'return' in q else 'restock'})
        if any(s in q for s in ('inventory','stock','restock','reorder')):
            return Action('tool','low_stock',{})
        return Action('tool','sales_summary',{'days':7})
    def observe(self,action,result):pass

class Audit:
    def __init__(self,path=':memory:'):
        self.con=sqlite3.connect(str(path),check_same_thread=False)
        self.con.execute('''CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY, question TEXT NOT NULL, result TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
        self.con.commit()
    def save(self,question,result):
        with self.con:self.con.execute('INSERT INTO runs(run_id,question,result) VALUES(?,?,?)',
                                        (result['run_id'],question,json.dumps(result)))
    def get(self,run_id):
        row=self.con.execute('SELECT result FROM runs WHERE run_id=?',(run_id,)).fetchone()
        return json.loads(row[0]) if row else None

class Agent:
    def __init__(self,audit:Audit|None=None,max_steps:int=3):
        if not 1<=max_steps<=10:raise ValueError('max_steps must be 1..10')
        self.audit=audit or Audit();self.max_steps=max_steps
    def run(self,question:str,planner=None):
        if not question or len(question)>1000:raise ValueError('question length must be 1..1000')
        planner=planner or RulePlanner()
        run_id=str(uuid.uuid4());observations=[];status='step_limit';answer='Stopped at the tool-call limit.'
        for _ in range(self.max_steps+1):
            action=planner.step(question,observations)
            if action.kind=='final':
                status='answered' if observations else 'no_evidence'
                answer=action.content if observations else 'No tool evidence was retrieved.'
                break
            if action.kind!='tool' or len(observations)>=self.max_steps:
                status='step_limit';break
            try:
                result=execute(action.name,action.args or {})
            except (ValueError,TypeError) as ex:
                status='blocked';answer=f'Tool invocation rejected: {str(ex)[:150]}';break
            observations.append({'tool':action.name,'arguments':action.args or {},'result':result})
            planner.observe(action,result)
        report={'run_id':run_id,'status':status,'answer':answer,'steps':len(observations),
                'trace':observations,'mode':type(planner).__name__}
        self.audit.save(question,report)
        return report
