(function($) {
    console.log("=== Project Admin JS Loading ===");
    
    $(document).ready(function() {
        console.log("=== Document Ready ===");
        
        // Check if jQuery is available
        console.log("jQuery version:", $.fn.jquery);
        
        // Check if the services field exists
        var servicesField = $('#id_services');
        console.log("Services field found:", servicesField.length > 0);
        console.log("Services field:", servicesField);
        
        // Check if child services field exists
        var childServicesField = $('#id_child_services');
        console.log("Child services field found:", childServicesField.length > 0);
        
        // Store the previous state of selected services to prevent infinite loops
        var previousSelectedServices = servicesField.val() || [];
        
        function updateChildServicesState() {
            var selectedServices = servicesField.val() || [];
            console.log("Selected service IDs:", selectedServices);
            
            if (selectedServices.length === 0) {
                // Disable child_services field
                childServicesField.prop('disabled', true);
                console.log("Child services field disabled");
            } else {
                // Enable child_services field
                childServicesField.prop('disabled', false);
                console.log("Child services field enabled");
                
                // Filter child services
                childServicesField.find('option').each(function() {
                    var opt = $(this);
                    var childId = opt.val();
                    if (childId === '') return; // Skip blank option
                    var parentId = childParents[childId];
                    if (parentId && selectedServices.includes(parentId)) {
                        opt.show();
                        console.log(`Showing child ID ${childId} (parent: ${parentId})`);
                    } else {
                        opt.hide();
                        opt.prop('selected', false);
                        console.log(`Hiding child ID ${childId} (parent: ${parentId || 'none'})`);
                    }
                });
            }

            // Log child services for selected parent services
            console.log("=== CHILD SERVICE IDs FOR SELECTED PARENTS ===");
            var childServiceIds = [];
            Object.keys(childParents).forEach(function(childId) {
                var parentId = childParents[childId];
                if (selectedServices.includes(parentId)) {
                    childServiceIds.push(childId);
                }
            });
            console.log("Child service IDs:", childServiceIds);
            
        }

        function triggerSaveAndContinue() {
            var selectedServices = servicesField.val() || [];
            // Convert arrays to strings for comparison to avoid reference issues
            var currentServicesStr = selectedServices.sort().join(',');
            var previousServicesStr = previousSelectedServices.sort().join(',');
            
            if (selectedServices.length > 0 && currentServicesStr !== previousServicesStr) {
                console.log("Triggering save and continue editing...");
                // Set the _continue input to trigger "Save and continue editing"
                var continueInput = $('<input>').attr({
                    type: 'hidden',
                    name: '_continue',
                    value: '1'
                });
                // Append to form and submit
                var form = servicesField.closest('form');
                form.append(continueInput);
                form.submit();
                // Update previous state
                previousSelectedServices = selectedServices.slice();
            } else {
                console.log("No save needed: Services unchanged or empty");
            }
        }

        // Initial state: disable child_services if no services selected
        updateChildServicesState();
        
        // Bind change event
        servicesField.on('change', function() {
            console.log("=== SERVICES CHANGE EVENT TRIGGERED ===");
            updateChildServicesState();
            triggerSaveAndContinue();
        });
        
        console.log("=== EVENT BINDING COMPLETED ===");
        
        // Handle autocomplete fields loading dynamically
        $(document).on('DOMNodeInserted', function(e) {
            if ($(e.target).find('#id_services, #id_child_services').length > 0) {
                console.log("=== AUTOCOMPLETE FIELD LOADED ===");
                setTimeout(updateChildServicesState, 500); // Delay to ensure autocomplete options load
            }
        });
    });
    
    // Fallback if jQuery is not available
    if (typeof $ === 'undefined') {
        console.error("=== JQUERY NOT AVAILABLE ===");
    }
    
})(window.jQuery || django.jQuery);

// // // =================================================





// (function($) {
//     console.log("=== Project Admin JS Loading ===");
    
//     $(document).ready(function() {
//         console.log("=== Document Ready ===");
//         console.log("jQuery version:", $.fn.jquery);
        
//         var servicesField = $('#id_services');
//         var childServicesField = $('#id_child_services');
        
//         console.log("Services field found:", servicesField.length > 0);
//         console.log("Child services field found:", childServicesField.length > 0);
        
