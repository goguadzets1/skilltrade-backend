from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import skills, rate, match, profiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://skilltrade-frontend-five.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(skills.router)
app.include_router(rate.router)
app.include_router(match.router)
app.include_router(profiles.router)
