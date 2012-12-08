/*** Gray theme for Highcharts JS - @author Torstein HÃ¸nsi ***/

Highcharts.theme = {
	colors: ["#c1d177", "#0e3d59", "#9d7cbb", "#d92525", "#d7ad63", "#ff0066", "#eeaaee", 
		"#55BF3B", "#DF5353", "#7798BF", "#aaeeee"],
	chart: {
		borderWidth: 0,
		borderRadius: 10,
		plotBackgroundColor: null,
		plotBorderWidth: 0
	},
	title: {
		style: { 
			color: '#000',
			font: '16px Arial, Helvetica, sans-serif',
		}
	},
	subtitle: {
		style: { 
			color: '#000',
			font: '12px Arial, Helvetica, sans-serif'
		}
	},
	xAxis: {
		gridLineWidth: 0,
		lineColor: '#a1adb3',
		labels: {
			style: {
				color: '#4c453d',
				fontWeight: 'normal'
			}
		},
		title: {
			style: {
				color: '#000',
				font: 'bold 12px Arial, Helvetica, sans-serif'
			}				
		}
	},
	yAxis: {
		alternateGridColor: null,
		minorTickInterval: null,
		gridLineColor: '#a1adb3',
		lineWidth: 0,
		tickWidth: 0,
		labels: {
			style: {
				color: '#4c453d',
				fontWeight: 'normal'
			}
		},
		title: {
			style: {
				color: '#000',
				font: 'bold 12px Arial, Helvetica, sans-serif'
			}				
		}
	},
	legend: {
		backgroundColor: '#4D5357',

		itemStyle: {
			color: '#8a9499'
		},
		itemHoverStyle: {
			color: '#F1F3EB'
		},
		itemHiddenStyle: {
			color: '#42474a'
		}
	},
	labels: {
		style: {
			color: '#CCC'
		}
	},
	tooltip: {
		backgroundColor: '#F1F3EB',
		borderWidth: 0,
		style: {
			color: '#4D5357'
		}
	},
	
	
	plotOptions: {
		line: {
			dataLabels: {
				color: '#CCC'
			},
			marker: {
				lineColor: '#333'
			}
		},
		spline: {
			marker: {
				lineColor: '#333'
			}
		},
		scatter: {
			marker: {
				lineColor: '#333'
			}
		},
		candlestick: {
			lineColor: 'white'
		}
	},
	
	toolbar: {
		itemStyle: {
			color: '#CCC'
		}
	},
	
	navigation: {
		buttonOptions: {
			backgroundColor: {
				linearGradient: [0, 0, 0, 20],
				stops: [
					[0.4, '#606060'],
					[0.6, '#333333']
				]
			},
			borderColor: '#000000',
			symbolStroke: '#C0C0C0',
			hoverSymbolStroke: '#FFFFFF'
		}
	},
	
	exporting: {
		buttons: {
			exportButton: {
				symbolFill: '#55BE3B'
			},
			printButton: {
				symbolFill: '#7797BE'
			}
		}
	},
	
	// scroll charts
	rangeSelector: {
		buttonTheme: {
			fill: {
				linearGradient: [0, 0, 0, 20],
				stops: [
					[0.4, '#888'],
					[0.6, '#555']
				]
			},
			stroke: '#000000',
			style: {
				color: '#CCC',
				fontWeight: 'bold'
			},
			states: {
				hover: {
					fill: {
						linearGradient: [0, 0, 0, 20],
						stops: [
							[0.4, '#BBB'],
							[0.6, '#888']
						]
					},
					stroke: '#000000',
					style: {
						color: 'white'
					}
				},
				select: {
					fill: {
						linearGradient: [0, 0, 0, 20],
						stops: [
							[0.1, '#000'],
							[0.3, '#333']
						]
					},
					stroke: '#000000',
					style: {
						color: 'yellow'
					}
				}
			}					
		},
		inputStyle: {
			backgroundColor: '#333',
			color: 'silver'
		},
		labelStyle: {
			color: 'silver'
		}
	},
	
	navigator: {
		handles: {
			backgroundColor: '#666',
			borderColor: '#AAA'
		},
		outlineColor: '#CCC',
		maskFill: 'rgba(16, 16, 16, 0.5)',
		series: {
			color: '#7798BF',
			lineColor: '#A6C7ED'
		}
	},
	
	scrollbar: {
		barBackgroundColor: {
				linearGradient: [0, 0, 0, 20],
				stops: [
					[0.4, '#888'],
					[0.6, '#555']
				]
			},
		barBorderColor: '#CCC',
		buttonArrowColor: '#CCC',
		buttonBackgroundColor: {
				linearGradient: [0, 0, 0, 20],
				stops: [
					[0.4, '#888'],
					[0.6, '#555']
				]
			},
		buttonBorderColor: '#CCC',
		rifleColor: '#FFF',
		trackBackgroundColor: {
			linearGradient: [0, 0, 0, 10],
			stops: [
				[0, '#000'],
				[1, '#333']
			]
		},
		trackBorderColor: '#666'
	},
	
	// special colors for some of the demo examples
	legendBackgroundColor: 'rgba(48, 48, 48, 0.8)',
	legendBackgroundColorSolid: 'rgb(70, 70, 70)',
	dataLabelsColor: '#444',
	textColor: '#E0E0E0',
	maskColor: 'rgba(255,255,255,0.3)'
};

