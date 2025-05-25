import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
from datetime import datetime
import numpy as np

import os
data_path = os.path.join("data", "Top Indian Places to Visit.csv")


st.set_page_config(
    page_title="Indian Tourism Explorer",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #FF6B35;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .section-header {
        color: #2E8B57;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .metric-container {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .chatbot-response {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FF6B35;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and process the tourism data"""
    try:
        df = pd.read_csv(data_path)
        
        df.columns = df.columns.str.strip()
        
        df['Google review rating'] = pd.to_numeric(df['Google review rating'], errors='coerce')
        df['Entrance Fee in INR'] = pd.to_numeric(df['Entrance Fee in INR'], errors='coerce').fillna(0)
        df['time needed to visit in hrs'] = pd.to_numeric(df['time needed to visit in hrs'], errors='coerce')
        df['Number of google review in lakhs'] = pd.to_numeric(df['Number of google review in lakhs'], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def create_festival_map():
    """Create month-wise festival mapping"""
    festival_map = {
        "January": ["Punjab", "Rajasthan", "Gujarat"],
        "February": ["Goa", "Rajasthan", "Himachal Pradesh"],
        "March": ["Rajasthan", "Uttar Pradesh", "Bihar"],
        "April": ["Kerala", "Tamil Nadu", "Punjab"],
        "May": ["Kashmir", "Himachal Pradesh", "Uttarakhand"],
        "June": ["Rajasthan", "Gujarat", "Maharashtra"],
        "July": ["Rajasthan", "Himachal Pradesh", "Uttarakhand"],
        "August": ["Kerala", "Karnataka", "Goa"],
        "September": ["West Bengal", "Bihar", "Odisha"],
        "October": ["Gujarat", "West Bengal", "Karnataka"],
        "November": ["Rajasthan", "Punjab", "Delhi"],
        "December": ["Goa", "Kerala", "Tamil Nadu"]
    }
    return festival_map

def generate_travel_plan(user_input, df):
    """Generate AI travel plan based on user input"""
    days = 3 
    month = "October" 
    city = "Delhi"  
    words = user_input.lower().split()

    for i, word in enumerate(words):
        if word.isdigit():
            days = int(word)
            break
        elif word in ['three', 'four', 'five', 'six', 'seven']:
            day_map = {'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7}
            days = day_map[word]
    
    months = ['january', 'february', 'march', 'april', 'may', 'june',
              'july', 'august', 'september', 'october', 'november', 'december']
    for month_name in months:
        if month_name in user_input.lower():
            month = month_name.capitalize()
            break

    cities = df['City'].unique()
    states = df['State'].unique()
    
    for city_name in cities:
        if city_name.lower() in user_input.lower():
            city = city_name
            break
    
    for state_name in states:
        if state_name.lower() in user_input.lower():
            city = state_name
            break

    if city in df['City'].values:
        attractions = df[df['City'] == city].copy()
    elif city in df['State'].values:
        attractions = df[df['State'] == city].copy()
    else:
        attractions = df[df['Google review rating'] >= 4.0].copy()
    
    attractions = attractions.sort_values(['Google review rating', 'Number of google review in lakhs'], 
                                        ascending=[False, False])
    
    plan = f"🎯 **{days}-Day Travel Plan for {city} in {month}**\n\n"
    
    selected_attractions = attractions.head(min(days * 2, len(attractions)))
    
    for day in range(1, days + 1):
        plan += f"**Day {day}:**\n"
        
        day_attractions = selected_attractions.iloc[(day-1)*2:day*2]
        
        for _, attraction in day_attractions.iterrows():
            time_needed = attraction.get('time needed to visit in hrs', 2)
            rating = attraction.get('Google review rating', 4.0)
            fee = attraction.get('Entrance Fee in INR', 0)
            
            plan += f"• **{attraction['Name']}** ({attraction['Type']})\n"
            plan += f"  - Rating: {rating:.1f}⭐ | Time: {time_needed}hrs | Fee: ₹{int(fee)}\n"
            plan += f"  - {attraction.get('Significance', 'Popular tourist destination')}\n"
        
        plan += "\n"
    
    plan += "**💡 Travel Tips:**\n"
    plan += f"• Best time to visit {city}: {month}\n"
    plan += "• Book tickets online for popular attractions\n"
    plan += "• Carry water and comfortable shoes\n"
    plan += "• Check weekly off days before visiting\n"
    
    return plan

def main():
    st.markdown('<h1 class="main-header">🏛️ Indian Tourism Explorer</h1>', unsafe_allow_html=True)

    df = load_data()
    
    if df.empty:
        st.error("Failed to load tourism data. Please check the data file.")
        return

    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a section:", 
                               ["Statewise Explorer", "Month-wise Festival Map", "AI Travel Planner", "Tourism Analytics"])
    
    if page == "Statewise Explorer":
        st.markdown('<h2 class="section-header">🗺️ Statewise Tourism Explorer</h2>', unsafe_allow_html=True)

        states = sorted(df['State'].unique())
        selected_state = st.selectbox("Select a State:", states)
        
        state_data = df[df['State'] == selected_state].copy()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Attractions", len(state_data))
        with col2:
            avg_rating = state_data['Google review rating'].mean()
            st.metric("Average Rating", f"{avg_rating:.1f}⭐")
        with col3:
            free_attractions = len(state_data[state_data['Entrance Fee in INR'] == 0])
            st.metric("Free Attractions", free_attractions)
        
        st.subheader(f"Attractions in {selected_state}")
        
        state_data = state_data.sort_values('Google review rating', ascending=False)
        
        for _, attraction in state_data.iterrows():
            with st.expander(f"**{attraction['Name']}** - {attraction['City']} ({attraction['Type']})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Rating:** {attraction['Google review rating']:.1f}⭐")
                    st.write(f"**Type:** {attraction['Type']}")
                    st.write(f"**Significance:** {attraction.get('Significance', 'N/A')}")
                    st.write(f"**Time needed:** {attraction.get('time needed to visit in hrs', 'N/A')} hours")
                    st.write(f"**Best time to visit:** {attraction.get('Best Time to visit', 'N/A')}")
                
                with col2:
                    st.write(f"**Entrance Fee:** ₹{int(attraction.get('Entrance Fee in INR', 0))}")
                    st.write(f"**DSLR Allowed:** {attraction.get('DSLR Allowed', 'N/A')}")
                    st.write(f"**Weekly Off:** {attraction.get('Weekly Off', 'N/A')}")
                    st.write(f"**Airport nearby:** {attraction.get('Airport with 50km Radius', 'N/A')}")
    
    elif page == "Month-wise Festival Map":
        st.markdown('<h2 class="section-header">🎭 Month-wise Festival Map</h2>', unsafe_allow_html=True)
        
        festival_map = create_festival_map()

        selected_month = st.selectbox("Select Month:", list(festival_map.keys()))
        
        st.subheader(f"Festival States for {selected_month}")
        festival_states = festival_map[selected_month]
        
        for state in festival_states:
            st.markdown(f"### 🎪 {state}")
            
            state_attractions = df[df['State'] == state].sort_values('Google review rating', ascending=False).head(5)
            
            if not state_attractions.empty:
                for _, attraction in state_attractions.iterrows():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"**{attraction['Name']}** ({attraction['City']})")
                        st.write(f"*{attraction['Type']} - {attraction.get('Significance', 'Popular destination')}*")
                    
                    with col2:
                        st.write(f"{attraction['Google review rating']:.1f}⭐")
                    
                    with col3:
                        st.write(f"₹{int(attraction.get('Entrance Fee in INR', 0))}")
                
                st.write("---")
        
        festival_data = []
        for month, states in festival_map.items():
            for state in states:
                state_count = len(df[df['State'] == state])
                festival_data.append({'Month': month, 'State': state, 'Attractions': state_count})
        
        festival_df = pd.DataFrame(festival_data)
        
        fig = px.bar(festival_df, x='Month', y='Attractions', color='State',
                    title="Festival States by Month - Number of Tourist Attractions",
                    height=500)
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    elif page == "AI Travel Planner":
        st.markdown('<h2 class="section-header">🤖 AI Travel Planner</h2>', unsafe_allow_html=True)
        
        st.write("Tell me about your travel plans and I'll create a personalized itinerary!")
        
        user_input = st.text_area("Describe your travel plans:", 
                                 placeholder="I have 5 days in July and want to visit Pune",
                                 height=100)
        
        if st.button("Generate Travel Plan", type="primary"):
            if user_input:
                with st.spinner("Creating your personalized travel plan..."):
                    travel_plan = generate_travel_plan(user_input, df)
                
                st.markdown('<div class="chatbot-response">', unsafe_allow_html=True)
                st.markdown(travel_plan)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("Please describe your travel plans first!")

        st.subheader("Sample Queries:")
        samples = [
            "I have 3 days in December and want to visit Kerala",
            "Plan a 4-day trip to Rajasthan in October",
            "5 days in Mumbai during monsoon season",
            "Weekend trip to Delhi with historical places"
        ]
        
        for sample in samples:
            if st.button(sample, key=sample):
                travel_plan = generate_travel_plan(sample, df)
                st.markdown('<div class="chatbot-response">', unsafe_allow_html=True)
                st.markdown(travel_plan)
                st.markdown('</div>', unsafe_allow_html=True)
    
    elif page == "Tourism Analytics":
        st.markdown('<h2 class="section-header">📊 Tourism Analytics Dashboard</h2>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Attractions", len(df))
        with col2:
            avg_rating = df['Google review rating'].mean()
            st.metric("Average Rating", f"{avg_rating:.1f}⭐")
        with col3:
            free_count = len(df[df['Entrance Fee in INR'] == 0])
            st.metric("Free Attractions", free_count)
        with col4:
            paid_avg = df[df['Entrance Fee in INR'] > 0]['Entrance Fee in INR'].mean()
            st.metric("Avg Entry Fee", f"₹{int(paid_avg)}")

        col1, col2 = st.columns(2)
        
        with col1:
            state_counts = df['State'].value_counts().head(10)
            fig1 = px.bar(x=state_counts.values, y=state_counts.index, 
                         orientation='h',
                         title="Top 10 States by Number of Attractions",
                         labels={'x': 'Number of Attractions', 'y': 'State'})
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            state_ratings = df.groupby('State')['Google review rating'].agg(['mean', 'count']).reset_index()
            state_ratings = state_ratings[state_ratings['count'] >= 5].sort_values('mean', ascending=False).head(10)
            
            fig2 = px.bar(state_ratings, x='State', y='mean',
                         title="Top 10 States by Average Rating (min 5 attractions)",
                         labels={'mean': 'Average Rating', 'State': 'State'})
            fig2.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig2, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            type_counts = df['Type'].value_counts().head(8)
            fig3 = px.pie(values=type_counts.values, names=type_counts.index,
                         title="Distribution of Attraction Types")
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            fee_bins = pd.cut(df['Entrance Fee in INR'], bins=[0, 1, 50, 200, 500, float('inf')], 
                             labels=['Free', '₹1-50', '₹51-200', '₹201-500', '₹500+'])
            fee_counts = fee_bins.value_counts()
            
            fig4 = px.bar(x=fee_counts.index, y=fee_counts.values,
                         title="Distribution of Entrance Fees",
                         labels={'x': 'Fee Range', 'y': 'Number of Attractions'})
            st.plotly_chart(fig4, use_container_width=True)
        
        st.subheader("Rating vs Popularity Analysis")
        
        analysis_df = df.dropna(subset=['Google review rating', 'Number of google review in lakhs'])
        
        if not analysis_df.empty:
            fig5 = px.scatter(analysis_df, x='Number of google review in lakhs', y='Google review rating',
                             color='State', size='Entrance Fee in INR',
                             hover_data=['Name', 'City', 'Type'],
                             title="Rating vs Number of Reviews (bubble size = entrance fee)",
                             labels={'Number of google review in lakhs': 'Reviews (in lakhs)',
                                   'Google review rating': 'Rating'})
            fig5.update_layout(height=500)
            st.plotly_chart(fig5, use_container_width=True)
        
        if 'Best Time to visit' in df.columns:
            best_time_counts = df['Best Time to visit'].value_counts().head(10)
            
            fig6 = px.bar(x=best_time_counts.index, y=best_time_counts.values,
                         title="Most Popular Visiting Times",
                         labels={'x': 'Best Time to Visit', 'y': 'Number of Attractions'})
            fig6.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig6, use_container_width=True)

if __name__ == "__main__":
    main()