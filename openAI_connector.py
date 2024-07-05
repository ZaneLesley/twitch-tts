from openai import OpenAI
import tiktoken
from dotenv import load_dotenv
from rich import print 
import os

"""
Most of this code can be found from the github link https://github.com/DougDougGithub/Babagaboosh/blob/main/openai_chat.py, I did small changes to variables and such, but for right now
that is all credit to DougDoug.
"""
def num_tokens_from_messages(messages, model='gpt-4'):
  """Returns the number of tokens used by a list of messages.
  Copied with minor changes from: https://platform.openai.com/docs/guides/chat/managing-tokens"""
  try:
      encoding = tiktoken.encoding_for_model(model)
      num_tokens = 0
      for message in messages:
          num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
          for key, value in message.items():
              num_tokens += len(encoding.encode(value))
              if key == "name":  # if there's a name, the role is omitted
                  num_tokens += -1  # role is always required and always 1 token
      num_tokens += 2  # every reply is primed with <im_start>assistant
      return num_tokens
  except Exception:
      raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
      #See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
  
class OpenAiManager():
    def __init__(self):
        self.chat_history = []
        load_dotenv()
        try:
            self.client = OpenAI(api_key=os.getenv('OPENAI_KEY'))
        except TypeError:
            exit("No OPENAI_KEY found")

    def chat(self, prompt=""):
        if not prompt:
            print("[yellow]No Input")
            return
        
        chat_question = [{"role": "user", "content" : prompt}]
        if num_tokens_from_messages(chat_question) > 8000:
            print("[red] Number of tokens in chat message too long")
        
        print("[purple] questions being asked...")
        completion = self.client.chat.completions.create(model="gpt-4o", messages=chat_question)

        response = completion.choices[0].message.content
        print(f"[green]{response}")
        return response
    
    def chat_with_history(self, prompt=""):
        if not prompt:
            print("[purple]No Input")
            return
        
        self.chat_history.append({"role" : "user", "content" : prompt})
        print(f"[blue] Chat History has a current token length of {num_tokens_from_messages(self.chat_history)}")
        while num_tokens_from_messages(self.chat_history) > 8000:
            self.chat_history.pop(1)    # Skip System Message
            print(f"[purple] Removed first message from the chat history, new length is {num_tokens_from_messages(self.chat_history)}")
        
        print("[purple] Asking a question...")
        completion = self.client.chat.completions.create(model="gpt-4o", messages=self.chat_history)
        self.chat_history.append({"role" : completion.choices[0].message.role, "content" : completion.choices[0].message.content})

        response = completion.choices[0].message.content
        print(f"[green]{response}")
        return response


if __name__ == '__main__':
    # Tests
    openai_manager = OpenAiManager()
    # print(openai_manager.chat("What is 2 + 2?"))

    # CHAT WITH HISTORY TEST
    FIRST_SYSTEM_MESSAGE = {"role": "system", "content": "Act like you are an Angry Pirate who is the main cook for the ship, you are always angry and yelling at me "}
    openai_manager.chat_history.append(FIRST_SYSTEM_MESSAGE)

    while True:
        new_prompt = input("\nNext question? \n\n")
        openai_manager.chat_with_history(new_prompt)