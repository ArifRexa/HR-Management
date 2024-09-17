document.addEventListener("DOMContentLoaded", function () {
    const path = window.location.pathname;
    const path_split = path.split("/");
    if (path_split.includes('change') || path_split.includes('add')) {
        let id_name;
        if (path_split.includes('group')) {
            id_name = 'id_permissions_to';
        } else {
            id_name = 'id_user_permissions_to';
        }
        function addSearchFunctionality() {
            console.log("addSearchFunctionality");
            
            let interval_count = 0
            if (selected_permissions_box == null) {
                console.log("null", interval_count);
                interval_count = interval_count + 1
                if (interval_count > 30) {
                    clearInterval(intervalId);
                }
                return
            }else{
                clearInterval(intervalId);
            }
            let selected_permissions_box = document.getElementById(
                id_name
            );
            let newHtml = `<p id="id_user_permissions_filter" class="selector-filter">
            <label for="id_user_permissions_selected_input">
            <span class="help-tooltip search-label-icon" title="Type into this box to filter down the list of available verbose name."></span>
            </label> 
            <input type="text" placeholder="Filter" id="id_user_permissions_selected_input" style="width: 88%; margin-left: 10px">
            </p>`;

            selected_permissions_box.style.height = "223.59px";
            selected_permissions_box.insertAdjacentHTML("beforebegin", newHtml);

            // Function to filter list based on search query
            function filterList(input, selectBox) {
                const searchTerm = input.value.toLowerCase();
                const options = selectBox.options;
                for (let i = 0; i < options.length; i++) {
                    const optionText = options[i].text.toLowerCase();
                    options[i].style.display = optionText.includes(searchTerm)
                        ? ""
                        : "none";
                }
            }

            const selectedSearchInput = document.getElementById(
                "id_user_permissions_selected_input"
            );

            selectedSearchInput.addEventListener("keyup", function () {
                console.log("key up");
                filterList(selectedSearchInput, selected_permissions_box);
            });
        }


        var intervalId = setInterval(addSearchFunctionality, 100);
        console.log(intervalId)
    }
});
