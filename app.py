import gradio as gr
import google.generativeai as genai
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
import pandas as pd
import os

# Configure Gemini API with the latest Flash model
def setup_gemini():
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in environment variables")
        return None
    
    try:
        genai.configure(api_key=api_key)
        # Use the latest Gemini Flash model - faster and more efficient
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Test the API
        print("Testing Gemini Flash API...")
        response = model.generate_content("Say 'Flash API Connected'")
        print(f"API Response: {response.text}")
        
        print("SUCCESS: Gemini Flash API configured successfully")
        return model
        
    except Exception as e:
        print(f"ERROR: Gemini setup failed: {str(e)}")
        return None

# Initialize model
model = setup_gemini()

# Global state
user_profile = {}
meal_log = []
fitness_plan = {}
chat_history = []

# Professional CSS Styling with Fitness Theme
css = """
:root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    --accent-color: #e74c3c;
    --success-color: #27ae60;
    --warning-color: #f39c12;
    --gradient-primary: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
    --gradient-hero: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --gradient-fitness: linear-gradient(135deg, #ff7e5f 0%, #feb47b 100%);
}
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
/* Navigation Bar */
.navbar {
    background: white;
    padding: 15px 30px;
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.nav-brand {
    font-size: 1.8em;
    font-weight: 700;
    color: var(--primary-color);
    text-decoration: none;
}
.nav-links {
    display: flex;
    gap: 30px;
}
.nav-link {
    color: var(--primary-color);
    text-decoration: none;
    font-weight: 600;
    padding: 8px 16px;
    border-radius: 5px;
    transition: all 0.3s ease;
}
.nav-link:hover {
    background: var(--gradient-primary);
    color: white;
}
.nav-actions {
    display: flex;
    gap: 15px;
}
.btn-primary {
    background: var(--gradient-primary);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 25px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}
.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
}
/* Hero Section */
.hero-section {
    background: var(--gradient-fitness);
    padding: 80px 50px;
    border-radius: 20px;
    color: white;
    text-align: center;
    margin-bottom: 50px;
    position: relative;
    overflow: hidden;
}
.hero-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.1);
    z-index: 1;
}
.hero-content {
    position: relative;
    z-index: 2;
}
.hero-title {
    font-size: 3.5em;
    font-weight: 700;
    margin-bottom: 20px;
    line-height: 1.2;
}
.hero-subtitle {
    font-size: 1.4em;
    margin-bottom: 30px;
    opacity: 0.95;
    font-weight: 300;
}
.hero-cta {
    background: white;
    color: var(--primary-color);
    border: none;
    padding: 15px 40px;
    border-radius: 30px;
    font-size: 1.1em;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s ease;
}
.hero-cta:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}
/* Feature Cards */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
    margin: 50px 0;
}
.feature-card {
    background: white;
    color: black;
    padding: 30px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    border-top: 5px solid var(--secondary-color);
}
.feature-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 15px 40px rgba(0,0,0,0.15);
}
.feature-icon {
    font-size: 3em;
    margin-bottom: 20px;
    color: var(--secondary-color);
}
.feature-title {
    font-size: 1.5em;
    font-weight: 700;
    margin-bottom: 15px;
    color: var(--primary-color);
}
.feature-description {
    color: #666;
    line-height: 1.6;
}
/* Analysis Components */
.analysis-box {
    background: #f8f9fa;
    padding: 25px;
    border-radius: 12px;
    border-left: 5px solid var(--success-color);
    margin: 20px 0;
    border: 1px solid #272a2c;
}
.meal-log {
    background: #fff3cd;
    padding: 20px;
    border-radius: 10px;
    margin: 15px 0;
    border-left: 4px solid var(--warning-color);
    border: 1px solid #ffeaa7;
}
.profile-badge {
    background: #d1ecf1;
    padding: 10px 18px;
    border-radius: 25px;
    margin: 8px;
    display: inline-block;
    font-weight: 600;
    color: #0c5460;
    font-size: 0.9em;
}
/* Chat Interface */
.chat-container {
    background: #f8f9fa;
    border-radius: 15px;
    padding: 25px;
    margin: 20px 0;
    border: 1px solid #272a2c;
}
.chat-message {
    padding: 18px;
    margin: 12px 0;
    border-radius: 15px;
    max-width: 80%;
    line-height: 1.6;
}
.user-message {
    background: var(--gradient-primary);
    color: white;
    margin-left: auto;
    text-align: right;
    box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
}
.bot-message {
    background: white;
    color: var(--primary-color);
    border: 1px solid #272a2c;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
/* Stats Grid */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 20px;
    margin: 25px 0;
}
.stat-item {
    background: white;
    padding: 25px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    border-top: 4px solid var(--secondary-color);
}
.stat-item h3 {
    font-size: 2.2em;
    margin-bottom: 8px;
    color: var(--primary-color);
    font-weight: 700;
}
/* Messages */
.success-message {
    background: #2b9544;
    color: #155724;
    padding: 18px;
    border-radius: 10px;
    border: 1px solid #c3e6cb;
    margin: 12px 0;
}
.error-message {
    background: #fd1a2f;
    color: #721c24;
    padding: 18px;
    border-radius: 10px;
    border: 1px solid #f5c6cb;
    margin: 12px 0;
}
.warning-message {
    background: #484744;
    color: #856404;
    padding: 18px;
    border-radius: 10px;
    border: 1px solid #ffeaa7;
    margin: 12px 0;
}
.flash-badge {
    background: var(--accent-color);
    color: white;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.8em;
    margin-left: 10px;
    font-weight: 600;
}
/* Quick Questions */
.quick-questions {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 15px;
    margin: 25px 0;
}
.quick-question-btn {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 15px 25px;
    border-radius: 10px;
    cursor: pointer;
    font-size: 1em;
    font-weight: 600;
    transition: all 0.3s ease;
    text-align: center;
}
.quick-question-btn:hover {
    background: var(--secondary-color);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}
/* Tab Styling - Permanent Black Text, White Background, No Hover */
.tab-nav {
    background: black !important;
    border-radius: 15px !important;
    padding: 10px !important;
    margin-bottom: 20px !important;
}

/* Force black text for all tab items in ALL states */
button[data-testid="tab"] {
    color: black !important;
    font-weight: 600 !important;
    background: white !important;
}

/* Remove ALL hover effects */
button[data-testid="tab"]:hover {
    color: black !important;
    background: white !important;
    transform: none !important;
    box-shadow: none !important;
}

/* Selected tab - only blue underline, no color change */
button[data-testid="tab"].selected {
    color: black !important;
    background: white !important;
    border-bottom: 3px solid #3498db !important;
}

/* Additional tab styling to ensure black text */
.gr-tabs {
    color: black !important;
}

.gr-tab-item {
    color: black !important;
    background: white !important;
}

.gr-tab-item.selected {
    color: black !important;
    background: white !important;
}

/* Remove any gradient or color transitions */
.gr-tab-item .gr-button {
    color: black !important;
    background: white !important;
}

/* Remove any border or shadow effects on tabs */
.gr-tabs .gr-tab-item {
    border: none !important;
    box-shadow: none !important;
}

/* Responsive Design */
@media (max-width: 768px) {
    .navbar {
        flex-direction: column;
        gap: 15px;
    }
    
    .nav-links {
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .hero-title {
        font-size: 2.5em;
    }
    
    .hero-section {
        padding: 50px 20px;
    }
    
    .feature-grid {
        grid-template-columns: 1fr;
    }
}
"""

