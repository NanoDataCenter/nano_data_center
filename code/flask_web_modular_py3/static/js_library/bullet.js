(function($){
	
	$.fn.bullet = function(params) { //Create the bullet plugin.
		
		params = $.extend({
							theWidth: this.width(),
							minValue: 0,
							maxValue: 100,
							featuredMeasure: 50,
							numberTicks: 40 //Specify the number of ticks between the first and last - unused at the moment.  (A) - add.
							}, params);		
		
                
		//Set values
		var scaleLength = params.maxValue - params.minValue;
		var chartWidth = this.width(); // 15px padding * 2 (for each side of the chart)
		var chartHeight = this.height() ;
		var eachUnit = chartWidth/scaleLength;
              
		var featuredLength = eachUnit * params.featuredMeasure;
		var comp1pos = eachUnit * params.compMeasure1;
		var qual1pos = eachUnit * params.qualScale1;
                
		//Set context
		var context = this[0].getContext("2d"); //Get the drawing context.
		context.font="15px sans-serif";
		//Drawing routine
		//Note to self:  Decimal values are percentages of the canvas element as defined in sketches.
		
		//Draw chart background (half of the canvas height)
		context.fillStyle = "Grey";
            
		context.fillRect(70,0,chartWidth,chartHeight );

		//Draw qualitative scale (half of the canvas height)
		if (params.qualScale1) {
			context.fillStyle = params.qualScale1Color
			context.fillRect(70, 0,qual1pos,chartHeight );
		}
	        
		//Comparative measure 1.  Only show if the parameter is provided.
		if (params.compMeasure1) {
			context.fillStyle = "Red";
			context.fillRect(100+comp1pos-1.5,chartHeight * 0.08,3,chartHeight*0.34); //1.5 is half the width of the featured marker.
		}
	        
		//Featured measure - appears in front of the comparative measure, according to the specification.
		context.fillStyle= "#FFA500"
                var featuredLength = eachUnit * params.featuredMeasure[0];
		context.fillRect(70,chartHeight * 0.85,featuredLength,chartHeight * 0.1);
                context.fillStyle= "#FFA510"
                var featuredLength = eachUnit * params.featuredMeasure[1];
                context.fillRect(70,chartHeight * 0.75,featuredLength,chartHeight * 0.1);
                context.fillStyle= "#FFA520"
                var featuredLength = eachUnit * params.featuredMeasure[2];
                context.fillRect(70,chartHeight * 0.65,featuredLength,chartHeight * 0.1);
                context.fillStyle= "#FFA530"
                var featuredLength = eachUnit * params.featuredMeasure[3];
                context.fillRect(70,chartHeight * 0.55,featuredLength,chartHeight * 0.1);
                context.fillStyle= "#FFA540"
                var featuredLength = eachUnit * params.featuredMeasure[4];
                context.fillRect(70,chartHeight * 0.45,featuredLength,chartHeight * 0.1);
                context.fillStyle= "#FFA550"
                var featuredLength = eachUnit * params.featuredMeasure[5];
                context.fillRect(70,chartHeight * 0.35,featuredLength,chartHeight * 0.1);
                context.fillStyle= "#FFA560"
                var featuredLength = eachUnit * params.featuredMeasure[6];
                context.fillRect(70,chartHeight * 0.25,featuredLength,chartHeight * 0.1);
                context.fillStyle= "#FFA570"
                var featuredLength = eachUnit * params.featuredMeasure[7];
                context.fillRect(70,chartHeight * 0.15,featuredLength,chartHeight * 0.1);
                context.fillStyle= "#FFA580"
                var featuredLength = eachUnit * params.featuredMeasure[8];
                context.fillRect(70,chartHeight * 0.05,featuredLength,chartHeight * 0.1);
                

                
                context.fillStyle= "GREEN"
               
                var i;
                for( i = 1; i< 100; i++ )
                {
                   if( (i*eachUnit*1)+70 <= chartWidth )
                   {
                     context.fillRect( (eachUnit*1*i)+70, 0, 1,chartHeight)
                   }
                   else
                   {
                      break;
                    }
                 }
               context.fillStyle= "RED"
               
                var i;
                for( i = 1; i< 100; i++ )
                {
                   if( (i*eachUnit*5)+70 <= chartWidth )
                   {
                     context.fillRect( (eachUnit*5*i)+70, 0, 1,chartHeight)
                   }
                   else
                   {
                      break;
                    }
                 }

		//Draw ticks and labels.  Will need to calculate how they appear on the chart and add some padding (15-20px on either side).
		//context.fillStyle = "Red";
		//context.fillRect(15,chartHeight * 0.5, 1, chartHeight * 0.20);
		//context.fillRect(14+chartWidth,chartHeight * 0.5,1,chartHeight * 0.20);
		//context.fillRect(14+(chartWidth*0.5),chartHeight * 0.5,1,chartHeight * 0.20);
		context.fillStyle = "Black"
		//Labels (beginning and end of scale)
		context.textAlign = "left";
		//context.fillText(params.minValue,16,(chartHeight * 0.70)+10); //Add 10 pixel gap between tick and label.
                context.fillText(params.titleText,10,chartHeight*.3);
                //context.textAlign = "right";
		//context.fillText(params.maxValueText, chartWidth,(chartHeight * 0.55)+10);
		//context.fillText(params.maxValue/2,15+(chartWidth*0.5),(chartHeight * 0.70)+10);

		return this.each(function() {
		
		});
	}
	
})(jQuery);
