<?php

if(isset($_GET["token"])){
    $token = $_GET["token"];
    if(ctype_xdigit($token) && strlen($token)==64){
        $file = "output/".$token.".mp4";
        
        $size   = filesize($file);

        header('Content-Description: File Transfer');
        header('Content-Type: application/octet-stream');
        header('Content-Disposition: attachment; filename=output.mp4'); 
        header('Content-Transfer-Encoding: binary');
        header('Connection: Keep-Alive');
        header('Expires: 0');
        header('Cache-Control: must-revalidate, post-check=0, pre-check=0');
        header('Pragma: public');
        header('Content-Length: ' . $size);
        
        ob_clean();
        flush();
        readfile($file);
        exit();
    }        
}

?>