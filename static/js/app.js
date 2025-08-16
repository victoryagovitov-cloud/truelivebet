// DOM Elements
const sportTypeSelect = document.getElementById('sportType');
const footballFields = document.getElementById('footballFields');
const tennisFields = document.getElementById('tennisFields');
const basketballFields = document.getElementById('basketballFields');
const analysisForm = document.getElementById('analysisForm');
const resultsSection = document.getElementById('resultsSection');
const resultsContent = document.getElementById('resultsContent');
const strategiesContent = document.getElementById('strategiesContent');

// Modal Elements
const totalCalculatorModal = document.getElementById('totalCalculatorModal');
const bankrollModal = document.getElementById('bankrollModal');

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Load strategies on page load
    loadStrategies();
    
    // Add event listeners
    sportTypeSelect.addEventListener('change', toggleSportFields);
    analysisForm.addEventListener('submit', handleAnalysisSubmit);
    
    // Modal close functionality
    setupModals();
}

// Toggle sport-specific fields
function toggleSportFields() {
    const selectedSport = sportTypeSelect.value;
    
    // Hide all sport fields
    [footballFields, tennisFields, basketballFields].forEach(field => {
        if (field) field.style.display = 'none';
    });
    
    // Show relevant fields
    switch(selectedSport) {
        case 'football':
            footballFields.style.display = 'block';
            break;
        case 'tennis':
            tennisFields.style.display = 'block';
            break;
        case 'basketball':
            basketballFields.style.display = 'block';
            break;
    }
}

// Handle form submission
async function handleAnalysisSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(analysisForm);
    const sportType = formData.get('sportType');
    
    if (!sportType) {
        showError('Пожалуйста, выберите вид спорта');
        return;
    }
    
    // Prepare data for API
    const analysisData = prepareAnalysisData(sportType, formData);
    
    try {
        showLoading();
        
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(analysisData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            displayResults(result);
        } else {
            showError(result.error || 'Ошибка анализа');
        }
        
    } catch (error) {
        showError('Ошибка соединения с сервером');
        console.error('Error:', error);
    } finally {
        hideLoading();
    }
}

// Prepare data for different sports
function prepareAnalysisData(sportType, formData) {
    switch(sportType) {
        case 'football':
            return {
                type: 'football',
                team1: formData.get('team1'),
                team2: formData.get('team2'),
                score: formData.get('score'),
                time: formData.get('time'),
                stats: {
                    control: parseInt(formData.get('control')) || 0,
                    shots: formData.get('shots')
                }
            };
            
        case 'tennis':
            return {
                type: 'tennis',
                player1: formData.get('player1'),
                player2: formData.get('player2'),
                sets: parseTennisSets(formData.get('sets')),
                current_set: parseCurrentSet(formData.get('sets'))
            };
            
        case 'basketball':
            return {
                type: 'basketball',
                team1: formData.get('bbTeam1'),
                team2: formData.get('bbTeam2'),
                score: formData.get('bbScore'),
                quarter: formData.get('quarter'),
                time: 'Q' + formData.get('quarter')
            };
            
        default:
            return { type: sportType };
    }
}

// Parse tennis sets data
function parseTennisSets(setsString) {
    if (!setsString) return [];
    
    const sets = setsString.split(',').map(set => {
        const [score1, score2] = set.trim().split(':').map(Number);
        return {
            score1,
            score2,
            winner: score1 > score2 ? 'player1' : 'player2'
        };
    });
    
    return sets;
}

// Parse current set data
function parseCurrentSet(setsString) {
    if (!setsString) return {};
    
    const sets = setsString.split(',');
    const currentSet = sets[sets.length - 1].trim();
    const [score1, score2] = currentSet.split(':').map(Number);
    
    return {
        score1,
        score2,
        leader: score1 > score2 ? 'player1' : 'player2'
    };
}

// Display analysis results
function displayResults(result) {
    if (result.error) {
        showError(result.error);
        return;
    }
    
    const resultHTML = createResultHTML(result);
    resultsContent.innerHTML = resultHTML;
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
    
    // Add fade-in animation
    resultsContent.classList.add('fade-in');
}

// Create HTML for results
function createResultHTML(result) {
    const confidenceClass = getConfidenceClass(result.confidence);
    
    return `
        <div class="result-card ${confidenceClass}">
            <div class="result-header">
                <span class="result-type">${getSportTypeLabel(result.match_type)}</span>
                <span class="confidence">${result.confidence}%</span>
            </div>
            
            ${result.recommendation ? `
                <div class="recommendation">${result.recommendation}</div>
            ` : ''}
            
            ${result.reasoning && result.reasoning.length > 0 ? `
                <div class="reasoning">
                    <strong>Обоснование:</strong>
                    <ul>
                        ${result.reasoning.map(reason => `<li>${reason}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${!result.recommendation ? `
                <div class="reasoning">
                    <em>Недостаточно данных для рекомендации. Продолжайте наблюдать за матчем.</em>
                </div>
            ` : ''}
        </div>
    `;
}

// Get confidence class for styling
function getConfidenceClass(confidence) {
    if (confidence >= 80) return 'success';
    if (confidence >= 60) return 'warning';
    return 'error';
}

// Get sport type label
function getSportTypeLabel(matchType) {
    const labels = {
        'football': '⚽ Футбол',
        'tennis': '🎾 Теннис',
        'basketball': '🏀 Баскетбол',
        'handball': '🤾 Гандбол',
        'tabletennis': '🏓 Настольный теннис'
    };
    return labels[matchType] || matchType;
}

// Load strategies from API
async function loadStrategies() {
    try {
        const response = await fetch('/api/strategies');
        const strategies = await response.json();
        displayStrategies(strategies);
    } catch (error) {
        console.error('Error loading strategies:', error);
    }
}

// Display strategies
function displayStrategies(strategies) {
    let strategiesHTML = '';
    
    Object.entries(strategies).forEach(([sport, sportStrategies]) => {
        strategiesHTML += `
            <div class="strategy-card">
                <h3>${getSportTypeLabel(sport)}</h3>
                ${sportStrategies.map(strategy => `
                    <div class="strategy-item">
                        <div class="strategy-name">${strategy.name}</div>
                        <div class="strategy-description">${strategy.description}</div>
                        <div class="strategy-meta">
                            <span class="bet-type">${strategy.bet_type}</span>
                            <span class="strategy-confidence">${strategy.confidence}%</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    });
    
    strategiesContent.innerHTML = strategiesHTML;
}

// Modal functions
function setupModals() {
    // Close modals when clicking on X
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            this.closest('.modal').style.display = 'none';
        });
    });
    
    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });
}

