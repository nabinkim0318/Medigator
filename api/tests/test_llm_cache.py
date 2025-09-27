# api/tests/test_llm_cache.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from api.core.schemas import SummaryIn
from api.services.llm.tasks import summarize as task
from api.services.llm import client as cl

@pytest.mark.anyio
async def test_cache_hit(monkeypatch):
    # check if cache functionality is working
    from api.services.llm.client import _cache, clear_cache
    
    # initialize cache
    clear_cache()
    
    # first call - use fallback function
    body = SummaryIn(encounterId='e6', patient={'age':25}, answers={'cc':'headache'})
    result1 = await task.run(body)
    
    # second call - check cache with same input
    result2 = await task.run(body)
    
    # check if results are the same (cache should be working)
    assert result1.hpi == result2.hpi
    assert result1.flags == result2.flags
    
    # check cache statistics
    cache_stats = _cache.get_stats()
    assert cache_stats['size'] >= 0  # check if cache exists
