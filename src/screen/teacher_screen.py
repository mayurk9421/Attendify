import streamlit as st

from src.ui.base_layout import style_background_dashboard,style_base_layout

from src.components.footer import footer_dashboard
from src.components.header import header_dashboard
from src.components.subject_card import subject_card
from src.database.db import check_teacher_exists, create_teacher, teacher_login,get_teacher_subjects,get_attendance_for_teacher,delete_attendance_session
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog

from src.pipelines.face_pipeline import predict_attendance
from src.components.Dialog_attendance_results import attendance_result_dialog
import numpy as np
from datetime import datetime
import pandas as pd
from src.database.config import supabase

from src.components.dialog_voice_attendance import voice_attendance_dialog

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

    
def change_teacher_tab(tab):
    st.session_state.current_teacher_tab=tab    


@st.dialog("⚠️ Low Attendance Students")
def low_attendance_dialog(low_attendance):
    st.caption(f"{len(low_attendance)} student(s) below 75% attendance")
    for student in low_attendance:
        st.write(f"🔴 **{student['name']}** — {student['subject']} — **{student['percentage']:.1f}%**")
    st.divider()
    if st.button("Close",type="primary",width='stretch'):
        st.rerun()



def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    
    if st.session_state.get("show_student_report", False):
        st.title("👤 Individual Student Report")
        if st.button("← Back to Dashboard", key="back_from_student_report"):
            st.session_state["show_student_report"] = False
            st.rerun()
        teacher_tab_individual_student_report()
        return

    if st.session_state.get("show_analytics",False):
        st.title("📊 Attendance Analytics")
        if st.button("← Back to Dashboard",key="back_from_analytics"):
            st.session_state["show_analytics"]=False
            st.rerun()
        teacher_tab_analytics()
        return
    c1,c2 = st.columns(2, vertical_alignment='center',gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.write("") 
        st.subheader(f"""Welcome, {teacher_data['name']}""")
        if st.button("Logout", type='secondary',key='loginbacktn',shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False 
            del st.session_state.teacher_data
            st.rerun() 

    st.space()
    teacher_id=teacher_data['teacher_id']
    records=get_attendance_for_teacher(teacher_id)

    if records:
        sessions=set(r.get('timestamp') for r in records if r.get('timestamp'))
        total_classes=len(sessions)
        total_students=len(set(r.get('students',{}).get('student_id') for r in records if r.get('students')))
        total_present=sum(bool(r.get('is_present',False)) for r in records)
        average_attendance=(total_present/len(records))*100
        latest_record=max(records,key=lambda x:x.get('timestamp',''))
        latest_subject=latest_record.get('subjects',{}).get('name','Unknown')
        latest_time=datetime.fromisoformat(latest_record['timestamp']).strftime("%d %b %Y, %I:%M %p")
    else:
        total_classes=0
        total_students=0
        average_attendance=0
        latest_subject="No attendance"
        latest_time="—"

    low_attendance=[]

    enrolled_res=supabase.table('subject_students').select("*,students(*),subjects!inner(*)").eq('subjects.teacher_id',teacher_id).execute()

    for node in enrolled_res.data:
        student=node.get('students')
        subject=node.get('subjects')
        if not student or not subject:
            continue

        student_id=student['student_id']
        subject_id=subject['subject_id']
        student_logs=[r for r in records if r.get('student_id')==student_id and r.get('subject_id')==subject_id]

        if student_logs:
            present=sum(bool(r.get('is_present',False)) for r in student_logs)
            percentage=(present/len(student_logs))*100
            if percentage<75:
                low_attendance.append({'name':student['name'],'subject':subject['name'],'percentage':percentage})

    with st.container(border=True,key="dashboard_overview"):
        o1,o2,o3,o4,o5=st.columns([1,1,1.3,1.6,1.5])

        with o1:
            st.metric("📚 Classes",total_classes)

        with o2:
            st.metric("👥 Students",total_students)

        with o3:
            st.metric("📊 Average Attendance",f"{average_attendance:.1f}%")

        with o4:
            st.markdown("🕒 **Last Attendance**")
            st.write(f"{latest_subject} • {latest_time}")

        with o5:
            if low_attendance:
                st.markdown('<div class="low-attendance-warning">',unsafe_allow_html=True)
                if st.button(f"⚠️ {len(low_attendance)} Students Below 75% ›",key="low_attendance_open",type="primary",width="stretch",use_container_width=True):
                    low_attendance_dialog(low_attendance)
                st.markdown('</div>',unsafe_allow_html=True)
            else:
                st.markdown("🟢 **All Good**")
                st.caption("Everyone ≥ 75%")
                
    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'

        
    student_report_col, analytics_col = st.columns(2, gap="medium")

    with student_report_col:
        if st.button(
            "👤 Student Report",
            key="open_student_report",
            type="secondary",
            width="stretch"
        ):
            st.session_state["show_student_report"] = True
            st.session_state["show_analytics"] = False
            st.rerun()

    with analytics_col:
        if st.button(
            "📊 Analytics",
            key="open_analytics",
            type="secondary",
            width="stretch"
        ):
            st.session_state["show_analytics"] = True
            st.session_state["show_student_report"] = False
            st.rerun()
    st.divider()
    
    st.markdown(
    "<h3 style='text-align: center;'>⚡ Quick Actions</h3>",unsafe_allow_html=True)
    st.markdown(
    "<p style='text-align: center; color: gray;'>Manage your classes and attendance</p>",unsafe_allow_html=True)
    tab1, tab2, tab3 = st.columns(3)

    with tab1:
        if st.button('Take Attendance',type='primary' if st.session_state.current_teacher_tab == 'take_attendance' else 'tertiary',width='stretch',icon=':material/ar_on_you:',on_click=change_teacher_tab,args=('take_attendance',)):
            pass

    with tab2:
        if st.button('Manage Subjects',type='primary' if st.session_state.current_teacher_tab == 'manage_subjects' else 'tertiary',width='stretch',icon=':material/book_ribbon:',on_click=change_teacher_tab,args=('manage_subjects',)):
            pass

    with tab3:
        if st.button('Attendance Records',type='primary' if st.session_state.current_teacher_tab == 'attendance_records' else 'tertiary',width='stretch',icon=':material/cards_stack:',on_click=change_teacher_tab,args=('attendance_records',)):
            pass
        
    st.divider()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    if st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    if st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()
        
        
    footer_dashboard()

def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.header('Take AI Attendance')

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.warning('You havent created any subjects yet! Please create one to begin!')
        return

    subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}

    col1, col2 = st.columns([3,1], vertical_alignment="bottom")

    with col1:
        selected_subject_label = st.selectbox('Select Subject', options=list(subject_options.keys()))

    with col2:
        if st.button('Add Photos', type='primary', icon =":material/photo_prints:", width='stretch'):
            add_photos_dialog()
    selected_subject_id = subject_options[selected_subject_label]
    enrolled_res=supabase.table('subject_students').select('student_id').eq('subject_id',selected_subject_id).execute()
    enrolled_count=len(enrolled_res.data)

    if enrolled_count==0:
        st.info("👥 No students enrolled in this subject yet. Ask students to join using the subject code.")
    st.divider()

    if st.session_state.attendance_images:
        st.header('Added Photos')
        gallery_cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4]:
                st.image(img, caption=f"Photo {idx+1}", width="stretch")
                if st.button('Remove', key=f'remove_{idx}', type='secondary', width='stretch'):
                    st.session_state.attendance_images.pop(idx)
                    st.rerun()

    has_photos = bool(st.session_state.attendance_images)
    c1,c2, c3 = st.columns(3)

    with c1:
        if st.button('Clear All Photos', type='tertiary', width='stretch', icon=':material/delete:',disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()

    with c2:
        
        if st.button('Run Face Analysis',type='secondary',icon=':material/analytics:',disabled=not has_photos or enrolled_count==0,width='stretch'):
                    with st.spinner('Deep Scanning Classroom Photos...'):
                        all_detected_ids = {}

                        for idx, img in enumerate(st.session_state.attendance_images):
                            imp_np = np.array(img.convert('RGB'))
                            detected, _, _ = predict_attendance(imp_np)

                            if detected:
                                for sid in detected.keys():
                                    student_id = int(sid)  

                                    all_detected_ids.setdefault(student_id, []).append(f"Photo {idx+1}")

                        enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id', selected_subject_id).execute()
                        enrolled_students = enrolled_res.data

                        if not enrolled_students:
                            st.warning("No students are enrolled in this subject.")
                        else:
                            results, attendance_to_log = [], [] 

                            current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                            for node in enrolled_students:
                                student = node['students']
                                sources = all_detected_ids.get(int(student['student_id']), [])
                                is_present = len(sources) > 0

                                results.append({
                                    "Name": student['name'],
                                    "ID": student['student_id'],
                                    "Source": ",".join(sources) if is_present else "_",
                                    "Status": "✅ Present" if is_present else "❌ Absent"
                                })

                                attendance_to_log.append({
                                    'student_id': student['student_id'],
                                    'subject_id': selected_subject_id,
                                    'timestamp': current_timestamp,
                                    'is_present' : bool(is_present)
                                })

                            attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button('Use Voice Attendance',type='primary',width='stretch',icon=':material/mic:',disabled=enrolled_count==0):
            voice_attendance_dialog(selected_subject_id)

    if st.session_state.get("voice_attendance_results"):
        df_results, logs = st.session_state.voice_attendance_results

        attendance_result_dialog(df_results, logs)

        del st.session_state.voice_attendance_results
       
            
def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']

    col1, col2 = st.columns(2)

    with col1:
        st.header('Manage Subjects', width='stretch')

    with col2:
        if st.button('Create New Subject', width='stretch'):
            create_subject_dialog(teacher_id)

    # LIST ALL SUBJECTS
    subjects = get_teacher_subjects(teacher_id)

    if subjects:
        for sub in subjects:

            stats = [
                ("🫂", "Students", sub['total_students']),
                ("🕰️", "Classes", sub['total_classes']),
            ]

            def share_btn(sub=sub):
                if st.button(
                    f"Share Code: {sub['name']}",
                    key=f"share_{sub['subject_code']}",
                    icon=":material/share:"
                ):
                    share_subject_dialog(
                        sub['name'],
                        sub['subject_code']
                    )

                st.space()

            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=stats,
                footer_callback=share_btn
            )

    else:
        st.info("NO SUBJECTS FOUND. CREATE ONE ABOVE")


