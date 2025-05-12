import json
import random
from datetime import datetime, timedelta

# --- Configuration ---
EXERCISE_DB_PATH = "exercises.json"
NUM_WARMUP_EXERCISES = 2
NUM_COOLDOWN_EXERCISES = 2
# For a PPL split, we might aim for 2 exercises per primary muscle group
# e.g., Push Day: 2 chest, 2 shoulder, 1-2 triceps
NUM_MAIN_EXERCISES_PER_PRIMARY_GROUP = 2
NUM_MAIN_EXERCISES_AUXILIARY = 1


# --- Helper Functions ---
def load_exercises():
    """Loads exercises from the JSON database."""
    try:
        with open(EXERCISE_DB_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {EXERCISE_DB_PATH} not found. Please create it and populate it.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {EXERCISE_DB_PATH}. Check for syntax errors.")
        return []

ALL_EXERCISES = load_exercises()

def filter_exercises_by_profile(user_profile):
    """Filters exercises based on user's available equipment and experience level."""
    available_equipment = user_profile.get("equipment", [])
    experience_level = user_profile.get("experience", "beginner").lower()

    # User's equipment list should include 'bodyweight' and 'none' by default
    allowed_equipment = set(available_equipment + ["bodyweight", "none"])

    filtered = []
    for ex in ALL_EXERCISES:
        equip_match = ex.get("equipment", "none").lower() in allowed_equipment
        ex_level = ex.get("level", "all").lower()

        level_match = False
        if ex_level == "all":
            level_match = True
        elif ex_level == experience_level:
            level_match = True
        elif experience_level == "intermediate" and ex_level == "beginner":
            level_match = True
        # Add more advanced logic if "advanced" level exists:
        # elif experience_level == "advanced" and (ex_level == "intermediate" or ex_level == "beginner"):
        #     level_match = True

        if equip_match and level_match:
            filtered.append(ex)
    return filtered

def select_random_exercises(exercise_list, exercise_type, count):
    """Selects a specified number of unique exercises of a given type."""
    typed_exercises = [ex for ex in exercise_list if ex.get("type", "").lower() == exercise_type]
    if not typed_exercises:
        return []
    actual_count = min(count, len(typed_exercises))
    return random.sample(typed_exercises, actual_count) if actual_count > 0 else []


def format_exercise_for_plan(exercise_data, week=1, goal="muscle_gain"):
    """
    Formats a single exercise for the workout plan, applying progression.
    Handles exercises with sets/reps or duration.
    """
    formatted_ex = {"name": exercise_data["name"]}

    # Progressive overload (simple model for sets/reps based exercises)
    # For duration based, progression might mean longer duration or more sets.
    current_sets = exercise_data.get("default_sets")
    current_reps = exercise_data.get("default_reps")
    current_duration = exercise_data.get("default_duration")

    if exercise_data["type"] == "main": # Apply progression primarily to main exercises
        # Progression for rep-based exercises
        if current_reps is not None:
            base_reps = exercise_data.get("default_reps", 8) # Default to 8 if not specified
            if week == 1:
                current_reps = base_reps
            elif week == 2:
                current_reps = base_reps + (2 if base_reps < 12 else 1) # Add 1-2 reps
            elif week == 3:
                current_sets = (current_sets or 3) + 1 # Add a set
                current_reps = base_reps # Reset reps or keep slightly higher
            elif week == 4:
                current_sets = (current_sets or 3) + 1
                current_reps = base_reps + (2 if base_reps < 12 else 1)
            
            # Cap sets and reps
            current_sets = min(current_sets, 5) if current_sets else 3
            current_reps = min(current_reps, 20) if current_reps else 10


        # Progression for duration-based exercises (e.g., Plank, Superman Hold)
        elif current_duration is not None and current_sets is not None: # e.g. Plank "3 sets of 30 sec"
             # For simplicity, let's increase sets for duration exercises if possible
            if week == 3 or week == 4:
                 current_sets = (current_sets or 2) + 1
            current_sets = min(current_sets, 4) if current_sets else 2


    if current_sets:
        formatted_ex["sets"] = current_sets
    if current_reps:
        formatted_ex["reps"] = current_reps
    if current_duration:
        formatted_ex["duration"] = current_duration

    # Add rest and tempo for main exercises
    if exercise_data["type"] == "main":
        formatted_ex["rest"] = exercise_data.get("default_rest", "60s")
        if exercise_data.get("default_tempo"): # Only add if tempo is relevant
             formatted_ex["tempo"] = exercise_data.get("default_tempo", "2-0-1")
             
    return formatted_ex


# --- Workout Structure Logic ---
def get_muscle_groups_for_day(session_num_overall, days_per_week):
    """Determines muscle groups for the day based on a PPL split or similar."""
    # PPL (Push, Pull, Legs) split for 3 days a week is standard
    day_in_weekly_cycle = (session_num_overall - 1) % days_per_week
    
    if days_per_week == 3:
        if day_in_weekly_cycle == 0: # Day 1 of 3
            return ["chest", "shoulders", "triceps"], "Push Day"
        elif day_in_weekly_cycle == 1: # Day 2 of 3
            return ["back", "biceps"], "Pull Day"
        else: # Day 3 of 3
            return ["legs", "glutes", "calves", "core"], "Leg Day & Core" # Core can be integrated
    # Add logic for other days_per_week if needed (e.g., Upper/Lower for 2 or 4 days)
    else: # Default to a full body approach if not 3 days
        return ["full_body", "core"], "Full Body & Core"


def select_main_exercises_for_day(filtered_exercises, muscle_groups_for_focus, experience):
    """Selects main exercises targeting specified muscle groups."""
    main_exercises_today = []
    
    # Shuffle to get variety if multiple exercises are available for a group
    random.shuffle(filtered_exercises)

    # Select for primary muscle groups
    for group in muscle_groups_for_focus:
        if group == "core" and "legs" in muscle_groups_for_focus: # Avoid double dipping core if it's part of leg day focus
            continue
        
        count_for_group = NUM_MAIN_EXERCISES_PER_PRIMARY_GROUP
        if group in ["triceps", "biceps", "calves", "core"]: # Auxiliary groups
            count_for_group = NUM_MAIN_EXERCISES_AUXILIARY
            if group == "core" and "legs" not in muscle_groups_for_focus : # if core is a focus itself
                count_for_group = NUM_MAIN_EXERCISES_PER_PRIMARY_GROUP


        selected_for_this_group = 0
        for ex in filtered_exercises:
            if ex.get("type") == "main" and ex.get("muscle_group") == group:
                if ex not in main_exercises_today: # Avoid duplicates
                    main_exercises_today.append(ex)
                    selected_for_this_group +=1
                if selected_for_this_group >= count_for_group:
                    break
    
    # If not enough exercises were found (e.g. limited equipment), try to fill with 'full_body'
    target_main_exercises = 4 if experience == "beginner" else 5 # Aim for 4-6 main exercises
    if len(main_exercises_today) < target_main_exercises:
        full_body_exercises = [
            ex for ex in filtered_exercises 
            if ex.get("type") == "main" and ex.get("muscle_group") == "full_body" and ex not in main_exercises_today
        ]
        needed = target_main_exercises - len(main_exercises_today)
        main_exercises_today.extend(random.sample(full_body_exercises, min(needed, len(full_body_exercises))))

    return main_exercises_today[:target_main_exercises + 1] # Cap at a reasonable number


# --- Main Plan Generation ---
def generate_workout_session(session_num, week_num, user_profile, available_exercises_for_user):
    """Generates a single workout session."""
    session_date = (datetime.now() + timedelta(days=(session_num - 1) * (7 / user_profile.get("days_per_week", 3)))).strftime("%Y-%m-%d")

    muscle_groups_today, day_focus_name = get_muscle_groups_for_day(session_num, user_profile.get("days_per_week", 3))

    # Warm-up
    warmup_ex_list = select_random_exercises(available_exercises_for_user, "warmup", NUM_WARMUP_EXERCISES)
    warmup_section = [format_exercise_for_plan(ex, week_num, user_profile.get("goal")) for ex in warmup_ex_list]

    # Main Exercises
    main_ex_list = select_main_exercises_for_day(available_exercises_for_user, muscle_groups_today, user_profile["experience"])
    main_section = [format_exercise_for_plan(ex, week_num, user_profile.get("goal")) for ex in main_ex_list]
    
    # Cool-down
    cooldown_ex_list = select_random_exercises(available_exercises_for_user, "cooldown", NUM_COOLDOWN_EXERCISES)
    cooldown_section = [format_exercise_for_plan(ex, week_num, user_profile.get("goal")) for ex in cooldown_ex_list]

    # Ensure core exercises are included if "core" was part of the focus or if it's a PPL leg day
    if "core" in muscle_groups_today and not any(ex.get("muscle_group") == "core" for ex in main_ex_list):
        core_exercises = select_random_exercises(available_exercises_for_user, "core", 1) # Add 1-2 core exercises
        if not core_exercises: # if 'core' type is not found, try 'main' type for 'core' muscle group
            core_exercises = select_random_exercises(
                [ex for ex in available_exercises_for_user if ex.get("muscle_group") == "core" and ex.get("type") == "main"],
                 "main", 1
            )
        for core_ex in core_exercises:
             main_section.append(format_exercise_for_plan(core_ex, week_num, user_profile.get("goal")))


    session = {
        "session": session_num,
        "date": session_date,
        "focus": day_focus_name,
        "sections": {
            "warmup": warmup_section,
            "main": main_section,
            "cooldown": cooldown_section
        }
    }
    # Optional custom section logic (e.g. Circuit) can be added here if desired based on assignment
    # For example, add a circuit on one day of the week for intermediate+ users
    # if user_profile["experience"] != "beginner" and (session_num % user_profile.get("days_per_week", 3) == 0) : # e.g. last day of week
    #     circuit_exercise_candidates = [ex for ex in available_exercises_for_user if ex.get("type") == "main" and ex.get("equipment") == "bodyweight"]
    #     if len(circuit_exercise_candidates) >= 3:
    #         circuit_ex_list = random.sample(circuit_exercise_candidates, 3)
    #         circuit_section = [format_exercise_for_plan(ex, week_num, user_profile.get("goal")) for ex in circuit_ex_list]
    #         # Remove sets/reps for circuit and add a note
    #         for cex in circuit_section:
    #             cex.pop("sets", None)
    #             cex.pop("reps", None)
    #             cex["duration"] = cex.get("duration", "30-45 sec") # Default duration for circuit exercises
    #         circuit_section.append({"name": "Circuit Note", "note": "Perform exercises back-to-back with minimal rest. Rest 60-90s after completing all exercises. Repeat for 2-3 rounds."})
    #         session["sections"]["circuit"] = circuit_section
    return session

def generate_full_workout_plan(user_profile):
    """Generates a 12-session workout plan."""
    if not ALL_EXERCISES:
        return {"error": "Exercise database is empty or could not be loaded. Please ensure 'exercises.json' is correct."}

    available_exercises_for_user = filter_exercises_by_profile(user_profile)
    if not available_exercises_for_user:
        return {"error": "No suitable exercises found for the user profile (check equipment and experience level against 'exercises.json')."}
    if len(available_exercises_for_user) < (NUM_WARMUP_EXERCISES + NUM_COOLDOWN_EXERCISES + 3): # Arbitrary threshold
         return {"error": f"Not enough variety of exercises ({len(available_exercises_for_user)} found) for the user profile to generate a meaningful plan. Check equipment and experience."}


    workout_plan = []
    # Assignment specifies 12 sessions (3 sessions/week for 4 weeks)
    num_total_sessions = 12
    days_per_week_from_user = user_profile.get("days_per_week", 3)
    
    # Ensure days_per_week is reasonable for a 12 session plan over ~4 weeks
    if days_per_week_from_user not in [2,3,4,5]: # Common training frequencies
        actual_days_per_week = 3 # Default to 3 if input is unusual
    else:
        actual_days_per_week = days_per_week_from_user
        
    user_profile["days_per_week"] = actual_days_per_week # Standardize for calculation

    num_weeks = num_total_sessions // actual_days_per_week
    if num_total_sessions % actual_days_per_week != 0:
        num_weeks +=1 # if 12 sessions and 5 days/week, it's over 2.x weeks

    current_session_overall_count = 0
    for week in range(1, num_weeks + 1):
        for day_in_week in range(actual_days_per_week):
            current_session_overall_count += 1
            if current_session_overall_count > num_total_sessions:
                break
            
            session = generate_workout_session(current_session_overall_count, week, user_profile, available_exercises_for_user)
            workout_plan.append(session)
        if current_session_overall_count > num_total_sessions:
            break


    return {
        "user_profile_processed": user_profile, # Echo back what was used
        "workout_plan": workout_plan
    }

if __name__ == '__main__':
    # Example Usage for direct testing
    sample_user_profile_beginner = {
        "name": "Beginner Test", "experience": "beginner",
        "equipment": ["bodyweight"], "days_per_week": 3, "goal": "general_fitness"
    }
    sample_user_profile_intermediate = {
        "name": "Intermediate Test", "experience": "intermediate",
        "equipment": ["dumbbell", "bench", "resistance_band"], "days_per_week": 3, "goal": "muscle_gain"
    }
    
    if not ALL_EXERCISES:
        print("Cannot run test: Exercise database failed to load.")
    else:
        print("\n--- Beginner Plan ---")
        beginner_plan = generate_full_workout_plan(sample_user_profile_beginner)
        if "error" in beginner_plan:
            print(f"Error: {beginner_plan['error']}")
        else:
            # print(json.dumps(beginner_plan["workout_plan"][0], indent=2)) # Print first session
            print(f"Generated {len(beginner_plan['workout_plan'])} sessions for beginner.")
            if beginner_plan['workout_plan']:
                 print(json.dumps(beginner_plan['workout_plan'][0]['sections']['main'][:2], indent=2))


        print("\n--- Intermediate Plan ---")
        intermediate_plan = generate_full_workout_plan(sample_user_profile_intermediate)
        if "error" in intermediate_plan:
            print(f"Error: {intermediate_plan['error']}")
        else:
            # print(json.dumps(intermediate_plan["workout_plan"][0], indent=2)) # Print first session
            print(f"Generated {len(intermediate_plan['workout_plan'])} sessions for intermediate.")
            if intermediate_plan['workout_plan']:
                print(json.dumps(intermediate_plan['workout_plan'][0]['sections']['main'][:2], indent=2))