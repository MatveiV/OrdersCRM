import { initAnimatedBackground } from './components/AnimatedBackground.js';
import { getAdminData, submitLead } from './api/index.js';
import { BehaviorTracker } from './tracking/behavior.js';

document.addEventListener('DOMContentLoaded', async () => {
    initAnimatedBackground();
    
    const tracker = new BehaviorTracker();
    
    const adminData = await getAdminData();
    populateDynamicFields(adminData);
    
    const form = document.getElementById('lead-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!validateForm()) return;
        
        const submitBtn = form.querySelector('.submit-btn');
        const btnText = submitBtn.querySelector('.btn-text');
        const btnLoader = submitBtn.querySelector('.btn-loader');
        
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline';
        
        try {
            const formData = new FormData(form);
            const leadData = Object.fromEntries(formData);
            
            if (leadData.budget) {
                leadData.budget = `${leadData.budget} ₽`;
            }
            
            const behaviorData = tracker.getData();
            
            const payload = {
                ...leadData,
                ...behaviorData
            };
            
            await submitLead(payload);
            
            form.style.display = 'none';
            document.getElementById('success-message').style.display = 'block';
            
        } catch (error) {
            alert('Произошла ошибка при отправке. Пожалуйста, попробуйте позже.');
            console.error('Submit error:', error);
        } finally {
            submitBtn.disabled = false;
            btnText.style.display = 'inline';
            btnLoader.style.display = 'none';
        }
    });
    
    const budgetSlider = document.getElementById('budget');
    const budgetValue = document.getElementById('budget-value');
    
    budgetSlider.addEventListener('input', (e) => {
        const value = parseInt(e.target.value);
        budgetValue.textContent = `${value.toLocaleString('ru-RU')} ₽`;
    });
});

function populateDynamicFields(adminData) {
    const companySizeSelect = document.getElementById('company_size');
    const taskTypeSelect = document.getElementById('task_type');
    const productInterestSelect = document.getElementById('product_interest');
    const budgetSlider = document.getElementById('budget');
    
    const companySizes = ['1-5 сотрудников', '5-10 сотрудников', '10-50 сотрудников', '50-100 сотрудников', '100+ сотрудников'];
    companySizes.forEach(size => {
        const option = document.createElement('option');
        option.value = size;
        option.textContent = size;
        companySizeSelect.appendChild(option);
    });
    
    if (adminData.service_name) {
        const services = adminData.service_name.split(',').map(s => s.trim());
        services.forEach(service => {
            const option = document.createElement('option');
            option.value = service;
            option.textContent = service;
            taskTypeSelect.appendChild(option);
        });
    }
    
    if (adminData.available_products) {
        const products = adminData.available_products.split(',').map(p => p.trim());
        products.forEach(product => {
            const option = document.createElement('option');
            option.value = product;
            option.textContent = product;
            productInterestSelect.appendChild(option);
        });
    }
    
    if (adminData.budget_range) {
        try {
            const range = typeof adminData.budget_range === 'string' 
                ? JSON.parse(adminData.budget_range) 
                : adminData.budget_range;
            
            if (range.min && range.max) {
                budgetSlider.min = range.min;
                budgetSlider.max = range.max;
                budgetSlider.value = Math.round((range.min + range.max) / 2);
                
                const labels = document.querySelector('.budget-labels');
                if (labels) {
                    labels.children[0].textContent = `${parseInt(range.min).toLocaleString('ru-RU')} ₽`;
                    labels.children[1].textContent = `${parseInt(range.max).toLocaleString('ru-RU')} ₽`;
                }
                
                document.getElementById('budget-value').textContent = 
                    `${parseInt(budgetSlider.value).toLocaleString('ru-RU')} ₽`;
            }
        } catch (e) {
            console.warn('Failed to parse budget range:', e);
        }
    }
}

function validateForm() {
    const requiredFields = ['first_name', 'last_name', 'contact_data'];
    let isValid = true;
    
    requiredFields.forEach(fieldName => {
        const field = document.getElementById(fieldName);
        const formGroup = field.closest('.form-group');
        const errorMsg = formGroup.querySelector('.error-msg');
        
        if (!field.value.trim()) {
            formGroup.classList.add('error');
            errorMsg.textContent = 'Это поле обязательно для заполнения';
            isValid = false;
        } else {
            formGroup.classList.remove('error');
            errorMsg.textContent = '';
        }
    });
    
    const contactField = document.getElementById('contact_data');
    const contactValue = contactField.value.trim();
    const contactGroup = contactField.closest('.form-group');
    const contactError = contactGroup.querySelector('.error-msg');
    
    if (contactValue && !isValidEmail(contactValue) && !isValidPhone(contactValue)) {
        contactGroup.classList.add('error');
        contactError.textContent = 'Введите корректный email или телефон';
        isValid = false;
    }
    
    return isValid;
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isValidPhone(phone) {
    return /^[\+]?[\d\s\-\(\)]{7,}$/.test(phone);
}
