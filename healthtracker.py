import gradio as gr
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

calorie_data = []

def calculate_bmi(weight, height):
    """Calculate BMI and return category"""
    if weight <= 0 or height <= 0:
        return "Please enter valid positive numbers", ""
    
    height_m = height / 100  
    bmi = weight / (height_m ** 2)
    
    if bmi < 18.5:
        category = "Underweight"
        color = "#4162CF"
    elif 18.5 <= bmi < 25:
        category = "Normal weight"
        color = "#14B8A6"
    elif 25 <= bmi < 30:
        category = "Overweight"
        color = "#D1D42D"
    else:
        category = "Obese"
        color = "#94160D"
    
    result = f"<div style='text-align: center; padding: 20px;'>"
    result += f"<h2 style='color: {color}; font-size: 48px; margin: 10px 0;'>{bmi:.1f}</h2>"
    result += f"<h3 style='color: {color}; margin: 5px 0;'>{category}</h3>"
    result += f"</div>"
    
    return result

def calculate_bmr_tdee(weight, height, age, gender, activity):
    """Calculate BMR and TDEE"""
    if weight <= 0 or height <= 0 or age <= 0:
        return "Please enter valid positive numbers"
    
    if gender == "Male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    activity_multipliers = {
        "Sedentary (little or no exercise)": 1.2,
        "Lightly active (exercise 1-3 days/week)": 1.375,
        "Moderately active (exercise 3-5 days/week)": 1.55,
        "Very active (exercise 6-7 days/week)": 1.725,
        "Super active (physical job or training twice/day)": 1.9
    }
    
    tdee = bmr * activity_multipliers[activity]
    
    result = f"<div style='text-align: center; padding: 20px;'>"
    result += f"<div style='margin: 20px 0;'>"
    result += f"<h3 style='color: #14B8A6; margin: 5px 0;'>Basal Metabolic Rate (BMR)</h3>"
    result += f"<h2 style='color: #14B8A6; font-size: 42px; margin: 10px 0;'>{bmr:.0f} cal/day</h2>"
    result += f"</div>"
    result += f"<div style='margin: 20px 0;'>"
    result += f"<h3 style='color: #2DD4BF; margin: 5px 0;'>Total Daily Energy Expenditure (TDEE)</h3>"
    result += f"<h2 style='color: #2DD4BF; font-size: 42px; margin: 10px 0;'>{tdee:.0f} cal/day</h2>"
    result += f"</div>"
    result += f"<div style='margin-top: 30px; padding: 15px; background: rgba(94, 234, 212, 0.1); border-radius: 10px; border: 1px solid #5EEAD4;'>"
    result += f"<p style='color: #0F766E; margin: 5px 0;'><strong>Weight Loss:</strong> {tdee - 500:.0f} cal/day (-0.5 kg/week)</p>"
    result += f"<p style='color: #0F766E; margin: 5px 0;'><strong>Maintain Weight:</strong> {tdee:.0f} cal/day</p>"
    result += f"<p style='color: #0F766E; margin: 5px 0;'><strong>Weight Gain:</strong> {tdee + 500:.0f} cal/day (+0.5 kg/week)</p>"
    result += f"</div>"
    result += f"</div>"
    
    return result

def add_calorie_entry(food_name, calories):
    """Add a calorie entry and return updated graph and history"""
    global calorie_data
    
    try:
        if not food_name or not food_name.strip():
            return create_calorie_graph(), "<p style='color: red;'>Please enter a food name</p>"
        
        if calories <= 0:
            return create_calorie_graph(), "<p style='color: red;'>Please enter calories greater than 0</p>"
        
        entry = {
            'date': datetime.now().date(),
            'food': food_name.strip(),
            'calories': float(calories),
            'timestamp': datetime.now()
        }
        calorie_data.append(entry)
        
        print(f"Added entry: {entry}")  
        print(f"Total entries: {len(calorie_data)}")  
        
        fig = create_calorie_graph()
        
        history = create_history_table()
        
        return fig, history
    except Exception as e:
        print(f"Error in add_calorie_entry: {e}")
        return create_calorie_graph(), f"<p style='color: red;'>Error: {str(e)}</p>"

