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
    StructuredTool.from_function(
        func=tools.decrypt_pdf,
        name="decrypt_pdf",
        description="Decrypt/Unlock a PDF. Args: filepath, output_path, password. If password is not provided, ASK the user."
    ),
    StructuredTool.from_function(
        func=tools.ask_human,
        name="ask_human",
        description="Ask the user for clarification or confirmation. INPUT: The question string. Use this when you need more information."
    ),
]

def get_agent_executor():
    llm = get_llm()
    
    # system prompt
    prompt = ChatPromptTemplate.from_messages([
      ("system", 
         "You are Max, an expert PDF CLI tool."
         "\n\nDEFINITION OF DONE (CRITICAL):"
         "\nYou are NOT done until you have successfully called one of the Action Tools: `merge_pdfs`, `rotate_pages`, `remove_pages`, or `get_pdf_info`."
         "\n- asking the user a question is NOT being done. You must wait for the answer and KEEP GOING."
         "\n- Listing files is NOT being done."
         "\n\nRULES:"
         "\n1. **Step-by-Step:** If you need 2 things (files and output name), ask for the first, wait for answer, THEN ask for the second."
         "\n2. **No Text Questions:** ALWAYS use `ask_human` tool to ask questions."
         "\n3. **Ambiguity:** If a parameter is missing, ASK. Do not guess."
         "\n\nEXAMPLES:"
         "\nUser: 'Merge these files'"
         "\nMax: [ask_human('Which files?')]"
         "\nUser: 'A and B'"
         "\nMax: (Still missing output path) -> [ask_human('What output name?')]"
         "\nUser: 'result'"
         "\nMax: [merge_pdfs(output_path='result', input_paths=['A','B'])]"
         "\nMax: 'Done.'"
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
    