/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

var rras_questions = {};
function resetRadio(survey_id, num) {
    var ele = document.getElementsByName("rras_" + survey_id + "_choice[" + num + "]");
    for(var i=0;i<ele.length;i++)
       ele[i].checked = false;
}
function hideQuestion(survey_id, num) {
    document.getElementById('rras-' + survey_id + '-question-' + num).style.display = 'none';
    resetRadio(num);
}
function showQuestion(survey_id, num, hide) {
    for(var i=0; i<hide.length; i++) {
        hideQuestion(survey_id, hide[i]);
    }
    if(num !== null) {
        document.getElementById('rras-' + survey_id + '-question-' + num).style.display = 'block';
    }
}
function resetAll(survey_id) {
    for(var i=0; i<rras_questions[survey_id].length; i++) {
        hideQuestion(survey_id, i);
        resetRadio(survey_id, i);
    }
    showQuestion(survey_id, 0, []);
}