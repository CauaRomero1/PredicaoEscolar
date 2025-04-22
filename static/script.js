document.addEventListener('DOMContentLoaded', () => {
    fetch('/dashboard_data')
        .then(response => response.json())
        .then(data => {
            const dist = data.distribution_data || {};
            const pred = data.prediction_counts || {};
            const predDist = data.prediction_distribution || {};

            if (dist.age_histogram) createAgeChart(dist.age_histogram);
            if (dist.gender_bar_chart) createGenderChart(dist.gender_bar_chart);
            if (Object.keys(pred).length > 0) createPredictionChart(pred);
            if (Object.keys(predDist).length > 0) createDistributionChart(predDist);
            if (dist.parental_education) createParentalEducationChart(dist.parental_education);
            if (dist.study_time_weekly) createStudyTimeChart(dist.study_time_weekly);
            if (dist.parental_support) createParentalSupportChart(dist.parental_support);
            if (dist.extracurricular) createExtracurricularChart(dist.extracurricular);
        })

        .catch(error => console.error('Error fetching dashboard data:', error));

    const predictForm = document.getElementById('predict-form');
    const resultElement = document.getElementById('result');

    // ⬇️ Agora está no lugar certo
    const binaryFields = ['tutoring', 'parentalSupport', 'extracurricular', 'sports', 'music', 'volunteering'];

    predictForm.addEventListener('submit', (event) => {
        event.preventDefault();

        const features = [
            'age', 'gender', 'ethnicity', 'parentalEducation', 'studyTimeWeekly', 'absences'
        ].map(id => parseInt(document.getElementById(id).value));

        binaryFields.forEach(name => {
            const selected = document.querySelector(`input[name="${name}"]:checked`);
            if (selected) {
                features.push(parseInt(selected.value));
            } else {
                console.warn(`Nenhuma opção selecionada para: ${name}`);
                features.push(0); // ou outro valor padrão
            }
        });

        fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ features })
        })
            .then(response => response.json())
            .then(data => {
                resultElement.textContent = data.erro ? `Erro: ${data.erro}` : `Aluno adicionado ao banco, PREDIÇÃO: ${data.predicao}`;

            })
            .catch(error => {
                console.error('Erro ao enviar predição:', error);
                resultElement.textContent = 'Erro ao enviar predição.';
            });
    });
});

// Opções padrão para todos os gráficos
const darkChartOptions = {
    plugins: {
        legend: {
            labels: {
                color: 'white'
            }
        }
    },
    scales: {
        y: {
            beginAtZero: true,
            ticks: {
                color: 'white'
            }
        },
        x: {
            ticks: {
                color: 'white'
            }
        }
    }
};


// Gráficos
function createAgeChart(data) {
    const ctx = document.getElementById('ageChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: 'Distribuição de Idades',
                data: Object.values(data),
                backgroundColor: '#ff6384',
                borderColor: '#000000',
                borderWidth: 1
            }]
        },
        options: darkChartOptions
    });
}

function createGenderChart(data) {
    const ctx = document.getElementById('genderChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data).map(gender => {
                if (gender === '0') return 'Masculino';
                if (gender === '1') return 'Feminino';
                return 'Outro';
            }),
            datasets: [{
                data: Object.values(data),
                backgroundColor: ['#36a2eb', '#cc65fe', '#ff6384'],
                label: 'Contagem de Gênero',
                // backgroundColor: ['#ff6384'],
                borderColor: '#000000',
                borderWidth: 1
            }]
        },
        options: darkChartOptions
    });
}

function createPredictionChart(data) {
    const ctx = document.getElementById('predictionChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: 'Contagem de Predições',
                data: Object.values(data),
                backgroundColor: '#9966ff',
                borderColor: '#000000',
                borderWidth: 1
            }]
        },
        options: darkChartOptions
    });
}

function createDistributionChart(data) {
    const ctx = document.getElementById('distributionChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                label: 'Distribuição das Predições',
                // backgroundColor: ['#ff6384', '#36a2eb', '#cc65fe', '#ffce56'],
                backgroundColor: ['#ff6384'],
                borderColor: '#000000',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: 'white' },
                    position: 'top'
                },
                title: {
                    display: true,
                    color: 'white',
                    font: { size: 18 }
                }
            }
        },
        options: darkChartOptions
    });
}

function createParentalEducationChart(data) {
    const ctx = document.getElementById('parentalEducationChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                label: 'Educação dos Pais',
                backgroundColor: ['#4bc0c0'],
                borderColor: '#000000',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: 'white' },
                    position: 'top'
                },
                title: {
                    display: true,
                    color: 'white',
                    font: { size: 18 }
                }
            }
        },
        options: darkChartOptions
    });
}

function createStudyTimeChart(data) {
    const ctx = document.getElementById('studyTimeChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: 'Tempo de Estudo Semanal',
                data: Object.values(data),
                backgroundColor: '#ff9f40',
                borderColor: '#000000',
                borderWidth: 1
            }]
        },
        options: darkChartOptions
    });
}

function createParentalSupportChart(data) {
    const labels = {
        0: 'Nenhum',
        1: 'Baixo',
        2: 'Moderado',
        3: 'Alto',
        4: 'Muito Alto'
    };

    const ctx = document.getElementById('parentalSupportChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data).map(k => labels[k] || k),
            datasets: [{
                data: Object.values(data),
                label: 'Suporte dos Pais',
                backgroundColor: ['#cc65fe'],
                borderColor: '#000000',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: 'white' },
                    position: 'top'
                },
                title: {
                    display: true,
                    color: 'white',
                    font: { size: 18 }
                }
            },
        },
        options: darkChartOptions
    });
}

function createExtracurricularChart(data) {
    const ctx = document.getElementById('extracurricularChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: 'Atividades Extracurriculares',
                data: Object.values(data),
                backgroundColor: '#36a2eb',
                borderColor: '#000000',
                borderWidth: 1
            }]
        },
        options: darkChartOptions
    });
}