#for poping "are you sure want to delte"
@st.dialog("Delete Attendance")
def delete_attendance_confirm_dialog():
    st.warning("Are you sure you want to delete this attendance session?")
    st.caption("This will permanently delete all attendance records for this class session.")
    col1,col2=st.columns(2)
    with col1:
        if st.button("Cancel",width="stretch"):
            st.session_state.pop('delete_attendance_session',None)
            st.session_state.pop('delete_attendance_subject_id',None)
            st.rerun()
    with col2:
        if st.button("Delete",type="primary",width="stretch",icon=":material/delete:"):
            try:
                delete_attendance_session(st.session_state['delete_attendance_subject_id'],st.session_state['delete_attendance_session'])
                st.session_state.pop('delete_attendance_session',None)
                st.session_state.pop('delete_attendance_subject_id',None)
                st.session_state.pop('selected_attendance_session',None)
                st.toast("Attendance session deleted successfully!")
                st.rerun()
            except Exception as e:
                st.error("Failed to delete attendance session.")
                st.exception(e)

def teacher_tab_attendance_records():
    st.header('Attendance Records')

    teacher_id = st.session_state.teacher_data['teacher_id']

    records = get_attendance_for_teacher(teacher_id)

    if not records:
        st.info("No attendance records found.")
        return

    data = []

    for r in records:
        ts = r.get('timestamp')

        subject = r.get('subjects', {})
        student = r.get('students', {})

        data.append({
            "ts_group": ts.split(".")[0] if ts else None,
            "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N/A",
            "Subject": subject.get("name", "Unknown"),
            "Subject Code": subject.get("subject_code", "N/A"),
            "subject_id": subject.get("subject_id"),
            "Student Name": student.get("name", "Unknown"),
            "Student ID": student.get("student_id", r.get("student_id")),
            "is_present": bool(r.get("is_present", False))
        })

    df = pd.DataFrame(data)

    # -----------------------------
    # Create class/session summary
    # -----------------------------

    summary = (
        df.groupby(
            ['ts_group', 'Time', 'Subject', 'Subject Code', 'subject_id']
        )
        .agg(
            Present_Count=('is_present', 'sum'),
            Total_Count=('is_present', 'count')
        )
        .reset_index()
    )

    summary['Attendance_stats'] = (
        "✅ "
        + summary['Present_Count'].astype(str)
        + "/"
        + summary['Total_Count'].astype(str)
        + " Students"
    )

    summary = summary.sort_values(
        by='ts_group',
        ascending=False
    ).reset_index(drop=True)

    # ==================================================
    # PROFESSIONAL SUMMARY CARDS
    # ==================================================

    total_classes = len(summary)

    # Get all students enrolled in this teacher's subjects
    enrolled_res = supabase.table(
        'subject_students'
    ).select(
        'student_id, subjects!inner(teacher_id)'
    ).eq(
        'subjects.teacher_id',
        teacher_id
    ).execute()

    # Count unique students
    total_students = len(
        set(
            row['student_id']
            for row in enrolled_res.data
            if row.get('student_id') is not None
        )
    )

    total_present = df['is_present'].sum()
    total_attendance = len(df)

    if total_attendance > 0:
        average_attendance = (
            total_present / total_attendance
        ) * 100
    else:
        average_attendance = 0

    # ==================================================
    # FILTERS
    # ==================================================

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:

        subject_options = ["All Subjects"] + sorted(
            summary['Subject'].unique().tolist()
        )

        selected_subject = st.selectbox(
            "📚 Filter by Subject",
            subject_options
        )

    with filter_col2:

        date_options = ["All Dates"] + sorted(
            summary['Time'].str[:10].unique().tolist(),
            reverse=True
        )

        selected_date = st.selectbox(
            "📅 Filter by Date",
            date_options
        )


    # ==================================================
    # APPLY FILTERS
    # ==================================================

    filtered_summary = summary.copy()

    if selected_subject != "All Subjects":

        filtered_summary = filtered_summary[
            filtered_summary['Subject'] == selected_subject
        ]

    if selected_date != "All Dates":

        filtered_summary = filtered_summary[
            filtered_summary['Time'].str[:10] == selected_date
        ]

    # ==================================================
    # ATTENDANCE RECORDS
    # ==================================================

    h1, h2, h3, h4, h5 = st.columns(
        ([2.2,1.1,1.8,1.3,3.0])
    )

    with h1:
        st.markdown("**Time**")

    with h2:
        st.markdown("**Subject**")

    with h3:
        st.markdown("**Subject Code**")

    with h4:
        st.markdown("**Attendance**")

    with h5:
        st.markdown("**Action**")

    st.divider()

    for index, row in filtered_summary.iterrows():

        col1, col2, col3, col4, col5 = st.columns(
            ([2.2,1.1,1.8,1.3,3.0])
        )

        with col1:
            st.write(row['Time'])

        with col2:
            st.write(row['Subject'])

        with col3:
            st.write(row['Subject Code'])

        with col4:
            st.write(row['Attendance_stats'])

        with col5:
            view_col, delete_col = st.columns(2)
            with view_col:
                if st.button("",key=f"view_attendance_{row['ts_group']}_{index}",icon=":material/visibility:",help="View attendance",width="stretch"):
                    st.session_state['selected_attendance_session'] = row['ts_group']
            with delete_col:
                if st.button("",key=f"delete_attendance_{row['ts_group']}_{index}",icon=":material/delete:",help="Delete attendance",width="stretch"):
                    st.session_state['delete_attendance_session'] = row['ts_group']
                    st.session_state['delete_attendance_subject_id'] = row['subject_id']
                    st.rerun()

    if st.session_state.get('delete_attendance_session') and st.session_state.get('delete_attendance_subject_id'):
        delete_attendance_confirm_dialog()
            
    # ==================================================
    # SHOW SELECTED CLASS DETAILS
    # ==================================================

    selected_session = st.session_state.get(
        'selected_attendance_session'
    )

    if selected_session:

        selected_df = df[
            df['ts_group'] == selected_session
        ].copy()

        if not selected_df.empty:

            st.divider()

            first_student = selected_df.iloc[0]

            st.subheader(
                f"Attendance Details — "
                f"{first_student['Subject']} "
                f"({first_student['Subject Code']})"
            )

            st.caption(
                f"Class Time: {first_student['Time']}"
            )

            student_display = selected_df[
                [
                    'Student Name',
                    'Student ID',
                    'is_present'
                ]
            ].copy()

            student_display['Status'] = (
                student_display['is_present']
                .apply(
                    lambda x:
                    "✅ Present"
                    if x
                    else "❌ Absent"
                )
            )

            student_display = student_display[
                [
                    'Student Name',
                    'Student ID',
                    'Status'
                ]
            ]

            st.dataframe(
                student_display,
                width='stretch',
                hide_index=True
            )
    

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

