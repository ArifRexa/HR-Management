window.onload = function(e){
    const _hour = document.getElementById('id_hours')
    _hour.readOnly=true
console.log("update project hour")
function updateProjectHour(project_hour_id=null){
    project = document.querySelector('#id_project');
    phour_date = document.querySelector("#id_date");
    add_btn = document.querySelector(".add-row a");
    // if (project.value == "" || phour_date.value == "") {
    //     alert("Please select project and project hours date !!!");
    //     return;
    // }
   let url= "/projects/get-this-week-hour/" + project.value +"/" + phour_date.value + "/"
    if (project_hour_id!=null){
        url +="?project_hour_id=" + project_hour_id
    }
   const type= "GET"
   const xhttp = new XMLHttpRequest();
   xhttp.onload = function() {
    const data = JSON.parse(this.responseText);
    hour = data.weekly_hour;
    for(var i=0; i<hour.length; i++){
        hour_input = document.querySelector(`#id_employeeprojecthour_set-${i}-hours`);
        employee_select = document.querySelector(`#id_employeeprojecthour_set-${i}-employee`);
        update_input = document.querySelector(`#id_employeeprojecthour_set-${i}-update`);
        update_id_input = document.querySelector(`#id_employeeprojecthour_set-${i}-update_id`);
        update_id_input.value = hour[i].id;
        date = document.querySelector(`#id_employeeprojecthour_set-${i}-date`);
        date.value = hour[i].created_at.substring(0, 10);
        if (hour_input != null){
            hour_input.addEventListener("keyup", update_total_hour)
        }
        // hour_input.value = hour[i].hours;
        if (hour[i].updates_json){
            let v = ""
            for(var j=0; j<hour[i].updates_json.length; j++){
                v += hour[i].updates_json[j][0]
            }
            update_input.value = v;
        }else{
            
            update_input.value = hour[i].update
        }
        // let update_data = hours[i].update;
        // update_input.value = update_data[0][0];
        // console.log("hour", hour_input.value)

        // var optionNode = document.createElement("option");
        // optionNode.value = hour[i].employee_id;
        // optionNode.textContent = hour[i].full_name;
        // employee_select.appendChild(optionNode);
        
        // {% comment %} employee_select.value = hours[i].id;  {% endcomment %}
        // {% comment %} console.log(hours[i].id, i); {% endcomment %}

        // {% comment %} employee_select.val('54');
        // employee_select.trigger('change'); {% endcomment %}
        // {% comment %} console.log($(`#id_employeeprojecthour_set-${i}-employee`)); {% endcomment %}

        // {% comment %} $(`#id_employeeprojecthour_set-${i}-employee`).val(hours[i].id).trigger('change'); {% endcomment %}

        // add_btn.click();
    }

    // document.querySelector("#id_hours").value = data.total_project_hours;
    generate_btn = document.querySelector("#generate-btn");
    // generate_btn.disabled = true;
    // console.log(generate_btn)
},
   xhttp.open(type, url);
   xhttp.send();
}
function getThisWeekHour(e){
    project = document.querySelector('#id_project');
    phour_date = document.querySelector("#id_date");
    console.log(project, phour_date);
    add_btn = document.querySelector(".add-row a");
    // if (project.value == "" || phour_date.value == "") {
    //     alert("Please select project and project hours date !!!");
    //     return;
    // }
    const xhttp = new XMLHttpRequest();
    
    $.ajax({
        url: "/projects/get-this-week-hour/" + project.value +"/" + phour_date.value + "/",
        type: "GET", //send it through get method

        success: function(data) {
            hour = data.weekly_hour;
            console.log(hour,"This is update hour");
            
            for(var i=0; i<hour.length; i++){
                hour_input = document.querySelector(`#id_employeeprojecthour_set-${i}-hours`);
                employee_select = document.querySelector(`#id_employeeprojecthour_set-${i}-employee`);
                date = document.querySelector(`#id_employeeprojecthour_set-${i}-date`);
                date.value = hour[i].created_at.substring(0, 10);
                update_input = document.querySelector(`#id_employeeprojecthour_set-${i}-update`);
                update_id_input = document.querySelector(`#id_employeeprojecthour_set-${i}-update_id`);
                update_id_input.value = hour[i].id;
                console.log(hour[i].created_at,"This is date")
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
                
                // {% comment %} employee_select.value = hours[i].id;  {% endcomment %}
                // {% comment %} console.log(hours[i].id, i); {% endcomment %}

                // {% comment %} employee_select.val('54');
                // employee_select.trigger('change'); {% endcomment %}
                // {% comment %} console.log($(`#id_employeeprojecthour_set-${i}-employee`)); {% endcomment %}

                // {% comment %} $(`#id_employeeprojecthour_set-${i}-employee`).val(hours[i].id).trigger('change'); {% endcomment %}

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
if (action == "change"){
    console.log("change action")
    // setTimeout(updateProjectHour, 1000, path_list[path_list.length-2]);
    updateProjectHour(path_list[path_list.length-2]);
}

function update_total_hour(e){
    console.log("input on change event")

    const total_hour = document.getElementById('id_hours')

    const child_hours = document.getElementsByClassName("field-hours")
    let total = 0
    for(var i=1; i<child_hours.length; i++){
        if (child_hours[i].childNodes[1].value != ""){
            total +=  parseInt(child_hours[i].childNodes[1].value)
        }
        
    }
    total_hour.value = total
}


const currentFile = document.getElementsByClassName("file-upload")[0]
console.log("current file", currentFile)
if(currentFile){

    currentFile.getElementsByTagName('a')[0].target = "_blank"
}

}
