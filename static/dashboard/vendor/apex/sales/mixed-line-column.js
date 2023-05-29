var options = {
  series: [{
    name: 'Sales',
    type: 'area',
    data: [200, 370, 50, 250, 650, 150, 400]
  }, {
    name: 'Income',
    type: 'line',
    data: [25, 42, 10, 30, 70, 20, 45]
  }],
  chart: {
    height: 300,
    type: 'area',
    zoom: {
      enabled: false
    },
    toolbar: {
      show: false
    },
  },
  stroke: {
    width: [0, 4],
    curve: 'smooth',
  },
  dataLabels: {
    enabled: true,
    enabledOnSeries: [1]
  },
  labels: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
  colors: ['#999999', '#ee0000'],
  xaxis: {
    type: 'day'
  },
  yaxis: [{
  }, {
    opposite: true,
  }]
};

var chart = new ApexCharts(document.querySelector("#mixed-line-column"), options);
chart.render();