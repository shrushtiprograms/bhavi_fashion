/**
 * Bhavi India Fashion - Custom Design Form
 * 
 * This file handles the multi-step custom design form functionality.
 */

document.addEventListener('DOMContentLoaded', function() {
    initMultiStepForm();
    initDesignTypeSelection();
    initMeasurementMode();
    initFormValidation();
    initImagePreview();
});

/**
 * Multi-step form navigation
 */
function initMultiStepForm() {
    const steps = document.querySelectorAll('.step-content');
    const stepIndicators = document.querySelectorAll('.step');
    const progressBar = document.querySelector('.steps-progress-bar');
    const prevButtons = document.querySelectorAll('.prev-step');
    const nextButtons = document.querySelectorAll('.next-step');
    const submitButton = document.querySelector('.submit-form');
    
    if (steps.length === 0) return;
    
    let currentStep = 0;
    
    // Initialize - show first step
    updateStepVisibility();
    
    // Previous button click handler
    prevButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (currentStep > 0) {
                currentStep--;
                updateStepVisibility();
                window.scrollTo(0, 0);
            }
        });
    });
    
    // Next button click handler
    nextButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Validate current step
            if (validateStep(currentStep)) {
                if (currentStep < steps.length - 1) {
                    currentStep++;
                    updateStepVisibility();
                    window.scrollTo(0, 0);
                }
            }
        });
    });
    
    // Submit button handler
    if (submitButton) {
        submitButton.addEventListener('click', function(e) {
            // Final validation is handled by the form's submit event
            // This is just for any additional actions before submission
            if (!validateStep(currentStep)) {
                e.preventDefault();
            }
        });
    }
    
    // Update step visibility and progress
    function updateStepVisibility() {
        steps.forEach((step, index) => {
            if (index === currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
        
        stepIndicators.forEach((indicator, index) => {
            if (index < currentStep) {
                indicator.classList.add('completed');
                indicator.classList.remove('active');
            } else if (index === currentStep) {
                indicator.classList.add('active');
                indicator.classList.remove('completed');
            } else {
                indicator.classList.remove('active', 'completed');
            }
        });
        
        if (progressBar) {
            // Calculate progress percentage
            const progress = (currentStep / (steps.length - 1)) * 100;
            progressBar.style.width = `${progress}%`;
        }
        
        // Show/hide prev/next/submit buttons
        prevButtons.forEach(button => {
            button.style.display = currentStep === 0 ? 'none' : 'inline-block';
        });
        
        nextButtons.forEach(button => {
            button.style.display = currentStep === steps.length - 1 ? 'none' : 'inline-block';
        });
        
        if (submitButton) {
            submitButton.style.display = currentStep === steps.length - 1 ? 'inline-block' : 'none';
        }
    }
    
    // Validate current step
    function validateStep(stepIndex) {
        const currentStepElement = steps[stepIndex];
        const requiredInputs = currentStepElement.querySelectorAll('input[required], select[required], textarea[required]');
        
        let isValid = true;
        
        requiredInputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                
                // Add error styling
                input.classList.add('is-invalid');
                
                // Create or update error message
                let errorMessage = input.nextElementSibling;
                if (!errorMessage || !errorMessage.classList.contains('invalid-feedback')) {
                    errorMessage = document.createElement('div');
                    errorMessage.className = 'invalid-feedback';
                    input.parentNode.insertBefore(errorMessage, input.nextElementSibling);
                }
                
                errorMessage.textContent = `${input.getAttribute('data-error-msg') || 'This field is required'}`;
            } else {
                // Remove error styling
                input.classList.remove('is-invalid');
                
                // Remove error message if it exists
                const errorMessage = input.nextElementSibling;
                if (errorMessage && errorMessage.classList.contains('invalid-feedback')) {
                    errorMessage.textContent = '';
                }
            }
        });
        
        // Special validation for radio buttons and checkboxes
        const radioGroups = {};
        
        currentStepElement.querySelectorAll('input[type="radio"][required]').forEach(radio => {
            const name = radio.getAttribute('name');
            if (!radioGroups[name]) {
                radioGroups[name] = [];
            }
            radioGroups[name].push(radio);
        });
        
        for (const name in radioGroups) {
            const group = radioGroups[name];
            const checked = group.some(radio => radio.checked);
            
            if (!checked) {
                isValid = false;
                
                // Add error message after the last radio in the group
                const lastRadio = group[group.length - 1];
                const container = lastRadio.closest('.form-group');
                
                let errorMessage = container.querySelector('.invalid-feedback');
                if (!errorMessage) {
                    errorMessage = document.createElement('div');
                    errorMessage.className = 'invalid-feedback d-block';
                    container.appendChild(errorMessage);
                }
                
                errorMessage.textContent = `Please select an option`;
            }
        }
        
        if (!isValid) {
            showAlert('Please fill in all required fields', 'error');
        }
        
        return isValid;
    }
}

