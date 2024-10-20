import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Connect to database
conn = sqlite3.connect('portal.db')
c = conn.cursor()

def login(username, password):
    c.execute('SELECT role FROM users WHERE username=? AND password=?', (username, password))
    role = c.fetchone()
    if role:
        return role[0]
    return None

def get_student_data(student_id):
    c.execute('SELECT * FROM marks WHERE student_id=?', (student_id,))
    return pd.DataFrame(c.fetchall(), columns=["ID", "Student ID", "Subject", "Marks", "Class", "Department"])

def get_class_data(class_name):
    c.execute('SELECT * FROM marks WHERE class=?', (class_name,))
    return pd.DataFrame(c.fetchall(), columns=["ID", "Student ID", "Subject", "Marks", "Class", "Department"])

def get_department_data(department_name):
    c.execute('SELECT * FROM marks WHERE department=?', (department_name,))
    return pd.DataFrame(c.fetchall(), columns=["ID", "Student ID", "Subject", "Marks", "Class", "Department"])

def get_all_data():
    c.execute('SELECT * FROM marks')
    return pd.DataFrame(c.fetchall(), columns=["ID", "Student ID", "Subject", "Marks", "Class", "Department"])

# Streamlit App
st.title("Portal Dashboard")

# Login
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    role = login(username, password)
    if role:
        st.success(f"Logged in as {role}")
        
        # Display different dashboards based on roles
        if role == 'Student':
            student_data = get_student_data(student_id=1)  # Example student ID
            st.write("Your Marks")
            st.dataframe(student_data)
            fig = px.pie(student_data, names='Subject', values='Marks', title='Marks Distribution')
            st.plotly_chart(fig)
        
        elif role == 'Staff':
            class_data = get_class_data(class_name='CTPS')  # Example class
            st.write("Class Marks")
            st.dataframe(class_data)
            fig = px.bar(class_data, x='Student ID', y='Marks', color='Subject', title='Class Marks Distribution')
            st.plotly_chart(fig)
        
        elif role == 'HOD':
            dept_data = get_department_data(department_name='AIML')  # Example department
            st.write("Department Marks")
            st.dataframe(dept_data)
            fig = px.line(dept_data, x='Student ID', y='Marks', color='Subject', title='Department Marks Over Time')
            st.plotly_chart(fig)
        
        elif role == 'Principal':
            all_data = get_all_data()
            st.write("All Marks")
            st.dataframe(all_data)
            fig = px.histogram(all_data, x='Marks', color='Class', title='Overall Marks Distribution')
            st.plotly_chart(fig)
    else:
        st.error("Invalid credentials")
