from raw_functions import *
from status_display import *
from openai import OpenAI
import streamlit as st

def app():
    initialize_session_state()

    # unchangable layout
    with st.sidebar:
        st.title(":grey[Multilingual Education Through AI and OCR]")
        st.caption('''
                    "Unlocking Global Learning: Empowering Minds with Multilingual AI and OCR"
                    ''')
        st.image("image.jpg")
        btn_next = st.button("⏩️ Next Module")
        st.caption(''' **This button is available after your successfully generate the outline begins.**''')

        
    st.title("Multilingual Education Through AI and OCR")
    st.subheader("Breaking Language Barriers, Building Bright Futures")
    st.markdown("""
                <style>
                    .footer {
                        position: fixed;
                        bottom: 0;
                        right: 10px;
                        width: auto;
                        background-color: transparent;
                        text-align: right;
                        padding-right: 10px;
                        padding-bottom: 10px;
                    }
                </style>
                <div class="footer">@2024~BVUCOEP</div>
                """, unsafe_allow_html=True)

    # display main page and initialize settings from it
    settings = display_main_page(ss.main_page_displayed)
    if settings is not None:
        (
            api_key, 
            use_35, 
            added_files, 
            num_lessons, 
            custom_options, 
            learning_intention,
            Hindi, 
            btn_start
        ) = settings
    else:
        api_key = use_35 = added_files = num_lessons = custom_options = learning_intention = Hindi = btn_start = None
    
    # If user encounter a blank screen, this will be the only info left on the main page.
    helpful_info = st.empty()
    helpful_info.caption('''
                :blue[**Interactive learning process**]: 
                - Whenever you feel to continue (or encounter any error), please touch "**Next lesson**" button on sidebar. 
                - You will never be left behind. 🙌 
               ''')

    # display chat input box
    user_question = display_chatInput_box(ss.chatInput_displayed)

    # Create learning page object
    learning_page = st.empty()

    # must divide btn_start and btn_next
    if btn_start:
        if api_key !="" and api_key.startswith("sk-") and len(api_key) == 51 and added_files:
            if ss.start_learning == 0:
                ss.main_page_displayed = False
                ss.chatInput_displayed = True
                helpful_info.empty()
                ss.start_learning = 1
                ss.num_lessons = num_lessons
                ss.style_options = add_prompt_course_style(custom_options)
                if ss["OPENAI_API_KEY"] == '':
                    ss["OPENAI_API_KEY"] = api_key
                if learning_intention:
                    ss.learning_intention = learning_intention
                if Hindi:
                    ss.language = "Hindi"
                if use_35:
                    ss["openai_model"] = 'gpt-3.5-turbo'
                ss.client = OpenAI(api_key = ss["OPENAI_API_KEY"])

                learning_page.empty()
                with learning_page.container():
                    st.success("✅ API Key stored successfully!")
                    ss.temp_file_paths = initialize_file(added_files)
                    ss.chroma_collection = initialize_vdb(ss.temp_file_paths)
                    ss.course_outline_list = initialize_outline(
                        ss.client, 
                        ss.temp_file_paths, 
                        ss.learning_intention,
                        num_lessons, 
                        ss.language, 
                        ss["openai_model"]
                    )
                    st.caption('''
                        :blue[**Now, please touch "Next lesson" button in the sidebar**]: 
                         
                    ''')
                    
            elif ss.start_learning == 1:
                display_warning_started()
        elif len(ss["OPENAI_API_KEY"]) != 51 and added_files:
            # here, need to clear the screen
            display_warning_api_key()
        elif not added_files:
            # here, need to clear the screen
            display_warning_upload_materials()
    
    if btn_next:
        if ss.num_lessons == 0:
            display_warning_not_started()
        else:
            helpful_info.empty() #here don't use ss. Valid.
            learning_page.empty()
            with learning_page.container():
                col1, col2 = st.columns([0.6,0.4])
                with col1:
                    if ss.course_content_list == []:
                        regenerate_outline(ss.course_outline_list)
                        ss.lesson_counter = 1
                        generating_warning = st.empty()
                        generating_warning.caption(
                            '''
                            - Please DO NOT touch "**Next lesson**" button while generating to avoid failure.
                            - :blue[Lesson script generating. Check out below!]
                            '''
                        )
                        new_lesson = visualize_new_content(
                            ss.client, 
                            ss.lesson_counter, 
                            ss.course_outline_list[ss.lesson_counter-1], 
                            ss.chroma_collection, 
                            ss.language, 
                            ss.style_options, 
                            ss.ts_suggestions,
                            ss["openai_model"]
                        )
                        ss.course_content_list.append(new_lesson)
                        generating_warning.empty()
                        
                    elif ss.lesson_counter < ss.num_lessons:
                        regenerate_outline(ss.course_outline_list)
                        regenerate_content(ss.course_content_list)
                        ss.lesson_counter += 1
                        new_lesson = visualize_new_content(
                            ss.client,
                            ss.lesson_counter,
                            ss.course_outline_list[ss.lesson_counter-1],
                            ss.chroma_collection, 
                            ss.language, 
                            ss.style_options, 
                            ss.ts_suggestions,
                            ss["openai_model"]
                        )
                        ss.course_content_list.append(new_lesson)
                            
                    elif ss.lesson_counter >= ss.num_lessons:
                        display_current_status_col1()
                        
                        course_md = convert_markdown_string(ss.course_outline_list,ss.course_content_list)
                        st.download_button(
                            label="Download Course Script",
                            data=course_md,
                            file_name='file1.md',
                        )
                with col2:
                    display_current_status_col2()

    if ss.chatInput_displayed and type(user_question) == str: # type check is to ensure the first 
        ss.main_page_displayed = False
        helpful_info.empty()

        ss.user_message_count += 1
        learning_page.empty()
        with learning_page.container():
            col1, col2 = st.columns([0.6,0.4])
            with col1:
                display_current_status_col1()
            with col2:
                st.caption(''':blue[AI Assistant]: Ask this TA any questions related to this course and get direct answers. :sunglasses:''')

                with st.chat_message("assistant"):
                    st.markdown("Hello👋, how can I help you today? 😄")

                # Display chat messages from history on app rerun
                for message in ss.messages_ui:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                

                ss.messages_ui.append({"role": "user", "content": user_question})
                # Display new user question.
                with st.chat_message("user"):
                    st.markdown(user_question)

                retrieved_chunks_for_user = searchVDB(user_question, ss.chroma_collection)[0]
                prompt = decorate_user_question(user_question, retrieved_chunks_for_user)
                ss.messages.append({"role": "user", "content": prompt})

                # Display assistant response in chat message container
                with st.chat_message("assistant"):
                    full_response = get_visualize_stream_completion_from_messages(
                        ss.client,
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages #用chatbot那边的隐藏消息记录
                        ],
                        model=ss["openai_model"]
                    )
                ss.messages.append({"role": "assistant", "content": full_response})
                ss.messages_ui.append({"role": "assistant", "content": full_response})

    if (ss.user_message_count >= 2) and (ss.user_message_count % 2 == 0) and (ss.messages_ui[-2]["role"] == "user"): # this last expression is significant
        supervisor_suggestion = teaching_supervision(
            ss.course_outline_list,
            [item["content"] for item in ss.messages_ui if item["role"] == "user"],
            ss.client,
            ss["openai_model"]
        )

        ss.ts_suggestions = add_prompt_ts_suggestions(
            supervisor_suggestion['student_level'], 
            supervisor_suggestion['student_interested'],
            supervisor_suggestion['script_revise_suggestions']
        )

        #update the UI
        learning_page.empty()
        with learning_page.container():
            col1, col2 = st.columns([0.6,0.4])
            with col1:
                display_current_status_col1()
            with col2:
                ss.messages_ui.append({"role": "assistant", "content": decorate_suggested_questions_supervisor(ss.language, supervisor_suggestion['suggest_question'])})
                display_current_status_col2()

if __name__ == "__main__":
    app()

    