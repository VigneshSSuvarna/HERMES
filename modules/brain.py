import os
import sys
import google.generativeai as genai

class HermesBrain:
    def __init__(self):
        # 💡 Extracting the key from your Windows environment variables safely
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            print("\n[Error]: GEMINI_API_KEY environment variable is missing!")
            print("Please restart VS Code or check your Windows environment variables.")
            sys.exit(1)
            
        # Configure the Google AI engine connection
        genai.configure(api_key=api_key)
        
       # We use gemini-2.5-flash as it is optimized for rapid, real-time desktop execution
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Give HERMES his identity blueprint restrictions
        self.system_prompt = (
            "You are HERMES, a highly advanced, crisp, and fiercely loyal desktop AI assistant. "
            "You address your creator with supreme professional respect ('Sir'). "
            "Keep your verbal responses incredibly concise, sharp, and executive. Avoid fluffy text."
        )

    def think(self, user_text):
        """Pipes text inputs straight to the core neural layer and extracts responses."""
        try:
            full_prompt = f"{self.system_prompt}\n\nUser: {user_text}\nHERMES:"
            response = self.model.generate_content(full_prompt)
            return response.text.strip()
            
        except Exception as e:
            return f"[Cognition Error]: Core matrix connection disrupted. Details: {e}"

if __name__ == "__main__":
    # Diagnostic module test block
    brain = HermesBrain()
    test_query = "Hello Hermes, report system status."
    print(f"\n[Testing Brain Input]: {test_query}")
    print(f"[HERMES Response]: {brain.think(test_query)}\n")