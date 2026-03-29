// filename: webapp/UI/predict.js
document.getElementById('predictionForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
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
        document.getElementById('predictionResult').innerHTML = `Prediction: ${data.prediction ? 'Survived' : 'Did Not Survive'}`;
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});