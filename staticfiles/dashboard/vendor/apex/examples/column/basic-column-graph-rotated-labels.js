var options = {
  annotations: {
    points: [{
      x: 'Burgers',
      seriesIndex: 0,
      label: {
        borderColor: '#ee0000',
        offsetY: 0,
        style: {
          color: '#ffffff',
          background: '#ee0000',
          textSize: '10px',
        },
        text: 'Great Sales',
      }
    }]
  },
  chart: {
    height: 380,
    type: "bar",
    toolbar: {
      show: true,
    },
  },
  plotOptions: {
    bar: {
      columnWidth: '50%',
      endingShape: 'rounded'
    }
  },
  dataLabels: {
    enabled: false
  },
  stroke: {
    width: 1
  },
  series: [{
    name: 'Servings',
    data: [44, 55, 41, 67, 22, 43, 21, 33, 45, 31, 87, 65, 35, 25]
  }],
  grid: {
    row: {
      colors: ['#f5f9fe', '#ffffff']
    }
  },
  xaxis: {
    labels: {
      rotate: -45
    },
    categories: ['Apples', 'Oranges', 'Strawberries', 'Pineapples', 'Mangoes', 'Burgers',
      'Blackberries', 'Pears', 'Watermelons', 'Cherries', 'Pomegranates', 'Tangerines', 'Papayas', 'Peaches'
    ],
  },
  yaxis: {
    labels: {
      show: false,
    },
    axisBorder: {
      show: false,
    },
  },
  theme: {
    monochrome: {
      enabled: true,
      color: '#ee0000',
      shadeIntensity: 0.1
    },
  },
  fill: {
    type: 'gradient',
    gradient: {
      shade: 'light',
      type: "horizontal",
      colors: ['#aa0000', '#cc0000', '#ee0000', '#ff3333', '#ff7777'],
      shadeIntensity: 0.25,
      inverseColors: true,
      opacityFrom: 0.75,
      opacityTo: 0.85,
      stops: [50, 100]
    },
  },
  title: {
    text: 'February, 2019 Sales',
    floating: true,
    align: 'center',
    style: {
      color: '#444'
    }
  },
}

var chart = new ApexCharts(
  document.querySelector("#basic-column-graph-rotated-labels"),
  options
);

chart.render();