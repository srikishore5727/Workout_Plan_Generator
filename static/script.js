// static/script.js
document.addEventListener('DOMContentLoaded', () => {
    // Tab functionality
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            
            // Update active tab button
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Show active tab content
            tabPanes.forEach(pane => {
                pane.classList.remove('active');
                if (pane.id === tabId) {
                    pane.classList.add('active');
                }
            });
        });
    });
    
    // Days per week buttons
    const dayBtns = document.querySelectorAll('.day-btn');
    const daysInput = document.getElementById('days_per_week');
    
    

    dayBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            dayBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            daysInput.value = btn.getAttribute('data-value');
        });
    });
    
    // Form and results functionality
    const form = document.getElementById('workoutForm');
    const planOutputDiv = document.getElementById('plan-output');
    const resultsContainer = document.getElementById('workout-results-container');
    const statusContainer = document.getElementById('status-message-container');
    const generateBtn = document.getElementById('generateBtn');
    const printBtn = document.getElementById('printBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const shareBtn = document.getElementById('shareBtn');
    const prevWeekBtn = document.getElementById('prevWeek');
    const nextWeekBtn = document.getElementById('nextWeek');
    const currentWeekSpan = document.getElementById('currentWeek');
    const resultsTab = document.querySelector('[data-tab="results-tab"]');
    
    let currentWeekIndex = 0;
    let allWorkoutSessions = [];
    let weeksData = [];
    
    // Equipment checkboxes
    const equipmentCheckboxes = document.querySelectorAll('input[type="checkbox"][name="equipment"]');
    const customEquipmentInput = document.getElementById('equipment');
    
    // Setup equipment checkboxes
    equipmentCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateEquipmentField);
    });
    
    function updateEquipmentField() {
        const checkedEquipment = Array.from(equipmentCheckboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);
        
        // Add custom equipment if any
        const customItems = customEquipmentInput.value
            .split(',')
            .map(item => item.trim())
            .filter(item => item.length > 0);
    }
    
    // Week navigation
    function setupWeekNavigation() {
        if (weeksData.length <= 1) {
            prevWeekBtn.disabled = true;
            nextWeekBtn.disabled = true;
            prevWeekBtn.classList.add('disabled');
            nextWeekBtn.classList.add('disabled');
            return;
        }
        
        updateWeekButtons();
        
        prevWeekBtn.addEventListener('click', () => {
            if (currentWeekIndex > 0) {
                currentWeekIndex--;
                displayWeek(currentWeekIndex);
                updateWeekButtons();
            }
        });
        
        nextWeekBtn.addEventListener('click', () => {
            if (currentWeekIndex < weeksData.length - 1) {
                currentWeekIndex++;
                displayWeek(currentWeekIndex);
                updateWeekButtons();
            }
        });
    }
    
    function updateWeekButtons() {
        prevWeekBtn.disabled = currentWeekIndex === 0;
        nextWeekBtn.disabled = currentWeekIndex === weeksData.length - 1;
        
        prevWeekBtn.classList.toggle('disabled', currentWeekIndex === 0);
        nextWeekBtn.classList.toggle('disabled', currentWeekIndex === weeksData.length - 1);
        
        currentWeekSpan.textContent = `Week ${currentWeekIndex + 1}`;
    }
    
    function displayWeek(weekIndex) {
        planOutputDiv.innerHTML = '';
        
        if (!weeksData[weekIndex]) return;
        
        weeksData[weekIndex].forEach(session => {
            planOutputDiv.appendChild(createSessionCard(session));
        });
    }
    
    // Action buttons
    if (printBtn) {
        printBtn.addEventListener('click', () => {
            window.print();
        });
    }
    
    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            // Create text representation of the workout plan
            let content = "MyFitMantra Workout Plan\n\n";
            
            allWorkoutSessions.forEach(session => {
                content += `SESSION ${session.session} ${session.focus ? `(${session.focus})` : ''}\n`;
                content += `Date: ${session.date}\n\n`;
                
                const sectionsOrder = ['warmup', 'main', 'circuit', 'cooldown'];
                sectionsOrder.forEach(sectionKey => {
                    if (session.sections[sectionKey] && session.sections[sectionKey].length > 0) {
                        let sectionTitle = sectionKey.charAt(0).toUpperCase() + sectionKey.slice(1);
                        if (sectionKey === 'main') sectionTitle = 'Main Workout';
                        
                        content += `${sectionTitle}:\n`;
                        
                        session.sections[sectionKey].forEach(ex => {
                            let details = [];
                            if (ex.sets) details.push(`Sets: ${ex.sets}`);
                            if (ex.reps) details.push(`Reps: ${ex.reps}`);
                            if (ex.duration) details.push(`Duration: ${ex.duration}`);
                            if (ex.rest) details.push(`Rest: ${ex.rest}`);
                            if (ex.tempo) details.push(`Tempo: ${ex.tempo}`);
                            if (ex.note) details.push(ex.note);
                            
                            content += `- ${ex.name} ${details.join(' | ')}\n`;
                        });
                        
                        content += '\n';
                    }
                });
                
                content += '-----------------------------------------\n\n';
            });
            
            // Create and download the file
            const blob = new Blob([content], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'MyFitMantra_Workout_Plan.txt';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    }
    
    if (shareBtn) {
        shareBtn.addEventListener('click', () => {
            // Basic share functionality - in a real app, this would use the Web Share API
            // or create a shareable link
            alert('Share feature would be implemented here in a production app.');
        });
    }
    
    // Main form submission
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        // Reset UI
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        resultsContainer.style.display = 'none';
        planOutputDiv.innerHTML = '';
        statusContainer.innerHTML = '<div class="status-message loading">Crafting your personalized workout plan...</div>';
        
        // Switch to results tab
        document.querySelector('[data-tab="results-tab"]').click();
        
        // Gather form data
        const name = document.getElementById('name').value || "User";
        
        // Get experience level
        let selectedExperience = 'intermediate';
        const experienceInputs = document.querySelectorAll('input[name="experience"]');
        for (const input of experienceInputs) {
            if (input.checked) {
                selectedExperience = input.value;
                break;
            }
        }
        
        // Get selected goal
        let selectedGoal = '';
        const goalInputs = document.querySelectorAll('input[name="goal"]');
        for (const input of goalInputs) {
            if (input.checked) {
                selectedGoal = input.value;
                break;
            }
        }
        
        // Get days per week
        const daysPerWeek = parseInt(daysInput.value);
        
        // Get selected equipment
        const selectedEquipment = Array.from(document.querySelectorAll('input[type="checkbox"][name="equipment"]:checked'))
            .map(cb => cb.value);
            
        // Add custom equipment if provided
        const customEquipment = customEquipmentInput.value
            .split(',')
            .map(item => item.trim())
            .filter(item => item.length > 0);
            
        const equipmentArray = [...selectedEquipment, ...customEquipment];
        
        const payload = {
            name: name,
            experience: selectedExperience,
            equipment: equipmentArray,
            days_per_week: daysPerWeek,
            goal: selectedGoal
        };
        
        try {
            const response = await fetch('/generate_workout_plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });
            
            statusContainer.innerHTML = ''; // Clear loading message
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Request failed with status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (!data.workout_plan || data.workout_plan.length === 0) {
                throw new Error('No workout plan was generated. Please try again.');
            }
            
            // Store the complete workout plan
            allWorkoutSessions = data.workout_plan;
            
            // Group sessions into weeks
            weeksData = groupIntoWeeks(data.workout_plan, daysPerWeek);
            
            // Reset to first week
            currentWeekIndex = 0;
            
            // Display first week
            displayWeek(currentWeekIndex);
            
            // Setup navigation buttons
            setupWeekNavigation();
            
            // Show results container
            resultsContainer.style.display = 'block';
            
            // Scroll to results
            resultsContainer.scrollIntoView({ behavior: 'smooth' });
            
        } catch (error) {
            console.error('Error:', error);
            statusContainer.innerHTML = `<div class="status-message error">
                <i class="fas fa-exclamation-circle"></i> Error: ${error.message}
            </div>`;
        } finally {
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-bolt"></i> Generate My Workout Plan';
        }
    });
    
    function groupIntoWeeks(sessions, daysPerWeek) {
        const weeks = [];
        
        for (let i = 0; i < sessions.length; i += daysPerWeek) {
            weeks.push(sessions.slice(i, i + daysPerWeek));
        }
        
        return weeks;
    }
    
    function createSessionCard(session) {
        const sessionCard = document.createElement('div');
        sessionCard.className = 'session-card';
        
        let sessionFocus = session.focus ? `(${session.focus})` : '';
        
        sessionCard.innerHTML = `
            <div class="session-header">
                <h3>Session ${session.session} ${sessionFocus}</h3>
                <span>${session.date}</span>
            </div>
        `;
        
        const sectionsOrder = ['warmup', 'main', 'circuit', 'cooldown'];
        sectionsOrder.forEach(sectionKey => {
            if (session.sections[sectionKey] && session.sections[sectionKey].length > 0) {
                const sectionDiv = document.createElement('div');
                sectionDiv.className = 'section';
                
                let sectionTitle = sectionKey.charAt(0).toUpperCase() + sectionKey.slice(1);
                if (sectionKey === 'main') sectionTitle = 'Main Workout';
                
                // Get icon based on section type
                let sectionIcon = '';
                switch(sectionKey) {
                    case 'warmup':
                        sectionIcon = '<i class="fas fa-fire"></i>';
                        break;
                    case 'main':
                        sectionIcon = '<i class="fas fa-dumbbell"></i>';
                        break;
                    case 'circuit':
                        sectionIcon = '<i class="fas fa-sync-alt"></i>';
                        break;
                    case 'cooldown':
                        sectionIcon = '<i class="fas fa-snowflake"></i>';
                        break;
                }
                
                const exerciseList = session.sections[sectionKey].map(ex => {
                    const details = [];
                    
                    if (ex.sets) details.push(`<span>Sets: ${ex.sets}</span>`);
                    if (ex.reps) details.push(`<span>Reps: ${ex.reps}</span>`);
                    if (ex.duration) details.push(`<span>Duration: ${ex.duration}</span>`);
                    if (ex.rest) details.push(`<span>Rest: ${ex.rest}</span>`);
                    if (ex.tempo) details.push(`<span>Tempo: ${ex.tempo}</span>`);
                    if (ex.note) details.push(`<span>${ex.note}</span>`);
                    
                    return `<li class="exercise-item">
                                <strong>${ex.name}</strong>
                                ${details.length > 0 ? `<div class="details">${details.join('')}</div>` : ''}
                            </li>`;
                }).join('');
                
                sectionDiv.innerHTML = `<h4>${sectionIcon} ${sectionTitle}</h4>
                                        <ul class="exercise-list">${exerciseList}</ul>`;
                                        
                sessionCard.appendChild(sectionDiv);
            }
        });
        
        return sessionCard;
    }
});