"""
BHARATSOLVE SEO AGENCY — Social Media UI
Create, schedule, and manage social media posts.
"""
import streamlit as st
from datetime import datetime, timedelta
from db.operations import get_clients, get_projects, get_scheduled_posts
from agents.social_agent import create_social_post, generate_content_calendar


def show_social_page():
    """Render social media management page."""
    user_id = st.session_state["user_id"]
    
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0;">
        <h1 style="background: linear-gradient(90deg, #00d2ff, #3a7bd5); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   font-size: 2rem; margin: 0;">📱 Social Media Manager</h1>
        <p style="color: #888;">AI-Powered Content for All Platforms</p>
    </div>
    """, unsafe_allow_html=True)
    
    clients = get_clients(user_id)
    if not clients:
        st.warning("⚠️ Please add a client first!")
        return
    
    # Select client and project
    col1, col2 = st.columns(2)
    with col1:
        client_names = [c['name'] for c in clients]
        selected_client = st.selectbox("Select Client", client_names, key="social_client")
        client = next(c for c in clients if c['name'] == selected_client)
    
    projects = get_projects(client['id'])
    if not projects:
        st.info("💡 Create a project first!")
        return
    
    with col2:
        proj_names = [p['name'] for p in projects]
        selected_project = st.selectbox("Select Project", proj_names, key="social_proj")
        project = next(p for p in projects if p['name'] == selected_project)
        project_id = project['id']
    
    st.markdown("---")
    
    # ── Create Post ──
    with st.expander("✍️ Create New Post", expanded=False):
        st.markdown("**AI will generate platform-optimized content**")
        
        col1, col2 = st.columns(2)
        with col1:
            platform = st.selectbox(
                "Platform",
                ["google_business", "facebook", "instagram", "telegram", "email"],
                format_func=lambda x: {
                    "google_business": "Google Business Profile",
                    "facebook": "Facebook",
                    "instagram": "Instagram",
                    "telegram": "Telegram",
                    "email": "Email Newsletter"
                }[x]
            )
            content_type = st.selectbox(
                "Content Type",
                ["promotional", "educational", "engaging", "offer", "update", "testimonial"]
            )
        
        with col2:
            topic = st.text_input("Topic (optional)", placeholder="e.g., New dental services launch")
        
        if st.button("🤖 Generate & Schedule Post", use_container_width=True, type="primary"):
            with st.spinner("🤖 Creating post..."):
                result = create_social_post(project_id, platform, topic, content_type)
            
            if result:
                st.success(f"✅ Post created and scheduled!")
                
                st.markdown("### 📱 Generated Post")
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.85); border-radius: 10px; padding: 1.5rem; margin: 1rem 0;
                            border: 1px solid #90e0ef; box-shadow: 0 2px 8px rgba(0,119,182,0.06);">
                    <p style="color: #333; font-size: 1.1rem;">{result.get('content', '')}</p>
                    <hr style="opacity: 0.2; border-color: #90e0ef;">
                    <p style="color: #0077b6;">{', '.join(result.get('hashtags', []))}</p>
                    <p style="color: #e07c1f;"><strong>CTA:</strong> {result.get('cta', '')}</p>
                    <p style="color: #666;"><strong>Best Time:</strong> {result.get('best_time', '')}</p>
                    <p style="color: #666;"><strong>Scheduled:</strong> {result.get('scheduled_for', '')}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("❌ Post creation failed!")
    
    # ── Content Calendar ──
    with st.expander("📅 Generate Content Calendar", expanded=False):
        st.markdown("**AI plans a week of social media content**")
        
        days = st.slider("Days", min_value=3, max_value=14, value=7)
        
        if st.button("🗓️ Generate Calendar", use_container_width=True):
            with st.spinner("🤖 Planning content calendar..."):
                calendar = generate_content_calendar(project_id, days)
            
            if calendar:
                st.success(f"✅ Generated {len(calendar)} days of content!")
                for day in calendar:
                    platform_icon = {
                        "google_business": "📍", "facebook": "📘", 
                        "instagram": "📸", "telegram": "✈️"
                    }.get(day.get('platform', ''), "📱")
                    
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.7); border-radius: 8px; padding: 0.8rem; margin: 0.3rem 0; border: 1px solid #e0f0ff;">
                        <strong style="color: #0077b6;">Day {day.get('day', '?')}</strong>
                        {platform_icon} <strong style="color: #0077b6;">{day.get('platform', 'N/A').title()}</strong>
                        <span style="color: #666;"> | {day.get('content_type', '').title()}</span>
                        <p style="color: #555; margin: 0.3rem 0 0 0; font-size: 0.9rem;">
                            📌 {day.get('post_preview', '')[:100]}...
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("❌ Calendar generation failed!")
    
    st.markdown("---")
    
    # ── Scheduled Posts ──
    st.markdown("### 📅 Scheduled Posts")
    scheduled = get_scheduled_posts(project_id)
    
    if scheduled:
        for post in scheduled:
            platform_icons = {
                "google_business": "📍", "facebook": "📘", 
                "instagram": "📸", "telegram": "✈️", "email": "📧"
            }
            icon = platform_icons.get(post['platform'], "📱")
            
            status_color = {
                "scheduled": "#ffa502",
                "posted": "#43e97b",
                "failed": "#ff6b6b"
            }.get(post['status'], "#888")
            
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.7); border-radius: 8px; padding: 0.8rem 1rem; margin: 0.4rem 0;
                        border-left: 3px solid {status_color}; box-shadow: 0 2px 6px rgba(0,119,182,0.06);">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <strong style="color: #333;">{icon} {post['platform'].replace('_', ' ').title()}</strong>
                        <p style="color: #555; margin: 0.3rem 0 0 0;">{post['content'][:100]}...</p>
                    </div>
                    <div style="text-align: right;">
                        <span style="color: {status_color}; font-size: 0.9rem;">{post['status'].upper()}</span>
                        <br>
                        <span style="color: #666; font-size: 0.8rem;">
                            {post.get('scheduled_for', 'N/A')[:10]}
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("💡 No scheduled posts yet. Create your first post above!")
