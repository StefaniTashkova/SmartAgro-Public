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
$(document).ready(function () {
     //Trigger href on icon click
     $('.fa-eye').on("click", function () {
        window.location = $(this).data('href');
        return false;
    });
    // Disable first options in select fields
    $("#mixed_grain_holder option:first, #grain_type option:first").attr("disabled", "disabled");
    $('#paid_amount_bgn').prop('readonly', true);

    // Displaying all owners with existing plots and contracts in dual list
    var settings = {
        // tab text
        tabNameText: "Разходен касов ордер",
        // right tab text
        rightTabNameText: "Платежно нареждане по банков път",
        // search placeholder text
        searchPlaceholderText: "Търси",
        // items data array
        dataArray: owners_json,
        valueName: "owner_id",
        itemName:"owner_name",

    };
    var myTransfer = $(".transfer").transfer(settings);

    //File upload
    var stored_doc_path = $('#stored_doc_path').val()
    $("#doc_path").fileinput({
        theme: "fas",
        overwriteInitial: true,
        initialPreviewAsData: true,
        initialPreview: [
            stored_doc_path,
        ],
        initialPreviewConfig: [
            {type: "pdf"},
        ],
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

    $('#generate_payment_btn').on('click',function(e){
		e.preventDefault();
    	$('.loader-container').css('display','block');
		var owners_for_cash_payment=[];
		$(".transfer-double-content-left").find('li.transfer-double-list-li:not(li.selected-hidden)').find(":checkbox").each(function(){
            if (this.hasAttribute("value")){
                owners_for_cash_payment.push($(this).attr("value"));
            }
        })
		var owners_for_bank_payment=[];
        $(".transfer-double-content-right").find(":checkbox").each(function(){
            if (this.hasAttribute("value")){
                owners_for_bank_payment.push($(this).attr("value"));
            }
        })
		$.ajax({
			method: 'POST',
			url: '/payments',
			data: {
			    owners_for_cash_payment: owners_for_cash_payment,
			    owners_for_bank_payment: owners_for_bank_payment
			},
			headers: {
				'X-CSRF-TOKEN': $('meta[name="csrf-token"]').attr('content')
			}
		}).done(function(result){
			window.location.href = "/payments";
		});

	});

    $('.make-payment-button').click(function(e){
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
    });
    //Displaying errors in current payment modal
    if($("#preclicked_payment_id").length){
        $("#make-payment-button-".concat($("#preclicked_payment_id").attr("value"))).click();
    }


    //Single payment page
    //Hide edit buttons until edit icon button is clicked
    $('.payment-buttons-container').css('display', 'none');
    // Disable all fields until edit icon button is clicked
    $('#notes').attr('disabled',true);
    $("#edit_payment_form :input").each(function () {
        $(this).attr("disabled", true);
    });
    //Show edit buttons and Enable  all fields when edit icon button is clicked
    $("#edit_payment_icon_btn").click(function(){
        $('.payment-buttons-container').css('display', 'flex');
        $('#notes').attr('disabled',false);
        $("#edit_payment_form :input").each(function () {
            $(this).attr("disabled", false);
        });
    });
     // Disable all fields when cancel button is clicked
    $('#edit_payment_cancel_btn').click(function(){
        $('#notes').attr('disabled',true);
        $("#edit_payment_form :input").each(function () {
            $(this).attr("disabled", true);
        });
        $('.payment-buttons-container').css('display', 'none');
    });

    // Paginated search JS
    $('#search_query_input').on("keydown", function (e) {
        if (e.which == 13) {
            window.location = $('#search_anchor').attr("href")
        }
    });

    $('#search_query_input').on("keyup", function () {
        // Updates the href attribute of the search button to match the search string in the query input text box
        var prev_anchor_href = $("#search_anchor").attr("href");
        var query_string = $(this).val();
        $('#search_anchor, .page-link').each(function () {
            var prev_anchor_href = $(this).attr("href");
            var index_of_query_param = prev_anchor_href.indexOf("&query=");
            if (index_of_query_param === -1) {
                // First change of the search text box, need to add '&query=' to the end of the <a> href
                var next_anchor_href = prev_anchor_href.concat('&query=', query_string);
            } else {
                // '&query=' is already in the <a> href, so we just need to change the part after '&query=' to what is in the text input
                var next_anchor_base = prev_anchor_href.slice(0, index_of_query_param);
                var next_anchor_href = next_anchor_base.concat("&query=", query_string);
            }
            $(this).attr("href", encodeURI(next_anchor_href))
        });
    });

    $('.payments-table tbody').on('click','.payment-delete',function(e){
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

});