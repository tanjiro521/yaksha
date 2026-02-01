document.addEventListener('DOMContentLoaded', () => {
    initVisuals();
    const form = document.getElementById('fraudForm');
    const resultPanel = document.getElementById('resultPanel');
    const analyzeBtn = document.getElementById('analyzeBtn');

    // Set default time to now
    const now = new Date();
    const timeString = now.toTimeString().slice(0, 5);
    const timeInput = document.getElementById('time');
    if (timeInput) {
        timeInput.value = timeString;
    }
    const dateInput = document.getElementById('date');
    if (dateInput) {
        dateInput.value = now.toISOString().split('T')[0];
    }

    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();

            // Gather Data
            const amount = parseFloat(document.getElementById('amount').value);
            const merchant = document.getElementById('merchant').value;
            const location = document.getElementById('location').value;
            const date = document.getElementById('date').value;
            const time = document.getElementById('time').value;
            const cardTypeInput = document.querySelector('input[name="cardType"]:checked');
            const cardType = cardTypeInput ? cardTypeInput.value : 'unknown';

            const payload = {
                amount: amount,
                merchant: merchant,
                location: location,
                date: date,
                time: time,
                cardType: cardType
            };

            analyzeTransaction(payload);
        });
    }
    // --- Credit Card 3D Effect ---
    const card = document.querySelector('.credit-card-bg');
    if (card) {
        document.addEventListener('mousemove', (e) => {
            const xAxis = (window.innerWidth / 2 - e.pageX) / 30;
            const yAxis = (window.innerHeight / 2 - e.pageY) / 30;

            card.style.transform = `
                rotateY(${xAxis}deg)
                rotateX(${yAxis}deg)
                translateY(-10px)
            `;
        });
    }

});

function setLoading(isLoading) {
    const btn = document.getElementById('analyzeBtn');
    if (!btn) return;
    const spinner = btn.querySelector('.spinner');
    const text = btn.querySelector('.btn-text');

    if (isLoading) {
        btn.disabled = true;
        if (text) text.style.opacity = '0';
        if (spinner) spinner.classList.remove('hidden');
    } else {
        btn.disabled = false;
        if (text) text.style.opacity = '1';
        if (spinner) spinner.classList.add('hidden');
    }
}

function displayResult(isFraud, riskScore, riskFactors = []) {
    const resultPanel = document.getElementById('resultPanel');
    const resultIcon = document.getElementById('resultIcon');
    const resultTitle = document.getElementById('resultTitle');
    const resultDesc = document.getElementById('resultDesc');
    const riskScoreValue = document.getElementById('riskScoreValue');
    const riskFill = document.getElementById('riskFill');

    if (!resultPanel) return;

    // Reset classes
    resultPanel.classList.remove('hidden', 'safe', 'danger', 'warning');
    void resultPanel.offsetWidth; // Trigger reflow

    let color, title, desc, icon;

    if (riskScore <= 40) {
        // Low Risk
        resultPanel.classList.add('safe');
        color = '#2ea043'; // Green
        icon = '<ion-icon name="shield-checkmark"></ion-icon>';
        title = 'The Vault is Secure';
        desc = 'My vigil finds no shadows here. This transaction walks in the light.';
    } else if (riskScore <= 70) {
        // Moderate Risk
        resultPanel.classList.add('warning');
        color = '#ffa900'; // Orange
        icon = '<ion-icon name="eye"></ion-icon>';
        title = 'I Sense a Disturbance';
        desc = '"I see shifting patterns." Proceed with caution, for the path is not entirely clear.';
    } else {
        // High Risk
        resultPanel.classList.add('danger');
        color = '#da3633'; // Red
        icon = '<ion-icon name="hand-left"></ion-icon>';
        title = 'THREAT TO THE TREASURE';
        desc = '"This transaction threatens the vault." I recommend an immediate freeze.';
    }

    if (resultIcon) resultIcon.innerHTML = icon;
    if (resultTitle) resultTitle.textContent = title;

    // Construct Description with Factors (Yaksha Translator)
    if (riskFactors && riskFactors.length > 0) {
        let factorsHtml = '<ul style="margin-top: 10px; text-align: left; padding-left: 20px;">';
        riskFactors.forEach(factor => {
            // Yaksha's Dictionary
            let displayFactor = factor;
            if (factor.includes("Impossible Location")) displayFactor = "<strong>The Superman Effect:</strong> This user appears in two places at once — a deception I cannot allow.";
            if (factor.includes("High Transaction Frequency")) displayFactor = "<strong>The Swift Hand:</strong> Coin flows too fast to be human.";
            if (factor.includes("Spending Spike")) displayFactor = "<strong>The Heavy Coffer:</strong> A withdrawal far beyond the norm.";

            factorsHtml += `<li>${displayFactor}</li>`;
        });
        factorsHtml += '</ul>';
        if (resultDesc) resultDesc.innerHTML = `${desc}<br><br><strong>Guardian's Insight:</strong>${factorsHtml}`;
    } else {
        if (resultDesc) resultDesc.textContent = desc;
    }

    // Animate numbers
    if (riskScoreValue) animateValue(riskScoreValue, 0, riskScore, 1000);

    // Animate Bar
    if (riskFill) {
        riskFill.style.width = '0%';
        setTimeout(() => {
            riskFill.style.width = `${riskScore}%`;
            riskFill.style.backgroundColor = color;
        }, 100);
    }
}

