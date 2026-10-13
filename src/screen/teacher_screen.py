import streamlit as st

from src.ui.base_layout import style_background_dashboard,style_base_layout

from src.components.footer import footer_dashboard
from src.components.header import header_dashboard

from src.database.db import check_teacher_exists, create_teacher, teacher_login
def teacher_screen():
 
    style_background_dashboard()
    style_base_layout()
    #teacher_screen_register()
    
    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type == "login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()

    
    

def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    c1,c2 = st.columns(2, vertical_alignment='center',gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.write("") 
        st.markdown(f"""<h1 style=" color:black;text-align:center;font-size:60px;font-family:'Outfit',sans-serif;margin:0;">Welcome, {teacher_data['name']}</h1>""",unsafe_allow_html=True,)
        if st.button("Logout", type='secondary',key='loginbacktn',shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False 
            del st.session_state.teacher_data
            st.rerun() 

    st.space()


    tab1, tab2, tab3 = st.columns(3)

    with tab1:
        st.button('Take Attendance',width='stretch',icon=':material/ar_on_you:')
    footer_dashboard()
    

def login_teacher(username, password):
    if not username or not password:
        return False

    teacher = teacher_login(username, password)

    if teacher:
        st.session_state.user_role ='teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True

    return False

def teacher_screen_login():    
    c1,c2 = st.columns(2, vertical_alignment='center',gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.write("") 
        if st.button("Go back to Home", type='secondary',key='loginbacktn',shortcut="control+backspace"):
            st.session_state['login_type']=None
            st.rerun()  

    st.markdown("""
<h2 style='text-align: center; margin-top: 15px; font-size: 36px; font-weight: bold; color: #1f77b4;'>
    Login using Paasword
</h2>
""", unsafe_allow_html=True)
    st.space()
    st.space()
    teacher_username = st.text_input("Enter Username",placeholder="@Aditya")
    
    teacher_password = st.text_input("Enter Password",placeholder="Enter The Password",type="password")
    st.divider() 

    btnc1 ,btnc2 =st.columns(2)
    with btnc1:
        if st.button('Login',icon=':material/passkey:',shortcut='control+enter',width='stretch'):
            if login_teacher(teacher_username, teacher_password):
                st.toast("Welcome back!")
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username and password combo")

    with btnc2:
        if st.button('Register Instead',type='primary',icon=':material/passkey:',shortcut='control+enter',width='stretch'):
            st.session_state.teacher_login_type = 'register'

    footer_dashboard()

    

def register_teacher(teacher_username, teacher_name, teacher_password, teacher_password_confirm):
    if not teacher_username or not teacher_name or not teacher_password:
        return False, "All Fields are required!"
    if check_teacher_exists(teacher_username):
        return False, "Username already taken"
    if teacher_password != teacher_password_confirm:
        return False, "Password doesn't match"

    try:
        create_teacher(teacher_username,teacher_password,teacher_name)
        return True, "Sucessfully Created! Login now"
    except Exception as e:
        return False, str(e)



def teacher_screen_register():  
    c1,c2 = st.columns(2, vertical_alignment='center',gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.write("") 
        if st.button("Go back to Home", type='secondary',key='loginbacktn',shortcut="control+backspace"):
            st.session_state['login_type']=None
            st.rerun()

    st.markdown("""
<h2 style='text-align: center; margin-top: 15px; font-size: 36px; font-weight: bold; color: #1f77b4;'>
    Register your Teacher Profile
</h2>
""", unsafe_allow_html=True)
    
    st.space()
    st.space()
    teacher_username = st.text_input("Enter Username",placeholder="@AdityaSky143")
    teacher_name = st.text_input("Enter Name",placeholder="Aditya Pawar")
    teacher_password = st.text_input("Enter Password",placeholder="Enter The Password",type="password")
    teacher_password_confirm = st.text_input("Enter Confirm Password",placeholder="Enter The Password",type="password")

    st.divider() 

    btnc1 ,btnc2 =st.columns(2)
    with btnc1:
        if st.button('Register Now',icon=':material/passkey:',shortcut='control+enter',width='stretch'):
            success,message = register_teacher(teacher_username, teacher_name, teacher_password, teacher_password_confirm)
            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)

    with btnc2:
        if st.button('Login Instead',type='primary',icon=':material/passkey:',width='stretch'):
            st.session_state.teacher_login_type = 'login'
            st.rerun()

    footer_dashboard()
