"""
BHARATSOLVE SEO AGENCY — Rank Tracking Agent
Checks and tracks keyword rankings in search results.
"""
import json
import time
import random
from datetime import datetime
from utils.llm_client import call_llm
from db.operations import get_keywords, update_keyword_position, get_project, log_agent_action

RANK_SYSTEM_PROMPT = """तुम एक SEO Rank Tracking Agent हो।
तुम्हारा काम simulated rank checking करना है जब तक real search API integrate न हो।
Actual search engine data के जैसा ही realistic data generate करो।"""


def check_rankings(project_id: int, simulate: bool = True) -> list:
    """
    Check rankings for all keywords in a project.
    When simulate=True, generates realistic mock data.
    """
    keywords = get_keywords(project_id)
    project = get_project(project_id)
    
    if not keywords:
        return []
    
    results = []
    for kw in keywords:
        if simulate:
            position = simulate_ranking(kw)
        else:
            position = check_real_ranking(kw, project)
        
        update_keyword_position(kw['id'], position)
        
        results.append({
            "keyword": kw['keyword'],
            "previous_position": kw['current_position'],
            "new_position": position,
            "change": kw['current_position'] - position if kw['current_position'] > 0 else 0,
            "checked_at": datetime.now().isoformat()
        })
    
    # Calculate summary
    improved = sum(1 for r in results if r['change'] > 0)
    declined = sum(1 for r in results if r['change'] < 0)
    
    log_agent_action("rank", f"Checked {len(results)} keywords for project {project_id}: {improved} improved, {declined} declined",
                     response_time_ms=len(results) * 200)
    
    return results


def simulate_ranking(keyword: dict) -> int:
    """
    Simulate realistic ranking changes.
    Uses current position as baseline with small fluctuations.
    """
    current = keyword['current_position'] or random.randint(30, 100)
    difficulty = keyword['difficulty'] or 50
    
    # Higher difficulty = harder to rank
    # Add realistic random walk
    change = random.gauss(0, 3)  # mean 0, std 3
    
    # Slow improvement trend if keyword is being worked on
    if current > 20:
        change -= random.uniform(0, 2)  # slight improvement bias
    
    # If already ranking well, more stable
    if current < 5:
        change = random.gauss(0, 1)
    
    new_pos = max(1, min(100, current + round(change)))
    return new_pos


def check_real_ranking(keyword: dict, project: dict) -> int:
    """
    Placeholder for real SERP checking.
    Will integrate with search APIs later.
    """
    # TODO: Integrate with Google Search Console API
    # TODO: Integrate with third-party rank tracker APIs
    return simulate_ranking(keyword)


def get_ranking_insights(project_id: int) -> dict:
    """Generate AI insights about current rankings."""
    keywords = get_keywords(project_id)
    
    if not keywords:
        return {"insights": "No keywords to analyze", "suggestions": []}
    
    top_10 = [k for k in keywords if k['current_position'] <= 10 and k['current_position'] > 0]
    top_30 = [k for k in keywords if 11 <= k['current_position'] <= 30]
    not_ranked = [k for k in keywords if k['current_position'] == 0]
    
    insights = {
        "total_keywords": len(keywords),
        "top_10_count": len(top_10),
        "top_30_count": len(top_30),
        "not_ranked_count": len(not_ranked),
        "top_10_keywords": [k['keyword'] for k in top_10],
        "needs_work": [k['keyword'] for k in not_ranked[:10]],
        "avg_position": round(
            sum(k['current_position'] for k in keywords if k['current_position'] > 0) / 
            max(len([k for k in keywords if k['current_position'] > 0]), 1), 1
        )
    }
    
    return insights
