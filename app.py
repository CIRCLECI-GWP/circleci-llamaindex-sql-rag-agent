import streamlit as st
import sqlalchemy as sa
import os
from dotenv import load_dotenv

from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core import SQLDatabase, Settings
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_index.core.tools import QueryEngineTool
from llama_index.core.agent import ReActAgent

# Load environment variables and configure page
load_dotenv()

st.set_page_config(
    page_title="US States Information Center",
    page_icon="🇺🇸",
    layout="centered"
)

# Initialize components just once and cache the result
@st.cache_resource
def initialize_components():
    """Initialize LLM, databases, and query engines once"""
    
    # Initialize LLM
    llm = GoogleGenAI(
        model="models/gemini-2.5-pro-exp-03-25",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3
    )
    Settings.llm = llm
    
    # Connect to the SQL database
    engine = sa.create_engine('sqlite:///states.db', future=True)
    sql_database = SQLDatabase(engine, include_tables=["states"])

    # Generate sample data description to help the LLM understand the data structure
    table_schema_str = """
    Database Schema:
    - states table:
    - object_id: Object ID like 
    - name: State name (e.g., "California", "Texas")
    - flag_url: link to states flag png image
    - link: url link to states page
    - postal_abbreviation: Two-letter state code (e.g., "CA", "TX")
    - capital: Capital city name
    - largest_city: name of largest city
    - established: date when state was established
    - population: state's population
    - total_area_square_miles= state total area in square miles
    - total_area_square_kilometers: total area in square kilometers
    - land_area_square_miles: land area in square miles
    - land_area_square_kilometers: land area in square kilometers
    - water_area_square_miles: water area in square miles
    - water_area_square_kilometers: water area in square kilometers
    - number_representatives: number of representatives
    - created_at: date of database creation
    - updated_at: date of database update
    """

    # Create the natural language to SQL query engine with more context
    sql_query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=["states"],
        # sample_rows_in_table_info=1,
        llm=llm,
        embed_model=llm,
        synthesize_response=True,
        table_schema_str=table_schema_str,
        verbose=True
    )
    
    # Initialize LlamaCloud index
    index = LlamaCloudIndex(
        name="US-States-Wiki",
        project_name=os.getenv("LLAMA_CLOUD_PROJECT_NAME"),
        organization_id=os.getenv("LLAMA_CLOUD_ORG_ID"),
        api_key=os.getenv("LLAMA_CLOUD_API_KEY")
    )
    llama_cloud_query_engine = index.as_query_engine()
    
    return {
        "llm": llm,
        "sql_query_engine": sql_query_engine,
        "llama_cloud_query_engine": llama_cloud_query_engine
    }

# Create the agent using the cached components
@st.cache_resource
def get_agent():
    """Create and return the agent using already initialized components"""
    components = initialize_components()
    
    # Create a tool for SQL queries
    sql_tool = QueryEngineTool.from_defaults(
        query_engine=components["sql_query_engine"],
        description=(
            "Useful for answering factual questions about US states like population, "
            "capital, land size, postal abbreviation, and other demographic statistics "
            "stored in a structured database. The states table contains fields: "
            "name, abbreviation, capital, population, area_sq_miles, region, "
            "admitted_to_union, and median_household_income."
        ),
        name="sql_tool"
    )

    # Create a tool for document-based queries
    llama_cloud_tool = QueryEngineTool.from_defaults(
        query_engine=components["llama_cloud_query_engine"],
        description=(
            "Useful for answering questions about US states' history, attractions, culture, "
            "geography, and other information that requires searching through documents. "
            "This tool contains Wikipedia information about all US states."
        ),
        name="llama_cloud_tool"
    )
    
    # Create the agent
    agent = ReActAgent.from_tools(
        [sql_tool, llama_cloud_tool],
        llm=components["llm"],
        verbose=False,
        system_prompt=(
            "You are an expert US States information system. "
            "You have access to two sources of information:\n\n"
            "1. A SQLite database with factual demographic data about US states in the 'states' table "
            "containing fields: object_id, name, flag_url, link, postal_abbreviation, capital, largest_city, "
            "established, population, total_area_square_miles, total_area_square_kilometers, land_area_square_miles, "
            "land_area_square_kilometers, water_area_square_miles, "
            "water_area_square_kilometers, number_representatives, created_at, updated_at\n\n"
            "2. Document retrieval for detailed information about history, attractions, and more\n\n"
            "Choose the appropriate tool based on the user's question. "
            "For the SQL tool, formulate clear SQL queries that match the database schema. "
            "Use the SQL tool for factual queries about population, area, capitals, etc. "
            "Use the document tool for questions about history, attractions, culture, and detailed information. "
            "If needed, you can use both tools and combine the information."
        )
    )
    
    return agent

# Cached query execution to improve performance
@st.cache_data(ttl=3600, show_spinner=False)  # Cache results for 1 hour
def execute_query(query_text):
    """Execute a query and cache the results"""
    agent = get_agent()
    try:
        response = agent.query(query_text)
        return response.response
    except Exception as e:
        print(f"Error details: {str(e)}")
        return f"I encountered an error while processing your question. Please try again or rephrase your question."

# App UI
st.image("us-flag.png", width=200)
st.title("US States Information Center")
st.markdown("""
Ask me anything about US states! I can help with:
- Demographic data (population, land area, etc.)
- State capitals and largest cities
- Popular attractions and landmarks
- State history and culture
- And much more!
""")

# Initialize state if needed
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Add clear chat button
col1, col2 = st.columns([4, 1])
with col2:
    if st.button("Clear Chat", type="primary"):
        st.session_state.chat_history = []
        st.rerun()

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about any US state..."):
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Add to history
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    # Process the query with spinner
    with st.spinner("Searching for information..."):
        response = execute_query(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        st.write(response)
    
    # Add to history
    st.session_state.chat_history.append({"role": "assistant", "content": response})

# Sidebar with example questions
with st.sidebar:
    st.header("Example Questions")
    example_questions = [
        "What are popular tourist attractions in Hawaii?",
        "Which state has the largest land area?",
        "Tell me about the history of New York.",
        "Which states border Florida?"
    ]
    
    st.write("Try asking:")
    # Use enumeration to create unique keys for each button
    for i, question in enumerate(example_questions):
        if st.button(question, key=f"btn_{i}"):
            # Display user message
            with st.chat_message("user"):
                st.write(question)
            
            # Add to history
            st.session_state.chat_history.append({"role": "user", "content": question})
            
            # Process the query
            with st.spinner("Searching for information..."):
                response = execute_query(question)
            
            # Display assistant response
            with st.chat_message("assistant"):
                st.write(response)
            
            # Add to history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            # Rerun to update UI
            st.rerun()

    st.divider()
    st.caption("This app uses a combination of SQL database querying and document retrieval to provide comprehensive information about US states.")