"""
Token Generation Script
Generate and store ZET API token in .env file
"""

import os
import sys
from dotenv import load_dotenv, set_key
from credit_card_agent.zet_api import ZETAPIClient

def generate_and_store_token():
    """Generate ZET API token and store in .env file"""
    
    # Load existing .env file
    load_dotenv()
    
    # Get API key and phone number from environment
    api_key = os.getenv("ZET_API_KEY")
    phone_number = os.getenv("ZET_PHONE_NUMBER")
    
    if not api_key:
        print("❌ ZET_API_KEY not found in .env file")
        print("Please set ZET_API_KEY in your .env file")
        return False
    
    if not phone_number:
        print("❌ ZET_PHONE_NUMBER not found in .env file")
        print("Please set ZET_PHONE_NUMBER in your .env file")
        return False
    
    print(f"🔑 Generating token for phone number: {phone_number}")
    
    try:
        # Initialize ZET client
        client = ZETAPIClient(api_key)
        
        # Generate token
        result = client.generate_token(phone_number)
        print(result)
        
        if result["success"]:
            token = result["token"]
            refresh_token = result["refresh_token"]
            expiry_date = result["expiry_date"]
            
            # Store token in .env file
            env_file = ".env"
            set_key(env_file, "ZET_ACCESS_TOKEN", token)
            set_key(env_file, "ZET_REFRESH_TOKEN", refresh_token)
            set_key(env_file, "ZET_TOKEN_EXPIRY", expiry_date)
            
            print("✅ Token generated and stored successfully!")
            print(f"   Access Token: {token[:20]}...")
            print(f"   Refresh Token: {refresh_token[:20]}...")
            print(f"   Expiry Date: {expiry_date}")
            
            return True
        else:
            print(f"❌ Token generation failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Error generating token: {str(e)}")
        return False

def refresh_token():
    """Refresh the stored ZET API token"""
    
    # Load existing .env file
    load_dotenv()
    
    # Get stored tokens
    access_token = os.getenv("ZET_ACCESS_TOKEN")
    refresh_token = os.getenv("ZET_REFRESH_TOKEN")
    
    if not access_token or not refresh_token:
        print("❌ No stored tokens found. Please run generate_token.py first")
        return False
    
    print("🔄 Refreshing token...")
    
    try:
        # Initialize ZET client with stored token
        client = ZETAPIClient(os.getenv("ZET_API_KEY"))
        client.token = access_token
        client.refresh_token = refresh_token
        
        # Refresh token
        result = client.refresh_access_token()
        
        if result["success"]:
            new_token = result["token"]
            new_refresh_token = result["refresh_token"]
            new_expiry = result["expiry_date"]
            
            # Update .env file with new tokens
            env_file = ".env"
            set_key(env_file, "ZET_ACCESS_TOKEN", new_token)
            set_key(env_file, "ZET_REFRESH_TOKEN", new_refresh_token)
            set_key(env_file, "ZET_TOKEN_EXPIRY", new_expiry)
            
            print("✅ Token refreshed successfully!")
            print(f"   New Access Token: {new_token[:20]}...")
            print(f"   New Refresh Token: {new_refresh_token[:20]}...")
            print(f"   New Expiry Date: {new_expiry}")
            
            return True
        else:
            print(f"❌ Token refresh failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Error refreshing token: {str(e)}")
        return False

def main():
    """Main function"""
    print("🔑 ZET API Token Management")
    print("=" * 30)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "refresh":
            refresh_token()
        elif sys.argv[1] == "generate":
            generate_and_store_token()
        else:
            print("Usage: python generate_token.py [generate|refresh]")
    else:
        # Default: generate token
        generate_and_store_token()

if __name__ == "__main__":
    main()