function openTotalCalculator() {
    totalCalculatorModal.style.display = 'block';
}

function openBankrollManager() {
    bankrollModal.style.display = 'block';
}

function openStatistics() {
    alert('Функция статистики будет добавлена в следующей версии!');
}

// Calculator functions
function calculateTotal() {
    const currentScore = document.getElementById('currentScore').value;
    const elapsedTime = parseInt(document.getElementById('elapsedTime').value);
    const remainingTime = parseInt(document.getElementById('remainingTime').value);
    
    if (!currentScore || !elapsedTime || !remainingTime) {
        showModalError('Пожалуйста, заполните все поля');
        return;
    }
    
    try {
        const [score1, score2] = currentScore.split(':').map(Number);
        const totalGoals = score1 + score2;
        
        // Формула: (текущий счет ÷ прошедшие минуты) × оставшиеся минуты + текущий счет
        const goalsPerMinute = totalGoals / elapsedTime;
        const predictedGoals = goalsPerMinute * remainingTime;
        const finalTotal = totalGoals + predictedGoals;
        
        const resultHTML = `
            <div class="total-calculation">
                <div><strong>Расчет:</strong></div>
                <div>Текущий счет: ${totalGoals} голов за ${elapsedTime} мин</div>
                <div>Темп: ${goalsPerMinute.toFixed(2)} гола/мин</div>
                <div>Прогноз: ${predictedGoals.toFixed(1)} голов за оставшееся время</div>
                <div><strong>Итоговый тотал: ${finalTotal.toFixed(1)}</strong></div>
                <div style="margin-top: 10px;">
                    <div>Тотал МЕНЬШЕ ${Math.ceil(finalTotal + 2)}: ✅</div>
                    <div>Тотал БОЛЬШЕ ${Math.floor(finalTotal - 2)}: ✅</div>
                </div>
            </div>
        `;
        
        document.getElementById('totalResult').innerHTML = resultHTML;
        
    } catch (error) {
        showModalError('Ошибка в расчетах. Проверьте формат счета (например: 15:20)');
    }
}

function calculateBetSize() {
    const totalBankroll = parseInt(document.getElementById('totalBankroll').value);
    const confidenceLevel = parseFloat(document.getElementById('confidenceLevel').value);
    
    if (!totalBankroll || totalBankroll <= 0) {
        showModalError('Пожалуйста, введите корректный размер банкролла');
        return;
    }
    
    const betSize = (totalBankroll * confidenceLevel) / 100;
    
    const resultHTML = `
        <div class="bet-calculation">
            <div><strong>Размер ставки:</strong></div>
            <div style="font-size: 1.2em; color: #667eea; margin: 10px 0;">
                ${betSize.toFixed(0)} ₽
            </div>
            <div>Процент от банка: ${confidenceLevel}%</div>
            <div style="margin-top: 10px; font-size: 0.9em; color: #666;">
                Рекомендуется не превышать 2.5% от банка за одну ставку
            </div>
        </div>
    `;
    
    document.getElementById('betSizeResult').innerHTML = resultHTML;
}

// Utility functions
function showLoading() {
    const btn = document.querySelector('.analyze-btn');
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Анализируем...';
    btn.disabled = true;
}

function hideLoading() {
    const btn = document.querySelector('.analyze-btn');
    btn.innerHTML = '<i class="fas fa-search"></i> Анализировать';
    btn.disabled = false;
}

function showError(message) {
    // Create error notification
    const notification = document.createElement('div');
    notification.className = 'error-notification';
    notification.innerHTML = `
        <div style="
            position: fixed;
            top: 20px;
            right: 20px;
            background: #dc3545;
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(220, 53, 69, 0.3);
            z-index: 1001;
            max-width: 300px;
        ">
            <i class="fas fa-exclamation-triangle"></i> ${message}
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function showModalError(message) {
    const resultElement = document.getElementById('totalResult') || document.getElementById('betSizeResult');
    resultElement.innerHTML = `<div style="color: #dc3545;">${message}</div>`;
}

// Add some interactive features
document.addEventListener('DOMContentLoaded', function() {
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add form validation
    const inputs = document.querySelectorAll('input[required], select[required]');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.style.borderColor = '#dc3545';
            } else {
                this.style.borderColor = '#e1e5e9';
            }
        });
    });
});