def teacher_tab_individual_student_report():
    teacher_id = st.session_state.teacher_data["teacher_id"]

    st.subheader("👤 Individual Student Report")
    st.caption("View attendance details for a student in your subjects.")

    # Get students enrolled in this teacher's subjects
    response = supabase.table("subject_students").select(
        "student_id, students(student_id, name), "
        "subjects!inner(subject_id, teacher_id)"
    ).eq("subjects.teacher_id", teacher_id).execute()

    student_map = {}

    for row in response.data or []:
        student = row.get("students") or {}

        if isinstance(student, list):
            student = student[0] if student else {}

        if student.get("student_id") is not None:
            sid = student["student_id"]
            student_map[sid] = student.get("name", f"Student {sid}")

    if not student_map:
        st.info("No students are enrolled in your subjects yet.")
        return

    student_options = {
        f"{name} (ID: {sid})": sid
        for sid, name in sorted(
            student_map.items(), key=lambda item: item[1].lower()
        )
    }

    selected_label = st.selectbox(
        "Select Student",
        list(student_options.keys()),
        key="individual_report_student"
    )
    selected_id = student_options[selected_label]

    records = get_attendance_for_teacher(teacher_id) or []

    student_records = [
        r for r in records
        if str(r.get("student_id")) == str(selected_id)
    ]

    if not student_records:
        st.info("No attendance records found for this student.")
        return

    # Subject filter
    subject_names = []
    for record in student_records:
        subject = record.get("subjects") or {}
        if isinstance(subject, list):
            subject = subject[0] if subject else {}
        subject_names.append(subject.get("name", "Unknown"))

    selected_subject = st.selectbox(
        "Filter by Subject",
        ["All Subjects"] + sorted(set(subject_names)),
        key="individual_report_subject"
    )

    rows = []
    for record in student_records:
        subject = record.get("subjects") or {}
        if isinstance(subject, list):
            subject = subject[0] if subject else {}

        name = subject.get("name", "Unknown")
        if selected_subject != "All Subjects" and name != selected_subject:
            continue

        present_value = record.get("is_present")

        rows.append({
            "Date": pd.to_datetime(
                record.get("timestamp"), errors="coerce"
            ).strftime("%d %b %Y")
            if pd.notna(pd.to_datetime(record.get("timestamp"), errors="coerce"))
            else "Unknown",
            "Subject": name,
            "Subject Code": subject.get("subject_code", "N/A"),
            "Status": (
                "Present" if present_value is True
                else "Absent" if present_value is False
                else "Unknown"
            ),
            "is_present": present_value
        })

    if not rows:
        st.info("No records match this subject filter.")
        return

    report_df = pd.DataFrame(rows)
    total = len(report_df)
    present = int((report_df["is_present"] == True).sum())
    absent = int((report_df["is_present"] == False).sum())
    rate = present / total * 100 if total else 0

    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Records", total)
    c2.metric("Present", present)
    c3.metric("Absent", absent)
    c4.metric("Attendance", f"{rate:.1f}%")
    st.progress(min(max(rate / 100, 0.0), 1.0))
    st.caption("Target attendance: 75%")

    if rate < 75:
        st.warning("⚠️ Attendance is below the 75% target.")
    else:
        st.success("✅ Attendance meets the 75% target.")

    st.divider()
    st.markdown("#### 📅 Attendance History")

    display_df = report_df.drop(columns=["is_present"]).sort_values(
        "Date", ascending=False
    )
    st.dataframe(display_df, hide_index=True, width="stretch")

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
                st.toast("👋🏻Welcome back!")
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