# Profile Management
def save_profile(name, age, gender, height, weight, goal, activity_level, dietary_preferences):
    global user_profile
    
    if not name.strip():
        return "Please enter your name", None
    
    bmi = round(weight / ((height/100) ** 2), 1)
    
    user_profile = {
        'name': name,
        'age': age,
        'gender': gender,
        'height': height,
        'weight': weight,
        'goal': goal,
        'activity_level': activity_level,
        'dietary_preferences': dietary_preferences,
        'bmi': bmi
    }
    
    profile_html = f"""
    <div class="success-message">
        <h4>Profile Saved Successfully</h4>
        <div style="display: flex; flex-wrap: wrap; margin: 15px 0;">
            <span class="profile-badge">Name: {user_profile['name']}</span>
            <span class="profile-badge">Goal: {user_profile['goal']}</span>
            <span class="profile-badge">BMI: {user_profile['bmi']}</span>
            <span class="profile-badge">Activity: {user_profile['activity_level']}</span>
        </div>
        <p><strong>Dietary Preferences:</strong> {', '.join(user_profile['dietary_preferences']) if user_profile['dietary_preferences'] else 'No restrictions'}</p>
    </div>
    """
    
    return "Profile saved successfully", profile_html

# Meal Analysis
def analyze_meal(meal_type, meal_description, estimated_calories, satisfaction):
    global meal_log
    
    if not user_profile:
        return "Please create your profile first", None
    
    if not meal_description.strip():
        return "Please describe your meal", None
    
    if not model:
        return "AI service is currently unavailable. Please try again later.", None
    
    prompt = f"""
    Analyze this meal for nutritional content and provide health insights:
    Meal: {meal_description}
    Meal Type: {meal_type}
    Estimated Calories: {estimated_calories}
    
    User Profile: {user_profile}
    
    Please provide:
    1. Nutritional breakdown (proteins, carbs, fats)
    2. Health score (1-10)
    3. 2 positive aspects
    4. 1 suggestion for improvement
    5. Fit it into the user's goal: {user_profile.get('goal', 'General Health')}
    
    Format the response clearly and concisely.
    """
    
    try:
        response = model.generate_content(prompt)
        analysis = response.text
        
        meal_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'meal_type': meal_type,
            'description': meal_description,
            'calories': estimated_calories,
            'satisfaction': satisfaction,
            'analysis': analysis
        }
        
        meal_log.append(meal_entry)
        
        analysis_html = f"""
        <div class="analysis-box">
            <h4>AI Meal Analysis <span class="flash-badge">Flash</span></h4>
            <div class="meal-log">
                <strong>Meal:</strong> {meal_entry['description']}<br>
                <strong>Type:</strong> {meal_entry['meal_type']}<br>
                <strong>Calories:</strong> {meal_entry['calories']}<br>
                <strong>Satisfaction:</strong> {'★' * meal_entry['satisfaction']}
            </div>
            <div style="margin-top: 15px; padding: 20px; background: #489cef; border-radius: 10px; border: 1px solid #246cb5;">
                {analysis.replace(chr(10), '<br>')}
            </div>
        </div>
        """
        
        return "Meal analyzed successfully", analysis_html
        
    except Exception as e:
        return f"Error analyzing meal: {e}", None

