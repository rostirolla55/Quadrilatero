<?php
header('Content-Type: application/json');
$file = 'cronologia_db.json';
$data = file_exists($file) ? json_decode(file_get_contents($file), true) : [];

$action = $_GET['action'] ?? '';

if ($action === 'add') {
    $input = json_decode(file_get_contents('php://input'), true);
    $token = $input['pairToken'];
    $pageId = $input['pageId'];
    
    if (!isset($data[$token])) {
        $data[$token] = [];
    }

    // Cerca se la pagina esiste già per questo token (Punto C)
    $found = false;
    foreach ($data[$token] as &$item) {
        if ($item['pageId'] === $pageId) {
            $item['timestamp'] = $input['timestamp']; // Aggiorna solo la data/ora
            $found = true;
            break;
        }
    }

    if (!$found) {
        $data[$token][] = $input;
    }

    file_put_contents($file, json_encode($data));
    echo json_encode(['status' => 'success']);
} 

elseif ($action === 'get') {
    $token = $_GET['pairToken'] ?? '';
    echo json_encode($data[$token] ?? []);
} 

elseif ($action === 'delete_one') {
    $input = json_decode(file_get_contents('php://input'), true);
    $token = $input['pairToken'];
    $pageId = $input['pageId'];

    if (isset($data[$token])) {
        $data[$token] = array_filter($data[$token], function($item) use ($pageId) {
            return $item['pageId'] !== $pageId;
        });
        file_put_contents($file, json_encode($data));
    }
    echo json_encode(['status' => 'deleted']);
} 

elseif ($action === 'clear_all') {
    $input = json_decode(file_get_contents('php://input'), true);
    $token = $input['pairToken'];
    
    unset($data[$token]);
    file_put_contents($file, json_encode($data));
    echo json_encode(['status' => 'cleared']);
}