/**
 * Handle design type selection
 */
function initDesignTypeSelection() {
    const designTypeSelect = document.querySelector('select[name="design_type"]');
    const otherDesignField = document.querySelector('.other-design-type-field');
    const measurementsContainer = document.querySelector('.measurements-container');
    
    if (designTypeSelect) {
        // Handle initial state
        if (designTypeSelect.value === 'other') {
            if (otherDesignField) otherDesignField.style.display = 'block';
        } else {
            if (otherDesignField) otherDesignField.style.display = 'none';
        }
        
        // Load initial measurements for selected design type
        if (measurementsContainer && designTypeSelect.value) {
            loadMeasurements(designTypeSelect.value);
        }
        
        // Handle change
        designTypeSelect.addEventListener('change', function() {
            if (this.value === 'other') {
                if (otherDesignField) otherDesignField.style.display = 'block';
            } else {
                if (otherDesignField) otherDesignField.style.display = 'none';
            }
            
            // Load measurements for selected design type
            if (measurementsContainer) {
                loadMeasurements(this.value);
            }
        });
    }
    
    function loadMeasurements(designType) {
        // Show loading indicator
        measurementsContainer.innerHTML = '<div class="text-center my-4"><div class="spinner-border text-primary" role="status"><span class="sr-only">Loading...</span></div><p class="mt-2">Loading measurements...</p></div>';
        
        // Fetch size chart data from backend
        fetch(`/custom-designs/size-charts/${designType}/`)
            .then(response => response.json())
            .then(data => {
                renderSizeCharts(data, designType);
            })
            .catch(error => {
                console.error('Error loading measurements:', error);
                measurementsContainer.innerHTML = '<div class="alert alert-danger">Error loading measurements. Please try again.</div>';
            });
    }
    
    function renderSizeCharts(data, designType) {
        const { size_chart, measurement_fields, measurement_guide } = data;
        
        let html = `
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Size Chart for ${designType.charAt(0).toUpperCase() + designType.slice(1)}</h5>
                </div>
                <div class="card-body">
        `;
        
        // Render size chart if available
        if (size_chart && size_chart.sizes && size_chart.measurements) {
            html += `
                <div class="table-responsive">
                    <table class="table table-bordered size-chart-table">
                        <thead>
                            <tr>
                                <th>Measurements</th>
                                ${size_chart.sizes.map(size => `<th>${size}</th>`).join('')}
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            for (const measurement in size_chart.measurements) {
                html += `
                    <tr>
                        <td>${measurement}</td>
                        ${size_chart.measurements[measurement].map(value => `<td>${value}</td>`).join('')}
                    </tr>
                `;
            }
            
            html += `
                        </tbody>
                    </table>
                </div>
                <div class="measurement-guide mt-3">
                    <h6>Measurement Guide</h6>
                    <ul class="list-unstyled">
            `;
            
            for (const field in measurement_guide) {
                html += `<li><strong>${field}:</strong> ${measurement_guide[field]}</li>`;
            }
            
            html += `
                    </ul>
                </div>
            `;
        } else {
            html += '<p>No size chart available for this design type.</p>';
        }
        
        html += `
                </div>
            </div>
        `;
        
        measurementsContainer.innerHTML = html;
    }
}

/**
 * Handle measurement mode selection
 */
function initMeasurementMode() {
    const measurementModeRadios = document.querySelectorAll('input[name="measurement_mode"]');
    const staticMeasurementsSection = document.querySelector('.static-measurements');
    const dynamicMeasurementsSection = document.querySelector('.dynamic-measurements');
    
    if (measurementModeRadios.length > 0) {
        // Handle initial state
        const checkedMode = document.querySelector('input[name="measurement_mode"]:checked');
        if (checkedMode) {
            if (checkedMode.value === 'static') {
                if (staticMeasurementsSection) staticMeasurementsSection.style.display = 'block';
                if (dynamicMeasurementsSection) dynamicMeasurementsSection.style.display = 'none';
            } else {
                if (staticMeasurementsSection) staticMeasurementsSection.style.display = 'none';
                if (dynamicMeasurementsSection) dynamicMeasurementsSection.style.display = 'block';
            }
        }
        
        // Handle change
        measurementModeRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'static') {
                    if (staticMeasurementsSection) staticMeasurementsSection.style.display = 'block';
                    if (dynamicMeasurementsSection) dynamicMeasurementsSection.style.display = 'none';
                    
                    // Make static fields required
                    if (staticMeasurementsSection) {
                        staticMeasurementsSection.querySelectorAll('input').forEach(input => {
                            if (!input.classList.contains('optional-field')) {
                                input.setAttribute('required', 'required');
                            }
                        });
                    }
                    
                    // Remove required from dynamic fields
                    if (dynamicMeasurementsSection) {
                        dynamicMeasurementsSection.querySelectorAll('input, select').forEach(input => {
                            input.removeAttribute('required');
                        });
                    }
                } else {
                    if (staticMeasurementsSection) staticMeasurementsSection.style.display = 'none';
                    if (dynamicMeasurementsSection) dynamicMeasurementsSection.style.display = 'block';
                    
                    // Make dynamic size select required
                    if (dynamicMeasurementsSection) {
                        const sizeSelect = dynamicMeasurementsSection.querySelector('select[name="predefined_size"]');
                        if (sizeSelect) {
                            sizeSelect.setAttribute('required', 'required');
                        }
                    }
                    
                    // Remove required from static fields
                    if (staticMeasurementsSection) {
                        staticMeasurementsSection.querySelectorAll('input').forEach(input => {
                            input.removeAttribute('required');
                        });
                    }
                }
            });
        });
    }
}

/**
 * Form validation
 */
function initFormValidation() {
    const form = document.querySelector('.custom-design-form');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            const requiredInputs = form.querySelectorAll('input[required], select[required], textarea[required]');
            let isValid = true;
            
            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    
                    // Add error styling
                    input.classList.add('is-invalid');
                    
                    // Create or update error message
                    let errorMessage = input.nextElementSibling;
                    if (!errorMessage || !errorMessage.classList.contains('invalid-feedback')) {
                        errorMessage = document.createElement('div');
                        errorMessage.className = 'invalid-feedback';
                        input.parentNode.insertBefore(errorMessage, input.nextElementSibling);
                    }
                    
                    errorMessage.textContent = `${input.getAttribute('data-error-msg') || 'This field is required'}`;
                } else {
                    // Remove error styling
                    input.classList.remove('is-invalid');
                    
                    // Remove error message if it exists
                    const errorMessage = input.nextElementSibling;
                    if (errorMessage && errorMessage.classList.contains('invalid-feedback')) {
                        errorMessage.textContent = '';
                    }
                }
            });
            
            // Check the Terms & Conditions checkbox
            const termsCheckbox = form.querySelector('input[name="terms"]');
            if (termsCheckbox && !termsCheckbox.checked) {
                isValid = false;
                
                // Add error styling
                termsCheckbox.classList.add('is-invalid');
                
                // Create or update error message
                const container = termsCheckbox.closest('.form-group');
                let errorMessage = container.querySelector('.invalid-feedback');
                if (!errorMessage) {
                    errorMessage = document.createElement('div');
                    errorMessage.className = 'invalid-feedback d-block';
                    container.appendChild(errorMessage);
                }
                
                errorMessage.textContent = 'You must accept the Terms & Conditions';
            }
            
            if (!isValid) {
                e.preventDefault();
                showAlert('Please fill in all required fields', 'error');
                
                // Find first error and scroll to it
                const firstError = form.querySelector('.is-invalid');
                if (firstError) {
                    const offset = firstError.getBoundingClientRect().top + window.pageYOffset - 100;
                    window.scrollTo({top: offset, behavior: 'smooth'});
                }
            }
        });
    }
}

/**
 * Image preview for file uploads
 */
function initImagePreview() {
    const imageInput = document.querySelector('input[type="file"][name="reference_image"]');
    const imagePreview = document.querySelector('.reference-image-preview');
    
    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                
                // Validate file type
                const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg'];
                if (!validTypes.includes(file.type)) {
                    showAlert('Please select a valid image file (JPEG, PNG, or GIF)', 'error');
                    this.value = '';  // Clear the input
                    imagePreview.innerHTML = '<div class="no-image">No image selected</div>';
                    return;
                }
                
                // Validate file size (max 2MB)
                const maxSize = 2 * 1024 * 1024;  // 2MB
                if (file.size > maxSize) {
                    showAlert('The selected image is too large. Maximum size is 2MB', 'error');
                    this.value = '';  // Clear the input
                    imagePreview.innerHTML = '<div class="no-image">No image selected</div>';
                    return;
                }
                
                // Show preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.innerHTML = `
                        <img src="${e.target.result}" alt="Reference Design" class="img-thumbnail">
                        <button type="button" class="btn btn-sm btn-danger remove-image mt-2">Remove</button>
                    `;
                    
                    // Add remove button handler
                    const removeButton = imagePreview.querySelector('.remove-image');
                    if (removeButton) {
                        removeButton.addEventListener('click', function() {
                            imageInput.value = '';
                            imagePreview.innerHTML = '<div class="no-image">No image selected</div>';
                        });
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    // Check if alertsContainer exists, if not use the main showAlert function
    if (typeof window.showAlert === 'function') {
        window.showAlert(message, type);
    } else {
        alert(message);
    }
}
