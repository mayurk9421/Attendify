import streamlit as st

def main():
    st.header("this is title")
    name= st.text_input('enter your name')

    col1,col2=st.columns(2)

    with col1:
      if st.button('hie',type='primary',key='but1',width='stretch'):
         print('hi',name)

    with col2:
      if st.button('bye',type='primary',key='but2',width='stretch'):
         print('bye',name)


    st.markdown("""<div><h1>its html</h1>
       </div>""",unsafe_allow_html=True)
       

main()        