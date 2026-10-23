import requests

class WikiEnvironmentState:
    def __init__(self):
        self.current_text = ""

wiki_state = WikiEnvironmentState()

def wikipedia_search(entity:str)->str:
    """
    Perform a Wikipedia search for the given query and return the summary of the first result.
    """
    url = f"https://en.wikipedia.org/api.php"
    headers = {
        "User-Agent": "ScratchReactAgent/1.0 (Educational Project)"

    }

    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "exintro": True,
        "explaintext": True,
        "exsentences": 5,
        "titles": entity
    }

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()

        pages = data.get("query",{}).get("pages",{})
        for page_id, page_info in pages.items():
            if page_id != "-1" and "extract" in page_info:  # Check if the page exists
                extract = page_info["extract"]
                wiki_state.current_text = extract
                return extract

        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": entity,
            "srlimit": 5
        }    

        search_resp = requests.get(url, headers=headers, params=search_params)
        search_data = search_resp.json()
        search_results = search_data.get("query", {}).get("search", [])

        if search_results:
            titles = [r["title"] for r in search_results]
            return f"No direct page found. Here are some related titles: {', '.join(titles)}"
        return "No results found for the given query."

def wikipedia_lookup(search_string:str)->str:
    """
    Perform a Wikipedia lookup for the given query and return the summary of the first result.
    """
    if not wiki_state.current_text:
        return "No previous search found. Please perform a search first."

    sentences = wiki_state.current_text.split('. ')
    for sentence in sentences:
        if search_string.lower() in sentence.lower():
            return f"Found in previous search: {sentence.strip()}."

    return f"No relevant information found in the previous search for '{search_string}'."

def execute_tool(action_name: str, action_arg:str) -> str:
    """
    Execute the specified tool action based on the action name and argument.
    """
    if action_name == "search":
        return wikipedia_search(action_arg)
    elif action_name == "lookup":
        return wikipedia_lookup(action_arg)
    elif action_name == "finish":
        return "Finish action executed."
    else:
        return f"Unknown action: {action_name}"    