def get_complete_analytics_data(records,teacher_id):
    enrollment=supabase.table("subject_students").select(
        "subject_id,student_id,students(*),subjects!inner(teacher_id)"
    ).eq("subjects.teacher_id",teacher_id).execute()

    enrolled={}
    student_names={}

    for row in enrollment.data or []:
        sid=row.get("subject_id")
        uid=row.get("student_id")
        if sid is None or uid is None:
            continue
        enrolled.setdefault(str(sid),set()).add(str(uid))
        student=row.get("students") or {}
        if isinstance(student,list):
            student=student[0] if student else {}
        student_names[str(uid)]=student.get("name","Unknown")

    sessions={}
    for r in records:
        subject=r.get("subjects") or {}
        if isinstance(subject,list):
            subject=subject[0] if subject else {}
        sid=r.get("subject_id",subject.get("subject_id"))
        ts=r.get("timestamp")
        if sid is None or not ts:
            continue
        session_key=(str(sid),str(ts).split(".")[0])
        sessions.setdefault(session_key,[]).append(r)

    complete=[]
    for (sid,session_time),logs in sessions.items():
        subject=logs[0].get("subjects") or {}
        if isinstance(subject,list):
            subject=subject[0] if subject else {}

        enrolled_ids=enrolled.get(sid,set())
        logged_ids={str(r.get("student_id")) for r in logs if r.get("student_id") is not None}

        # Include logged students even if they are no longer enrolled.
        student_ids=enrolled_ids | logged_ids

        for uid in student_ids:
            student_logs=[r for r in logs if str(r.get("student_id"))==uid]
            is_present=any(bool(r.get("is_present",False)) for r in student_logs)

            complete.append({
                "Timestamp":session_time,
                "Subject":subject.get("name","Unknown"),
                "Subject Code":subject.get("subject_code","N/A"),
                "Student":student_names.get(uid,"Unknown"),
                "Student ID":uid,
                "Present":is_present
            })

    return pd.DataFrame(complete)


