
// $.alert(message, title)
function add_alert_function()
{
  alert("extending jquery")
$.extend({ alert: function (message, title) {
  $("<div></div>").dialog( {
    buttons: { "Ok": function () { $(this).dialog("close"); } },
    close: function (event, ui) { $(this).remove(); },
    resizable: false,
    title: title,
    modal: true
  }).text(message);
}
});
}


meone can increment the idea.

Heres the full code:


<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Unobtrusive Confirm Javascript Replacement with jquery UI Dialog</title>

<link href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.10/themes/smoothness/jquery-ui.css" rel="stylesheet" type="text/css" />
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.5.1/jquery.min.js"></script>
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.10/jquery-ui.min.js"></script>

<script>
$(function ($) {
	$.each($('a'), function() {
		e = $(this).attr("onclick");
		if(e!=undefined) {
			string = $(this).attr("onclick").toString();
			if (string.indexOf('return confirm(')!=-1) {
				target = $(this).attr("href");
				$(this).click(function (e) {
					e.preventDefault();
					confirm(null, function () {						
						window.location.href = target;
					});
				});
			}
		}
    });
});

function confirm(message, callback) {
	$('body').append('<div id="confirm" style="display:none">'+message+'</div>');
	$( "#confirm" ).dialog({
		resizable: false,
		title: 'Confirm',
		modal: true,
		buttons: [
			{
				text: "Yes",
				click: function() {
					$(this).dialog("close");
					if ($.isFunction(callback)) {	
						callback.apply();
					}
				
				}
			},{
				text: "No",
				click: function() { $(this).dialog("close");}
			}
		],
		close: function(event, ui) { 
			$('#confirm').remove();
		}
	});
}
</script>

</head>

<body>

<a href="http://www.google.com" onclick="return confirm('Are you sure?');">Send me to google!</a>

</body>
</html>
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Unobtrusive Confirm Javascript Replacement with jquery UI Dialog</title>
 
<link href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.10/themes/smoothness/jquery-ui.css" rel="stylesheet" type="text/css" />
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.5.1/jquery.min.js"></script>
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.10/jquery-ui.min.js"></script>
 
<script>
$(function ($) {
	$.each($('a'), function() {
		e = $(this).attr("onclick");
		if(e!=undefined) {
			string = $(this).attr("onclick").toString();
			if (string.indexOf('return confirm(')!=-1) {
				target = $(this).attr("href");
				$(this).click(function (e) {
					e.preventDefault();
					confirm(null, function () {						
						window.location.href = target;
					});
				});
			}
		}
    });
});
 
function confirm(message, callback) {
	$('body').append('<div id="confirm" style="display:none">'+message+'</div>');
	$( "#confirm" ).dialog({
		resizable: false,
		title: 'Confirm',
		modal: true,
		buttons: [
			{
				text: "Yes",
				click: function() {
					$(this).dialog("close");
					if ($.isFunction(callback)) {	
						callback.apply();
					}
				
				}
			},{
				text: "No",
				click: function() { $(this).dialog("close");}
			}
		],
		close: function(event, ui) { 
			$('#confirm').remove();
		}
	});
}
</script>
 
</head>
 
<body>
 
<a href="http://www.google.com" onclick="return confirm('Are you sure?');">Send me to google!</a>
 
</body>
</html>