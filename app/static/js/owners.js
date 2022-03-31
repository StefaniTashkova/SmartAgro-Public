var kg_per_dka = 0;
function rent_calculator() {
    var total_area = Number($('#total_area_cell').text());
    var price_per_dka = Number($('#rent_per_unit_of_area_field').text());
    var total_sum = total_area*kg_per_dka*price_per_dka;
    var total_kg = total_area*kg_per_dka;
    $('#total_sum_field').text(total_sum.toFixed(2));
    $('#total_kg_field').text(total_kg.toFixed(2));
    if($("#payment_type-0").attr("checked")==="checked"){
        // Парично
        $("#paid_amount_bgn").val($('#total_sum_field').text());
    } else if ($("#payment_type-1").attr("checked")==="checked"){
        // В натура
        var total_grain_weight_kg = Number($('#grain_weight').val()) + Number($('#mixed_grain_weight').val());
        if (total_grain_weight_kg > total_kg){
            $("#paid_amount_bgn").val('Моля въведете общо тегло на зърно и смески по-малко от '+$('#total_kg_field').text()+'кг.');
        } else {
            $("#paid_amount_bgn").val((total_sum-total_grain_weight_kg*price_per_dka).toFixed(2))
        }
    }
}

function populate_payment_modal(e){
        $('.payments-popover').each(function(){
            $(this).popover('hide');
        })
        jQuery('#payment_type-0').click();
        $('#grain_type').children().not(':first-child').remove();
        $('#mixed_grain_holder').children().not(':first-child').remove();
        e.preventDefault();
        var url = $(this).attr('data-url');
        $.ajax({
				method: 'GET',
				url: url,
				headers: {
		        	'X-CSRF-TOKEN': $('meta[name="csrf-token"]').attr('content')
  		        }
        }).done(function(result){
            var json = JSON.parse(result);
            var action = $("#payment_form").attr("action").split('/').slice(0, -1).join('/').concat("/",json["payment_id"]);
            $("#payment_form").attr("action", encodeURI(action))
            $('#contract_id_field').text('Дог. №: ' + json["contract_id"]);
            $('#owner_name_field').text('Собственик: ' + json["owner_name"]);
            $('#owner_egn_field').text('ЕГН: ' + json["owner_egn"]);
            $('#payment_date_field').text(json["payment_date"]);
            $('#kg_per_dka_field').text(json["kg_per_dka"] + ' кг.');
            $('#kg_per_dka_rent_radio').val(json["kg_per_dka"]);
            $('#kg_per_dka_in_contract_field').text(json["kg_per_dka_in_contract"] + ' кг.(по договор)');
            $('#kg_per_dka_contract_radio').val(json["kg_per_dka_in_contract"]);
            $('#rent_per_unit_of_area_field').text(json["rent_per_unit_of_area"]);

            var grain_type_options = json["selected_grain_types"].split(",");
            for(i = 0; i < grain_type_options.length; i++ ){
               optionValue = grain_type_options[i];
               optionText = grain_type_options[i];
               $('#grain_type').append(`<option value="${optionValue}">
                                               ${optionText}
                                               </option>`);
            }
            var grain_type_mixers_options = json["selected_grain_mixers"].split(",");
            for(i = 0; i < grain_type_mixers_options.length; i++ ){
               optionValue = grain_type_mixers_options[i];
               optionText = grain_type_mixers_options[i];
               $('#mixed_grain_holder').append(`<option value="${optionValue}">
                                               ${optionText}
                                               </option>`);
            }
            $('.contract-details tbody tr').remove();
            var table_body = $('.contract-details tbody')
            var total_area = 0;
            var plots = json["plots"]
            for(i = 0; i < plots.length; i++ ){
                total_area += plots[i]["area"];
                table_body.append($('<tr>')
                    .append($('<td>').text(i+1))
                    .append($('<td>').text(plots[i]["area"]))
                    .append($('<td>').text(plots[i]["sublocality"]))
                    .append($('<td>').text(plots[i]["id"]))
                );
            }
            $('#total_area_cell').text(total_area.toFixed(2));
            jQuery('#kg_per_dka_rent_radio').click();
            rent_calculator();
        });
    }

