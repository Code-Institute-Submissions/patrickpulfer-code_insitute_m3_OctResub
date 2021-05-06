/*jshint esversion: 6 */
/*globals $:false, google */

$(document).ready(function () {
    $("#hidden_question_cards_grid").toggle();

    /* Collapse Hidden Cards Card */
    $(".toggle_hidden_cards").click(function () {
        $("#hidden_question_cards_grid").slideToggle("slow");
    });
});


