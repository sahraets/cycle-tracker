const resultSection = document.getElementById('result');
const statusCircle = document.getElementById('status-circle');
const statusText = document.getElementById('status-text');
const cycleDay = document.getElementById('cycle-day');
const coverlineEl = document.getElementById('coverline');
const logBtn = document.getElementById('log-btn');

// Save entry and check fertility status
logBtn.addEventListener('click', async () => {
    const temperature = document.getElementById('temperature').value;
    const date = document.getElementById('date').value;
    const menstruation = document.getElementById('menstruation').checked;

    if (!temperature || !date) {
        alert('Please enter both temperature and date');
        return;
    }

    try {
        const logResponse = await fetch('http://127.0.0.1:5001/api/log', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({temperature, date, menstruation})
        });

        const logData = await logResponse.json();

        if (logData.error) {
            alert(logData.error);
            return;
        }

        const predictResponse = await fetch('http://127.0.0.1:5001/api/predict', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({temperature, date})
        });

        const data = await predictResponse.json();

        resultSection.style.display = 'block';

        if (data.fertile) {
            statusCircle.style.backgroundColor = '#e74c3c';
            statusText.textContent = '🔴 Fertile day';
        } else {
            statusCircle.style.backgroundColor = '#2ecc71';
            statusText.textContent = '🟢 Not fertile';
        }

        cycleDay.textContent = `Cycle day: ${data.cycle_day}`;
        coverlineEl.textContent = `Coverline: ${data.coverline.toFixed(2)}°C`;
    } catch (error) {
        alert('Could not connect to API. Is Flask running?');
    }
});