<?php

const ADDR = 'localhost:8080';

function verifyCreate(){
	$curl = curl_init();

	curl_setopt_array($curl, array(
		CURLOPT_URL => 'http://'.ADDR.'/verify',
		CURLOPT_RETURNTRANSFER => true,
		CURLOPT_ENCODING => '',
		CURLOPT_MAXREDIRS => 10,
		CURLOPT_TIMEOUT => 0,
		CURLOPT_FOLLOWLOCATION => true,
		CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
		CURLOPT_CUSTOMREQUEST => 'POST',
	));

	$response = curl_exec($curl);
	if(curl_getinfo($curl,CURLINFO_HTTP_CODE)!==200 || strlen($response)===0){
		http_response_code(500);
		throw new Exception("用户消息获取错误，这不是您的错");
	}
	curl_close($curl);
	return $response;
}

function verifyQuery($code){
	if($code==null){
		return null;
	}
	$curl = curl_init();
	curl_setopt_array($curl, array(
		CURLOPT_URL => 'http://'.ADDR."/verify/{$code}",
		CURLOPT_RETURNTRANSFER => true,
		CURLOPT_ENCODING => '',
		CURLOPT_MAXREDIRS => 10,
		CURLOPT_TIMEOUT => 0,
		CURLOPT_FOLLOWLOCATION => true,
		CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
		CURLOPT_CUSTOMREQUEST => 'GET',
	));

	$response = curl_exec($curl);
	if(curl_getinfo($curl,CURLINFO_HTTP_CODE)===404){
		return null;
	}
	curl_close($curl);
	return json_decode($response,true);
}