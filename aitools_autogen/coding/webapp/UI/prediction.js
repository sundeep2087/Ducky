// filename: webapp/UI/prediction.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('predictionForm');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => data[key] = value);
        
        fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('predictionResult').innerHTML = `Prediction: ${data.prediction}`;
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
});