//         // Store the previous state of selected services
//         var previousSelectedServices = servicesField.val() || [];
        
//         function updateChildServicesAutocomplete() {
//             var selectedServices = servicesField.val() || [];
//             console.log("Selected parent service IDs:", selectedServices);
            
//             // Check if using django-autocomplete-light (Select2)
//             if (typeof childServicesField.data('select2') !== 'undefined') {
//                 console.log("Using Select2 autocomplete");
                
//                 if (selectedServices.length === 0) {
//                     // Disable the field
//                     childServicesField.prop('disabled', true);
//                     // Clear selections
//                     childServicesField.val(null).trigger('change');
//                 } else {
//                     // Enable the field
//                     childServicesField.prop('disabled', false);
                    
//                     // Update Select2 to use custom endpoint with parent filter
//                     var customUrl = '/admin/project_management/project/autocomplete-child-services/';
                    
//                     // Destroy existing Select2 instance
//                     childServicesField.select2('destroy');
                    
//                     // Reinitialize with custom AJAX configuration
//                     childServicesField.select2({
//                         ajax: {
//                             url: customUrl,
//                             dataType: 'json',
//                             delay: 250,
//                             data: function(params) {
//                                 return {
//                                     term: params.term,
//                                     parent_services: selectedServices.join(','),
//                                     page: params.page || 1
//                                 };
//                             },
//                             processResults: function(data) {
//                                 return {
//                                     results: data.results,
//                                     pagination: data.pagination
//                                 };
//                             },
//                             cache: true
//                         },
//                         minimumInputLength: 0,
//                         placeholder: 'Search for child services...',
//                         allowClear: true
//                     });
                    
//                     console.log("Select2 reinitialized with parent filter");
//                 }
//             } else {
//                 console.log("Using regular select field or admin-autocomplete");
                
//                 // Fallback for regular select fields
//                 if (selectedServices.length === 0) {
//                     childServicesField.prop('disabled', true);
//                     childServicesField.find('option:not([value=""])').hide().prop('selected', false);
//                 } else {
//                     childServicesField.prop('disabled', false);
                    
//                     // Get valid child service IDs
//                     var validChildIds = [];
//                     Object.keys(childParents).forEach(function(childId) {
//                         var parentId = childParents[childId];
//                         if (parentId && selectedServices.includes(parentId)) {
//                             validChildIds.push(childId);
//                         }
//                     });
                    
//                     console.log("Valid child service IDs:", validChildIds);
                    
//                     // Show/hide options
//                     childServicesField.find('option').each(function() {
//                         var opt = $(this);
//                         var childId = opt.val();
                        
//                         if (childId === '') return;
                        
//                         if (validChildIds.includes(childId)) {
//                             opt.show();
//                         } else {
//                             opt.hide();
//                             opt.prop('selected', false);
//                         }
//                     });
//                 }
//             }
//         }

//         function triggerSaveAndContinue() {
//             var selectedServices = servicesField.val() || [];
//             var currentServicesStr = selectedServices.sort().join(',');
//             var previousServicesStr = previousSelectedServices.sort().join(',');
            
//             if (selectedServices.length > 0 && currentServicesStr !== previousServicesStr) {
//                 console.log("Parent services changed - triggering save and continue...");
                
//                 var continueInput = $('<input>').attr({
//                     type: 'hidden',
//                     name: '_continue',
//                     value: '1'
//                 });
                
//                 var form = servicesField.closest('form');
//                 form.append(continueInput);
//                 form.submit();
                
//                 previousSelectedServices = selectedServices.slice();
//             } else {
//                 console.log("No save needed: Services unchanged or empty");
//             }
//         }

//         // Wait for autocomplete fields to initialize
//         setTimeout(function() {
//             updateChildServicesAutocomplete();
//         }, 500);
        
//         // Bind change event to parent services
//         servicesField.on('change', function() {
//             console.log("=== SERVICES CHANGE EVENT TRIGGERED ===");
//             updateChildServicesAutocomplete();
//             triggerSaveAndContinue();
//         });
        
//         console.log("=== EVENT BINDING COMPLETED ===");
//     });
    
//     if (typeof $ === 'undefined') {
//         console.error("=== JQUERY NOT AVAILABLE ===");
//     }
    
// })(window.jQuery || django.jQuery);