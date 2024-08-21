window.onload = function() {
    let blog_content_el = document.getElementsByClassName('form-row field-content')[0].getElementsByClassName("readonly")[0]
    console.log("blog_content_el", blog_content_el);
    
    if (blog_content_el!=undefined){
        
        blog_content_el.innerHTML = blog_content_el.innerText
    }
    // console.log(blog_content_el.innerText);

    const blog_context_group = document.getElementById("blog_contexts-group")
    const blog_context_field_container = blog_context_group.getElementsByClassName("inline-related")
    for (let i = 0; i < blog_context_field_container.length; i++) {

        const blog_context_description = blog_context_field_container[i].getElementsByClassName("form-row field-description")[0]
        const description = blog_context_description.getElementsByClassName("readonly")[0]
        if(description!=undefined){

            description.innerHTML = description.innerText
            console.log(description);
        }

    }


    const blog_feedback_group = document.getElementById("blogmoderatorfeedback_set-group")
    
    const blog_feedback_field_container = blog_feedback_group.getElementsByClassName("inline-related")
    console.log(blog_feedback_field_container.length);
    
    // for (var i = 0; blog_feedback_field_container.length<i; i++) {
    //     console.log("i", i);
        
    //   const element = blog_feedback_field_container[i];
    //   console.log("element", element);
       
    // }
    // const user = "{{request.user}}"
    // console.log(user);
    
    for (let index = 0; index < blog_feedback_field_container.length; index++) {
        const element = blog_feedback_field_container[index];
        const created_by = element.getElementsByClassName("form-row field-created_by_title")[0].getElementsByClassName("readonly")[0]
        const feedback = element.getElementsByClassName("form-row field-feedback")[0].getElementsByClassName("readonly")[0]
        feedback.innerHTML = feedback.innerText
        
        
    }
    
}