# # app/api/deps.py
# from fastapi import Header, HTTPException

# API_KEY = "change-me"

# async def require_api_key(x_api_key: str | None = Header(default=None)):
#     if x_api_key != API_KEY:
#         raise HTTPException(status_code=401, detail="Unauthorized")
