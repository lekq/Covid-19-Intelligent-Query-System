// <script src="/static/js/FormHandling.js"></script>
// <!-- <script>
// 		console.log($siteFiles);
// 		function buildHtmlTable(selector) {
// 			var columns = addAllColumnHeaders($siteFiles, selector);

// 		  	for (var i = 0; i < $siteFiles.length; i++) {
// 		    	var row$ = $('<tr/>');
// 		    for (var colIndex = 0; colIndex < columns.length; colIndex++) {
// 		      	var cellValue = $siteFiles[i][columns[colIndex]];
// 		      	if (cellValue == null) cellValue = "";
// 		      		row$.append($('<td/>').html(cellValue));
// 		    	}
// 		    $(selector).append(row$);
// 		  	}
// 		}

// 		// Adds a header row to the table and returns the set of columns.
// 		// Need to do union of keys from all records as some records may not contain
// 		// all records.
// 		function addAllColumnHeaders($siteFiles, selector) {
// 			var columnSet = [];
// 			var headerTr$ = $('<tr/>');

// 			for (var i = 0; i < $siteFiles[children].length; i++) {
// 			    var rowHash = $siteFiles[children][i];
// 			    for (var key in rowHash) {
// 			      	if ($.inArray(key, columnSet) == -1) {
// 			        	columnSet.push(key);
// 			        	headerTr$.append($('<th/>').html(key));
// 			      	}
// 			    }
// 			}
// 			$(selector).append(headerTr$);

// 			return columnSet;
// 		}
// 	</script> -->

// 	<!-- <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script> -->
// 	<!-- <script>
// 		var whiteList = {
// 			"&#39;":"'",
// 			"&#38;":"&"
// 		};
// 		var specialCharDecoder = /&#39;|&#38;/g;
// 		function htmlDecode (string) {
// 			return ('' + string).replace(specialCharDecoder, function (match) {
// 			   return whiteList[match]; 
// 			});
// 		}
// 		newSiteFile = htmlDecode(document.write($siteFile));
// 		console.log(newSiteFile)
// 		// console.log(JSON.stringify(newSiteFile, null, 2));
// 	</script> -->


// 	<!-- <div>
//   		<table id="excelDataTable" border="1">
//   		</table>
// 	</div> -->

// 	<!-- directory = 'static/upload/'
// 		siteFile = json.dumps(self.path_hierarchy(directory), indent=2, sort_keys=True)
// 		siteFile = json.loads(siteFile)
// 		siteFile = siteFile.get('children') -->