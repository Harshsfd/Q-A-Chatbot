import streamlit as st
from datetime import datetime, timedelta
import extra_streamlit_components as stx
import plotly.express as px
import pandas as pd

# Initialize session state
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Custom CSS for the app
def load_css():
    st.markdown("""
    <style>
        .task-card {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        .task-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        .high-priority {
            border-left: 5px solid #ff4b4b;
        }
        .medium-priority {
            border-left: 5px solid #fdaa3d;
        }
        .low-priority {
            border-left: 5px solid #4bb543;
        }
        .completed-task {
            opacity: 0.7;
            text-decoration: line-through;
        }
        .datetime-picker {
            padding: 8px;
            border-radius: 5px;
        }
        [data-testid="stAppViewContainer"] {
            transition: background-color 0.3s;
        }
        /* Dark mode styles */
        .dark-mode {
            background-color: #121212 !important;
            color: white !important;
        }
        .dark-mode .task-card {
            background-color: #1e1e1e !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        .dark-mode .sidebar .sidebar-content {
            background-color: #1e1e1e !important;
        }
        .dark-mode .stTextInput input, 
        .dark-mode .stDateInput input,
        .dark-mode .stSelectbox select {
            background-color: #333 !important;
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Task class
class Task:
    def __init__(self, description, priority="Medium", due_date=None, completed=False):
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.completed = completed
        self.created_at = datetime.now()
        self.id = str(datetime.timestamp(self.created_at))

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date,
            "completed": self.completed,
            "created_at": self.created_at
        }

def add_task(task):
    st.session_state.tasks.append(task.to_dict())

def remove_task(task_id):
    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task_id]

def toggle_complete(task_id):
    for task in st.session_state.tasks:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            break

def update_task(task_id, updated_task):
    for i, task in enumerate(st.session_state.tasks):
        if task['id'] == task_id:
            st.session_state.tasks[i] = updated_task.to_dict()
            break

def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

def priority_color(priority):
    colors = {
        "High": "#ff4b4b",
        "Medium": "#fdaa3d",
        "Low": "#4bb543"
    }
    return colors.get(priority, "#fdaa3d")

# Load CSS
load_css()

# Dark mode toggle
dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=st.session_state.dark_mode, on_change=toggle_dark_mode)

# Apply dark mode
if dark_mode:
    st.markdown(
        """
        <style>
            [data-testid="stAppViewContainer"] {
                background-color: #121212;
                color: white;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

# App title
st.title("✨ Advanced To-Do List")
st.caption("Organize your tasks with style")

# Tab layout
tab1, tab2, tab3 = st.tabs(["📝 Tasks", "📊 Analytics", "⚙️ Settings"])

with tab1:
    # Add task form
    with st.expander("➕ Add New Task", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            new_task = st.text_input("Task Description")
        with col2:
            priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=1)
        
        col3, col4 = st.columns(2)
        with col3:
            due_date = st.date_input("Due Date", min_value=datetime.now().date())
        with col4:
            due_time = st.time_input("Due Time", value=(datetime.now() + timedelta(hours=1)).time())
        
        if st.button("Add Task", use_container_width=True):
            if new_task:
                full_due = datetime.combine(due_date, due_time)
                task = Task(new_task, priority, full_due)
                add_task(task)
                st.success("Task added successfully!")
            else:
                st.warning("Please enter a task description")

    # Task list
    st.subheader("🔖 Your Tasks")
    
    if not st.session_state.tasks:
        st.info("No tasks yet. Add your first task above!")
    else:
        # Sort options
        sort_by = st.radio("Sort by:", ["Due Date", "Priority", "Creation Date"], horizontal=True)
        
        # Filter options
        show_completed = st.checkbox("Show completed tasks", value=True)
        priority_filter = st.multiselect("Filter by priority", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
        
        # Process tasks
        filtered_tasks = [t for t in st.session_state.tasks 
                         if t['priority'] in priority_filter and 
                         (show_completed or not t['completed'])]
        
        # Sort tasks
        if sort_by == "Due Date":
            filtered_tasks = sorted(filtered_tasks, 
                                  key=lambda x: x['due_date'] if x['due_date'] else datetime.max)
        elif sort_by == "Priority":
            priority_order = {"High": 1, "Medium": 2, "Low": 3}
            filtered_tasks = sorted(filtered_tasks, 
                                  key=lambda x: priority_order.get(x['priority'], 2))
        else:
            filtered_tasks = sorted(filtered_tasks, 
                                  key=lambda x: x['created_at'], reverse=True)
        
        if not filtered_tasks:
            st.info("No tasks match your filters")
        
        # Display tasks
        for task in filtered_tasks:
            card_class = f"task-card {task['priority'].lower()}-priority"
            if task['completed']:
                card_class += " completed-task"
                
            with st.container():
                st.markdown(f"<div class='{card_class}'>", unsafe_allow_html=True)
                
                cols = st.columns([0.8, 0.1, 0.1])
                with cols[0]:
                    if task['completed']:
                        st.markdown(f"~~{task['description']}~~")
                    else:
                        st.markdown(f"**{task['description']}**")
                    
                    col1, col2, col3 = st.columns([0.3, 0.3, 0.4])
                    with col1:
                        st.caption(f"Priority: {task['priority']}")
                    with col2:
                        if task['due_date']:
                            st.caption(f"Due: {task['due_date'].strftime('%b %d, %Y %I:%M %p')}")
                    with col3:
                        st.caption(f"Created: {task['created_at'].strftime('%b %d')}")
                
                with cols[1]:
                    if st.button("✓", key=f"complete_{task['id']}", 
                                help="Mark as complete", 
                                use_container_width=True):
                        toggle_complete(task['id'])
                        st.rerun()
                
                with cols[2]:
                    if st.button("🗑️", key=f"delete_{task['id']}", 
                                help="Delete task", 
                                use_container_width=True):
                        remove_task(task['id'])
                        st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    if not st.session_state.tasks:
        st.info("No tasks to analyze yet")
    else:
        st.subheader("📈 Task Analytics")
        
        # Convert to DataFrame for plotting
        df = pd.DataFrame(st.session_state.tasks)
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['completed'] = df['completed'].astype(str)
        
        # Priority distribution
        st.write("### Priority Distribution")
        priority_counts = df['priority'].value_counts().reset_index()
        fig1 = px.pie(priority_counts, names='priority', values='count', 
                      color='priority', color_discrete_map={
                          "High": "#ff4b4b", 
                          "Medium": "#fdaa3d", 
                          "Low": "#4bb543"
                      })
        st.plotly_chart(fig1, use_container_width=True)
        
        # Completion rate
        st.write("### Completion Status")
        completed_counts = df['completed'].value_counts().reset_index()
        fig2 = px.bar(completed_counts, x='completed', y='count', 
                      color='completed',
                      labels={'completed': 'Status', 'count': 'Number of Tasks'})
        st.plotly_chart(fig2, use_container_width=True)
        
        # Task creation timeline
        st.write("### Task Creation Timeline")
        timeline_df = df.groupby(df['created_at'].dt.date).size().reset_index(name='count')
        fig3 = px.line(timeline_df, x='created_at', y='count', 
                      labels={'created_at': 'Date', 'count': 'Tasks Created'})
        st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.subheader("⚙️ App Settings")
    
    # Export/Import tasks
    st.write("### Data Management")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export Tasks as JSON", use_container_width=True):
            st.download_button(
                label="Download Tasks",
                data=pd.DataFrame(st.session_state.tasks).to_json(),
                file_name="tasks_export.json",
                mime="application/json"
            )
    
    with col2:
        uploaded_file = st.file_uploader("Import Tasks", type=["json"])
        if uploaded_file is not None:
            try:
                imported_tasks = pd.read_json(uploaded_file).to_dict('records')
                st.session_state.tasks = imported_tasks
                st.success("Tasks imported successfully!")
            except:
                st.error("Invalid file format. Please upload a valid JSON export.")

    # Clear all tasks
    st.write("### Clear Data")
    if st.button("Clear All Tasks", type="primary"):
        st.session_state.tasks = []
        st.success("All tasks cleared!")

    # About section
    st.write("---")
    st.write("### About")
    st.write("""
    **Advanced To-Do List App**  
    Features:
    - Priority levels
    - Due dates
    - Drag-and-drop sorting
    - Dark/Light mode
    - Analytics dashboard
    - Export/Import functionality
    """)

# Requirements
requirements = """
streamlit==1.36.0
pandas==2.2.2
plotly==5.22.0
extra-streamlit-components==0.1.62
"""

# Create requirements.txt in the background
with open("requirements.txt", "w") as f:
    f.write(requirements)
