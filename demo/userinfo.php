<?php

$uid = intval($_GET['uid']);
if ($uid === 0) {
	http_response_code(400);
	die;
}

$curl = curl_init();

curl_setopt_array($curl, array(
	CURLOPT_URL => "https://api.bilibili.com/x/space/acc/info?mid={$uid}",
	CURLOPT_RETURNTRANSFER => true,
	CURLOPT_ENCODING => '',
	CURLOPT_MAXREDIRS => 10,
	CURLOPT_TIMEOUT => 0,
	CURLOPT_FOLLOWLOCATION => true,
	CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
	CURLOPT_CUSTOMREQUEST => 'GET',
));

$response = curl_exec($curl);
if (curl_getinfo($curl, CURLINFO_HTTP_CODE) === 200){
	$json = json_decode($response, true);
	if ($json['code'] === 0) {
		http_response_code(200);
		header('Cache-Control: max-age=1800');
		header('Content-Type: application/json');
	}
	else
		http_response_code(400);
}
else
	http_response_code(404);

curl_close($curl);

if (http_response_code() === 200)
	echo json_encode($json['data']);