def teacher_tab_analytics():
    teacher_id=st.session_state.teacher_data['teacher_id']
    records=get_attendance_for_teacher(teacher_id)

    st.caption("Your attendance performance, student insights, and class trends in one place.")

    if not records:
        st.info("📭 No attendance data yet. Take attendance to unlock your analytics.")
        return

    
    df=get_complete_analytics_data(records,teacher_id)
    if df.empty:
        st.info("No attendance records available for analytics.")
        return

    df["Timestamp"]=pd.to_datetime(df["Timestamp"],errors="coerce")
    df=df.dropna(subset=["Timestamp"])
    if df.empty:
        st.info("No valid attendance timestamps were found.")
        return

    df["Session"]=df["Timestamp"].dt.floor("s")
    df["Date"]=df["Timestamp"].dt.strftime("%Y-%m-%d")


    st.divider()
    f1,f2=st.columns(2)
    with f1:
        subjects=["All Subjects"]+sorted(df["Subject"].unique().tolist())
        selected_subject=st.selectbox("📚 Filter by Subject",subjects,key="analytics_subject")
    with f2:
        dates=["All Dates"]+sorted(df["Date"].unique().tolist(),reverse=True)
        selected_date=st.selectbox("📅 Filter by Date",dates,key="analytics_date")

    filtered=df.copy()
    if selected_subject!="All Subjects":
        filtered=filtered[filtered["Subject"]==selected_subject]
    if selected_date!="All Dates":
        filtered=filtered[filtered["Date"]==selected_date]

    if filtered.empty:
        st.warning("No attendance data matches these filters.")
        return

    total_entries=len(filtered)
    present=int(filtered["Present"].sum())
    absent=total_entries-present
    attendance_rate=present/total_entries*100
    total_classes=filtered.groupby(["Session","Subject"]).ngroups
    total_students=filtered["Student ID"].nunique()

    
    
    
    st.subheader("📌 Attendance Overview")
    k1,k2,k3,k4=st.columns(4,gap="small")

    with k1:
        with st.container(border=True):
            st.caption("📚 TOTAL CLASSES")
            st.metric("Classes Conducted",total_classes)
            st.caption("Recorded sessions")

    with k2:
        with st.container(border=True):
            st.caption("👥 TOTAL STUDENTS")
            st.metric("Students Recorded",total_students)
            st.caption("Unique students")

    with k3:
        with st.container(border=True):
            st.caption("📊 ATTENDANCE RATE")
            st.metric("Attendance",f"{attendance_rate:.1f}%")
            st.progress(min(max(attendance_rate/100,0.0),1.0))
            st.caption("Target: 75%")

    with k4:
        with st.container(border=True):
            st.caption("📝 ATTENDANCE ENTRIES")
            st.metric("Present / Absent",f"{present} / {absent}")
            st.caption(f"{total_entries} entries")


    subject_chart=filtered.groupby(["Subject","Subject Code"]).agg(
        Present=("Present","sum"),
        Total=("Present","count")
    ).reset_index()
    subject_chart["Attendance %"]=(subject_chart["Present"]/subject_chart["Total"]*100).round(1)

    left,right=st.columns([1.2,1],gap="large")
    with left:
        with st.container(border=True):
            st.markdown("**📊 Subject-wise Attendance**")
            st.caption("Attendance percentage by subject")
            chart_data=subject_chart.set_index("Subject")["Attendance %"]
            st.bar_chart(chart_data,height=280)
            st.caption("Target attendance: 75%")

    with right:
        with st.container(border=True):
            st.markdown("**🟢 Present vs Absent**")
            st.caption("Distribution of recorded attendance entries")
            distribution=pd.DataFrame({
                "Status":["Present","Absent"],
                "Entries":[present,absent]
            })
            st.bar_chart(
                distribution,
                x="Status",
                y="Entries",
                color="#5865F2",
                height=280
            )

    st.divider()
    
    st.divider()
    with st.container(border=True):
        st.markdown("**📅 Daily Attendance Trend**")
        st.caption("Attendance percentage by date")

        daily=filtered.groupby("Date").agg(
            Present=("Present","sum"),
            Total=("Present","count")
        ).reset_index()

        daily["Attendance %"]=(daily["Present"]/daily["Total"]*100).round(1)

        if len(daily)<2:
            st.info("The daily trend will appear when attendance data is available for at least two dates.")
        else:
            st.line_chart(
                daily.set_index("Date")["Attendance %"],
                height=280,
                color="#5865F2"
            )


    st.divider()
    st.subheader("⚠️ Students Needing Attention")

    student_stats=filtered.groupby(["Student ID","Student","Subject","Subject Code"]).agg(
        Present=("Present","sum"),
        Classes=("Present","count")
    ).reset_index()
    student_stats["Attendance %"]=(student_stats["Present"]/student_stats["Classes"]*100).round(1)
    low=student_stats[student_stats["Attendance %"]<75].copy()

    if low.empty:
        st.success("🎉 Great work! No recorded students are below 75% for this selection.")
    else:
        st.warning(f"{len(low)} student-subject record(s) are below 75% attendance.")
        low["Status"]=low["Attendance %"].apply(
            lambda x:"🔴 Critical" if x<50 else "🟠 Needs Improvement"
        )
        low["Attendance %"]=low["Attendance %"].map(lambda x:f"{x:.1f}%")
        low=low.rename(columns={
            "Student ID":"Student ID",
            "Student":"Student Name",
            "Subject":"Subject",
            "Subject Code":"Code",
            "Present":"Present",
            "Classes":"Classes Recorded"
        })
        st.dataframe(
            low[["Student Name","Student ID","Subject","Code","Present","Classes Recorded","Attendance %","Status"]],
            hide_index=True,
            width="stretch"
        )

    st.divider()
    with st.container(border=True):
        st.markdown("**📋 Subject Performance Summary**")
        summary=subject_chart.rename(columns={
            "Subject":"Subject",
            "Subject Code":"Code",
            "Present":"Present Entries",
            "Total":"Total Entries"
        })
        summary["Performance"]=summary["Attendance %"].apply(
            lambda x:"🟢 Good" if x>=75 else "🔴 Below Target"
        )
        st.dataframe(summary,hide_index=True,width="stretch")
