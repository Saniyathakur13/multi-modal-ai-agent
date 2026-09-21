// API Configuration
const API_URL = 'http://localhost:8001';

// DOM Elements
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const analyzeBtn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const resultsContent = document.getElementById('resultsContent');

// State
let selectedFile = null;

// Check API Status
async function checkAPI() {
    const badge = document.getElementById('apiStatus');
    try {
        const response = await fetch(`${API_URL}/api/health`);
        if (response.ok) {
            badge.textContent = '● Online';
            badge.className = 'status-badge online';
        } else {
            badge.textContent = '● Offline';
            badge.className = 'status-badge offline';
        }
    } catch {
        badge.textContent = '● Offline';
        badge.className = 'status-badge offline';
    }
}

// Check API on load
checkAPI();
setInterval(checkAPI, 30000);

// Upload handlers
uploadBox.addEventListener('click', () => fileInput.click());
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.classList.add('drag-over');
});
uploadBox.addEventListener('dragleave', () => {
    uploadBox.classList.remove('drag-over');
});
uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.classList.remove('drag-over');
    if (e.dataTransfer.files.length) {
        handleFile(e.dataTransfer.files[0]);
    }
});
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        handleFile(e.target.files[0]);
    }
});

function handleFile(file) {
    selectedFile = file;
    fileName.textContent = `📎 ${file.name}`;
    fileSize.textContent = `(${(file.size / 1024).toFixed(1)} KB)`;
    fileInfo.classList.add('show');
    analyzeBtn.disabled = false;
    results.classList.remove('show');
}

function clearFile() {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.classList.remove('show');
    analyzeBtn.disabled = true;
}

// Analyze Report
async function analyzeReport() {
    if (!selectedFile) {
        alert('Please select a file first!');
        return;
    }
    
    loading.classList.add('show');
    results.classList.remove('show');
    analyzeBtn.disabled = true;
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
        const response = await fetch(`${API_URL}/analyze-report`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResults(data);
        } else {
            showError(data.error || 'Analysis failed');
        }
    } catch (error) {
        showError('Failed to connect to server. Make sure the API is running.');
        console.error('Error:', error);
    } finally {
        loading.classList.remove('show');
        analyzeBtn.disabled = false;
    }
}

function displayResults(data) {
    results.classList.add('show');
    
    let html = '';
    const sd = data.structured_data || {};
    
    // Patient Info
    html += `
        <div class="result-card">
            <h3>👤 Patient Information</h3>
            <div class="info-grid">
                <div class="info-item">
                    <label>Patient Name</label>
                    <span>${sd.patient_name || 'N/A'}</span>
                </div>
                <div class="info-item">
                    <label>Hemoglobin</label>
                    <span>${sd.hemoglobin || 'N/A'} g/dl</span>
                </div>
                <div class="info-item">
                    <label>WBC</label>
                    <span>${sd.wbc || 'N/A'} cells/cu</span>
                </div>
                <div class="info-item">
                    <label>RBC</label>
                    <span>${sd.rbc || 'N/A'} mill/cmm</span>
                </div>
                <div class="info-item">
                    <label>Platelets</label>
                    <span>${sd.platelets || 'N/A'} Lakhs/cu</span>
                </div>
            </div>
        </div>
    `;
    
    // Abnormal Findings
    if (sd.abnormal_findings && sd.abnormal_findings.length > 0) {
        html += `
            <div class="result-card abnormal">
                <h3>⚠️ Abnormal Findings</h3>
                <ul class="finding-list">
                    ${sd.abnormal_findings.map(f => `<li>${f}</li>`).join('')}
                </ul>
            </div>
        `;
    } else {
        html += `
            <div class="result-card">
                <h3>✅ No Abnormal Findings</h3>
                <p>All values are within normal ranges.</p>
            </div>
        `;
    }
    
    // Summary
    if (sd.summary) {
        html += `
            <div class="result-card summary">
                <h3>📝 Summary</h3>
                <p style="color: #2d3748; line-height: 1.6;">${sd.summary}</p>
            </div>
        `;
    }
    
    // Validation
    if (sd.validation_findings && sd.validation_findings.length > 0) {
        html += `
            <div class="result-card validation">
                <h3>✅ Validation Findings</h3>
                <ul class="validation-list">
                    ${sd.validation_findings.map(f => `<li>${f}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    // Raw OCR Text
    if (data.extracted_text) {
        html += `
            <div class="result-card raw">
                <h3>📄 Extracted OCR Text</h3>
                <pre>${data.extracted_text.substring(0, 1000)}${data.extracted_text.length > 1000 ? '...' : ''}</pre>
            </div>
        `;
    }
    
    resultsContent.innerHTML = html;
}

function showError(message) {
    results.classList.add('show');
    resultsContent.innerHTML = `
        <div class="result-card" style="border-left-color: #fc8181;">
            <h3>❌ Error</h3>
            <p style="color: #c62828;">${message}</p>
        </div>
    `;
}