from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse # Changed from Jinja2Templates for simplicity here
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Import the core workout generation logic
from workout_logic import generate_full_workout_plan, ALL_EXERCISES

# --- Pydantic Models (Keep these as they are) ---
class UserProfileInput(BaseModel):
    name: Optional[str] = Field("User", example="Aarav")
    age: Optional[int] = Field(None, example=35)
    gender: Optional[str] = Field(None, example="male")
    goal: Optional[str] = Field("general_fitness", example="muscle_gain")
    experience: str = Field(..., example="intermediate")
    equipment: List[str] = Field(..., example=["dumbbell", "bench", "resistance_band"])
    days_per_week: int = Field(..., gt=0, lt=8, example=3)

class ExerciseDetailOutput(BaseModel): # Ensure this matches the output from workout_logic
    name: str
    sets: Optional[int] = None
    reps: Optional[int] = None
    duration: Optional[str] = None
    rest: Optional[str] = None
    tempo: Optional[str] = None
    note: Optional[str] = None

class WorkoutSectionsOutput(BaseModel):
    warmup: List[ExerciseDetailOutput]
    main: List[ExerciseDetailOutput]
    cooldown: List[ExerciseDetailOutput]
    circuit: Optional[List[ExerciseDetailOutput]] = None

class WorkoutSessionOutput(BaseModel):
    session: int
    date: str
    focus: Optional[str] = None
    sections: WorkoutSectionsOutput

class WorkoutPlanResponse(BaseModel):
    user_profile_processed: Dict[str, Any]
    workout_plan: List[WorkoutSessionOutput]

class ErrorResponseMessage(BaseModel):
    detail: str

# --- FastAPI Application Instance ---
app = FastAPI(
    title="MyFitMantra Workout Plan Generator",
    description="API and UI to generate a 12-session progressive workout plan.",
    version="1.1.0" # Incremented version for UI addition
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS Middleware (already good)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- HTML Serving Endpoint ---
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_homepage(request: Request):
    try:
        with open("static/index.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: Main page (index.html) not found.</h1>", status_code=404)


# --- API Endpoints (Keep these as they are) ---
@app.post(
    "/generate_workout_plan",
    response_model=WorkoutPlanResponse,
    # ... (rest of the endpoint definition from previous version) ...
)
async def create_workout_plan_endpoint(user_profile: UserProfileInput = Body(...,
    examples={ # Examples for Swagger UI
        "intermediate_muscle_gain": {
            "summary": "Intermediate user for muscle gain",
            "value": {
                "name": "Aarav", "age": 35, "gender": "male", "goal": "muscle_gain",
                "experience": "intermediate", "equipment": ["dumbbell", "bench", "resistance_band"], "days_per_week": 3
            }
        },
        "beginner_bodyweight": {
            "summary": "Beginner user, bodyweight only",
            "value": {
                "name": "Priya", "age": 28, "gender": "female", "goal": "general_fitness",
                "experience": "beginner", "equipment": ["bodyweight"], "days_per_week": 3
            }
        },
         "beginner_no_equipment_specified": {
            "summary": "Beginner, no specific equipment (implies bodyweight)",
            "value": {
                 "experience": "beginner", "equipment": [], "days_per_week": 3
            }
        }
    }
)):
    if not ALL_EXERCISES:
        raise HTTPException(status_code=500, detail="Critical Error: Exercise database could not be loaded.")
    plan_input_dict = user_profile.dict(exclude_unset=True)
    if not plan_input_dict.get("equipment"):
        plan_input_dict["equipment"] = ["bodyweight", "none"]
    else:
        if "bodyweight" not in plan_input_dict["equipment"]:
            plan_input_dict["equipment"].append("bodyweight")
        if "none" not in plan_input_dict["equipment"]:
             plan_input_dict["equipment"].append("none")
    generated_plan_data = generate_full_workout_plan(plan_input_dict)
    if "error" in generated_plan_data:
        raise HTTPException(status_code=400, detail=generated_plan_data["error"])
    return generated_plan_data

@app.get("/health", summary="Health Check", tags=["Utilities"])
async def health_check():
    return {"status": "ok", "exercise_db_loaded": bool(ALL_EXERCISES), "num_exercises": len(ALL_EXERCISES)}

# To run: uvicorn main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    print("Access UI at http://127.0.0.1:8000/")
    print("Access API docs at http://127.0.0.1:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)