// Apply the theme
var highchartsOptions = Highcharts.setOptions(Highcharts.theme);

//----------------------------------------------------------

/*** First Chart in Dashboard page / Second Chart in Charts.html ***/

	$(document).ready(function() {
		info = new Highcharts.Chart({
			chart: {
				renderTo: 'money',
				margin: [0, 0, 0, 0],
				backgroundColor: null,
                plotBackgroundColor: 'none',
							
			},
			
			title: {
				text: null
			},

			tooltip: {
				formatter: function() { 
					return this.point.name +': '+ this.y +' %';
						
				} 	
			},
		    series: [
				{
				borderWidth: 2,
				borderColor: '#F1F3EB',
				shadow: false,	
				type: 'pie',
				name: 'Income',
				innerSize: '50%',
				data: [
					{ name: 'Subscriptions', y: 35.0, color: '#62c462' },
					{ name: 'Sales', y: 35.0, color: '#a8ca42' },
					{ name: 'Referrals', y: 8.3, color: '#2f9734' },
					{ name: 'Donations', y: 3.3, color: '#edb836' },
					{ name: 'Other', y: 1.6, color: '#8A9499' },
					{ name: 'eBay', y: 16.6, color: '#6eb042' }
				],
				dataLabels: {
					enabled: false,
					color: '#000000',
					connectorColor: '#000000'
				}
			}]
		});
		
	});

/*** second Chart in Dashboard page / Third chart in charts.html ***/

	$(document).ready(function() {
		info = new Highcharts.Chart({
			chart: {
				renderTo: 'site',
				margin: [0, 0, 0, 0],
				backgroundColor: null,
                plotBackgroundColor: 'none',
							
			},
			
			title: {
				text: null
			},

			tooltip: {
				formatter: function() { 
					return this.point.name +': '+ this.y +' %';
						
				} 	
			},
		    series: [
				{
				borderWidth: 2,
				borderColor: '#F1F3EB',
				shadow: false,	
				type: 'pie',
				name: 'SiteInfo',
				innerSize: '50%',
				data: [
					{ name: 'Visits', y: 65.0, color: '#d84436' },
					{ name: 'Rest', y: 35.0, color: '#babab8' }
				],
				dataLabels: {
					enabled: false,
					color: '#000000',
					connectorColor: '#000000'
				}
			}]
		});
		
	});

