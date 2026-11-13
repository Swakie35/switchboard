"""Read-only, schema-validated tools over a deliberately synthetic operations snapshot."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from pydantic import BaseModel, ConfigDict, Field

class Params(BaseModel):
    model_config = ConfigDict(extra='forbid')

class Empty(Params):pass

class PolicyArgs(Params):
    topic: str=Field(min_length=2,max_length=50)

class SalesArgs(Params):
    days: int=Field(ge=1,le=30)

INVENTORY=[
    {'sku':'COF-101','name':'Coffee beans','stock':8,'reorder_point':20,'source':'demo/inventory.csv#1'},
    {'sku':'TEA-202','name':'Black tea','stock':37,'reorder_point':15,'source':'demo/inventory.csv#2'},
    {'sku':'JUI-303','name':'Orange juice','stock':6,'reorder_point':12,'source':'demo/inventory.csv#3'},
]
POLICIES={
    'restock':'Reorder when physical stock falls strictly below the configured reorder point. Manager approval is needed before placing an order.',
    'returns':'Returns require a receipt and manual review within 14 days of purchase.',
}
DAILY_REVENUE=[11000,12400,9800,13500,12700,12100,14300,10400,13900,14500,12000,12800,11600,13200,14100,12900,11700,13400,12200,14300,13600,11000,12800,13500,12300,13200,14900,12500,13000,13900]

def low_stock(_:Empty):
    return {'items':[x for x in INVENTORY if x['stock']<x['reorder_point']],
            'provenance':'demo inventory snapshot; no live systems connected'}

def policy_lookup(args:PolicyArgs):
    topic=args.topic.strip().lower()
    if topic not in POLICIES:return {'matches':[],'provenance':'demo/policy.md'}
    return {'matches':[{'topic':topic,'text':POLICIES[topic],
                        'citation':f'demo/policy.md#{topic}'}],'provenance':'invented policy fixture'}

def sales_summary(args:SalesArgs):
    sample=DAILY_REVENUE[-args.days:]
    return {'period_days':args.days,'net_revenue_pence':sum(sample),
            'average_daily_revenue_pence':round(sum(sample)/len(sample)),
            'source':f'demo/sales.csv#last-{args.days}-days',
            'provenance':'seeded demonstration values'}

@dataclass(frozen=True)
class Tool:
    description: str
    parameters: type[Params]
    handler: Callable

REGISTRY={
    'low_stock':Tool('Return products strictly below their reorder point; read-only.',Empty,low_stock),
    'policy_lookup':Tool('Look up a named demo policy: restock or returns.',PolicyArgs,policy_lookup),
    'sales_summary':Tool('Summarise the last 1–30 days of synthetic sales.',SalesArgs,sales_summary),
}

def execute(name:str,args:dict):
    if name not in REGISTRY:raise ValueError(f'Unapproved tool: {name}')
    tool=REGISTRY[name]
    return tool.handler(tool.parameters.model_validate(args))

def openai_tools()->list[dict]:
    return [{'type':'function','function':{
      'name':name,'description':tool.description,'parameters':tool.parameters.model_json_schema(),
      'strict':True}} for name,tool in REGISTRY.items()]
