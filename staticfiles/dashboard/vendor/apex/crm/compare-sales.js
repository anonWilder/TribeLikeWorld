var options = {
	chart: {
		height: 240,
		type: 'area',
		toolbar: {
			show: false,
		},
	},
	dataLabels: {
		enabled: false
	},
	stroke: {
		curve: 'smooth',
		width: 3
	},
	series: [{
		name: 'Sales',
		data: [200, 450, 200, 400]
	}],
	grid: {
		row: {
			colors: ['transparent'], // takes an array which will be repeated on columns
			opacity: 0.5,
		},
		xaxis: {
      lines: {
        show: false
      }
    },   
    yaxis: {
      lines: {
        show: false
      }
    },
	},
	xaxis: {
		categories: ['Pizzas', 'Burgers', 'Sandwich', 'Coffee'],
		// labels: {
	 //    show: false
	 //  }
	},
	colors: ['#ee0000', '#333333'],
	markers: {
		size: 5,
		opacity: 0.2,
		colors: ["#ee0000"],
		strokeColor: "#ffffff",
		strokeWidth: 2,
		hover: {
			size: 7,
		}
	},
	tooltip: {
		y: {
			formatter: function(val) {
				return  "$" + val + 'k'
			}
		}
	},
}

var chart = new ApexCharts(
	document.querySelector("#compare-sales"),
	options
);

chart.render();