$(document).ready(function () {

    $('[data-toggle="popover"]').popover({html:true, sanitize: false});

    $('#search_query_input').on("keydown", function (e) {
        if (e.which == 13) {
            window.location = $('#search_anchor').attr("href")
        }
    });

    $('#search_query_input').on("keyup", function () {
        var prev_anchor_href = $("#search_anchor").attr("href");
        var query_string = $(this).val();
        var index_of_query_param = prev_anchor_href.indexOf("&query=");
        if (index_of_query_param === -1) {
            var next_anchor_href = prev_anchor_href.concat('&query=', query_string);
        } else {
            var next_anchor_base = prev_anchor_href.slice(0, index_of_query_param);
            var next_anchor_href = next_anchor_base.concat("&query=", query_string);
        }
        $('#search_anchor').attr("href", encodeURI(next_anchor_href))
    });

     $('.owners-table tbody').on('click','.owner-delete',function(e){
		e.preventDefault();
		var element = $(this).closest('tr');
		var url = $(this).attr('data-url');
		$.ajax({
			method: 'DELETE',
			url: url,
			headers: {
				'X-CSRF-TOKEN': $('meta[name="csrf-token"]').attr('content')
			}
		}).done(function(result){
			element.remove();
		});

	});

    //Add owner form JS

    $("#payment_location option:first, #BIC option:first").attr("disabled", "disabled");

    $('.owner-details-container,.company-details-container').hide();
    $('input[type="radio"]').click(function () {

        if ($('#owner_type-0').is(":checked")) {
            $(".owner-details-container").show('slow');
            $(".company-details-container").hide();
        }
        if ($('#owner_type-1').is(":checked")) {
            $(".company-details-container,.owner-details-container").show('slow');
        }
    });

    var current_fs, next_fs, previous_fs;

    $(".next").click(function () {

        current_fs = $(this).parent();
        next_fs = $(this).parent().next();

        $("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");

        next_fs.show();
        current_fs.hide();

    });

    $(".previous").click(function () {

        current_fs = $(this).parent();
        previous_fs = $(this).parent().prev();

        $("#progressbar li").eq($("fieldset").index(current_fs)).removeClass("active");

        previous_fs.show();
        current_fs.hide();

    });

    $('.add-owner-cancel-btn').click(function () {
        console.log('in reset');
        $("#msform").trigger('reset');
    });


    // Displaying data(preview)
    $('.next').last().click(function () {
        var map = {};
        $('fieldset').not(":last").find('input[type=text],select,textarea').each(function () {
            map[$(this).attr("name")] = $(this).val();
        });

        $('fieldset').last().find('input[type=text],select,textarea').each(function () {
            $(this).prop('disabled', true);
            $(this).val(map[$(this).attr("name").split('_').slice(0, -1).join('_')]);
        });

    });

    //Displaying modal with errors
    if ($('.preselected_owner_type').val() == 'COMPANY') {
        console.log('in company errors');
        jQuery(function () {
            jQuery('#open_addOwnerModal_btn').click();
            jQuery('#owner_type-1').click();
        });
    } else if ($('.preselected_owner_type').val() == 'PERSON') {
        console.log('in owner errors');
        jQuery(function () {
            jQuery('#open_addOwnerModal_btn').click();
            jQuery('#owner_type-0').click();
        });
    }
    if ($('.user-exists').val() == true) {
        console.log('in use exists errors');
        jQuery('#open_addOwnerModal_btn').click();
        if ($('.preselected_owner_type').val() == 'COMPANY') {
            jQuery('#owner_type-1').click();
        } else {
            jQuery('#owner_type-0').click();
        }

    }
    $('#open_addOwnerModal_btn').click(function(){
        jQuery('#owner_type-0').click();
    });


    $('*[data-href]').on("click", function () {
        window.location = $(this).data('href');
        return false;
    });


    // Single Owner Page JS
    $('.edit-owner-buttons-container').hide();

    $("#edit_owner_form :input").each(function () {
        $(this).attr("disabled", true);
    });

    $("#edit-icon-btn").click(function () {
        $('.edit-owner-buttons-container').show();
        $("#edit_owner_form :input").each(function () {
            $(this).attr("disabled", false);
        });
    });
    $('#edit_owner_cancel_btn').click(function () {
        $("#edit_owner_form :input").each(function () {
            $(this).attr("disabled", true);
        });
        $('.edit-owner-buttons-container').hide();
    });

    // Functionality on type of payment radio selection
    $('input[type="radio"]').click(function (e) {
        if (e.currentTarget.id === 'kg_per_dka_rent_radio'){
            kg_per_dka = Number($(this).val());
        } else if (e.currentTarget.id === 'kg_per_dka_contract_radio'){
            kg_per_dka = Number($(this).val());
        } else if (e.currentTarget.id === 'payment_type-0'){
            $("#calculator_selects_container").hide();
            $("#payment_type-1").removeAttr("checked");
            $(this).attr("checked", "checked");
        } else if (e.currentTarget.id === 'payment_type-1'){
            $("#calculator_selects_container").show('slow');
            $("#payment_type-0").removeAttr("checked");
            $(this).attr("checked", "checked");
        }
        rent_calculator();
    });


    $("#grain_weight, #mixed_grain_weight").change(function(){
      rent_calculator();
    });

//    $('.make-payment-button').on("click", null, populate_payment_modal);
    $('.payments-popover').on('shown.bs.popover', function () {
        $('.make-payment-button').each(function(){
            $(this).on("click", null, populate_payment_modal);
        })
    });

    //Displaying errors in current payment modal
    if($("#preclicked_payment_id").length){
        $("#make-payment-button-".concat($("#preclicked_payment_id").attr("value"))).click();
    }

});

