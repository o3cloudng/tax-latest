const ctx2 = document.getElementById('distribution').getContext('2d')

const sectorData = {
  labels: ["Banks", "Telecoms", "Multimedia", "Religion", "Government"],

  datasets: [
    {
      data: [30, 20, 15, 10, 25],

      backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4CAF50", "#9C27B0"],
    },
  ],
};

const config = {
  type: 'doughnut',
  data: sectorData,
  options: {
    plugins: {
      title: {
        display: true,
        text: 'Sectors Distribution Distribution',
      },
    },
  },
}

new Chart(ctx2, config)
