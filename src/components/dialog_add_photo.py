from PIL import Image

import streamlit as st

import time


@st.dialog("capture or upload photos")
def add_photos_dialog():

    st.write('Add Classroom Photos to scan for attendance. ')

    if 'photo_tab' not in st.session_state:
        st.session_state.photo_tab = 'camera'

    if "upload_key" not in st.session_state:
        st.session_state.upload_key = 0

    if "camera_key" not in st.session_state:
        st.session_state.camera_key = 0

    t1,t2 = st.columns(2)
    with t1:
        type_camera = "primary" if st.session_state.photo_tab == 'camera' else 'tertiary'
        if st.button('Camera',type=type_camera,width='stretch',icon=':material/camera:'):
            st.session_state.photo_tab = 'camera'

    with t2:
        type_upload = "primary" if st.session_state.photo_tab == 'upload' else 'tertiary'
        if st.button('Upload',type=type_upload,width='stretch',icon=':material/file_upload:'):
            st.session_state.photo_tab = 'upload'

    if st.session_state.photo_tab == 'camera':
        cam_photo = st.camera_input('Take Snapshot' , key = f'dialog_cam_{st.session_state.camera_key}')
        if cam_photo:
            st.session_state.attendance_images.append(Image.open(cam_photo))
            st.session_state.camera_key += 1
            st.success('Photo Captured!')
            time.sleep(1)
            

    if st.session_state.photo_tab == 'upload':
        uploaded_files = st.file_uploader(
            'Choose Image Files',
            type=['png','jpg','jpeg'],
            accept_multiple_files=True,
            key=f'dialog_upload_{st.session_state.upload_key}'
        )

        if uploaded_files:
            for f in uploaded_files:
                st.session_state.attendance_images.append(Image.open(f))
            st.session_state.upload_key += 1
            st.success('Photo uploaded successfully!')
            time.sleep(1)
            

    st.divider()
    if st.button('Done', type='primary', width='stretch'):
        st.rerun()