# Fitness Plan Generation
def generate_fitness_plan():
    global fitness_plan
    
    if not user_profile:
        return "Please create your profile first", None
    
    if not model:
        return "AI service is currently unavailable. Please try again later.", None
    
    prompt = f"""
    Create a personalized weekly fitness plan based on this user profile:
    {json.dumps(user_profile, indent=2)}
    
    Please provide a comprehensive weekly plan that includes:
    1. Daily workout routines (specify exercises, sets, reps)
    2. Cardio recommendations
    3. Rest days
    4. Progression tips
    5. Equipment needed (bodyweight or basic gym equipment)
    
    Make it appropriate for:
    - Goal: {user_profile.get('goal')}
    - Activity Level: {user_profile.get('activity_level')}
    - Age: {user_profile.get('age')}
    
    Format the response in a clear, structured way.
    Use sections and bullet points for better readability.
    """
    
    try:
        response = model.generate_content(prompt)
        fitness_plan_text = response.text
        
        fitness_plan = {
            'plan': fitness_plan_text,
            'generated_date': datetime.now().strftime("%Y-%m-%d")
        }
        
        plan_html = f"""
        <div class="analysis-box">
            <h4>Your Personalized Fitness Plan <span class="flash-badge">Flash</span></h4>
            <div style="background: #fff3e0; padding: 25px; border-radius: 10px; margin: 20px 0; border: 1px solid #ffeaa7;">
                {fitness_plan_text.replace(chr(10), '<br>')}
            </div>
            <p><strong>Generated on:</strong> {fitness_plan['generated_date']}</p>
        </div>
        """
        
        return "Fitness plan generated successfully", plan_html
        
    except Exception as e:
        return f"Error generating fitness plan: {e}", None

