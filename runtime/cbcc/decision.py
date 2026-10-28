from __future__ import annotations
from typing import Any


def compile_persuasion_frameworks(shopper_questions:list[str], product:dict[str,Any], offer:dict[str,Any]|None=None, requested:list[str]|None=None)->dict[str,Any]:
    """Compile optional persuasion frameworks into decision aids.

    Frameworks are not asset templates. They annotate decision jobs so downstream
    content can use only the parts that actually help a shopper move forward.
    """
    requested=[] if requested is None else list(requested)
    qs=[q for q in shopper_questions if str(q).strip()]
    out={'status':'COMPILED' if requested else 'NOT_REQUESTED','frameworks':{},'requested':requested,'principle':'Frameworks are optional reasoning tools. Apply only frameworks the user/Agent selected because they change a concrete decision; they never determine a fixed asset sequence.'}
    if 'AIDA' in requested:
        stages=['ATTENTION','INTEREST','DESIRE','ACTION']
        out['frameworks']['AIDA']=[{'stage':stages[min(i,3)],'shopper_question':q} for i,q in enumerate(qs)]
    if 'FABE' in requested:
        out['frameworks']['FABE']={
            'feature_sources':sorted(product.keys()),
            'advantage_job':'Translate verified product differences into relevant advantages.',
            'benefit_job':'Connect approved advantages to the shopper job without expanding the claim.',
            'evidence_job':'Bind the message to source/claim evidence before publication.'
        }
    if '4P' in requested:
        out['frameworks']['4P']={
            'product':'Resolved from Product Truth and Commerce Entity.',
            'price':'Resolved from Offer/Economics when supplied.',
            'place':'Resolved from Market × Platform × Site × Surface.',
            'promotion':'Resolved from approved Offer/Content/Ads contracts.',
            'offer_status':(offer or {}).get('status','INSUFFICIENT_DATA')
        }
    return out
