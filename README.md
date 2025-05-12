# MyFitMantra - AI Workout Plan Generator



<p align="center">
  <strong>Generate personalized 12-session workout plans tailored to your fitness goals, experience level, and available equipment!</strong>
</p>

<p align="center">
  <a href="YOUR_DEPLOYMENT_LINK_HERE">
    <img src="https://img.shields.io/badge/Live_Demo-Visit_Now-brightgreen?style=for-the-badge&logo=rocket" alt="Live Demo"/>
  </a>
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python" alt="Python Version"/>
  <img src="https://img.shields.io/badge/FastAPI-0.70%2B-green?style=for-the-badge&logo=fastapi" alt="FastAPI Version"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License: MIT"/>
</p>

---

## 📋 Table of Contents
- [✨ Features](#-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [📸 Screenshots](#-screenshots)
- [🧠 How It Works](#-how-it-works)
- [📥 Installation](#-installation)
- [⚙️ Usage](#️-usage)
- [📚 API Documentation](#-api-documentation)

---

## ✨ Features
MyFitMantra empowers you to achieve your fitness aspirations with intelligent workout planning:

-   **Personalized Plans:** Generates a structured 12-session (4-week) workout program.
-   **Adaptive Experience Levels:** Caters to both **Beginner** and **Intermediate** fitness levels.
-   **Equipment Flexible:** Works with the equipment you have:
    -   Dumbbells
    -   Bench
    -   Resistance Bands
    -   Barbell
    -   Bodyweight (implied if no equipment selected)
-   **Multiple Fitness Goals:** Supports a variety of objectives:
    -   Strength Training
    -   Muscle Gain
    -   Fat Loss
    -   Endurance
-   **User-Friendly Interface:** Clean, interactive web interface for easy plan generation.
-   **Balanced Splits:** Creates logical workout splits (e.g., Push/Pull/Legs, Full Body) based on selected days per week.
-   **Progressive Overload (Implied):** Designed to help you progress over the 4-week cycle.
-   **Comprehensive Sessions:** Each session includes:
    -   Warm-up exercises
    -   Main workout sets & reps
    -   Cool-down suggestions

---

## 🛠️ Tech Stack
This project leverages a modern and efficient technology stack:

| Component         | Technology                                      |
|-------------------|-------------------------------------------------|
| **Backend**       | Python 3.8+ with FastAPI                       |
| **Frontend**      | HTML5, CSS3, JavaScript (Vanilla)               |
| **Exercise Data** | JSON file (for easy updates & management)       |
| **API Server**    | Uvicorn (ASGI server)                           |
| **Development**   | Virtual Environment (`venv`)                    |

---


## 📸 Screenshots

<div align="center">
  <table>
    <tr>
      <td align="center">
        <strong>User Input Form</strong><br/>
        <img src="https://res.cloudinary.com/dpgmbfxsz/image/upload/v1747033711/MyFitMantra-Your-Personal-Workout-Journey_oodep4.png" alt="MyFitMantra Form Input" width="400"/>
      </td>
      <td align="center">
        <strong>Generated Workout Plan</strong><br/>
        <img src="https://res.cloudinary.com/dpgmbfxsz/image/upload/v1747033625/MyFitMantra-Your-Personal-Workout-Journey_1_fntcdl.png" alt="MyFitMantra Generated Plan" width="400"/>
      </td>
    </tr>
  </table>
</div>

---

## 🧠 How It Works

MyFitMantra follows a straightforward process to create your custom workout plan:

1.  **User Input:** You submit your preferences (experience, equipment, days/week, goal) via the intuitive web form.
2.  **Exercise Filtering:** The system intelligently filters its comprehensive exercise database based on:
    *   Your available equipment.
    *   Your declared experience level (ensuring appropriate exercise complexity).
    *   Your selected fitness goal (influencing exercise selection, rep ranges, and volume).
3.  **Workout Split Creation:** Based on the `days_per_week`, a balanced workout split is determined (e.g., 3 days might be Push/Pull/Legs, while 2 days might be Full Body A/B).
4.  **Progressive Plan Generation:** A 4-week plan (totaling 12 sessions if 3 days/week) is generated. Progression might be implicitly built-in through exercise variety or suggested intensity.
5.  **Structured Output:** The system returns a well-structured workout plan for each session, including:
    *   Specific **Warm-up** exercises and durations.
    *   The **Main Workout** with exercises, sets, and reps.
    *   Suggested **Cool-down** activities.

---

## 📥 Installation

Get MyFitMantra running on your local machine with these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/srikishore5727/Workout_Plan_Generator.git
    cd Workout_Plan_Generator
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    ```
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## ⚙️ Usage

Once the installation is complete, you can start the application:

1.  **Start the Uvicorn server:**
    ```bash
    uvicorn main:app --reload
    ```
    The `--reload` flag enables auto-reloading when code changes, which is useful for development.

2.  **Access the web interface:**
    Open your web browser and navigate to:
    [http://localhost:8000](http://localhost:8000)

3.  **Generate your plan:**
    Fill out the form with your preferences and click "Generate Plan"!

---

## 📚 API Documentation

MyFitMantra exposes a RESTful API for generating workout plans.

### Endpoint: Generate Workout Plan

-   **URL:** `/generate_workout_plan`
-   **Method:** `POST`
-   **Description:** Accepts user preferences and returns a 12-session workout plan.

#### Request Body (JSON):
```json
{
  "experience": "intermediate",
  "equipment": ["dumbbells", "bench"],
  "days_per_week": 3,
  "goal": "muscle_gain"
}
```

## Parameters:

- experience (string): User's experience level.
    - Allowed values: "beginner", "intermediate"
- equipment (array of strings): List of available equipment.
    - Allowed values: "dumbbells", "bench", "bands", "barbell"
- days_per_week (integer): Number of workout days per week.
    - Allowed values: 2, 3, 4, 5 (Adjust if your app supports different ranges)
- goal (string): User's fitness goal.
    - Allowed values: "strength_training", "muscle_gain", "fat_loss", "endurance"

## Sample Success Response (200 OK):

```bash
{
  "workout_plan": [
    {
      "session": 1,
      "focus": "Push Day",
      "sections": {
        "warmup": [
          {"name": "Arm Circles", "duration": "30-60 seconds per direction"},
          {"name": "Dynamic Chest Stretch", "duration": "30-60 seconds"}
        ],
        "main": [
          {"name": "Dumbbell Bench Press", "sets": 3, "reps": "8-12"},
          {"name": "Dumbbell Shoulder Press", "sets": 3, "reps": "8-12"},
          {"name": "Tricep Pushdowns (Bands)", "sets": 3, "reps": "10-15"}
        ],
        "cooldown": [
          {"name": "Static Chest Stretch", "duration": "30 seconds"},
          {"name": "Triceps Stretch", "duration": "30 seconds per arm"}
        ]
      }
    },
    // ... other sessions
  ]
}
```
### Project Link: https://github.com/srikishore5727/Workout_Plan_Generator
<p align="center">
<em>Made with ❤️ and Python</em>
</p>
