"""
BHARATSOLVE SEO AGENCY — Auto-Pilot Mode
Self-healing autonomous mode that runs all agents and monitors performance.
NOTE: On Streamlit Cloud, auto-pilot runs via the scheduler in each session refresh.
"""
import time
import threading
import os
from datetime import datetime
from db.operations import log_agent_action, get_agent_status_summary
from harness.scheduler import run_all_agents

_auto_pilot_active = False
_auto_pilot_thread = None

# Streamlit Cloud does NOT support background threads reliably
_IS_CLOUD = os.environ.get('STREAMLIT_RUNNER_ID') is not None


def run_auto_pilot(interval_minutes: int = 60):
    """
    Start auto-pilot mode.
    Runs all agents on a loop with self-healing monitoring.
    """
    global _auto_pilot_active, _auto_pilot_thread
    
    if _auto_pilot_active:
        return "Auto-pilot is already running"
    
    # On Streamlit Cloud, background threads don't work reliably
    if _IS_CLOUD:
        return "⚠️ Auto-pilot not available on Streamlit Cloud. Agents run during page loads."
    
    _auto_pilot_active = True
    
    def _loop():
        cycle = 0
        while _auto_pilot_active:
            cycle += 1
            print(f"\n{'='*50}")
            print(f"🔄 Auto-Pilot Cycle {cycle} at {datetime.now().isoformat()}")
            print(f"{'='*50}")
            
            try:
                run_all_agents()
                log_agent_action("auto_pilot", f"Completed cycle {cycle}", response_time_ms=0)
            except Exception as e:
                log_agent_action("auto_pilot", f"Cycle {cycle} failed", status="error", error_message=str(e))
                print(f"❌ Cycle {cycle} failed: {e}")
            
            # Check agent health
            statuses = get_agent_status_summary()
            for s in statuses:
                if s['status'] == 'error':
                    print(f"⚠️ Agent {s['agent_name']} reported error: {s['error_message'][:100]}")
            
            # Wait for next cycle (check every 10s if we should stop)
            for _ in range(interval_minutes * 6):
                if not _auto_pilot_active:
                    break
                time.sleep(10)
    
    _auto_pilot_thread = threading.Thread(target=_loop, daemon=True)
    _auto_pilot_thread.start()
    
    return f"✅ Auto-pilot started! Running every {interval_minutes} minutes."


def stop_auto_pilot():
    """Stop auto-pilot mode."""
    global _auto_pilot_active
    _auto_pilot_active = False
    log_agent_action("auto_pilot", "Auto-pilot stopped")
    return "⏹️ Auto-pilot stopped."
