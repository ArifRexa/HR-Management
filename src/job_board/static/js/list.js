window.onload = () => {
    console.log('asdf')
    let filterToggleButton = document.createElement('BUTTON')
    filterToggleButton.innerHTML = '>>'
    filterToggleButton.className = "btn btn-filter"

    let mainContent = document.getElementById('content-main')
    mainContent.style.position = 'relative'
    mainContent.prepend(filterToggleButton)

    let filter = document.getElementById('changelist-filter')

    filterToggleButton.onclick = () => {
        if (filter.style.display === 'none') {
            filter.style.display = 'block'
            filterToggleButton.innerHTML = '>>'
        } else {
            filter.style.display = 'none'
            filterToggleButton.innerHTML = '<<'
        }
    }


















    function getThisWeekHour(e){
        project = document.querySelector('#id_project');
        phour_date = document.querySelector("#id_date");

        add_btn = document.querySelector(".add-row a");
        if (project.value == "" || phour_date.value == "") {
            alert("Please select project and project hours date !!!");
            return;
        }
        $.ajax({
            url: "/projects/get-this-week-hour/" + project.value +"/" + phour_date.value + "/",
            type: "GET", //send it through get method

            success: function(data) {
                hour = data.weekly_hour;
                console.log(hour);
                for(var i=0; i<hour.length; i++){
                    hour_input = document.querySelector(`#id_employeeprojecthour_set-${i}-hours`);
                    employee_select = document.querySelector(`#id_employeeprojecthour_set-${i}-employee`);

                    update_input = document.querySelector(`#id_employeeprojecthour_set-${i}-update`);
                    update_id_input = document.querySelector(`#id_employeeprojecthour_set-${i}-update_id`);
                    update_id_input.value = hour[i].id;
                    console.log(hour[i].updates_json);
                    hour_input.value = hour[i].hours;
                    if (hour[i].updates_json){
                        console.log("json", hour[i]);
                        let v = ""
                        for(var j=0; j<hour[i].updates_json.length; j++){
                            v += hour[i].updates_json[j][0]
                        }
                        console.log(v)
                        update_input.value = v;
                    }else{
                        console.log("not json", hour[i].updates_json);
                        
                        update_input.value = hour[i].update
                    }
                    // let update_data = hours[i].update;
                    // update_input.value = update_data[0][0];
                    // console.log("hour", hour_input.value)

                    var optionNode = document.createElement("option");
                    optionNode.value = hour[i].employee_id;
                    optionNode.textContent = hour[i].full_name;
                    employee_select.appendChild(optionNode);
                    
                    {% comment %} employee_select.value = hours[i].id;  {% endcomment %}
                    {% comment %} console.log(hours[i].id, i); {% endcomment %}

                    {% comment %} employee_select.val('54');
                    employee_select.trigger('change'); {% endcomment %}
                    {% comment %} console.log($(`#id_employeeprojecthour_set-${i}-employee`)); {% endcomment %}

                    {% comment %} $(`#id_employeeprojecthour_set-${i}-employee`).val(hours[i].id).trigger('change'); {% endcomment %}

                    add_btn.click();
                }

                document.querySelector("#id_hours").value = data.total_project_hours;
                generate_btn = document.querySelector("#generate-btn");
                generate_btn.disabled = true;
                console.log(generate_btn)
            },
            error: function(xhr) {
                console.log("error");
                console.log(data)
            }
        });
        
    }
    const path = window.location.pathname;
    const path_list = path.split("/").filter(n=>n);
    const action = path_list[path_list.length-1];
    console.log(action)
    if (action == "change"){
        console.log("change action")
        getThisWeekHour();
    }

}