import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase
from PIL import Image
import time


from src.database.db import create_attendance

def show_attendance_result(df, logs):
    st.write("Please review attendance before confirming.")

    if "review_attendance_logs" not in st.session_state:
        st.session_state.review_attendance_logs = [
            log.copy() for log in logs
        ]

    updated_logs = st.session_state.review_attendance_logs

    for i, row in df.iterrows():

        student_id = int(row["ID"])
        student_name = row["Name"]

        # Find this student's attendance log
        log = next(
            (
                item for item in updated_logs
                if int(item["student_id"]) == student_id
            ),
            None
        )

        if log is None:
            continue

        # AI detected status comes from the ORIGINAL result
        # Do not use log["is_present"] here because it can be
        # changed manually by the teacher.

        ai_detected = row["Status"] == "✅ Present"

        # AI detected
        if ai_detected:

            st.checkbox(
                f"✅ {student_name} — Present (AI Detected)",
                value=True,
                disabled=True,
                key=f"ai_present_{student_id}"
            )

        # AI did NOT detect
        else:

            manually_present = st.checkbox(
                f"⚠️ {student_name} — Mark Present Manually",
                value=bool(log["is_present"]),
                key=f"manual_present_{student_id}"
            )

            log["is_present"] = manually_present

    st.divider()

    # --------------------------------------------------
    # FINAL PREVIEW
    # --------------------------------------------------

    # --------------------------------------------------
    # FINAL PREVIEW
    # --------------------------------------------------

    st.subheader("Final Attendance")

    preview = df.copy()

    for i, row in preview.iterrows():

        student_id = int(row["ID"])

        log = next(
            (
                item for item in updated_logs
                if int(item["student_id"]) == student_id
            ),
            None
        )

        if log:
            is_present = bool(log["is_present"])

            preview.at[i, "Status"] = (
                "✅ Present"
                if is_present
                else "❌ Absent"
            )

            # Source
            if row["Status"] == "✅ Present":
                preview["Source"] = preview["Source"].astype("object")
                preview.at[i, "Source"] = "🤖 AI"
            elif is_present:
                preview.at[i, "Source"] = "👨‍🏫 Manual"
            else:
                preview.at[i, "Source"] = "—"

    st.dataframe(
        preview,
        hide_index=True,
        width="stretch"
    )
    # --------------------------------------------------
    # BUTTONS
    # --------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Discard",
            width="stretch"
        ):
            st.session_state.pop(
                "review_attendance_logs",
                None
            )
            st.rerun()

    with col2:
        if st.button(
            "Confirm & Save",
            width="stretch",
            type="primary"
        ):
            try:

                create_attendance(updated_logs)

                st.toast("Attendance taken!")

                st.session_state.attendance_images = []
                st.session_state.voice_attendance_results = None

                st.session_state.pop(
                    "review_attendance_logs",
                    None
                )

                st.rerun()

            except Exception as e:
                st.error("Sync failed!")
                st.exception(e)

@st.dialog("Attendance Reports")
def attendance_result_dialog(df,logs):
    show_attendance_result(df,logs)

   
    
                     