<?php

/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

// global debug flat for working out kinks
$rras_DEBUG = true;


// load rs_* functions
require_once dirname(__FILE__) . '/rstools.php';

// introuce global vars to keep track of arrays
$rras_surveys = array();
$rras_flat = array();

function rras_add_survey($survey_json) {
    global $rras_surveys, $rras_flat;
    $newid = 's'.count($rras_surveys);
    $survey = json_decode($survey_json);
    if(!empty($survey)) {
        //check that survey is valid before output
        $validation = rras_validate($survey);
        if(!$validation->valid) {
            return array("valid"=>false, 
                "message" => '<b>' . $validation->message . '</b>') ;
        }
        $rras_surveys[$newid] = $survey;
        $rras_flat[$newid] = rs_flatten($survey);
        return array("valid"=>true, "id"=>$newid);
    } else {
        return array("valid"=>false, "message"=>"Invalid JSON in shortcode");
    }
}

function rras_javascript_onload($survey_id) {
    global $rras_flat;
    ?>
    <script type="text/javascript">
        rras_questions['<?php echo $survey_id;?>'] = <?php echo json_encode($rras_flat[$survey_id]); ?>;
        resetAll('<?php echo $survey_id; ?>');
    </script>
    <?php
}

function rras_the_question_id($survey_id, $question) {
    echo "rras-" . $survey_id . "-question-".$question->_id;
}

function rras_the_question($question) {
    echo "<p>" . $question->question . "</p>\n";
}

function rras_the_style($question) {
    $display = $question->_id != 0 ? 'none': 'block';
    $padding = $question->level * 20 . 'px';
    echo ' style="display: '. $display . '; padding-left: '. $padding . ';"';
}

function rras_the_choices($survey_id, $question) {
    
    $next_question = (array)$question->next_question;
    $dependents = $question->dependents ;
    foreach($question->choices as $choice) : ?>
        <?php
        $radio_name = 'rras_' . $survey_id . '_choice[' . $question->_id  .']';
        $onclick = '';
        if(!empty($next_question)) {
            $showkey = $next_question[$choice];
            if(empty($showkey)) {
                $showkey = "null";
            }
            $hidekeys = implode(',', array_diff(array_values($dependents), array($showkey)));
            $onclick = ' onclick="showQuestion(\''. $survey_id . '\', ' . $showkey . ', [' . $hidekeys . ']);"';
        }
        ?>
        <input type="radio" class="rras-question-choice" name="<?php echo $radio_name; ?>" 
               value="<?php echo esc_attr($choice);?>"<?php echo $onclick ?>/> <?php echo $choice ?><br/>
    <?php endforeach; ?>
    <?php
    
}

function rras_random_answers_link($survey_id) {
    global $rras_flat;
    $flat = $rras_flat[$survey_id];
    $items = array("rras_survey_id=" . $survey_id);
    foreach($flat as $question) {
        $name = 'rras_' . $survey_id . '_choice[' . $question->_id  .']';
        $choice = $question->choices[array_rand($question->choices)];
        $items[] = $name . '=' . urlencode($choice);
    }
    echo "?" . implode('&', $items);
}

function rras_load_answers($survey_id, $flat=null, $method='GET') {
    if(empty($flat)) {
        global $rras_flat;
        $flat = $rras_flat[$survey_id];
    }
    $source = $method == 'POST' ? $_POST : $_GET;
    if($source["rras_survey_id"] == $survey_id) {
        // populate the $flat object with the answers
        for($i=0; $i<count($flat); $i++) {
            $key = "rras_" . $survey_id . "_choice";
            $answer = stripslashes($source[$key][$i]) ;
            
            $flat[$i]->answer = $answer;
            if(!empty($answer) && !in_array($answer, $flat[$i]->choices)) {
                $flat[$i]->error = "Answer '" . $answer . "' not in choices (" . 
                        implode(', ', $flat[$i]->choices) . ")";
            }
        }
        return true;
    } else {
        return false;
    }
}

