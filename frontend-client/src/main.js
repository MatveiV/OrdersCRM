import { initAnimatedBackground } from './components/AnimatedBackground.js';
import { renderProjects, initProjectFilters } from './components/ProjectsShowcase.js';
import { getPublicServices, submitLead } from './api/index.js';
import { BehaviorTracker } from './tracking/behavior.js';

document.addEventListener('DOMContentLoaded', async () => {
    initAnimatedBackground();
    renderProjects();
    initProjectFilters();
    
    const tracker = new BehaviorTracker();
    const services = await getPublicServices();
    populateDynamicFields(services);
    initForm(tracker);
    initScrollAnimations();
});

function populateDynamicFields(services) {
    const taskTypeSelect = document.getElementById('task_type');
    const productInterestSelect = document.getElementById('product_interest');
    const budgetSlider = document.getElementById('budget');

    taskTypeSelect.innerHTML = '<option value="">Выберите тип</option>';
    productInterestSelect.innerHTML = '<option value="">Выберите продукт</option>';

    if (!Array.isArray(services) || services.length === 0) return;

    const uniqueTypes = [...new Set(services.map(s => s.task_type).filter(Boolean))];
    uniqueTypes.forEach(type => {
        const opt = document.createElement('option');
        opt.value = type;
        opt.textContent = type;
        taskTypeSelect.appendChild(opt);
    });

    const uniqueProducts = [...new Set(services.map(s => s.product_interest).filter(Boolean))];
    uniqueProducts.forEach(product => {
        const opt = document.createElement('option');
        opt.value = product;
        opt.textContent = product;
        productInterestSelect.appendChild(opt);
    });

    const budgets = services.map(s => {
        try { return s.budget_range ? JSON.parse(s.budget_range) : null; }
        catch { return null; }
    }).filter(Boolean);
    if (budgets.length > 0) {
        const min = Math.min(...budgets.map(b => b.min).filter(Boolean));
        const max = Math.max(...budgets.map(b => b.max).filter(Boolean));
        if (min && max && max > min) {
            budgetSlider.min = min;
            budgetSlider.max = max;
            budgetSlider.value = Math.round((min + max) / 2);
            document.querySelector('.budget-labels').children[0].textContent = `${parseInt(min).toLocaleString('ru-RU')} ₽`;
            document.querySelector('.budget-labels').children[1].textContent = `${parseInt(max).toLocaleString('ru-RU')} ₽`;
            document.getElementById('budget-value').textContent = `${parseInt(budgetSlider.value).toLocaleString('ru-RU')} ₽`;
        }
    }
}

function initForm(tracker) {
    const form = document.getElementById('lead-form');
    
    const budgetSlider = document.getElementById('budget');
    budgetSlider.addEventListener('input', (e) => {
        document.getElementById('budget-value').textContent = `${parseInt(e.target.value).toLocaleString('ru-RU')} ₽`;
    });
    
    const deadlineSlider = document.getElementById('project_deadline');
    const deadlineLabels = ['1 неделя', '3 недели', '6 недель', '3 месяца', '6 месяцев', '12 месяцев'];
    deadlineSlider.addEventListener('input', (e) => {
        const idx = Math.round((parseInt(e.target.value) - 1) / 2);
        e.target.closest('.form-group').querySelector('label').innerHTML = `Срок реализации: <span id="deadline-value">${deadlineLabels[Math.min(idx, deadlineLabels.length - 1)]}</span>`;
    });
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!validateForm(form)) return;
        
        const submitBtn = form.querySelector('.submit-btn');
        const btnText = submitBtn.querySelector('.btn-text');
        const btnLoader = submitBtn.querySelector('.btn-loader');
        
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline';
        
        try {
            const formData = new FormData(form);
            const leadData = Object.fromEntries(formData);
            if (leadData.budget) leadData.budget = `${leadData.budget} ₽`;
            
            const companySizeLabels = ['1-10', '11-50', '51-200', '201-500', '500+'];
            leadData.company_size = companySizeLabels[parseInt(leadData.company_size)] || leadData.company_size;
            
            const taskVolumeLabels = ['Малый', 'Ниже среднего', 'Средний', 'Большой', 'Очень большой'];
            leadData.task_volume = taskVolumeLabels[parseInt(leadData.task_volume)] || leadData.task_volume;
            
            const payload = { ...leadData, ...tracker.getData() };
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
}

function validateForm(form) {
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

function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.hero-section, .projects-section, .form-section').forEach(section => {
        section.classList.add('animate-on-scroll');
        observer.observe(section);
    });
}
