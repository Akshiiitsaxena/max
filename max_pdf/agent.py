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

def get_agent_executor(verbose=False):
    llm = get_llm()
    
    # system prompt
    prompt = ChatPromptTemplate.from_messages([
    ("system", 
         "You are Max, an expert PDF CLI tool."
         "\n\nPRIME DIRECTIVE: DEFINITION OF DONE"
         "\nYou are NOT done until a PDF modification tool (merge, rotate, remove, decrypt) returns {{'status': 'success'}}."
         "\n- Asking a question is NOT done. Wait for the answer and CONTINUE."
         "\n- Listing files is NOT done."
         "\n\nPROTOCOL 1: DEFAULTS & ASSUMPTIONS (ACT FIRST)"
         "\n- **Rotation:** If user doesn't specify pages, assume `pages='all'`. DO NOT ASK."
         "\n- **Output Filename:** If user doesn't specify an output name, create a sensible default (e.g., 'rotated_file.pdf') OR overwrite if the user implies it. (Only ask if ambiguous)."
         "\n"
         "\n🎤 PROTOCOL 2: INTERROGATION (MISSING DATA)"
         "\n- If a critical parameter is missing (e.g., input files, password), you MUST use `ask_human`."
         "\n- **Chain Rule:** If you need 2 things, ask for one, get the answer, then ask for the other. Do not stop."
         "\n- **NO TEXT:** Never output a text question. Always use the tool."
         "\n"
         "\nPROTOCOL 3: RESILIENCE (ERROR HANDLING)"
         "\n- If a tool returns 'File not found' or 'Error', DO NOT give up."
         "\n- **Immediate Action:** Call `list_files` to see what is actually in the directory."
         "\n- **Recovery:** If you see the correct file in the list, retry the command automatically. If unsure, `ask_human`."
         "\n"
         "\nPROTOCOL 4: SAFETY"
         "\n- If the user asks to DELETE pages or overwrite a file, verify the filename first if you used fuzzy matching."
         "\n"
         "\nEXAMPLES (MENTAL MODEL):"
         "\n1. **Ambiguity Loop:** User: 'Merge' -> Max: `ask_human('Which files?')` -> User: 'A and B' -> Max: `ask_human('Output name?')` -> User: 'Out' -> Max: `merge_pdfs(...)`."
         "\n2. **Lazy Rotation:** User: 'Rotate A.pdf 90' -> Max: `rotate_pages(..., pages='all')`."
         "\n3. **Password:** User: 'Unlock A.pdf' -> Max: `ask_human('Password?')` -> User: '123' -> Max: `decrypt_pdf(..., password='123')`."
         "\n4. **Recovery:** User: 'Rotate ghost' -> Tool: 'Error' -> Max: `list_files()` -> Max: 'Ah, found ghost_v2.pdf' -> Max: `ask_human('Did you mean ghost_v2?')`."
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(llm, tools=defined_tools, prompt=prompt)
    return AgentExecutor(agent=agent, tools=defined_tools, verbose=verbose)


def run_max(user_query: str, verbose= False):
    # Entry point for CLI
    
    try:
        agent_executor = get_agent_executor(verbose=verbose)
        result = agent_executor.invoke({"input": user_query})
        return result["output"]
    
    except Exception as e:
        return f"Max crashed: {str(e)}"
    