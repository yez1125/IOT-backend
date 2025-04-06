import argparse
import os
from dotenv import load_dotenv
import uvicorn

#設定指令
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run the server in different modes.")
    parser.add_argument("--prod",action="store_true", help="Run the server in production mode.")
    parser.add_argument("--dev",action="store_true", help="Run the server in development mode.")
    
    args = parser.parse_args()
    
    if args.prod:
        load_dotenv("setting/.env.prod")
    else:
        load_dotenv("setting/.env.dev")
    
    uvicorn.run("server:app", host="127.0.0.1" , port=int(os.getenv("PORT")) , reload=True )