"""
BHARATSOLVE SEO AGENCY — Task Scheduler
Runs agents on schedule using APScheduler.
NOTE: On Streamlit Cloud, APScheduler background threads are avoided.
"""
import time
import threading
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from db.operations import get_all_projects, log_agent_action
from agents.keyword_agent import research_keywords
from agents.rank_agent import check_rankings
from agents.social_agent import create_social_post

_IS_CLOUD = os.environ.get('STREAMLIT_RUNNER_ID') is not None

scheduler = BackgroundScheduler()
_is_running = False


def run_keyword_agent():
    """Batch keyword research for all active projects."""
    projects = get_all_projects()
    for p in projects:
        try:
            research_keywords(p['id'])
            log_agent_action("keyword", f"Scheduled research for project {p['id']}")
        except Exception as e:
            log_agent_action("keyword", f"Scheduled research failed", status="error", error_message=str(e))


def run_rank_agent():
    """Batch rank checking for all active projects."""
    projects = get_all_projects()
    for p in projects:
        try:
            check_rankings(p['id'], simulate=True)
            log_agent_action("rank", f"Scheduled rank check for project {p['id']}")
        except Exception as e:
            log_agent_action("rank", f"Scheduled rank check failed", status="error", error_message=str(e))


def run_social_agent():
    """Post scheduled social media content."""
    projects = get_all_projects()
    for p in projects:
        try:
            # Create a daily post for each project
            create_social_post(p['id'], "google_business", content_type="update")
            log_agent_action("social", f"Scheduled daily post for project {p['id']}")
        except Exception as e:
            log_agent_action("social", f"Scheduled post failed", status="error", error_message=str(e))


def run_all_agents():
    """Run all agents once."""
    print(f"🚀 Running all agents at {datetime.now().isoformat()}")
    
    threads = [
        threading.Thread(target=run_keyword_agent),
        threading.Thread(target=run_rank_agent),
        threading.Thread(target=run_social_agent),
    ]
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    print(f"✅ All agents completed at {datetime.now().isoformat()}")


def start_scheduler():
    """Start the background scheduler with all jobs."""
    global _is_running
    if _is_running:
        return
    
    # Run rank check every 6 hours (as per config)
    scheduler.add_job(run_rank_agent, 'interval', hours=6, id='rank_check', replace_existing=True)
    
    # Run keyword research daily
    scheduler.add_job(run_keyword_agent, 'interval', hours=24, id='keyword_research', replace_existing=True)
    
    # Social posts every 8 hours
    scheduler.add_job(run_social_agent, 'interval', hours=8, id='social_posts', replace_existing=True)
    
    # Daily full run
    scheduler.add_job(run_all_agents, 'cron', hour=2, minute=0, id='daily_full_run', replace_existing=True)
    
    scheduler.start()
    _is_running = True
    print("✅ Scheduler started - agents will run automatically")


def stop_scheduler():
    """Stop the background scheduler."""
    global _is_running
    if _is_running:
        scheduler.shutdown(wait=False)
        _is_running = False
        print("⏹️ Scheduler stopped")
