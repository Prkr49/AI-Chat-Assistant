import pyautogui
import time
import pyperclip
from openai import OpenAI

client = OpenAI(
  api_key="<sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx>",
)

def is_last_message_from_sender(chat_log, sender_name="Prince"):
    # Split the chat log into individual messages
    messages = chat_log.strip().split("/2024] ")[-1]
    if sender_name in messages:
        return True 
    return False
    
    

    # Step 1: Click on the chrome icon at coordinates (1600, 988)
pyautogui.click(1600, 988)

time.sleep(1)  # Wait for 1 second to ensure the click is registered
while True:
    time.sleep(3)  # Wait for 3 seconds before performing the next action
    # Step 2: Drag the mouse from (1003, 237) to (2187, 1258) to select the text
    pyautogui.moveTo(972,202)
    pyautogui.dragTo(2213, 1278, duration=2.0, button='left')  # Drag for 1 second

    # Step 3: Copy the selected text to the clipboard
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(2)  # Wait for 1 second to ensure the copy command is completed
    pyautogui.click(1994, 281)

    # Step 4: Retrieve the text from the clipboard and store it in a variable
    chat_history = pyperclip.paste()

    # Print the copied text to verify
    print(chat_history)
    print(is_last_message_from_sender(chat_history))
    if is_last_message_from_sender(chat_history):
        completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a person named Prince from India who speaks Hindi and English. Reply in a funny style. Only return the next chat message."},
            {"role": "system", "content": "Do not start like this [21:02, 18/02/2025] Prince: "},
            {"role": "user", "content": chat_history}
        ]
        )

        response = completion.choices[0].message.content
        pyperclip.copy(response)

        # Step 5: Click at coordinates (1808, 1328)
        pyautogui.click(1808, 1328)
        time.sleep(1)  # Wait for 1 second to ensure the click is registered

        # Step 6: Paste the text
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1)  # Wait for 1 second to ensure the paste command is completed

        # Step 7: Press Enter
        pyautogui.press('enter')