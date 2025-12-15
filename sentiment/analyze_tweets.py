import pandas as pd
import os
from google import genai 

# --- Configuration ---
# Update this to the actual file name you generated
FILE_PATH = 'market_tweets_2025-12-08.csv' 

TEXT_COLUMN = 'Text'    
USERNAME_COLUMN = 'Handle' 

def generate_gemini_prompt(df: pd.DataFrame) -> str:
    """
    Transforms the DataFrame of posts into a single, structured prompt string.
    """
    
    # 1. Set up the overall instruction for the Gemini model
    prompt_instructions = (
        "TASK: Analyze the sentiment and key themes from the financial/macro X posts provided below. "
        "The posts are from highly influential traders, analysts, and economists. "
        "Analyze the posts from the last week and provide a clear, structured summary with the following sections:\n\n"
        "1. **Overall Market Sentiment:** A single sentence summary (e.g., Strongly Bearish, Moderately Bullish).\n"
        "2. **Key Themes:** A bulleted list of the top 3-5 macro topics discussed (e.g., Fed Policy, VIX Skew, Recession Risk).\n"
        "3. **Account Sentiment Breakdown:** A brief, 1-2 sentence analysis for the accounts with the most polarized (extreme positive or negative) posts, citing specific examples or keywords."
        "\n\n--- POSTS FOR ANALYSIS ---\n"
    )
    
    # 2. Structure each individual post for clarity using .join()
    
    # Check for 'post_id' and 'created_at' before attempting to access them
    post_strings = []
    for _, row in df.iterrows():
        post_id = row.get('post_id', 'N/A')
        created_at = row.get('created_at', 'N/A')
        
        post_strings.append(
            f"[ACCOUNT: @{row[USERNAME_COLUMN]}] Post ID: {post_id} | Date: {created_at} | Text: \"{row[TEXT_COLUMN]}\""
        )
    
    data_block = "\n\n".join(post_strings)
    
    return prompt_instructions + data_block


def main():
    """Reads the CSV, generates the prompt, and attempts the API call."""
    
    try:
        df = pd.read_csv(FILE_PATH)
    except FileNotFoundError:
        print(f"Error: File not found at {FILE_PATH}. Please check your file name.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Check for mandatory columns
    if TEXT_COLUMN not in df.columns or USERNAME_COLUMN not in df.columns:
        print(f"Error: CSV is missing required columns ('{TEXT_COLUMN}' or '{USERNAME_COLUMN}').")
        print(f"Available columns: {df.columns.tolist()}")
        return

    # Generate the complete prompt string
    final_prompt = generate_gemini_prompt(df)

    # --- Output/API Call ---
    print("=" * 70)
    print("GENERATED GEMINI PROMPT (Ready to Copy/Paste or Send via API):")
    print("=" * 70)
    print(final_prompt)
    print("=" * 70)
    
    # Check if the API key is set in the environment
    if os.getenv("GEMINI_API_KEY"):
        try:
            # The client automatically picks up the GEMINI_API_KEY from the environment
            client = genai.Client() 
            print("\nSending request to Gemini API...")
            
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=final_prompt
            )
            
            print("\n--- GEMINI ANALYSIS RESULT ---")
            print(response.text)
            print("------------------------------")

        except Exception as e:
            print(f"\nGemini API Error: {e}")
            print("Please check your API key and ensure the 'google-genai' library is installed.")
    else:
        print("\nGEMINI_API_KEY environment variable not found. Printing prompt only.")


if __name__ == "__main__":
    main()
