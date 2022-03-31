$(document).ready(function () {

    // Save base action path /plots in add plot form
    var base_add_contract_form_action = $('#add_contract_form').attr('action')
    // Disable btn-next if owner is not selected
    $('.first-next-btn').attr('disabled', true);



    $('*[data-href]').on("click", function () {
        window.location = $(this).data('href');
        return false;
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

    $('.contracts-table tbody').on('click','.contract-delete',function(e){
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

//	$('.print-contracts-btn').on('click',function(e){
//		e.preventDefault();
//		$.ajax({
//			method: 'GET',
//			url: '/contracts/download',
//			headers: {
//				'X-CSRF-TOKEN': $('meta[name="csrf-token"]').attr('content')
//			}
//		}).done(function(result){
//			console.log(result)
//		});
//
//	});

    //.................Add contract form JS...........................

    // Multistep form controls
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

    /*If owner_id is preselected (if redirected to contracts page from add plot form or if errors exist on add contract form)
  open add contract modal beginning from step 2 
  */

    if ($('.preselected-owner-id').val() != "None") {
        jQuery('#open_addContractModal_btn').click();
        jQuery('.first-next-btn').click();
        $('.first-prev-btn').attr('disabled', true);
    }
    // Owners table in add contract form(step 1)
    // On keyup search for owner in table
    $("#select_owner_search").on("keyup", function () {
        value = $(this).val().toLowerCase();
        $(".select-owners-table tbody tr").filter(function () {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });

    // Getting owner_id on current selected row

    $('.select-owners-table tbody tr').click(function () {
        if ($(this).hasClass('active')) {
            $(this).removeClass('active');
            $('#add_contract_form').attr('action', base_add_contract_form_action);
            $('.first-next-btn').attr('disabled', true);
        } else {
            $('#add_contract_form').attr('action', base_add_contract_form_action + '?owner_id=' + $(this).attr('owner_id'));
            $(this).addClass('active').siblings().removeClass('active');
            $('.first-next-btn').attr('disabled', false);
        }
    });
    // Contract details in add contract(step 2)
    // Radio buttons check/uncheck on click
     $('input[type="radio"]').click(function (e) {
        if (e.currentTarget.id === 'contract_type-0'){
            $("#contract_type-1").removeAttr("checked");
            $(this).attr("checked", "checked");
        } else if (e.currentTarget.id === 'contract_type-1'){
            $("#calculator_selects_container").show('slow');
            $("#contract_type-0").removeAttr("checked");
            $(this).attr("checked", "checked");
        }
    });

    // If radio contract_type-1 is checked show 1 year in contract duration field
    $('#contract_type-1').click();
    if($("#contract_type-1").attr("checked")==="checked"){
        $('#duration_years').val(1);
    }
    //Date pickers for contract signed date and contract started date

    jQuery('#date_signed').datetimepicker({
        timepicker: false,
        format: 'd/m/Y',
        scrollInput: false,
    });
    jQuery('#date_started').datetimepicker({
        timepicker: false,
        format: 'd/m/Y',
        scrollInput: false,
    });
    $.datetimepicker.setLocale('bg');

    // Disable first options in select fields
    $("#locality_id option:first").attr("disabled", "disabled");


    //Select all checkboxes
    $('.selectall').click(function (e) {
        var table = $(e.target).closest('table');
        var is_selectall_checked = this.checked;
        $('tr', table).each(function () {
            if ($(this).hasClass("hidden")) {
                $('td input:checkbox', this).removeAttr('checked');
            } else {
                if (is_selectall_checked) {
                    $('td input:checkbox', this).attr('checked', 'checked');
                } else {
                    $('td input:checkbox', this).removeAttr('checked');
                }
            }
        });
    });

    // Plots details in add contract(step 3)
    $(".second-next-btn").click(function () {
        var parts = $("#add_contract_form").attr("action").split("=");
        var owner_id = parts[parts.length - 1];
        var date_started_parts = $("#date_started").val().split("/");
        var first_agricultural_year;
        if (parseInt(date_started_parts[1], 10) < 10) {
            first_agricultural_year = parseInt(date_started_parts[2], 10);
        } else {
            first_agricultural_year = parseInt(date_started_parts[2], 10) + 1;
        }
        $(".accordion-plots-table tbody tr").each(function () {
            if (($(this).attr("owner_id") == owner_id) && ($(this).attr("first_available_year") <= first_agricultural_year)) {
                $(this).removeClass("hidden");
            } else {
                $(this).addClass("hidden");
            }
        });
        $('.selectall').each(function () {
            $(this).click()
        });
        $(".accordion-plots-table").each(function () {
            var num_checked = $(this).find("td input[type='checkbox']:checked").length;
            if (num_checked < 1) {
                $(this).closest(".card").addClass("hidden");
            } else {
                $(this).closest(".card").removeClass("hidden");
            }
        });
    });

    $('.single_plot_checkbox, .selectall').click(function () {
        var total_num_checked = $('#accordionExample').find("td input[type='checkbox']:checked").length;
        if (total_num_checked < 1) {
            $("#third-next-btn").attr('disabled','disabled');
        } else {
            $("#third-next-btn").removeAttr('disabled');
        }
    });

    // Preview details in add contract(step 4)
    // Displaying data(preview)

    $('.next').last().click(function () {
        //Get radio selected value
        var radio_id = $("input[type='radio']:checked").attr("id");
        radio_value = $("label[for='" + radio_id + "']").text();
        $("input[name='contract_type_preview']").val(radio_value).prop('disabled', true);

        //Get  selected owner name from owners table
        var owner_name = $('.select-owners-table tbody tr.active td:first-child').text();
        $("input[name='owner_preview']").val(owner_name).prop('disabled', true);

        // Get content from all rows with checked inputs
        plots = []
        $(".plots-table input[type=checkbox]:checked").not($('.selectall')).each(function () {
            var row = $(this).closest("tr")[0];
            plots.push([row.cells[1].innerHTML, row.cells[2].innerHTML, row.cells[4].innerHTML])
        });

        // Append retrieved rows content to plots-preview table
        var rows = ''
        plots.forEach(function (plot) {
            rows += `<tr><td> ${plot[0]}</td><td> ${plot[1]}</td><td> ${plot[2]}</td></tr>`
        });
        tableBody = $('table.plots-table-preview tbody')
        tableBody.append(rows)

        // Map selected inputs names from contract add form with their equivalents from preview inputs to display selected values
        var map = {};
        $('fieldset').not(":last").find('input[type=text],input[type=number],select,textarea').each(function () {
            map[$(this).attr("name")] = $(this).val();
        });
        $('fieldset').last().find('input[type=text]:not(input[name=contract_type_preview],input[name=owner_preview]),select,textarea').each(function () {
            $(this).prop('disabled', true);
            $(this).val(map[$(this).attr("name").split('_').slice(0, -1).join('_')]);
        });

    });

    //Show loader while generating contracts on submit button
    $('#add_contract_btn').click(function(){
        $('.loader-container').css('display','block');
    });
    // Single Contract Page JS
    //Disable inputs in contract details
    $('#contract_details :input').each(function () {
        $(this).attr("disabled", true);
    });

    // Disable inputs in edit contract form and hide edit buttons container until edit icon is clicked
    $('.edit-contract-buttons-container').hide();
    $("#edit_contract_form :input").each(function () {
            $(this).attr("disabled", true);
    });
    $("#edit_contract_form #notes").attr("disabled", true);

    // Show and enable edit buttons and form inputs on edit icon click
    $("#edit-icon-btn").click(function () {
        $('.edit-contract-buttons-container').show();
        $("#edit_contract_form :input").each(function () {
            $(this).attr("disabled", false);
        });
    });
    $('#edit_contract_cancel_btn').click(function () {
        $("#edit_contract_form #notes").attr("disabled", true);
        $('.edit-contract-buttons-container').hide();
    });

    //FIle upload
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

});