function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = Math.floor(progress * (end - start) + start) + "%";
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}


window.resetForm = function () {
    const resultPanel = document.getElementById('resultPanel');
    const form = document.getElementById('fraudForm');

    if (resultPanel) resultPanel.classList.add('hidden');
    if (form) form.reset();

    // Reset time
    const now = new Date();
    const timeInput = document.getElementById('time');
    if (timeInput) timeInput.value = now.toTimeString().slice(0, 5);
}

// --- Chatbot Logic ---
let LAST_CONTEXT = {};

function setChatContext(score, factors) {
    LAST_CONTEXT = {
        riskScore: score,
        riskFactors: factors
    };
}

// UI Functions for Chatbot

function toggleChat() {
    const chatWindow = document.getElementById('chatWindow');
    chatWindow.classList.toggle('open');
}

function handleEnter(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    // 1. User Message
    appendMessage(message, 'user');
    input.value = '';

    // 2. Loading Indicator
    const processingId = 'proc-' + Date.now();
    const chatMessages = document.getElementById('chatMessages');
    const typing = document.createElement('div');
    typing.className = 'typing';
    typing.id = processingId;
    typing.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
    chatMessages.appendChild(typing);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // 3. Send to Backend
    try {
        const response = await fetch('http://localhost:5000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                context: LAST_CONTEXT
            })
        });
        const data = await response.json();

        // Remove typing
        const typingEl = document.getElementById(processingId);
        if (typingEl) typingEl.remove();

        // 4. Bot Response
        if (data.reply) {
            appendMessage(data.reply, 'bot');
        } else {
            appendMessage("I cannot speak right now.", 'bot');
        }

    } catch (error) {
        console.error("Chat Error:", error);
        const typingEl = document.getElementById(processingId);
        if (typingEl) typingEl.remove();
        appendMessage("The connection to the Vault is severed.", 'bot');
    }
}

function appendMessage(text, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    msgDiv.textContent = text;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// --- Visualizer & Logic ---
let map, mapMarker, mapPolyline;
let riskChart;
let chaosInterval = null;

function initVisuals() {
    // Fix Leaflet Icons (Common issue with CDNs)
    if (typeof L !== 'undefined') {
        delete L.Icon.Default.prototype._getIconUrl;
        L.Icon.Default.mergeOptions({
            iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
            iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
            shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
        });
    }

    // 1. Init Map
    if (document.getElementById('map')) {
        try {
            map = L.map('map').setView([22.5726, 88.3639], 4);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; OpenStreetMap &copy; CARTO',
                subdomains: 'abcd',
                maxZoom: 19
            }).addTo(map);

            // Force resize to prevent gray map
            setTimeout(() => { map.invalidateSize(); }, 200);
        } catch (e) {
            console.error("Map Init Failed:", e);
        }
    }

    // 2. Init Chart
    if (document.getElementById('riskRadar')) {
        const ctx = document.getElementById('riskRadar').getContext('2d');
        riskChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Amount', 'Frequency', 'Location', 'Time Anomaly'],
                datasets: [{
                    label: 'Transaction Risk Profile',
                    data: [10, 10, 10, 10],
                    backgroundColor: 'rgba(255, 71, 87, 0.2)',
                    borderColor: '#ff4757',
                    pointBackgroundColor: '#ff4757'
                }]
            },
            options: {
                scales: {
                    r: {
                        angleLines: { color: 'rgba(255,255,255,0.1)' },
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        pointLabels: { color: 'white' },
                        suggestedMin: 0,
                        suggestedMax: 100
                    }
                },
                plugins: {
                    legend: { labels: { color: 'white' } }
                }
            }
        });
    }
}

