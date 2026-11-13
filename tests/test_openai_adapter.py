"""Offline fake checks the real adapter's function-call protocol without a paid API."""
from types import SimpleNamespace as NS
from switchboard.openai_planner import OpenAIPlanner
from switchboard.agent import Agent

class FakeCompletions:
    def __init__(self):self.requests=[]
    def create(self,**kwargs):
        self.requests.append(kwargs)
        if len(self.requests)==1:
            call=NS(id='call_1',function=NS(name='low_stock',arguments='{}'))
            msg=NS(content=None,tool_calls=[call])
        else:
            assert any(m['role']=='tool' and m['tool_call_id']=='call_1' for m in kwargs['messages'])
            msg=NS(content='Coffee beans [demo/inventory.csv#1] need review.',tool_calls=[])
        return NS(choices=[NS(message=msg)])

def test_llm_function_call_protocol_without_network():
    fake=FakeCompletions()
    client=NS(chat=NS(completions=fake))
    result=Agent().run('What is below reorder point?',OpenAIPlanner(model='fake-model',client=client))
    assert result['status']=='answered' and result['steps']==1
    assert 'Coffee beans' in result['answer']
    assert fake.requests[0]['parallel_tool_calls'] is False
