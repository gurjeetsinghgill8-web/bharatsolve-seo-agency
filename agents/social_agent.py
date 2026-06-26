"""
BHARATSOLVE SEO AGENCY — Social Media Agent
Manages social media posts across platforms.
"""
import json
import time
from datetime import datetime, timedelta
from utils.llm_client import call_llm
from db.operations import schedule_social_post, get_scheduled_posts, log_agent_action, get_project

SOCIAL_SYSTEM_PROMPT = """तुम एक Social Media Marketing Agent हो।
तुम्हारा काम:
1. Business और platform के according engaging social media posts बनाना
2. Platform-specific content strategy देना
3. Hinglish में catchy posts लिखना
4. Emojis और hashtags include करना

Platforms: Google Business Profile, Facebook, Instagram, Telegram, Email"""


def create_social_post(project_id: int, platform: str, topic: str = "", 
                       content_type: str = "promotional") -> dict:
    """
    Generate and schedule a social media post.
    """
    project = get_project(project_id)
    
    platform_prompts = {
        "google_business": "Google Business Profile post (local SEO focused, with offers/updates)",
        "facebook": "Facebook post (engaging, shareable, with CTA)",
        "instagram": "Instagram post with caption (visual description, hashtags, emojis)",
        "telegram": "Telegram channel post (informative, direct, with link)",
        "email": "Email newsletter (subject line, body, CTA button)"
    }
    
    platform_style = platform_prompts.get(platform, f"{platform} post")
    
    prompt = f"""
Business: {project['name'] if project else 'General Business'}
Location: {project.get('target_location', '') if project else ''}
Platform: {platform_style}
Topic: {topic or project['name'] if project else 'general update'}
Type: {content_type}

Generate a complete post:
- Platform-appropriate tone and length
- Emojis where suitable
- 3-5 relevant hashtags
- Call to action
- Best posting time suggestion

Return JSON:
{{
  "content": "Full post content...",
  "hashtags": ["#tag1", "#tag2"],
  "best_time": "10:00 AM",
  "cta": "Call to action text",
  "media_suggestion": "Description of suggested image/video"
}}
"""
    
    messages = [
        {"role": "system", "content": SOCIAL_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    start = time.time()
    response = call_llm(messages, provider="groq", model="llama-3.1-8b-instant")
    elapsed = int((time.time() - start) * 1000)
    
    # Parse response
    result = parse_social_response(response, platform, topic)
    
    # Schedule the post (for tomorrow at best time)
    scheduled_time = (datetime.now() + timedelta(days=1)).replace(
        hour=10, minute=0, second=0, microsecond=0
    )
    
    post_id = schedule_social_post(
        project_id=project_id,
        platform=platform,
        content=result.get("content", response),
        scheduled_for=scheduled_time.isoformat()
    )
    result["id"] = post_id
    result["scheduled_for"] = scheduled_time.isoformat()
    
    log_agent_action("social", f"Created {platform} post for project {project_id}",
                     response_time_ms=elapsed)
    
    return result


def parse_social_response(response: str, platform: str, topic: str) -> dict:
    """Parse LLM response into structured post dict."""
    try:
        json_match = __import__('re').search(r'\{.*\}', response, __import__('re').DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return {
                "content": data.get("content", response),
                "hashtags": data.get("hashtags", []),
                "best_time": data.get("best_time", "10:00 AM"),
                "cta": data.get("cta", "Learn More"),
                "media_suggestion": data.get("media_suggestion", "")
            }
    except:
        pass
    
    return {
        "content": response,
        "hashtags": [],
        "best_time": "10:00 AM",
        "cta": "Learn More",
        "media_suggestion": ""
    }


def generate_content_calendar(project_id: int, days: int = 7) -> list:
    """Generate a multi-day social media content calendar."""
    project = get_project(project_id)
    platforms = ["google_business", "facebook", "instagram", "telegram"]
    
    prompt = f"""
Business: {project['name'] if project else 'Business'}
Location: {project.get('target_location', '') if project else ''}
Days: {days}
Platforms: {', '.join(platforms)}

Create a {days}-day social media content calendar with one post per day.
Mix across platforms.

Return JSON array:
[
  {{
    "day": 1,
    "platform": "instagram",
    "topic": "...",
    "content_type": "educational|promotional|engaging",
    "post_preview": "brief preview..."
  }}
]
"""
    
    messages = [
        {"role": "system", "content": SOCIAL_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    response = call_llm(messages, provider="groq", model="llama-3.1-8b-instant")
    
    try:
        json_match = __import__('re').search(r'\[.*?\]', response, __import__('re').DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    
    return []