# Insights and Analytics
def show_insights():
    if not meal_log:
        return "No meals logged yet. Start by analyzing some meals", None
    
    # Basic stats
    total_meals = len(meal_log)
    avg_satisfaction = sum(meal['satisfaction'] for meal in meal_log) / total_meals
    total_calories = sum(meal['calories'] for meal in meal_log)
    
    # Create DataFrame for analysis
    df = pd.DataFrame(meal_log)
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    
    stats_html = f"""
    <div class="analysis-box">
        <h4>Your Nutrition Insights</h4>
        <div class="stats-grid">
            <div class="stat-item">
                <h3>{total_meals}</h3>
                <p>Total Meals</p>
            </div>
            <div class="stat-item">
                <h3>{avg_satisfaction:.1f}/5</h3>
                <p>Avg Satisfaction</p>
            </div>
            <div class="stat-item">
                <h3>{total_calories}</h3>
                <p>Total Calories</p>
            </div>
            <div class="stat-item">
                <h3>{len(df['date'].unique())}</h3>
                <p>Days Tracked</p>
            </div>
        </div>
    </div>
    """
    
    # Recent meals
    recent_meals_html = "<div class='feature-card'><h4>Recent Meals</h4>"
    for meal in meal_log[-3:]:
        recent_meals_html += f"""
        <div class="meal-log">
            <strong>{meal['meal_type']}</strong> - {meal['timestamp']}<br>
            <em>{meal['description']}</em><br>
            Calories: {meal['calories']} | Satisfaction: {'★' * meal['satisfaction']}
        </div>
        """
    recent_meals_html += "</div>"
    
    return stats_html + recent_meals_html, None

# Chatbot Functionality
def chat_with_ai(message, chat_history):
    if not model:
        error_msg = "AI service is currently unavailable. Please check if the API key is properly configured in Hugging Face secrets."
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": error_msg})
        
        formatted_history = ""
        for chat in chat_history[-10:]:
            if chat["role"] == "user":
                formatted_history += f'<div class="chat-message user-message"><strong>You:</strong> {chat["content"]}</div>'
            else:
                formatted_history += f'<div class="chat-message bot-message"><strong></strong> {chat["content"].replace(chr(10), "<br>")}</div>'
        
        return chat_history, formatted_history
    
    if not message.strip():
        return chat_history, "Please enter a message."
    
    # Add user message to chat history
    chat_history.append({"role": "user", "content": message})
    
    try:
        # Create context-aware prompt
        context = f"""
        You are Vitalmina, a professional health and fitness assistant using the latest AI technology.
        
        User Profile: {user_profile if user_profile else "No profile created yet"}
        
        User's Question: {message}
        
        Please provide:
        - Accurate, evidence-based information
        - Practical, actionable advice
        - Personalized recommendations when possible
        - Clear explanations
        - Warnings about consulting professionals for medical advice
        
        Focus on these areas:
        Fitness & Exercise
        Nutrition & Diet
        Keto & Special Diets
        Health & Wellness
        Workout Routines
        Meal Planning
        Weight Management
        Supplement Guidance
        
        Keep responses concise but informative and professional.
        """
        
        response = model.generate_content(context)
        ai_response = response.text
        
        # Add AI response to chat history
        chat_history.append({"role": "assistant", "content": ai_response})
        
        # Format chat history for display
        formatted_history = ""
        for chat in chat_history[-10:]:
            if chat["role"] == "user":
                formatted_history += f'<div class="chat-message user-message"><strong>You:</strong> {chat["content"]}</div>'
            else:
                formatted_history += f'<div class="chat-message bot-message"><strong>Vitalmina </strong> {chat["content"].replace(chr(10), "<br>")}</div>'
        
        return chat_history, formatted_history
        
    except Exception as e:
        error_msg = f"Error processing your request: {str(e)}"
        chat_history.append({"role": "assistant", "content": error_msg})
        
        formatted_history = ""
        for chat in chat_history[-10:]:
            if chat["role"] == "user":
                formatted_history += f'<div class="chat-message user-message"><strong>You:</strong> {chat["content"]}</div>'
            else:
                formatted_history += f'<div class="chat-message bot-message"><strong>Vitalmina:</strong> {chat["content"].replace(chr(10), "<br>")}</div>'
        
        return chat_history, formatted_history

