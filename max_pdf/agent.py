from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import StructuredTool
from langchain_core.prompts import ChatPromptTemplate
from max_pdf import config, tools


def get_llm():
    api_key = config.get_api_key()
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=api_key,
        temperature=0
    )

# tools

defined_tools = [
    StructuredTool.from_function(
        func=tools.get_pdf_info,
        name="get_pdf_info",
        description="Get metadata about a PDF (page, count, encryption). ALWAYS call this first if you need to calculate page ranges (like 'last 3 pages')"
    ),
    StructuredTool.from_function(
        func=tools.list_pdf_files,
        name="list_pdf_files",
        description="List PDF files in the current directory"
    ),
    StructuredTool.from_function(
        func=tools.rotate_pages,
        name="rotate_pages",
        description="Rotate pages in a PDF. Arguments: filepath, output_path, pages (e.g. '1' or '1-3'), angle (90, 180, -90)."
    ),
    StructuredTool.from_function(
        func=tools.remove_pages,
        name="remove_pages",
        description="Remove pages from a PDF. Arguments: filepath, output_path, pages (e.g. '1,3' or '5-10')",
    ),
    StructuredTool.from_function(
        func=tools.merge_pdfs,
        name="merge_pdfs",
        description="Merge multiple PDFs into one. Arguments: output_path, input_paths (list of strings)."
    ),
]

def get_agent_executor():
    llm = get_llm()
    
    # system prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are Max, an expert PDF CLI tool. "
         "Your goal is to do precise PDF manipulations. "
         "\nRULES:"
         "\n1. If the user asks for 'last N pages', YOU MUST call get_pdf_info first to find the total pages."
         "\n2. Always outpout the result of your actions to the user succinctly."
         "\n3. If an error occers, explain it cleary."
         ),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(llm, tools=defined_tools, prompt=prompt)
    return AgentExecutor(agent=agent, tools=defined_tools, verbose=True)


def run_max(user_query: str):
    # Entry point for CLI
    
    try:
        agent_executor = get_agent_executor()
        result = agent_executor.invoke({"input": user_query})
        return result["output"]
    
    except Exception as e:
        return f"Max crashed: {str(e)}"
    