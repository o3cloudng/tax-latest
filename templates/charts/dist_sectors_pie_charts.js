const ctx2 = document.getElementById('distribution').getContext('2d')
let sector_name = selectedElement.dataset.sector_name;
let sector_count = selectedElement.dataset.sector_count;
console.log(sector_name)
console.log(sector_count)
const sectorData = {
  labels: sector_name,

  datasets: [
    {
      data: sector_count,

      backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4CAF50', '#9C27B0'],
    },
  ],
}

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