def clear_chat():
    global chat_history
    chat_history = []
    return [], ""

# Create Gradio Interface
def create_interface():
    with gr.Blocks(css=css, theme=gr.themes.Soft()) as demo:
        # Navigation Bar
        gr.HTML("""
        <div class="navbar">
            <div class="nav-brand">Vitalmina</div>
            <div class="nav-links">

            </div>
            <div class="nav-actions">
                <button class="nav-link">Login</button>
            </div>
        </div>
        """)
        
        with gr.Tabs(elem_classes="tab-nav"):
            # Home Tab - Redesigned
            with gr.TabItem("Home"):
                # Hero Section
                gr.HTML("""
                <div class="hero-section">
                    <div class="hero-content">
                        <h1 class="hero-title">FITNESS JOURNEY,<br>AI-OPTIMIZED</h1>
                        <p class="hero-subtitle">Achieve Weight Loss, Muscle Gain, Or A Healthier Lifestyle<br>Effortlessly With AI-Driven Personalized Training</p>
                    </div>
                </div>
                """)
                
                # Features Grid
                gr.HTML("""
                <div class="feature-grid">
                    <div class="feature-card">
                        <div class="feature-icon">💪</div>
                        <h3 class="feature-title">Personalized Workouts</h3>
                        <p class="feature-description">AI-generated fitness plans tailored to your goals, fitness level, and available equipment</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🍎</div>
                        <h3 class="feature-title">Smart Nutrition</h3>
                        <p class="feature-description">Get instant nutritional insights and meal recommendations powered by advanced AI analysis</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">📊</div>
                        <h3 class="feature-title">Progress Tracking</h3>
                        <p class="feature-description">Monitor your fitness journey with detailed analytics and personalized insights</p>
                    </div>
                </div>
                """)
                
                # Stats Section
                gr.HTML("""
                <div class="stats-grid">
                    <div class="stat-item">
                        <h3>Keto Diet</h3>
                    </div>
                    <div class="stat-item">
                        <h3>Workout Routine</h3>
                    </div>
                    <div class="stat-item">
                        <h3>Meals Analyzed</h3>
                    </div>
                    <div class="stat-item">
                        <h3>Best Exercises</h3>
                    </div>
                </div>
                """)
            
            # Profile Tab
            with gr.TabItem("Profile"):
                with gr.Row():
                    with gr.Column():
                        name = gr.Textbox(label="Full Name", placeholder="Enter your name")
                        age = gr.Slider(label="Age", minimum=10, maximum=100, value=25)
                        gender = gr.Dropdown(label="Gender", choices=["Male", "Female", "Other"])
                        height = gr.Slider(label="Height (cm)", minimum=100, maximum=250, value=170)
                    
                    with gr.Column():
                        weight = gr.Slider(label="Weight (kg)", minimum=30, maximum=200, value=70)
                        goal = gr.Dropdown(
                            label="Fitness Goal", 
                            choices=["Weight Loss", "Muscle Gain", "Maintenance", "Improve Fitness", "General Health"]
                        )
                        activity_level = gr.Dropdown(
                            label="Activity Level", 
                            choices=["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"]
                        )
                        dietary_preferences = gr.CheckboxGroup(
                            label="Dietary Preferences",
                            choices=["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Low-Carb", "Keto", "No Restrictions"]
                        )
                
                save_btn = gr.Button("Save Profile", variant="primary")
                profile_output = gr.HTML()
                save_btn.click(
                    save_profile,
                    inputs=[name, age, gender, height, weight, goal, activity_level, dietary_preferences],
                    outputs=[gr.Textbox(label="Status"), profile_output]
                )
            
            # Meal Analysis Tab
            with gr.TabItem("Meal Analysis"):
                with gr.Row():
                    with gr.Column():
                        meal_type = gr.Dropdown(label="Meal Type", choices=["Breakfast", "Lunch", "Dinner", "Snack"])
                        meal_description = gr.Textbox(
                            label="Meal Description",
                            placeholder="e.g., Grilled chicken breast with quinoa and steamed vegetables, 1 apple",
                            lines=3
                        )
                    
                    with gr.Column():
                        estimated_calories = gr.Number(label="Estimated Calories", value=0)
                        satisfaction = gr.Slider(label="Satisfaction", minimum=1, maximum=5, value=3, step=1)
                
                analyze_btn = gr.Button("Analyze Meal", variant="primary")
                meal_output = gr.HTML()
                analyze_btn.click(
                    analyze_meal,
                    inputs=[meal_type, meal_description, estimated_calories, satisfaction],
                    outputs=[gr.Textbox(label="Status"), meal_output]
                )
            
            # Fitness Plan Tab
            with gr.TabItem("Fitness Plan"):
                fitness_btn = gr.Button("Generate Fitness Plan", variant="primary")
                fitness_output = gr.HTML()
                fitness_btn.click(
                    generate_fitness_plan,
                    outputs=[gr.Textbox(label="Status"), fitness_output]
                )
            
            # Insights Tab
            with gr.TabItem("Insights"):
                insights_btn = gr.Button("Refresh Insights", variant="primary")
                insights_output = gr.HTML()
                insights_btn.click(
                    show_insights,
                    outputs=[gr.Textbox(label="Status"), insights_output]
                )
            
            # AI Chatbot Tab
            with gr.TabItem("AI Assistant"):
                # Quick questions buttons
                gr.Markdown("### Quick Questions")
                with gr.Row():
                    q1_btn = gr.Button("Best exercises for weight loss", size="sm")
                    q2_btn = gr.Button("Keto diet basics", size="sm")
                    q3_btn = gr.Button("Healthy breakfast ideas", size="sm")
                
                with gr.Row():
                    q4_btn = gr.Button("Home workout routine", size="sm")
                    q5_btn = gr.Button("Meal prep tips", size="sm")
                    q6_btn = gr.Button("Calculate my calories", size="sm")
                
                with gr.Row():
                    q7_btn = gr.Button("Importance of hydration", size="sm")
                    q8_btn = gr.Button("How to break plateau", size="sm")
                    q9_btn = gr.Button("Keto meal ideas", size="sm")
                
                # Chat interface
                chat_state = gr.State([])
                chat_display = gr.HTML(label="Chat History")
                
                with gr.Row():
                    chat_input = gr.Textbox(
                        placeholder="Ask about fitness, nutrition, workouts, meal plans...",
                        label="Your Question",
                        lines=2
                    )
                    send_btn = gr.Button("Send", variant="primary")
                
                with gr.Row():
                    clear_btn = gr.Button("Clear Chat", variant="secondary")
                
                # Chat functionality
                send_btn.click(
                    chat_with_ai,
                    inputs=[chat_input, chat_state],
                    outputs=[chat_state, chat_display]
                ).then(lambda: "", outputs=[chat_input])
                
                chat_input.submit(
                    chat_with_ai,
                    inputs=[chat_input, chat_state],
                    outputs=[chat_state, chat_display]
                ).then(lambda: "", outputs=[chat_input])
                
                clear_btn.click(
                    clear_chat,
                    outputs=[chat_state, chat_display]
                )
                
                # Quick question handlers
                quick_questions = [
                    "What are the best exercises for weight loss?",
                    "Explain keto diet basics for beginners",
                    "Give me some healthy breakfast ideas",
                    "Suggest a home workout routine without equipment",
                    "What are good meal prep tips for the week?",
                    "How do I calculate my daily calorie needs?",
                    "Why is hydration important for fitness?",
                    "How can I break through a fitness plateau?",
                    "What are some good keto meal ideas?"
                ]
                
                question_buttons = [q1_btn, q2_btn, q3_btn, q4_btn, q5_btn, q6_btn, q7_btn, q8_btn, q9_btn]
                
                for i, (btn, question) in enumerate(zip(question_buttons, quick_questions)):
                    btn.click(
                        lambda q=question: q,
                        outputs=[chat_input]
                    ).then(
                        chat_with_ai,
                        inputs=[chat_input, chat_state],
                        outputs=[chat_state, chat_display]
                    ).then(lambda: "", outputs=[chat_input])
        
        # Footer
        gr.Markdown("---")
        gr.Markdown("### Vitalmina AI - Powered by Google Gemini 2.5 Flash")
        
    return demo

# Launch the app
if __name__ == "__main__":
    demo = create_interface()
    demo.launch(share=True)
