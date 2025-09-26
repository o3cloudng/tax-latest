const ctx5 = document.getElementById('disputedDn').getContext('2d')

const dnData = {
  labels: ['Resolved', 'Unresolved'],

  datasets: [
    {
      data: [60, 40],

      backgroundColor: ['#FF6384', '#36A2EB'],
    },
  ],
}

const config3 = {
  type: 'pie',
  data: dnData,
  options: {
    plugins: {
      title: {
        display: true,
        text: 'Disputed Demand Notice',
      },
    },
  },
}

new Chart(ctx5, config3)
