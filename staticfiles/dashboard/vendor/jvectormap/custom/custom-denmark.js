// Denmark
$(function(){
	$('#mapDenmark').vectorMap({
		map: 'dk_mill',
		zoomOnScroll: false,
		regionStyle:{
			initial: {
				fill: '#ee0000',
			},
			hover: {
				"fill-opacity": 0.8
			},
			selected: {
				fill: '#aa0000'
			},
		},
		backgroundColor: 'transparent',
	});
});