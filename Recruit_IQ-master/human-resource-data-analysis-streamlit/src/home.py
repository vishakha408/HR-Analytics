"""Home page with navigation to Interview Session and HR Analytics"""

import streamlit as st


def render_home():
    """Render home page with two large navigation cards"""
    
    # Page title
    st.markdown("""
    <style>
        .home-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 60vh;
            gap: 40px;
            padding: 40px 20px;
        }
        
        .home-title {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .home-title h1 {
            font-size: 48px;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .home-title p {
            font-size: 18px;
            color: #666;
        }
        
        .cards-container {
            display: flex;
            gap: 40px;
            justify-content: center;
            flex-wrap: wrap;
            width: 100%;
            max-width: 1200px;
        }
        
        .nav-card {
            flex: 1;
            min-width: 300px;
            max-width: 450px;
            padding: 40px;
            border-radius: 15px;
            border: 2px solid transparent;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            background: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
        }
        
        .nav-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
            border-color: #667eea;
        }
        
        .nav-card.interview {
            border-left: 5px solid #667eea;
        }
        
        .nav-card.interview:hover {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        }
        
        .nav-card.analytics {
            border-left: 5px solid #4ECDC4;
        }
        
        .nav-card.analytics:hover {
            background: linear-gradient(135deg, rgba(78, 205, 196, 0.05) 0%, rgba(68, 169, 158, 0.05) 100%);
        }
        
        .card-icon {
            font-size: 72px;
            margin-bottom: 20px;
        }
        
        .card-title {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }
        
        .nav-card.interview .card-title {
            color: #667eea;
        }
        
        .nav-card.analytics .card-title {
            color: #4ECDC4;
        }
        
        .card-description {
            font-size: 16px;
            color: #666;
            line-height: 1.6;
            margin-bottom: 20px;
        }
        
        .card-button {
            display: inline-block;
            padding: 12px 30px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 16px;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 10px;
        }
        
        .card-button.interview {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .card-button.interview:hover {
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            transform: scale(1.05);
        }
        
        .card-button.analytics {
            background: linear-gradient(135deg, #4ECDC4 0%, #44A99E 100%);
            color: white;
        }
        
        .card-button.analytics:hover {
            box-shadow: 0 6px 20px rgba(78, 205, 196, 0.4);
            transform: scale(1.05);
        }
        
        .card-features {
            font-size: 13px;
            color: #999;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }
        
        .card-features li {
            margin: 5px 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Title section
    st.markdown("""
    <div class="home-container">
        <div class="home-title">
            <h1>🏢 HR Management System</h1>
            <p>Select a module to get started</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for cards
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <div class="nav-card interview">
            <div class="card-icon">👨‍💼</div>
            <div class="card-title">Interview Session</div>
            <div class="card-description">
                Conduct and manage employee interviews with AI-powered insights and recommendations.
            </div>
            <ul class="card-features">
                <li>✓ Real-time interview guidance</li>
                <li>✓ AI-powered insights</li>
                <li>✓ Performance scoring</li>
                <li>✓ Candidate assessment</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(
            "📋 Go to Interview Session",
            key="btn_interview",
            use_container_width=True,
            help="Navigate to Interview Session module"
        ):
            st.session_state['page'] = 'interview'
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="nav-card analytics">
            <div class="card-icon">📊</div>
            <div class="card-title">HR Analytics</div>
            <div class="card-description">
                Comprehensive HR analytics with detailed insights into employee data, trends, and attrition prediction.
            </div>
            <ul class="card-features">
                <li>✓ Executive summary</li>
                <li>✓ Capacity analysis</li>
                <li>✓ Attrition insights</li>
                <li>✓ ML predictions</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(
            "📈 Go to HR Analytics",
            key="btn_analytics",
            use_container_width=True,
            help="Navigate to HR Analytics module"
        ):
            st.session_state['page'] = 'analytics'
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #999; font-size: 13px; padding: 20px;">
        <p>HR Management System v1.0 | Choose a module to begin</p>
    </div>
    """, unsafe_allow_html=True)
