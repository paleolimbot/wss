<?php

/**
 * @package rras
 * @version 0.1
 */
/*
Plugin Name: RRAS for Wordpress
Plugin URI: http://github.com/paleolimbot/wsp
Description: Add JSON-based recursive risk asessment surveys (RRAS) to posts and pages using the [rras] shortcode.
Author: Dewey Dunnington
Version: 0.1
Author URI: http://www.fishandwhistle.net/
*/

/*
 * Import the rendering functions
 */
require_once dirname(__FILE__) . '/rras_functions.php';

/*
 * Add the js functions and defaultplot.css to the header
 */
add_action( 'wp_enqueue_scripts', 'rras_enqueue_scripts' );
function rras_enqueue_scripts() {
    wp_enqueue_script( 'rras_js', plugins_url('rras_functions.js', __FILE__), false );
    wp_enqueue_style('rras_styles', plugins_url('rras_styles.css', __FILE__), false);
}

/*
 * Add shortcode to add surveys to posts
 */
add_shortcode( 'rras', 'rras_shortcode' );
function rras_shortcode( $atts, $content = null ) {
    if(empty($content)) {
        return "";
    }
    $result = rras_add_survey($content);
    if(!$result["valid"]) {
        return '<b>' . $result["message"] . '</b>' . $content;
    }
    $sid = $result["id"];
    // use output buffering, since functions echo and don't return
    ob_start();
    if(rras_the_results($sid)) {
        // do nothing
    } else {
        rras_the_survey($sid);
    }
    $output = ob_get_contents();
    ob_end_clean();
    return $output;
}

/*
 * Make sure wpautop and texturize-ing don't invalidate JSON in shortcode
 */
add_filter( 'no_texturize_shortcodes', 'rras_shortcodes_to_exempt_from_wptexturize' );
function rras_shortcodes_to_exempt_from_wptexturize( $shortcodes ) {
    $shortcodes[] = 'rras';
    return $shortcodes;
}
remove_filter( 'the_content', 'wpautop' );
add_filter( 'the_content', 'wpautop' , 99);