function rras_the_survey($survey_id, $method='GET') {
    global $rras_flat, $rras_DEBUG;
    $flat = $rras_flat[$survey_id];
    rras_load_answers($survey_id, $flat, $method);
    ?>
    <div class="rras-survey" id="rras-survey-<?php echo $survey_id; ?>">
    <form id="rras-<?php echo $survey_id; ?>" method="<?php echo $method; ?>">
    <input type="hidden" name="rras_survey_id" value="<?php echo $survey_id; ?>">
    <?php foreach($flat as $question) : ?>
        <div class="rras-question" id="<?php rras_the_question_id($survey_id, $question); ?>"<?php rras_the_style($question);?>>
            <?php rras_the_question($question); ?>
            <?php rras_the_choices($survey_id, $question); ?>
        </div>
    <?php endforeach; ?>
        <div class="rras-buttons">
            <input type="submit" value="Submit"/>
            <input type="button" value="Clear" onclick="resetAll('<?php echo $survey_id; ?>');"/>
        </div>
    <?php rras_javascript_onload($survey_id) ?>
    </form>
    <?php if($rras_DEBUG) : ?>
        <a href="<?php rras_random_answers_link($survey_id); ?>">Take this survey for me</a>
    <?php endif; ?>
    </div>
    <?php
}


function rras_group_sections($report) {
    $groups = array();
    foreach($report as $node) {
        if(!empty($node->likelihood_name)) {
            $name = $node->likelihood_name;
            if(!array_key_exists($name, $groups)) {
                $longname = $name;
                if(!empty($node->likelihood_id)) {
                    $longname = $node->likelihood_id . ' ' . $name;
                }
                $groups[$name] = array("name"=> $longname, "nodes"=>array());
            }
            $groups[$name]["nodes"][] = $node;
        } else if(!empty($node->consequence_name)) {
            $name = $node->consequence_name;
            if(!array_key_exists($name, $groups)) {
                $longname = $name;
                if(!empty($node->consequence_id)) {
                    $longname = $node->consequence_id . ' ' . $name;
                }
                $groups[$name] = array("name"=> $longname, "nodes"=>array());
            }
            $groups[$name]["nodes"][] = $node;
        }
    }
    if(empty($groups)) {
        return array(array("name"=>null, "nodes"=>$report));
    } else {
        return $groups;
    }
}


function rras_the_result_questions($node) {
    if(is_array($node->question)) {
        $rows = array();
        for($i=0; $i<count($node->question); $i++) {
            $rows[] = $node->question[$i] . " <i>" . $node->answer[$i] . "</i>" ;
        }
        echo implode('<br/>', $rows);
    } else if(!empty($node->question)) {
        echo $node->question . " " . $node->answer;
    }
    
}

function rras_the_results($survey_id, $method='GET') {
    global $rras_flat, $rras_surveys, $rras_DEBUG;
    $flat = $rras_flat[$survey_id];
    if(rras_load_answers($survey_id, $flat, $method)) {
        $report = rras_report($rras_surveys[$survey_id], $flat);
        if(array_key_exists("error", $report)) {
            echo "Error processing results: " . $report->error;
            if($rras_DEBUG) {
                echo '<h3>Report object</h3><pre>';
                var_dump($report);
                echo '</pre>';

                echo '<h3>Evaluated object</h3><pre>';
                var_dump(rras_evaluate($rras_surveys[$survey_id], $flat));
                echo '</pre>';
            }
            return true;
        }
        
        if($rras_DEBUG) {
            echo '<!--<h3>Report object</h3><pre>\n';
            var_dump($report);
            echo '</pre>';

            echo '<h3>Evaluated object</h3><pre>\n';
            var_dump(rras_evaluate($rras_surveys[$survey_id], $flat));
            echo '</pre>-->';
        }
            
        $cols = array("id", "info", "likelihood", "consequence", "risk");
        $colnames = array("ID", "Info", "Likelihood", "Consequence", "Risk");
        
        $groups = rras_group_sections($report);
        ?>
        <div class="rras-results" id="rras-results-<?php echo $survey_id; ?>">
        <?php foreach($groups as $group) : ?>
            <?php if(!empty($group["name"])) : ?>
            <h3><?php echo $group["name"] ; ?></h3>
            <?php endif; ?>
            <table>
                <tr>
                    <?php foreach($colnames as $colname) {
                        echo '<th>' . $colname . '</th>';
                        
                    } ?>
                </tr>
            <?php foreach($group["nodes"] as $node) : ?>
                <tr>
                    <?php foreach($cols as $col): ?>
                    <td>
                        <?php if($col == 'info') : ?>
                        <b><?php echo $node->name; ?></b><br/>
                        <?php rras_the_result_questions($node); ?>
                        <?php else: ?>
                            <?php echo $node->$col; ?>
                        <?php endif; ?>
                    </td>
                    <?php endforeach; ?>
                </tr>
            <?php endforeach; ?>
            </table>
        <?php endforeach; ?>
             <p><a href="?">Take this survey again</a></p>
        </div>
        <?php
        return true;
    } else {
        return false;
    }
}
