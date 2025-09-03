import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from rag_agent.graph.graph import app

# Load environment variables first

# Configure the page
st.set_page_config(
    page_title="LangGraph Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🤖 LangGraph Chatbot")


# Generate and display the graph visualization
@st.cache_data
def generate_graph_image():
    """Generate the graph visualization once and cache it"""
    try:
        app.get_graph().draw_mermaid_png(output_file_path="graph.png")
        return True
    except Exception as e:
        st.error(f"Error generating graph: {e}")
        return False


# Sidebar with graph visualization
with st.sidebar:
    st.header("Workflow Visualization")
    if generate_graph_image():
        st.image("graph.png", caption="LangGraph Workflow", use_column_width=True)

    st.divider()

    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if user_input := st.chat_input("Ask me anything..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)


    # Display assistant response with streaming
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            # Stream the response
            for partial_response in app.stream(
                    input={"question": user_input},
                    stream_mode="messages"
            ):
                if partial_response[0].content:
                    full_response += partial_response[0].content
                    # Update the placeholder with accumulated response
                    response_placeholder.markdown(full_response + "▌")

            # Final response without cursor
            response_placeholder.markdown(full_response)

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Error generating response: {e}")
