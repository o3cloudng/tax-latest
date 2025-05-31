const ctx3 = document.getElementById('infrastructure').getContext('2d')

const infraData = {
  labels: ['Mast', 'Fibre', 'Powerline', 'Pipeline', 'Row Gas'],

  datasets: [
    {
      data: [30, 20, 15, 10, 25],

      backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4CAF50', '#9C27B0'],
    },
  ],
}

const config2 = {
  type: 'pie',
  data: infraData,
  options: {
    plugins: {
      title: {
        display: true,
        text: 'Infrastructure Distribution',
      },
    },
  },
}

new Chart(ctx3, config2)
