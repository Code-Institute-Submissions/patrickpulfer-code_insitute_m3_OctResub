/*jshint esversion: 6 */
/*globals $:false, google */

$(document).ready(function () {
    $("#hidden_question_cards_grid").toggle();

    /* Collapse Hidden Cards Card */
    $(".toggle_hidden_cards").click(function () {
        $("#hidden_question_cards_grid").slideToggle("slow");
    });

    /* Tick the checkbox in admin update card page IF value is visible */
    if ('{{ card.visible }}' == 'Yes') {
        $('#visible_update').prop('checked', true);
    }


});