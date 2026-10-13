import streamlit as st
import pandas as pd
from src.ui.base_layout import style_background_dashboard,style_base_layout

from src.components.footer import footer_dashboard
from src.components.header import header_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predict_attendance , get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import get_all_students, create_student, get_student_subjects, get_student_attendance, unenroll_student_to_subject
import time

from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card


def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']

    # Load student subjects and attendance
    with st.spinner('Loading your dashboard...'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    # Calculate overall attendance
    total_classes = len(logs)
    attended_classes = sum(1 for log in logs if log.get('is_present'))
    attendance_rate = (
        attended_classes / total_classes * 100
        if total_classes else 0
    )

    # Header
    st.markdown("""
    <div style="
        padding:24px;
        border-radius:18px;
        background:linear-gradient(135deg,#5865F2,#8277F5);
        color:white;
        margin-bottom:20px;
    ">
        <div style="font-size:13px;opacity:0.85;">ATTENDIFY · STUDENT PORTAL</div>
        <h1 style="margin:8px 0 4px 0;color:white;font-size:30px;">
            Welcome back, {}
        </h1>
        <p style="margin:0;opacity:0.9;">Track your attendance and manage your subjects.</p>
    </div>
    """.format(student_data['name']), unsafe_allow_html=True)

    # Logout
    logout_col, _ = st.columns([1, 4])
    with logout_col:
        if st.button("↪ Logout", key="student_logout", width="stretch"):
            st.session_state['is_logged_in'] = False
            st.session_state.pop('student_data', None)
            st.rerun()

    # Summary cards
    st.markdown("### 📊 Your Overview")
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        with st.container(border=True):
            st.caption("📚 ENROLLED SUBJECTS")
            st.metric("My Subjects", len(subjects))

    with c2:
        with st.container(border=True):
            st.caption("✅ CLASSES ATTENDED")
            st.metric("Present", attended_classes)

    with c3:
        with st.container(border=True):
            st.caption("📈 OVERALL ATTENDANCE")
            st.metric("Attendance Rate", f"{attendance_rate:.1f}%")
            st.progress(attendance_rate / 100)
            st.caption("Target: 75%")

    st.divider()

    
    # Student dashboard tabs
    tab_subjects, tab_attendance = st.tabs(["📚 My Subjects", "📊 My Attendance"])

    with tab_subjects:
        title_col, button_col = st.columns([2, 1], vertical_alignment="center")

        with title_col:
            st.markdown("### My Enrolled Subjects")
            st.caption("View your courses and attendance progress.")

        with button_col:
            if st.button("＋ Enroll in Subject", type="primary", width="stretch", key="student_enroll"):
                enroll_dialog()

        if not subjects:
            st.info("You haven't enrolled in any subjects yet.")
        else:
            cols = st.columns(2, gap="medium")

            for i, sub_node in enumerate(subjects):
                sub = sub_node['subjects']
                sid = sub['subject_id']

                subject_logs = [
                    log for log in logs
                    if log.get('subject_id') == sid
                ]
                total = len(subject_logs)
                attended = sum(1 for log in subject_logs if log.get('is_present'))
                percentage = attended / total * 100 if total else 0

                with cols[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"#### 📘 {sub['name']}")
                        st.caption(
                            f"Code: {sub.get('subject_code', 'N/A')} · "
                            f"Section: {sub.get('section', 'N/A')}"
                        )

                        m1, m2 = st.columns(2)
                        m1.metric("Total Classes", total)
                        m2.metric("Attended", attended)

                        st.progress(percentage / 100)
                        st.caption(f"Attendance: {percentage:.1f}%")

                        if total == 0:
                            st.info("No attendance records yet.")
                        elif percentage < 75:
                            st.warning("Below the 75% attendance target.")
                        else:
                            st.success("Attendance on track.")

                        if st.button(
                            "🗑 Unenroll from Subject",
                            key=f"unenroll_{sid}",
                            width="stretch"
                        ):
                            unenroll_student_to_subject(student_id, sid)
                            st.toast(f"Unenrolled from {sub['name']} successfully!")
                            time.sleep(1)
                            st.rerun()
    footer_dashboard()
    with tab_attendance:
        st.markdown("### 📊 My Attendance Report")
        st.caption("Review your attendance by subject and date.")

        total = len(logs)
        present = sum(1 for log in logs if log.get("is_present") is True)
        absent = sum(1 for log in logs if log.get("is_present") is False)

        m1, m2, m3 = st.columns(3)

        m1.metric("Total Records", total)
        m2.metric("Present", present)
        m3.metric("Absent", absent)

        rate = present / total * 100 if total else 0
        st.progress(rate / 100)
        st.caption(f"Overall attendance: {rate:.1f}%")
        if total == 0:
            st.info("No attendance records available yet.")
        elif rate < 75:
            st.warning("⚠️ Your attendance is below the required 75% target.")
        else:
            st.success("✅ Your attendance is meeting the 75% target.")
        st.divider()
        st.markdown("#### Subject-wise Attendance")
       
        if not logs:
            st.info("No attendance records are available yet.")
        else:
            report_rows = []

            for sub_node in subjects:
                sub = sub_node['subjects']
                sid = sub['subject_id']

                subject_logs = [
                    log for log in logs
                    if log.get('subject_id') == sid
                ]

                subject_total = len(subject_logs)
                subject_present = sum(
                    1 for log in subject_logs
                    if log.get('is_present') is True
                )
                subject_absent = sum(
                    1 for log in subject_logs
                    if log.get('is_present') is False
                )

                subject_rate = (
                    subject_present / subject_total * 100
                    if subject_total else 0
                )

                report_rows.append({
                    "Subject": sub['name'],
                    "Code": sub.get('subject_code', 'N/A'),
                    "Present": subject_present,
                    "Absent": subject_absent,
                    "Total": subject_total,
                    "Attendance (%)": f"{subject_rate:.1f}%"
                })

            if report_rows:
                report_df = pd.DataFrame(report_rows)

                report_subjects = ["All Subjects"] + sorted(
                    report_df["Subject"].unique().tolist()
                )

                selected_report_subject = st.selectbox(
                    "Filter attendance by subject",
                    report_subjects,
                    key="student_report_subject"
                )

                if selected_report_subject != "All Subjects":
                    report_df = report_df[
                        report_df["Subject"] == selected_report_subject
                    ]

                st.dataframe(
                    report_df,
                    hide_index=True,
                    width="stretch"
                )
            else:
                st.info("No subject attendance records available yet.")

        st.divider()
        st.markdown("#### 🗓️ Attendance History")
        st.caption("Your latest attendance records, with the newest first.")

        if logs:
            history_rows = []

            for log in sorted(
                logs,
                key=lambda item: str(item.get('timestamp', '')),
                reverse=True
            ):
                subject_info = log.get('subjects') or {}
                is_present = log.get('is_present')

                history_rows.append({
                    "Date": str(log.get('timestamp', ''))[:10],
                    "Subject": subject_info.get('name', 'Unknown'),
                    "Status": (
                        "🟢 Present" if is_present is True
                        else "🔴 Absent" if is_present is False
                        else "⚪ Unknown"
                    )
                })

            history_df = pd.DataFrame(history_rows)

            # Filter attendance history by subject
            subject_options = ["All Subjects"] + sorted(
                history_df["Subject"].unique().tolist()
            )
            selected_history_subject = st.selectbox(
                "Filter by Subject",
                subject_options,
                key="student_history_subject"
            )

            if selected_history_subject != "All Subjects":
                history_df = history_df[
                    history_df["Subject"] == selected_history_subject
                ]

            st.dataframe(
                history_df,
                hide_index=True,
                width="stretch",
                column_config={
                    "Date": st.column_config.TextColumn("Date"),
                    "Subject": st.column_config.TextColumn("Subject"),
                    "Status": st.column_config.TextColumn("Attendance Status")
                }
            )
        else:
            st.info("Your attendance history will appear here once records are available.")

       

def student_screen():


    style_background_dashboard()
    style_base_layout()


    if "student_data"in st.session_state:
        student_dashboard()
        return
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
        Login using FaceID
    </h2>
    """, unsafe_allow_html=True)
    st.space()
    st.space()
    
    st.markdown("<h6 style='text-align:center; color:black;'>Position your face at Center</h6>",unsafe_allow_html=True)

    photo_source= st.camera_input("", label_visibility="collapsed")

    show_registration = False
    if photo_source:
        img = np.array(Image.open(photo_source))

        with st.spinner("AI is scanning.."):
            detected,all_ids, num_faces = predict_attendance(img)

            if num_faces == 0:
                st.warning('Face not found!')
            elif num_faces >1:
                st.warning('Multiple faces found')
            else:
                if detected:
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students()
                    student = next((s for s in all_students if s['student_id']==student_id),None)

                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student
                        st.toast(f"👋🏻Welcome back! {student['name']}")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info('Face not recognized! You might be a new student!')
                    show_registration = True
    if show_registration:
        with st.container(border=True):
            st.header('Register new Profile')
            new_name = st.text_input("Enter your name", placeholder='E.g. Mayur Kavathekar')

            st.subheader('Optional : Voice Enrollement')
            st.info("Enroll your for voice only attendance")

            audio_data = None

            try:
                audio_data = st.audio_input('Record a short phrase like I am present, My name is Mayur')
            except Exception:
                st.error('Audio Data failed!')

            if st.button('Create Account', type='primary'):
                if new_name:
                    with st.spinner('Creating Profile..'):
                        img = np.array(Image.open(photo_source))
                        encodings= get_face_embeddings(img)
                        if encodings:
                            face_emb = encodings[0].tolist()

                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embedding(audio_data.read())

                            response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)

                            if response_data:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = response_data[0]
                                st.toast(f"Profile Created! Hi {new_name}!")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error('Couldnt capture your facial features for registration')
                else:
                    st.warning('Please enter your name!')                                
    

  
                 



    footer_dashboard()