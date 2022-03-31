function calculate_total_owned_area() {
    var owned_plot_fraction_numerator = $('#owned_plot_fraction_numerator').val();
    var owned_plot_fraction_denominator = $('#owned_plot_fraction_denominator').val();
    var additional_owned_area = $('#additional_owned_area').val();
    var area_by_doc = $('#area_display').val();
    if (!$.isNumeric(owned_plot_fraction_numerator) && !$.isNumeric(owned_plot_fraction_denominator) && !$.isNumeric(additional_owned_area) && !$.isNumeric(area_by_doc)) {
        $('#total_owned_area').val('Въведете само числа в полетата от формулата');
    } else {
        owned_plot_fraction_numerator = Number(owned_plot_fraction_numerator);
        owned_plot_fraction_denominator = Number(owned_plot_fraction_denominator);
        additional_owned_area = Number(additional_owned_area);
        area_by_doc = Number(area_by_doc);
        if (!Number.isInteger(owned_plot_fraction_numerator) && !Number.isInteger(owned_plot_fraction_denominator)) {
            $('#total_owned_area').val('Числителят и знаменателят трябва да са цели числа');
        } else if (!(owned_plot_fraction_denominator > 0)) {
            $('#total_owned_area').val('Знаменателят трябва да е положително число');
        } else if ((owned_plot_fraction_numerator < 0)) {
            $('#total_owned_area').val('Числителят трябва да е неотрицателно число');
        } else if (owned_plot_fraction_numerator > owned_plot_fraction_denominator) {
            $('#total_owned_area').val('Числителят не може да бъде по-голям от знаменателя');
        } else {
            var total_owned_area = additional_owned_area + (owned_plot_fraction_numerator / owned_plot_fraction_denominator) * area_by_doc;
            if (total_owned_area > area_by_doc) {
                $('#total_owned_area').val('Притежаваната площ не може да е по-голяма от площта на нивата');
            } else {
                $('#total_owned_area').val(total_owned_area);
            }
        }
    }
}

function populate_locality_fields() {
    var input_text_split = $('#id').val().split(".", 3);
    if (input_text_split.length > 1) {
        var locality_id = input_text_split[0];
        $('#locality_id').attr('value', locality_id);
        if (locality_id in localities_json) {
            $('#locality_name').attr('value', localities_json[locality_id][0]);
        } else {
            $('#locality_name').attr('value', 'Неразпознато ЕКАТТЕ');
        }
    } else {
        $('#locality_id').attr('value', '');
        $('#locality_name').attr('value', '');
    }
    if (input_text_split.length > 2) {
        var sublocality_id = input_text_split[1];
        $('#sublocality_id').attr('value', sublocality_id);
        $('#plot').attr('value', input_text_split[2]);
        if (typeof localities_json[locality_id] === 'undefined') {
            $('#sublocality_name').attr('value', 'Неразпозната местност');
        } else {
            var current_locality_sublocalities = localities_json[locality_id][1];
            if (typeof current_locality_sublocalities[sublocality_id] === 'undefined') {
                $('#sublocality_name').attr('value', 'Неразпозната местност');
            } else {
                $('#sublocality_name').attr('value', current_locality_sublocalities[sublocality_id]);
            }
        }
    } else {
        $('#sublocality_id').attr('value', '');
        $('#sublocality_name').attr('value', '');
        $('#plot').attr('value', '');
    }
}

