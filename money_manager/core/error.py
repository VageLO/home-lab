from fastapi import HTTPException as error
from typing import Optional, List, Dict, Any

def HTTPException(
    status_code: int, 
    detail: List[Dict[str, Any]],
):
    raise error(
        status_code=status_code, 
        detail=detail
    )

def makeDetail(
    msg: str,
    type_str: Optional[str] = '', 
    loc: Optional[list] = [], 
):
    return {
        'type': type_str,
        'loc': loc,
        'msg': msg,
    }
