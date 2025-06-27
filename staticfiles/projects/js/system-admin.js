// projects/static/projects/js/system-admin.js
function initializeTechnologySelector() {
    const techSelector = document.querySelector('.technology-selector');
    if (!techSelector) return;
    
    const checkboxes = techSelector.querySelectorAll('input[type="checkbox"]');
    const selectedTechs = document.createElement('div');
    selectedTechs.className = 'selected-technologies';
    techSelector.appendChild(selectedTechs);
    
    function updateSelectedDisplay() {
        const selected = Array.from(checkboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.nextElementSibling.textContent.trim());
        
        selectedTechs.innerHTML = selected.length 
            ? selected.map(tech => `<span class="tech-tag">${tech}</span>`).join('')
            : '<span class="no-selection">No technologies selected</span>';
    }
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectedDisplay);
    });
    
    updateSelectedDisplay();
}

function initializeMetricsSliders() {
    const scoreInputs = document.querySelectorAll('.score-input');
    
    scoreInputs.forEach(input => {
        const container = input.closest('.metric-field');
        if (!container) return;
        
        // Create visual slider
        const slider = document.createElement('div');
        slider.className = 'score-slider';
        slider.innerHTML = `
            <div class="slider-track">
                <div class="slider-fill"></div>
            </div>
            <div class="slider-value">${input.value || 0}</div>
        `;
        
        input.parentNode.appendChild(slider);
        
        function updateSlider() {
            const value = parseInt(input.value) || 0;
            const percentage = (value / 100) * 100;
            const fill = slider.querySelector('.slider-fill');
            const valueDisplay = slider.querySelector('.slider-value');
            
            fill.style.width = percentage + '%';
            valueDisplay.textContent = value;
            
            // Color coding
            fill.className = 'slider-fill';
            if (value >= 80) fill.classList.add('excellent');
            else if (value >= 60) fill.classList.add('good');
            else if (value >= 40) fill.classList.add('fair');
            else fill.classList.add('poor');
        }
        
        input.addEventListener('input', updateSlider);
        updateSlider();
    });
}

function initializeRepoValidation() {
    const repoInput = document.querySelector('input[name="github_repo"]');
    const validateBtn = document.querySelector('[data-action="validate"]');
    
    if (!repoInput || !validateBtn) return;
    
    validateBtn.addEventListener('click', function() {
        const repoUrl = repoInput.value;
        if (!repoUrl) {
            showRepoStatus('error', 'Please enter a repository URL');
            return;
        }
        
        if (!repoUrl.includes('github.com')) {
            showRepoStatus('error', 'Please enter a valid GitHub URL');
            return;
        }
        
        validateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Validating...';
        validateBtn.disabled = true;
        
        // Simulate API call (you'd implement actual GitHub API validation)
        setTimeout(() => {
            const isValid = Math.random() > 0.3; // Simulate 70% success rate
            
            if (isValid) {
                showRepoStatus('success', 'Repository validated successfully');
            } else {
                showRepoStatus('error', 'Repository not found or private');
            }
            
            validateBtn.innerHTML = '<i class="fas fa-check"></i> Validate';
            validateBtn.disabled = false;
        }, 2000);
    });
}

function showRepoStatus(type, message) {
    const repoInput = document.querySelector('input[name="github_repo"]');
    let statusDiv = document.querySelector('.repo-status');
    
    if (!statusDiv) {
        statusDiv = document.createElement('div');
        statusDiv.className = 'repo-status';
        repoInput.parentNode.appendChild(statusDiv);
    }
    
    statusDiv.className = `repo-status ${type}`;
    statusDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check' : 'exclamation-triangle'}"></i>
        ${message}
    `;
    
    setTimeout(() => {
        statusDiv.style.opacity = '0';
        setTimeout(() => statusDiv.remove(), 300);
    }, 5000);
}

function calculateHealthScore() {
    const performanceInput = document.querySelector('input[name="performance_score"]');
    const qualityInput = document.querySelector('input[name="code_quality_score"]');
    const coverageInput = document.querySelector('input[name="test_coverage"]');
    const docsInput = document.querySelector('input[name="documentation_score"]');
    
    if (!performanceInput || !qualityInput || !coverageInput || !docsInput) return;
    
    function updateHealthScore() {
        const performance = parseInt(performanceInput.value) || 0;
        const quality = parseInt(qualityInput.value) || 0;
        const coverage = parseFloat(coverageInput.value) || 0;
        const docs = parseInt(docsInput.value) || 0;
        
        // Weighted health score calculation
        const healthScore = Math.round(
            (performance * 0.3) + 
            (quality * 0.3) + 
            (coverage * 0.2) + 
            (docs * 0.2)
        );
        
        updateHealthDisplay(healthScore);
    }
    
    [performanceInput, qualityInput, coverageInput, docsInput].forEach(input => {
        input.addEventListener('input', updateHealthScore);
    });
    
    updateHealthScore();
}

function updateHealthDisplay(score) {
    const healthBar = document.querySelector('.health-fill');
    const healthValue = document.querySelector('.metric-value');
    
    if (healthBar) {
        healthBar.style.width = score + '%';
        
        // Color coding
        healthBar.className = 'health-fill';
        if (score >= 80) healthBar.classList.add('excellent');
        else if (score >= 60) healthBar.classList.add('good');
        else if (score >= 40) healthBar.classList.add('fair');
        else healthBar.classList.add('poor');
    }
    
    if (healthValue) {
        healthValue.textContent = score + '%';
    }
}