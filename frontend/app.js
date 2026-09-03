const API = 'http://127.0.0.1:5001';

const resultSection = document.getElementById('result');
const statusCircle = document.getElementById('status-circle');
const statusText = document.getElementById('status-text');
const cycleDay = document.getElementById('cycle-day');
const coverlineEl = document.getElementById('coverline');
const logBtn = document.getElementById('log-btn');
const messageEl = document.getElementById('message');
const dateInput = document.getElementById('date');

// Default the date field to today
dateInput.value = new Date().toLocaleDateString('sv-SE');

function showMessage(text) {
    messageEl.textContent = text;
    messageEl.hidden = false;
}

function clearMessage() {
    messageEl.hidden = true;
}

// Flask returns an HTML error page on a 500, so don't blindly call .json()
async function readJson(response) {
    try {
        return await response.json();
    } catch {
        return {error: `Server error (${response.status}). Check the Flask log.`};
    }
}

// Save entry and check fertility status
logBtn.addEventListener('click', async () => {
    const temperature = document.getElementById('temperature').value;
    const date = dateInput.value;
    const menstruation = document.getElementById('menstruation').checked;

    clearMessage();

    if (!temperature || !date) {
        showMessage('Please enter both temperature and date.');
        return;
    }

    logBtn.disabled = true;
    logBtn.textContent = 'Saving…';

    try {
        const logResponse = await fetch(`${API}/api/log`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({temperature, date, menstruation})
        });

        const logData = await readJson(logResponse);

        if (logData.error) {
            showMessage(logData.error);
            return;
        }

        const predictResponse = await fetch(`${API}/api/predict`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({temperature, date})
        });

        const data = await readJson(predictResponse);

        if (data.error) {
            showMessage(data.error);
            return;
        }

        resultSection.hidden = false;

        if (data.fertile) {
            statusCircle.style.backgroundColor = 'var(--fertile)';
            statusText.textContent = 'Fertile day';
        } else {
            statusCircle.style.backgroundColor = 'var(--not-fertile)';
            statusText.textContent = 'Not fertile';
        }

        cycleDay.textContent = data.cycle_day ?? '–';
        coverlineEl.textContent =
            typeof data.coverline === 'number' ? `${data.coverline.toFixed(2)} °C` : '–';
    } catch (error) {
        showMessage('Could not reach the API. Is Flask running on port 5001?');
    } finally {
        logBtn.disabled = false;
        logBtn.textContent = 'Save & check fertility';
    }
});
