// Global functions for creating multi selects
Array.prototype.search = function(elem) {
    for(var i = 0; i < this.length; i++) {
        if(this[i] == elem) return i;
    }
    return -1;
};

var Multiselect = function(selector) {
    if(!$(selector)) {
        console.error("ERROR: Element %s does not exist.", selector);
        return;
    }

    this.selector = selector;
    this.selections = [];

    (function(that) {
        that.events();
    })(this);
};

Multiselect.prototype = {
    open: function(that) {
        var target = $(that).parent().attr("data-target");

        // If we are not keeping track of this one's entries, then
        // start doing so.
        if(!this.selections) {
            this.selections = [ ];
        }

        $(this.selector + ".multiselect").toggleClass("active");
    },

    close: function() {
        $(this.selector + ".multiselect").removeClass("active");
    },

    events: function() {
        var that = this;

        $(document).on("click", that.selector + ".multiselect > .title", function(e) {
            if(e.target.className.indexOf("close-icon") < 0) {
                that.open();
            }
        });

        $(document).on("click", that.selector + ".multiselect option", function(e) {
            var selection = $(this).attr("value");
            var target = $(this).parent().parent().attr("data-target");

            var io = that.selections.search(selection);

            if(io < 0) that.selections.push(selection);
            else that.selections.splice(io, 1);

            that.selectionStatus();
            that.setSelectionsString();
        });

        $(document).on("click", that.selector + ".multiselect > .title > .close-icon", function(e) {
            that.clearSelections();
        });

        $(document).click(function(e) {
            if(e.target.className.indexOf("title") < 0) {
                if(e.target.className.indexOf("text") < 0) {
                    if(e.target.className.indexOf("-icon") < 0) {
                        if(e.target.className.indexOf("selected") < 0 ||
                           e.target.localName != "option") {
                            that.close();
                        }
                    }
                }
            }
        });
    },

    selectionStatus: function() {
        var obj = $(this.selector + ".multiselect");

        if(this.selections.length) obj.addClass("selection");
        else obj.removeClass("selection");
    },

    clearSelections: function() {
        this.selections = [];
        this.selectionStatus();
        this.setSelectionsString();
    },

    getSelections: function() {
        return this.selections;
    },

    setSelectionsString: function() {
        var selects = this.getSelectionsString().split(", ");
        $(this.selector + ".multiselect > .title").attr("title", selects);

        var opts = $(this.selector + ".multiselect option");

        if(selects.length > 6) {
            var _selects = this.getSelectionsString().split(", ");
            _selects = _selects.splice(0, 6);
            $(this.selector + ".multiselect > .title > .text")
                .text(_selects + " [...]");
        }
        else {
            $(this.selector + ".multiselect > .title > .text")
                .text(selects);
        }

        for(var i = 0; i < opts.length; i++) {
            $(opts[i]).removeClass("selected");
        }

        for(var j = 0; j < selects.length; j++) {
            var select = selects[j];

            for(var i = 0; i < opts.length; i++) {
                if($(opts[i]).attr("value") == select) {
                    $(opts[i]).addClass("selected");
                    break;
                }
            }
        }
    },

    getSelectionsString: function() {
        if(this.selections.length > 0)
            return this.selections.join(", ");
        else{
             if(this.selector == '#grain_types_select')
                return "Изберете житни култури";
             else
                return "Изберете семистели за смески";
        }
    },

    setSelections: function(arr) {
        if(!arr[0]) {
            error("ERROR: This does not look like an array.");
            return;
        }

        this.selections = arr;
        this.selectionStatus();
        this.setSelectionsString();
    },
};

$(document).ready(function () {
    // Settings menu
    var navItems = $('.settings-menu li > a');
    var navListItems = $('.settings-menu li');
    var allWells = $('.settings-content');
    var allWellsExceptFirst = $('.settings-content:not(:first)');
    allWellsExceptFirst.hide();
    navItems.click(function(e)
    {
        e.preventDefault();
        navListItems.removeClass('active');
        $(this).closest('li').addClass('active');
        allWells.hide();
        var target = $(this).attr('data-target-id');
        $('#' + target).show();
    });
     // Add options to multi selects
     var grain_type_options = ['Пшеница', 'Ечемик', 'Рапица', 'Слънчоглед', 'Царевица', 'Кориандър']
     for(i = 0; i < grain_type_options.length; i++ ){
       optionValue = grain_type_options[i];
       optionText = grain_type_options[i];
       $('.grain-types-options-list').append(`<option value="${optionValue}">
                                       ${optionText}
                                       </option>`);
     }
     var mixed_grain_holders_options = ['Мария Пенева','Васил Петров','Петър Петров']
     for(i = 0; i < mixed_grain_holders_options.length; i++ ){
       optionValue = mixed_grain_holders_options[i];
       optionText = mixed_grain_holders_options[i];
       $('.mixed-grain-holders-options-list').append(`<option value="${optionValue}">
                                       ${optionText}
                                       </option>`);
     }
      var multi_grain_types = new Multiselect("#grain_types_select");
      var multi_mixed_grain_holders = new Multiselect("#mixed_grain_holders");

     //Date pickers for contract settings

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
    jQuery('#cash_payment_doc_date').datetimepicker({
        timepicker: false,
        format: 'd/m/Y',
        scrollInput: false,
    });
    jQuery('#bank_payment_doc_date').datetimepicker({
        timepicker: false,
        format: 'd/m/Y',
        scrollInput: false,
    });

    $.datetimepicker.setLocale('bg');

    // Disable first options in select fields
    $("#BIC option:first").attr("disabled", "disabled");

    // Get selected values from multi selects and put them in inputs in order to be submitted with the form
    $("#selected_grain_mixers_component").on('DOMSubtreeModified', function () {
        $("#selected_grain_mixers_input").attr("value", this.textContent);
        console.log(this.textContent);
    });

    $("#selected_grain_types_component").on('DOMSubtreeModified', function () {
        $("#selected_grain_types_input").attr("value", this.textContent);
        console.log(this.textContent);
    });
    // Preview data in multi selects from settings config file
    var selected_grain_types_input = $('#selected_grain_types_input').val();
    var selected_grain_mixers_input = $('#selected_grain_mixers_input').val();
    $("#selected_grain_types_component").text(selected_grain_types_input);
    $("#selected_grain_mixers_component").text(selected_grain_mixers_input);

    // Check chosen radio button based on settings config file
    if($("#checked_radio_value").val()=='ByDocumentArea'){
        $("#rent_by_doc_option").prop("checked", true);
    }else if($("#checked_radio_value").val()=='ByWorkableArea'){
        $("#rent_by_workable_area_radio").prop("checked", true);
    }

});