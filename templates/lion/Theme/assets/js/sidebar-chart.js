/*** Chart used in Sidebar Demostration / Second Chart in Charts.html ***/

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

