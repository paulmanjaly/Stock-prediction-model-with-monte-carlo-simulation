let chart;
let sparklineChart;

async function getPrediction() {
    const symbol = document.getElementById("stockInput").value.trim().toUpperCase();
    if (!symbol) return alert("Enter a stock symbol");

    try {
        const res = await fetch(`http://127.0.0.1:8000/predict/${symbol}`);
        if (!res.ok) throw new Error("API error");

        const data = await res.json();
        console.log("API response:", data);

        const price = parseFloat(data.last_price);
        const predictedTomorrow = parseFloat(data.predicted_price_tomorrow);
        const prob = parseFloat(data.probability_up_tomorrow);
        const expectedReturn = parseFloat(data.expected_return) * 100;
        const predictedMove = parseFloat(data.predicted_return_pct);
        const predictedVol = parseFloat(data.predicted_volatility_pct);

        const probColor = prob >= 0.5 ? "#16a34a" : "#dc2626";
        const returnColor = expectedReturn >= 0 ? "#16a34a" : "#dc2626";
        const moveColor = predictedMove >= 0 ? "#16a34a" : "#dc2626";

        document.getElementById("result").innerHTML = `
            <b>Last Price:</b> $${price.toFixed(2)} <br>
            <b>Estimated Price Tomorrow:</b> 
            <span style="color:${moveColor}">
                $${predictedTomorrow.toFixed(2)}
            </span><br>
            <b>Predicted Move Tomorrow:</b> 
            <span style="color:${moveColor}">
                ${predictedMove.toFixed(2)}%
            </span><br>
            <b>Predicted Volatility:</b> ${predictedVol.toFixed(2)}% <br>
            <b>Probability Up Tomorrow:</b> 
            <span style="color:${probColor}">
                ${(prob * 100).toFixed(2)}%
            </span><br>
            <b>Expected 30-Day Return (MC):</b>
            <span style="color:${returnColor}">
                ${expectedReturn.toFixed(2)}%
            </span>
        `;

        drawChart(
            data.monte_carlo_avg_path.map(Number),
            data.mc_lower_band.map(Number),
            data.mc_upper_band.map(Number)
        );

        if (Array.isArray(data.historical_prices)) {
            drawSparkline(data.historical_prices.map(Number));
        }

    } catch (err) {
        console.error(err);
        alert("Prediction failed. Check backend.");
    }
}

/* Monte Carlo Chart with Confidence Bands */
function drawChart(avgPath, lowerBand, upperBand) {
    const ctx = document.getElementById("chart").getContext("2d");
    if (chart) chart.destroy();

    chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: avgPath.map((_, i) => `Day ${i + 1}`),
            datasets: [
                {
                    label: "Upper Confidence (90%)",
                    data: upperBand,
                    borderColor: "rgba(37, 99, 235, 0.2)",
                    pointRadius: 0,
                    fill: false
                },
                {
                    label: "Lower Confidence (10%)",
                    data: lowerBand,
                    borderColor: "rgba(37, 99, 235, 0.2)",
                    backgroundColor: "rgba(37, 99, 235, 0.12)",
                    pointRadius: 0,
                    fill: "-1"
                },
                {
                    label: "Average Forecast Path",
                    data: avgPath,
                    borderColor: "#2563eb",
                    borderWidth: 2,
                    tension: 0.3,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: true }
            }
        }
    });
}

/* Historical Sparkline */
function drawSparkline(prices) {
    const ctx = document.getElementById("sparklineChart").getContext("2d");
    if (sparklineChart) sparklineChart.destroy();

    sparklineChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: prices.map((_, i) => i),
            datasets: [{
                data: prices,
                borderColor: "#00b386",
                borderWidth: 2,
                pointRadius: 0,
                tension: 0.3,
                fill: false
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { x: { display: false }, y: { display: false } }
        }
    });
}

/* Autocomplete Search */
async function searchStocks(query) {
    if (query.length < 2) {
        document.getElementById("suggestions").innerHTML = "";
        return;
    }

    try {
        const res = await fetch(`http://127.0.0.1:8000/search/${query}`);
        const data = await res.json();

        document.getElementById("suggestions").innerHTML = data.map(q => `
            <div class="suggestion-item" onclick="selectStock('${q.symbol}')">
                <strong>${q.symbol}</strong> — ${q.name || ""}
            </div>
        `).join("");
    } catch (err) {
        console.error("Search error:", err);
    }
}

function selectStock(symbol) {
    document.getElementById("stockInput").value = symbol;
    document.getElementById("suggestions").innerHTML = "";
}
