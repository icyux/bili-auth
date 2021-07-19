<?php

if(!isset($_GET['uid'])){
	http_response_code(400);
	die;
}

$uid = intval($_GET['uid']);
if($uid===0){
	http_response_code(400);
	die;
}

$curl = curl_init();

curl_setopt_array($curl, array(
  CURLOPT_URL => "https://api.bilibili.com/x/space/acc/info?mid={$uid}&jsonp=jsonp",
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_ENCODING => '',
  CURLOPT_MAXREDIRS => 10,
  CURLOPT_TIMEOUT => 0,
  CURLOPT_FOLLOWLOCATION => true,
  CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
  CURLOPT_CUSTOMREQUEST => 'GET',
));

$response = curl_exec($curl);
if(curl_getinfo($curl,CURLINFO_HTTP_CODE)===200){
	header('Content-Type: application/json');
  header('Cache-Control: max-age=1800');
}
else{
	http_response_code(404);
}
curl_close($curl);
echo $response;