$(document).ready(function () {
    populate_locality_fields();

    // Paginated search JS
    $('#search_query_input').on("keydown", function (e) {
        if (e.which == 13) {
            window.location = $('#search_anchor').attr("href")
        }
    });

    $('#search_query_input').on("keyup", function () {
        var prev_anchor_href = $("#search_anchor").attr("href");
        var query_string = $(this).val();
        $('#search_anchor, .page-link').each(function () {
            var prev_anchor_href = $(this).attr("href");
            var index_of_query_param = prev_anchor_href.indexOf("&query=");
            if (index_of_query_param === -1) {
                var next_anchor_href = prev_anchor_href.concat('&query=', query_string);
            } else {
                var next_anchor_base = prev_anchor_href.slice(0, index_of_query_param);
                var next_anchor_href = next_anchor_base.concat("&query=", query_string);
            }
            $(this).attr("href", encodeURI(next_anchor_href))
        });
    });

    // Save base action path /plots in add plot form
    var base_add_plot_form_action = $('#add_plot_form').attr('action')
    // Disable btn-next if owner is not selected
    $('.first-next-btn').attr('disabled', true);
    // Preload data in ownership plot details
    $('#area_display').attr('disabled', true);
    $('#total_owned_area').attr('disabled', true);
    $('.second-next-btn').click(function () {
        $('#area_display').val($('#area_by_doc').val());
        calculate_total_owned_area();
    });
    $("#owned_plot_fraction_numerator").val('1');
    $("#owned_plot_fraction_denominator").val('1');
    $("#additional_owned_area").val('0');

    //........................Plots main page JS.................
    $('*[data-href]').on("click", function () {
        window.location = $(this).data('href');
        return false;

    });
    $('.plots-table tbody').on('click','.plot-delete',function(e){
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


    //.................Add plot form JS...........................

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

    // Owners table in add plot form(step 1)
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
            $('#add_plot_form').attr('action', base_add_plot_form_action);
            $('.first-next-btn').attr('disabled', true);
        } else {
            $('#add_plot_form').attr('action', base_add_plot_form_action + '?owner_id=' + $(this).attr('owner_id'));
            $(this).addClass('active').siblings().removeClass('active');
            $('.first-next-btn').attr('disabled', false);
        }
    });

    //Plot information form(step 2)
    // Disable fields only for displaying information
    $('#locality_id, #locality_name, #sublocality_id, #sublocality_name, #plot').attr("disabled", true);

    /* Loading data from localities_json(global defined variable in plots.html scripts)
     and displaying it in disabled fields from above) */
    $('#id').keyup(populate_locality_fields);

    $('#area_by_doc').keyup(function () {
        $('#area_display').attr('value', $('#area_by_doc').val());
        calculate_total_owned_area();
    });

    // Disable first options in select fields
    $("#category option:first, #use_type_id option:first").attr("disabled", "disabled");

    // Reset all form fields on btn cancel click
    $('#add_plot_cancel_btn').click(function () {
        $("#add_plot_form").trigger('reset');
    });

    /*If owner_id is preselected (if redirected to plots page from add owner form or if errors exist on add plot form)
    open add plot modal beginning from step 2
    */

    if ($('.preselected-owner-id').val() != "None") {
        jQuery('#open_addPlotModal_btn').click();
        jQuery('.first-next-btn').click();
        $('.first-prev-btn').attr('disabled', true);
    }

    //Ownership plot information form(step 3)
    //Date picker
    jQuery('#doc_date').datetimepicker({
        timepicker: false,
        format: 'd/m/Y',
        scrollInput: false,
    });
    $.datetimepicker.setLocale('bg');

    var stored_doc_path = $('#stored_doc_path').val()
    //FIle upload
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

    // Hide main modal on file preview modal
    $('#kvFileinputModal').on('shown.bs.modal', function () {
        $('#addPlotModal').modal('hide');
    });
    $('#kvFileinputModal').on('hidden.bs.modal', function () {
        $('#addPlotModal').modal('show');
    });
    //Total owned area calculation
    $("#owned_plot_fraction_numerator, #owned_plot_fraction_denominator, #additional_owned_area").on("keyup", calculate_total_owned_area);

    // Displaying data(preview)


    //$('.select-owners-table tbody tr .active').find('.active');

    $('.next').last().click(function () {
        var map = {};
        $('fieldset').not(":last").find('input[type=text],select,textarea').each(function () {
            map[$(this).attr("name")] = $(this).val();
        });
        console.log(map);

        $('fieldset').last().find('input[type=text],select,textarea').each(function () {
            $(this).prop('disabled', true);
            $(this).val(map[$(this).attr("name").split('_').slice(0, -1).join('_')]);
        });

    });

    //.................Edit plot form JS...........................

    //Hide edit buttons until edit icon button is clicked
    $('.edit-plot-buttons-container').hide();

    // Disable all fields until edit icon button is clicked
    $("#edit_plot_form :input").each(function () {
        $(this).attr("disabled", true);
    });


    //Show edit buttons and Enable  all fields except specified when edit icon button is clicked
    $("#edit-icon-btn").click(function () {
        $('.edit-plot-buttons-container').show();
        $("#edit_plot_form :input").not("#id, #locality_id, #sublocality_id, #locality_name, #sublocality_name, #plot").each(function () {
            $(this).attr("disabled", false);
        });
    });

    // Disable all fields when cancel button is clicked
    $('#edit_plot_cancel_btn').click(function () {
        $("#edit_plot_form :input").each(function () {
            $(this).attr("disabled", true);
        });
        $('.edit-plot-buttons-container').hide();
    });


});

