$(document).ready(function() {
	UI = {
		"NL": "\r\n",
		"SHELL_EXECUTE": " Executing> "
	
	}


	$(".spawn-shell").click(function() {
		$("#active-shell").text($(this).text());
		current_id = $(this).data("id");
	});

	$("#cmd").change(function() {
		data = $(this).val();
		$(this).val("");
		request_api("POST", "shell/" + current_id, data);
		$("#output").append(UI.NL + current_user + UI.SHELL_EXECUTE + data); 
	});


	function request_api(method, url, data) {
		$.ajax({
			type: method,
			beforeSend: function(xhr) {
				xhr.setRequestHeader("Authorization", auth);
			},
			url: api_path + url,
			data: data,
			success: function(data) {
				alert(data);
			}
		});
	}

});
