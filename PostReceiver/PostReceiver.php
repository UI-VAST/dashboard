<?php 

// php script is executed whenever the page is loaded (i.e., whenever HTTP request is made here.
// the actual script here is only executed if the request contains POST data containing an 'imei' field.

//logfile.php will contain the $PacketsPath var, where packets.csv is located to write packets to.
//can echo from StartServer.sh into logfile.php the directory we want.
//ex:  $ echo "<?php \$PacketsPath = \"/var/www/html/Dashboard/packets/\"; ?\>\" > ./logfile.php
include_once 'logfile.php';

//if(1) {     // writing any and all received post requests.  this is dangerous, probably
// if there's an 'imei' data field, it came from the(a) modem.
// to be more secure, should check if imei == our specific modem.
if(isset($_POST['imei'])) {
    //create directory if not exists.
    if (!file_exists($PacketsPath)) { mkdir($PacketsPath); }

    //packetsfile contains actual transmitted data; logfile contains all data posted from iridium (imei, serial, datetime etc)
    $packetsFile = fopen($PacketsPath . '/packets.csv','a');
    $logFile = fopen($PacketsPath . 'log.txt','a');

    //write everything to logfile
    foreach($_POST as $key => $value) {
        fwrite($logFile, $key . ":" . $value . "\n");
    }

    //decode data, and write to packetsfile
    $dataPacket = hex2str($_POST['data']);
    
    fwrite($packetsFile,$dataPacket . "\n");
    fclose($logFile);
    fclose($packetsFile);

}

// data is sent encoded as hex bytes.  function to decode it into ascii here.
function hex2str($hex) {
    if(!ctype_xdigit($hex))
        return "data is not hex encoded";
    $str = '';
    for($i=0;$i<strlen($hex);$i+=2) $str .= chr(hexdec(substr($hex,$i,2)));
    return $str;
}

?>
