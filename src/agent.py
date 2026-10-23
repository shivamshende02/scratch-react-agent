# src/agent.py

import os
import re
from dotenv import load_dotenv
from mistralai import Mistral
from src.prompt import HOTPOTQA_REACT_PROMPT
from src.tools import execute_tool

load_dotenv()

class ReActAgent:
    def __init__(self, model_name="mistral-large-latest"):
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables. Please check your .env file.")
        
        # Initialize the official Mistral client
        self.client = Mistral(api_key=api_key)
        self.model_name = model_name

    def run(self, question: str, max_steps: int = 6):
        # Format the prompt template with the user's question
        prompt = HOTPOTQA_REACT_PROMPT.format(user_question=question)
        conversation_history = prompt
        
        print(f"\n==========================================")
        print(f"Running ReAct Agent on Question: '{question}'")
        print(f"==========================================\n")

        for step in range(1, max_steps + 1):
            print(f"--- Step {step} ---")
            
            # Call Mistral AI API
            response = self.client.chat.complete(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": conversation_history}
                ],
                temperature=0.0,
                max_tokens=300,
                stop=["Observation:"]  # Instruct model to pause so we can supply the live tool observation
            )
            
            model_output = response.choices[0].message.content.strip()
            print(model_output)
            
            # Append the model's generated text to history
            conversation_history += "\n" + model_output
            
            # Parse the Action format using Regular Expressions (e.g., search[entity] or finish[answer])
            action_match = re.search(r"Action:\s*([a-zA-Z]+)\[(.*?)\]", model_output)
            
            if not action_match:
                # Fallback parser if brackets are unstructured
                action_match = re.search(r"Action:\s*(.+)", model_output)
                if not action_match:
                    print("\n[Error] Could not parse action from model output. Stopping loop.")
                    break
                action_line = action_match.group(1).strip()
                if "[" in action_line and action_line.endswith("]"):
                    parts = action_line.split("[", 1)
                    action_name = parts[0].strip()
                    action_arg = parts[1][:-1].strip()
                else:
                    print(f"\n[Error] Malformed action format: {action_line}")
                    break
            else:
                action_name = action_match.group(1).strip()
                action_arg = action_match.group(2).strip()

            print(f"\n[Execution] Dispatching Tool -> Name: '{action_name}', Argument: '{action_arg}'")
            
            # Execute the tool via our tools.py dispatcher
            observation = execute_tool(action_name, action_arg)
            print(f"Observation: {observation}\n")
            
            # Check if the agent successfully finished the task
            if action_name.lower() == "finish":
                print(f"==========================================")
                print(f"Task Completed Successfully!")
                print(f"Final Answer: {action_arg}")
                print(f"==========================================")
                return action_arg

            # Append observation to conversation history for the next turn
            obs_string = f"\nObservation: {observation}"
            conversation_history += obs_string
            
        print("\n[Warning] ReAct agent reached maximum steps without finishing.")
        return None

if __name__ == "__main__":
    # Test execution using a standard multi-hop question
    sample_question = "Which magazine was started first Arthur's Magazine or First for Women?"
    
    agent = ReActAgent()
    agent.run(sample_question)