(function($) {
    $(document).ready(function() {
        var parentSelect = $('#id_parent_services');
        var childSelect = $('#id_child_services');
        var childServicesData = window.childServicesData || [];

        function updateChildServices() {
            var selectedParents = parentSelect.val() || [];
            childSelect.empty();
            childSelect.append('<option value="">---------</option>');

            // Disable child select if no parents are selected
            if (selectedParents.length === 0) {
                childSelect.prop('disabled', true);
                if (childSelect.data('select2')) {
                    childSelect.trigger('change');
                }
                return;
            } else {
                childSelect.prop('disabled', false);
            }

            // Filter child services based on selected parents
            selectedParents = selectedParents.map(String);
            $.each(childServicesData, function(index, service) {
                if (service.parent_id && selectedParents.includes(String(service.parent_id))) {
                    var option = $('<option></option>')
                        .attr('value', service.id)
                        .text(service.title);
                    // Check if this child service was previously selected
                    if (childSelect.data('selected') && childSelect.data('selected').includes(String(service.id))) {
                        option.attr('selected', 'selected');
                    }
                    childSelect.append(option);
                }
            });

            // Trigger select2 update
            if (childSelect.data('select2')) {
                childSelect.trigger('change');
            }
        }

        // Store initial selected child services
        childSelect.data('selected', childSelect.val() || []);

        // Disable child select on page load if no parent is selected
        childSelect.prop('disabled', parentSelect.val() ? false : true);

        // Bind change event to parent select
        parentSelect.on('change', updateChildServices);

        // Handle select2 events
        if (parentSelect.data('select2')) {
            parentSelect.on('select2:select select2:unselect', updateChildServices);
        }

        // Initial update
        updateChildServices();
    });
})(django.jQuery);