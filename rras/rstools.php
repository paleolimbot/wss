<?php

/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

function _rs_call_rstools($subcommand, $survey, $answers=null) {
    $command = "python3 " . dirname(__FILE__) . "/rstools.py " . $subcommand .
            " " . escapeshellarg(json_encode($survey)) ;
    if(!empty($answers)) {
        $command = $command . " -a " . escapeshellarg(json_encode($answers));
    }
    $flatjson = exec($command) ;
    return json_decode($flatjson);
}

function _rs_call_rrastools($subcommand, $survey) {
    $command = "python3 " . dirname(__FILE__) . "/rrastools.py " . $subcommand .
            " " . escapeshellarg(json_encode($survey)) ;
    $flatjson = exec($command) ;
    return json_decode($flatjson);
}

function rs_flatten($survey) {
    return _rs_call_rstools("flatten", $survey);
}

function rras_validate($survey) {
    return _rs_call_rrastools("validate", $survey);
}

function rras_evaluate($survey, $answers) {
    return _rs_call_rstools("evaluate", $survey, $answers);
}

function rras_report($survey, $answers) {
    $evaluated = rras_evaluate($survey, $answers);
    if(empty($evaluated)) {
        return json_decode('{"error": "Empty array from rstools evaluate"}');
    }
    if(array_key_exists("error", (array)$evaluated)) {
        return $evaluated;
    } else {
        return _rs_call_rrastools("report", $evaluated);
    } 
}
