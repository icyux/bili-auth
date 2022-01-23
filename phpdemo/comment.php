<?php

const db_path = './comments.db';

$db = new Sqlite3(db_path);
assert($db);

$from = $_GET['from'];
$count = $_GET['count'];
$stmt = $db->prepare('SELECT pid, sender, context, ts FROM comment ORDER BY ts DESC LIMIT :f, :c;');
$stmt->bindValue(':f', intval($from));
$stmt->bindValue(':c', intval($count));
$result = $stmt->execute();

header('Content-Type: application/json');
$comments = [];
while ($row = $result->fetchArray(SQLITE3_ASSOC))
	$comments[] = $row;

echo json_encode($comments);
