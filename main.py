import streamlit as st
import pandas as pd
from datetime import datetime

# Initialize session state
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# Custom CSS for styling
st.markdown("""
<style>
    .task-card {
        border-left: 4px solid #4CAF50;
        background-color: #f9f9f9;
        padding: 12px;
        margin-bottom: 8px;
        border-radius: 4px;
    }
    .high-priority { border-left-color: #FF5722; }
    .medium-priority { border-left-color: #FFC107; }
    .low-priority { border-left-color: #4CAF50; }
    .completed { text-decoration: line-through; opacity: 0.7; }
    .header { color: #2E86C1; }
    .stButton>button {
        min-width: 80px;
    }
</style>
""", unsafe_allow_html=True)

# Task functions
def add_task(description, priority, due_date):
    task = {
        'id': str(len(st.session_state.tasks) + 1),
        'description': description,
        'priority': priority,
        'due_date': due_date.strftime('%Y-%m-%d') if due_date else None,
        'completed': False,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    st.session_state.tasks.append(task)

def toggle_complete(task_id):
    for task in st.session_state.tasks:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            break

def delete_task(task_id):
    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task_id]

# App UI
st.title("🚀 Streamlined To-Do App")
st.markdown('<div class="header">Manage your tasks efficiently</div>', unsafe_allow_html=True)

# Input form
with st.form("task_form"):
    col1, col2 = st.columns(2)
    with col1:
        task_input = st.text_input("Task description")
    with col2:
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    
    due_date = st.date_input("Due date", min_value=datetime.now().date())
    
    submitted = st.form_submit_button("Add Task")
    if submitted:
        if task_input:
            add_task(task_input, priority, due_date)
            st.success("Task added!")
        else:
            st.warning("Please enter a task description")

# Task list
if not st.session_state.tasks:
    st.info("No tasks yet. Add your first task above!")
else:
    st.subheader("Your Tasks")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        show_completed = st.checkbox("Show completed tasks", True)
    with col2:
        filter_priority = st.selectbox("Filter by priority", ["All", "High", "Medium", "Low"])

    # Filter and sort tasks
    filtered_tasks = [
        t for t in st.session_state.tasks 
        if (show_completed or not t['completed']) and 
        (filter_priority == "All" or t['priority'] == filter_priority)
    ]

    for task in filtered_tasks:
        card_class = f"task-card {task['priority'].lower()}-priority"
        if task['completed']:
            card_class += " completed"
            
        with st.container():
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
            
            cols = st.columns([5,1,1])
            with cols[0]:
                st.write(f"**{task['description']}**")
                st.caption(f"Priority: {task['priority']} • Due: {task['due_date'] or 'No deadline'}")
            with cols[1]:
                if st.button("✓", key=f"complete_{task['id']}"):
                    toggle_complete(task['id'])
                    st.experimental_rerun()
            with cols[2]:
                if st.button("🗑️", key=f"delete_{task['id']}"):
                    delete_task(task['id'])
                    st.experimental_rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

# Simple statistics
if st.session_state.tasks:
    st.subheader("📊 Task Overview")
    completed = sum(1 for t in st.session_state.tasks if t['completed'])
    total = len(st.session_state.tasks)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tasks", total)
    col2.metric("Completed", completed)
    col3.metric("Completion", f"{round((completed/total)*100 if total > 0 else 0)}%")
    
    # Simple priority distribution
    st.write("Priority Distribution:")
    priority_counts = pd.DataFrame([
        {"Priority": "High", "Count": sum(1 for t in st.session_state.tasks if t['priority'] == "High")},
        {"Priority": "Medium", "Count": sum(1 for t in st.session_state.tasks if t['priority'] == "Medium")},
        {"Priority": "Low", "Count": sum(1 for t in st.session_state.tasks if t['priority'] == "Low")},
    ])
    st.bar_chart(priority_counts.set_index('Priority'))
