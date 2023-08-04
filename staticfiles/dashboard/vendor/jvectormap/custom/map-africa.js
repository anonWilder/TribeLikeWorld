// Africa
$(function(){
	$('#mapAfrica').vectorMap({
		map: 'africa_mill',
		backgroundColor: 'transparent',
		scaleColors: ['#FF7E39'],
		zoomOnScroll:false,
		zoomMin: 1,
		hoverColor: true,
		series: {
			regions: [{
				values: gdpData,
				scale: ['#aa0000', '#cc0000', '#ee0000', '#ff3333', '#ff7777'],
				normalizeFunction: 'polynomial'
			}]
		},
	});
});