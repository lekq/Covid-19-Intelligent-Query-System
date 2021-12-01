// Code goes here
(() => {
  angular
  .module('dateRangeDemo', ['ui.bootstrap', 'rzModule'])
  .controller('dateRangeCtrl', function dateRangeCtrl($scope) {
    var vm = this;

    // Single Date Slider    
    var dates = [];
    for (var i = 1; i <= 31; i++) {
      dates.push(new Date(2016, 7, i));
    }
    $scope.slider_dates = {
      value: new Date(2016, 7, 15),
      options: {
        stepsArray: dates,
        translate: function(date) {
          if (date !== null)
            return date.toDateString();
          return '';
        }
      }
    };
   
    $scope.getvalue=function()
    {
        var time_min=$scope.dateRangeSlider.minValue;
        var dateFromMillis_min = new Date(time_min);
        
        var time_max=$scope.dateRangeSlider.maxValue;
        var dateFromMillis_max = new Date(time_max);
        
        var filteredArray=[]; 
        show_ele_date=[]; 
        $scope.start_date=publicationdate(dateFromMillis_min);
        $scope.end_date=publicationdate(dateFromMillis_max);

        var spans = document.getElementsByTagName("span");
        var match_count=0;
        for(i=0;i<spans.length;i++)
            {
                 if (spans[i].id.includes('p_date_')){
                  var p_date=document.getElementById(spans[i].id).innerHTML;
                  var p_date_millis=Date.parse(p_date); 
                  var li_id="li_"+spans[i].id.split("_")[2];
                  document.getElementById(li_id).style.display = "none";  
                  if(p_date_millis >= time_min && p_date_millis <= time_max) {
                      show_ele_date.push(li_id); 
                    
                  }
                }
             }
         if (show_ele.length>0)
          filteredArray = show_ele.filter(value => show_ele_date.includes(value)); //find array intersection between publication type and publication date
         else
          filteredArray = show_ele_date;

         match_count=0;
         for (i=0;i<filteredArray.length;i++){
                   var li_id=filteredArray[i];
                   document.getElementById(li_id).style.display = "block";
                   match_count+=1;
              }
 
        document.getElementById("search_count").innerHTML = "Found "+match_count+" articles in the date range"; 
        var rank_length=document.getElementById("rank_length").value; //clean(click) all buttons
        if (rank_length >10)
                document.getElementById('load_2').click();
        
        if (rank_length >20)
                document.getElementById('load_3').click();

    }   

 
    // Date Range Slider
    var floorDate = new Date(2019, 0, 1).getTime();
    var ceilDate = new Date(2021, 3, 30).getTime();
    var minDate = new Date(2019, 0, 1).getTime();
    var maxDate = new Date(2021, 3, 30).getTime();
    var millisInDay = 24*60*60*1000;

    var monthNames =
    [
      "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"
    ];

    var formatDate = function (date_millis)
    {
      var date = new Date(date_millis);
      return date.getDate()+"-"+monthNames[date.getMonth()]+"-"+date.getFullYear();
    }

   var publicationdate = function (date_millis)
    {
      var date = new Date(date_millis);
      var slider_date=date.getDate();
      var date_length=slider_date.toString().length;
      if (date_length==1)
       return date.getFullYear()+"-"+monthNames[date.getMonth()]+"-0"+date.getDate();
      else
       return date.getFullYear()+"-"+monthNames[date.getMonth()]+"-"+date.getDate();     
    }


    //Range slider config 
    $scope.dateRangeSlider = {
      minValue: minDate,
      maxValue: maxDate,
      options: {
        floor: floorDate,
        ceil: ceilDate,
        step: millisInDay,
        showTicks: false,
        draggableRange: true,
        translate: function(date_millis) {
          if ((date_millis !== null)) {
            var dateFromMillis = new Date(date_millis);
            // console.log("date_millis="+date_millis);
            // return dateFromMillis.toDateString();
            return publicationdate(dateFromMillis);
          }
          return '';
        }
      }
    };
    
  });
})();
