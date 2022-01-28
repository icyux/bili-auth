<?php
session_start();

const db_path = './comments.db';

$db = new Sqlite3(db_path);
assert($db);

$method = $_SERVER['REQUEST_METHOD'];

if (isset($_SESSION['user']))
	$user = $_SESSION['user'];
else {
	http_response_code(403);
	echo 'OAuth authorization required';
	die;
}


if ($method === 'POST' && isset($_POST['content'])) {
	$content = $_POST['content'];
	$stmt = $db->prepare('INSERT INTO comment (sender, context, ts) VALUES (:sender, :context, :ts)');
	$stmt->bindValue(':sender', $user['uid']);
	$stmt->bindValue(':context', $content);
	$stmt->bindValue(':ts', time());
	$result = $stmt->execute();
	if ($result === false) {
		http_response_code(500);
		echo 'database writing failed';
		die;
	}
	else {
		http_response_code(201);
		die;
	}
}
else if ($method === 'DELETE' && isset($_GET['pid'])) {
	$stmt = $db->prepare('SELECT sender FROM comment WHERE pid=:pid');
	$stmt->bindValue(':pid', intval($_GET['pid']));
	$result = $stmt->execute();
	$query = $result->fetchArray(SQLITE3_ASSOC);
	if (isset($query) && $query['sender'] === intval($user['uid'])) {
		$stmt = $db->prepare('DELETE FROM comment WHERE pid=:pid');
		$stmt->bindValue(':pid', intval($_GET['pid']));
		$result = $stmt->execute();
		if ($result === false) {
			http_response_code(500);
			echo 'database writing failed';
			die;
		}
		else {
			http_response_code(200);
			die;
		}
	}
}

http_response_code(405);