def create_calorie_graph():
    """Create a 7-day calorie graph"""
    try:
        if not calorie_data:
            fig = go.Figure()
            fig.add_annotation(
                text="No data yet. Start tracking your calories!",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="#666666")
            )
            fig.update_layout(
                height=400,
                margin=dict(t=40, b=40, l=40, r=40)
            )
            return fig
        
        today = datetime.now().date()
        last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
        
        daily_calories = {}
        for date in last_7_days:
            daily_calories[date] = 0
        
        for entry in calorie_data:
            if entry['date'] in daily_calories:
                daily_calories[entry['date']] += entry['calories']
        
        dates = list(daily_calories.keys())
        calories = list(daily_calories.values())
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=[d.strftime('%m/%d') for d in dates],
            y=calories,
            marker=dict(
                color='#5EEAD4',
                line=dict(color='#14B8A6', width=2)
            ),
            text=[f'{c:.0f}' for c in calories],
            textposition='outside'
        ))
        
        fig.update_layout(
            title='7-Day Calorie Tracker',
            xaxis_title='Date',
            yaxis_title='Calories',
            height=400,
            showlegend=False,
            margin=dict(t=60, b=60, l=60, r=30),
            paper_bgcolor='white',
            plot_bgcolor='#F0FDFA',
            font=dict(color='#0F766E')
        )
        
        return fig
    except Exception as e:
        print(f"Error in create_calorie_graph: {e}")
        import traceback
        traceback.print_exc()
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating graph: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

def create_history_table():
    """Create HTML table of today's entries"""
    try:
        if not calorie_data:
            return "<p style='text-align: center; color: #666; padding: 20px;'>No entries yet</p>"
        
        today = datetime.now().date()
        today_entries = [e for e in calorie_data if e['date'] == today]
        
        if not today_entries:
            return "<p style='text-align: center; color: #666; padding: 20px;'>No entries for today</p>"
        
        total_calories = sum(e['calories'] for e in today_entries)
        
        html = "<div style='padding: 10px;'>"
        html += f"<h3 style='text-align: center; margin-bottom: 20px; color: #0F766E;'>Today's Total: <span style='color: #14B8A6;'>{total_calories:.0f} cal</span></h3>"
        html += "<table style='width: 100%; border-collapse: collapse;'>"
        html += "<tr style='background: #CCFBF1;'>"
        html += "<th style='padding: 12px; text-align: left; border-bottom: 2px solid #5EEAD4; color: #0F766E;'>Time</th>"
        html += "<th style='padding: 12px; text-align: left; border-bottom: 2px solid #5EEAD4; color: #0F766E;'>Food</th>"
        html += "<th style='padding: 12px; text-align: right; border-bottom: 2px solid #5EEAD4; color: #0F766E;'>Calories</th>"
        html += "</tr>"
        
        for entry in reversed(today_entries[-10:]):  # Show last 10 entries
            html += "<tr style='border-bottom: 1px solid #CCFBF1;'>"
            html += f"<td style='padding: 10px; color: #0F766E;'>{entry['timestamp'].strftime('%H:%M')}</td>"
            html += f"<td style='padding: 10px; color: #0F766E;'>{entry['food']}</td>"
            html += f"<td style='padding: 10px; text-align: right; font-weight: bold; color: #14B8A6;'>{entry['calories']:.0f}</td>"
            html += "</tr>"
        
        html += "</table></div>"
        return html
    except Exception as e:
        print(f"Error in create_history_table: {e}")
        import traceback
        traceback.print_exc()
        return f"<p style='color: red;'>Error creating table: {str(e)}</p>"



custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Montserrat', sans-serif !important;
}

