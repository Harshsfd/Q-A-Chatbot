import streamlit as st
import pandas as pd

# Initialize session state for tasks
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# Function to add a task
def add_task(task):
    st.session_state.tasks.append(task)

# Function to remove a task
def remove_task(task):
    st.session_state.tasks.remove(task)

# Streamlit app layout
st.title("To-Do List App")

# Input box for new tasks
new_task = st.text_input("Enter a new task:")

# Button to add the task
if st.button("Add Task"):
    if new_task:
        add_task(new_task)
        st.success(f'Task "{new_task}" added!')
    else:
        st.warning("Please enter a task.")

# Display the current tasks
if st.session_state.tasks:
    st.subheader("Your Tasks:")
    for task in st.session_state.tasks:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(task)
        with col2:
            if st.button("Remove", key=task):
                remove_task(task)
                st.success(f'Task "{task}" removed!')
else:
    st.write("No tasks yet!")

# Optional: Clear all tasks
if st.button("Clear All Tasks"):
    st.session_state.tasks.clear()
    st.success("All tasks cleared!")