async function analyzeTransaction(payload) {
    setLoading(true);
    try {
        const response = await fetch('http://localhost:5000/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();

        if (data.error) {
            console.error('Error:', data.error);
            setLoading(false);
            return;
        }

        // Store Context
        setChatContext(data.riskScore, data.riskFactors);

        // Display
        displayResult(data.isFraud, data.riskScore, data.riskFactors);

        // Visuals
        updateVisuals(data, payload);

        setLoading(false);

    } catch (error) {
        console.error('Error:', error);
        setLoading(false);
    }
}

function updateVisuals(data, payload) {
    // 1. Update Map
    if (map && data.locationData) {
        map.invalidateSize(); // Ensure map is rendered size-correct
        const curr = data.locationData.current;
        const prev = data.locationData.previous;

        // Remove old layers
        if (mapMarker) map.removeLayer(mapMarker);
        if (mapPolyline) map.removeLayer(mapPolyline);

        // Add Marker
        mapMarker = L.circleMarker([curr.lat, curr.long], {
            color: data.isFraud ? '#ff4757' : '#2ea043',
            radius: 8
        }).addTo(map);

        // Draw Line if prev exists
        if (prev) {
            const latlngs = [
                [prev.lat, prev.long],
                [curr.lat, curr.long]
            ];
            const color = data.isFraud ? '#ff4757' : '#2ea043';
            mapPolyline = L.polyline(latlngs, { color: color, weight: 3, dashArray: '5, 10' }).addTo(map);
            map.fitBounds(L.latLngBounds(latlngs).pad(0.1));
        } else {
            map.setView([curr.lat, curr.long], 5);
        }
    }

    // 2. Update Chart
    if (riskChart && data.details) {
        // Normalize metrics to 0-100 for radar
        // Velocity: 0-5 -> 0-100
        const velScore = Math.min(data.details.velocity * 20, 100);
        // Amount: mock normalization relative to avg
        const amtScore = Math.min((payload.amount / (data.details.avg_spending || 1)) * 20, 100);
        // Distance: 
        const distScore = Math.min(data.details.dist_km / 10, 100);

        riskChart.data.datasets[0].data = [
            amtScore,
            velScore,
            distScore,
            data.mlScore // Time/ML score
        ];
        riskChart.data.datasets[0].borderColor = data.isFraud ? '#ff4757' : '#2ea043';
        riskChart.data.datasets[0].backgroundColor = data.isFraud ? 'rgba(255, 71, 87, 0.2)' : 'rgba(46, 160, 67, 0.2)';
        riskChart.update();
    }
}

window.toggleChaosMode = function () {
    if (chaosInterval) {
        clearInterval(chaosInterval);
        chaosInterval = null;
        alert("Chaos Mode Deactivated.");
        return;
    }

    alert("⚠ CHAOS MODE ACTIVE: Simulating Random Global Transactions...");

    chaosInterval = setInterval(() => {
        const randomAmount = Math.floor(Math.random() * 5000) + 10;
        const locs = ['local', 'domestic', 'international'];
        const randomLoc = locs[Math.floor(Math.random() * locs.length)];

        const payload = {
            amount: randomAmount,
            merchant: "Chaos Sim " + Math.floor(Math.random() * 100),
            location: randomLoc,
            time: "12:00",
            cardType: "visa"
        };

        analyzeTransaction(payload);

    }, 1500); // Every 1.5s
}

/* Mobile Menu */
window.toggleMenu = function () {
    document.querySelector('.nav-links').classList.toggle('active');
}
