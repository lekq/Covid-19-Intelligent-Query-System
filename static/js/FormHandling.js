jQuery(document).ready(function(){
	
});

function getParam() {
	var site = jQuery('#upload_site option:selected').val();
	var filetype = jQuery('#upload_filetype option:selected').val();
	if (site == "") {
		alert("Please select a Site!");
		jQuery('#upload_site').focus();
		return false;
	} else if(filetype == "") {
		alert("Please select File Type!");
		jQuery('#upload_filetype').focus();
		return false;
	} 
	
	return true;
}	