/*** third Chart in Dashboard page / Fourth chart in charts.html ***/

	$(document).ready(function() {
		info = new Highcharts.Chart({
			chart: {
				renderTo: 'users',
				margin: [0, 0, 0, 0],
				backgroundColor: null,
                plotBackgroundColor: 'none',
							
			},
			
			title: {
				text: null
			},

			tooltip: {
				formatter: function() { 
					return this.point.name +': '+ this.y +' %';
						
				} 	
			},
		    series: [
				{
				borderWidth: 2,
				borderColor: '#F1F3EB',
				shadow: false,	
				type: 'pie',
				name: 'TotalUsers',
				innerSize: '50%',
				data: [
					{ name: 'Users', y: 85.0, color: '#08c6d4' },
					{ name: 'Rest', y: 15.0, color: '#babab8' }
				],
				dataLabels: {
					enabled: false,
					color: '#000000',
					connectorColor: '#000000'
				}
			}]
		});
		
	});
	
/*** Chart in charts.html example. ***/

/*** First Chart in Chart page ***/


	$(document).ready(function() {
		info = new Highcharts.Chart({
			chart: {
				renderTo: 'otherstat',
				margin: [0, 0, 0, 0],
				backgroundColor: null,
                plotBackgroundColor: 'none',
							
			},
			
			title: {
				text: null
			},

			tooltip: {
				formatter: function() { 
					return this.point.name +': '+ this.y +' %';
						
				} 	
			},
		    series: [
				{
				borderWidth: 2,
				borderColor: '#F1F3EB',
				shadow: false,	
				type: 'pie',
				name: 'otherstat',
				innerSize: '50%',
				data: [
					{ name: 'Users', y: 75.0, color: '#ff6e01' },
					{ name: 'Rest', y: 25.0, color: '#babab8' }
				],
				dataLabels: {
					enabled: false,
					color: '#000000',
					connectorColor: '#000000'
				}
			}]
		});
		
	});
/*** CHART EXAMPLE Nº 5 ***/

		var heartratewrapper = new Highcharts.Chart({
			chart: {
				renderTo: 'chartline',
				defaultSeriesType: 'line',
				marginRight: 10,
				marginBottom: 30,
				backgroundColor:'rgba(255, 255, 255, 0.1)'

			},
			title: {
				text: null
			},
			subtitle: {
				text: null
			},
			xAxis: {
				categories: ['9am','10am', '11am', '12pm', '1pm', '2pm', '3pm', '4pm', '5pm', 
					'6pm', '7pm', '8pm', '9pm']
			},
			yAxis: {
				title: {
					text: null
				},
				plotLines: [{
					value: 0,
					width: 1,
					color: '#808080'
					
				}]
			},
			tooltip: {
				formatter: function() {
					return ''+
						 this.x +': '+ this.y +' visits';
				}
			},
			
			plotOptions: {
				line: {
					lineWidth: 7,
					marker: {
						enabled: false
					}
				}
			},
			
			legend: {
				enabled: false
			},
			series: [{
				name: 'Tokyo',
				shadow: false,	

				data: [60, 80, 110, 70, 90, 100, 80, 80, 60, 90, 100, 90, 110]
			}]
		});


/*** CHART EXAMPLE Nº 6 ***/

	var sleepwrapper = new Highcharts.Chart({
			chart: {
				renderTo: 'chartbars',
				defaultSeriesType: 'column',
				marginBottom: 30,
				backgroundColor:'rgba(255, 255, 255, 0.1)'


			},
			title: {
				text: null
			},
			xAxis: {
				categories: ['Sun', 'Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat']
			},
			yAxis: {
				min: 0,
				title: {
					text: null
				},
				stackLabels: {
					enabled: false,
					
				}
			},
			legend: {
				enabled: false
			},
			tooltip: {
				formatter: function() {
					return '<b>'+ this.x +'</b><br/>'+
						 
						 'Total: '+ this.point.stackTotal;
				}
			},
			plotOptions: {
				column: {
					stacking: 'normal',
					dataLabels: {
						enabled: false,

					}
				}
			},
		    series: [
			
			{							
				name: 'set 1',
				data: [0, 0, 0, 0, 0, 0, 0]
			}, {
				borderWidth: 2,
				name: 'blue',
				data: [18, 0, 0, 0, 0, 8, 24]

			}, {
				name: 'set 2',
				data: [0, 0, 0, 0, 0, 0, 0]
			}, {
				borderWidth: 2,
				name: 'red',
				data: [0, 14, 16, 6, 27, 0, 0]

			}
			
			
			]
		});
		