.gradio-container {
    font-family: 'Montserrat', sans-serif !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Montserrat', sans-serif !important;
}

label {
    font-weight: 500 !important;
}
"""



with gr.Blocks(theme=gr.themes.Soft(primary_hue="teal", secondary_hue="emerald"), css=custom_css) as app:
    gr.Markdown(
        """
        #  Health & Fitness Tracker
        ### Your complete wellness companion
        """,
        elem_id="header"
    )
    
    with gr.Tabs():
        with gr.Tab("BMI Calculator"):
            gr.Markdown("## Body Mass Index Calculator", elem_id="tab-title")
            gr.Markdown("Calculate your BMI and understand your weight category", elem_id="tab-subtitle")
            
            with gr.Row():
                with gr.Column():
                    bmi_weight = gr.Number(label="Weight (kg)", value=70, minimum=0)
                    bmi_height = gr.Number(label="Height (cm)", value=170, minimum=0)
                    bmi_calculate = gr.Button("Calculate BMI", variant="primary", size="lg")
                
                with gr.Column():
                    bmi_output = gr.HTML(label="Results")
            
            bmi_calculate.click(
                fn=calculate_bmi,
                inputs=[bmi_weight, bmi_height],
                outputs=bmi_output
            )
        
        with gr.Tab("BMR & TDEE Calculator"):
            gr.Markdown("## Metabolic Rate Calculator", elem_id="tab-title")
            gr.Markdown("Calculate your daily calorie needs based on your lifestyle", elem_id="tab-subtitle")
            
            with gr.Row():
                with gr.Column():
                    bmr_weight = gr.Number(label="Weight (kg)", value=70, minimum=0)
                    bmr_height = gr.Number(label="Height (cm)", value=170, minimum=0)
                    bmr_age = gr.Number(label="Age (years)", value=30, minimum=0)
                    bmr_gender = gr.Radio(["Male", "Female"], label="Gender", value="Male")
                    bmr_activity = gr.Dropdown(
                        [
                            "Sedentary (little or no exercise)",
                            "Lightly active (exercise 1-3 days/week)",
                            "Moderately active (exercise 3-5 days/week)",
                            "Very active (exercise 6-7 days/week)",
                            "Super active (physical job or training twice/day)"
                        ],
                        label="Activity Level",
                        value="Moderately active (exercise 3-5 days/week)"
                    )
                    bmr_calculate = gr.Button("Calculate BMR & TDEE", variant="primary", size="lg")
                
                with gr.Column():
                    bmr_output = gr.HTML(label="Results")
            
            bmr_calculate.click(
                fn=calculate_bmr_tdee,
                inputs=[bmr_weight, bmr_height, bmr_age, bmr_gender, bmr_activity],
                outputs=bmr_output
            )
        
        with gr.Tab("Calories Tracker"):
            gr.Markdown("## Daily Calorie Tracker", elem_id="tab-title")
            gr.Markdown("Track your daily food intake and monitor your 7-day calorie history", elem_id="tab-subtitle")
            
            with gr.Row():
                with gr.Column(scale=1):
                    food_name = gr.Textbox(label="Food Name", placeholder="e.g. Boiled egg")
                    food_calories = gr.Number(label="Calories", value=0, minimum=0)
                    add_button = gr.Button("Add Entry", variant="primary", size="lg")
                    
                    with gr.Accordion("Today's Entries", open=True):
                        history_output = gr.HTML()
                
                with gr.Column(scale=2):
                    calorie_graph = gr.Plot(label="Last 7-Days Calorie Chart")
            
            def init_tracker():
                return create_calorie_graph(), create_history_table()
            
            calorie_graph.value = create_calorie_graph()
            history_output.value = create_history_table()
            
            add_button.click(
                fn=add_calorie_entry,
                inputs=[food_name, food_calories],
                outputs=[calorie_graph, history_output]
            )

if __name__ == "__main__":
    app.launch(share=True)