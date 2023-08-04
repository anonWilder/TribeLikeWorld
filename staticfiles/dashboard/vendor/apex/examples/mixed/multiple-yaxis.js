var options = {
	chart: {
		height: 320,
		type: 'line',
		stacked: false,
		toolbar: {
			show: false,
		},
	},
	dataLabels: {
		enabled: false
	},
	series: [{
		name: 'Orders',
		type: 'column',
		data: [4, 2, 2, 5, 6, 8, 8, 7]
	},{
		name: 'Sales',
		type: 'column',
		data: [2, 3, 1, 4, 5, 9, 5, 8]
	},{
		name: 'Revenue',
		type: 'line',
		data: [20, 10, 15, 36, 44, 45, 50, 58]
	}],
	stroke: {
		width: [1, 1, 3]
	},
	title: {
		text: 'Overall income in millon dollors form online and offline sales from 2010 to 2018.',
		align: 'center',
	},
	colors: ['#aa0000', '#ee0000', '#666666'],
	xaxis: {
		categories: [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018],
	},
	yaxis: [{
		axisTicks: {
			show: true,
		},
		axisBorder: {
			show: true,
			color: '#aa0000'
		},
		labels: {
			style: {
				color: '#aa0000',
			}
		},
		title: {
			text: "Orders (in thousands)",
			style: {
				color: '#aa0000',
			}
		},
		tooltip: {
			enabled: true
		}
	},{
			seriesName: 'Orders',
			opposite: true,
			axisTicks: {
				show: true,
			},
			axisBorder: {
				show: true,
				color: '#ee0000'
			},
			labels: {
				style: {
					color: '#ee0000',
				}
			},
			title: {
				text: "Sales (in thousand)",
				style: {
					color: '#ee0000',
				}
			},
		},{
			seriesName: 'Revenue',
			opposite: true,
			axisTicks: {
				show: true,
			},
			axisBorder: {
				show: true,
				color: '#333333'
			},
			labels: {
				style: {
					color: '#333333',
				},
			},
			title: {
				text: "Revenue (in crores)",
				style: {
					color: '#333333',
				}
			}
		},
	],
	legend: {
		horizontalAlign: 'center',
		offsetY: -5
	}
}

var chart = new ApexCharts(
	document.querySelector("#multiple-yaxis"),
	options
);
chart.render();