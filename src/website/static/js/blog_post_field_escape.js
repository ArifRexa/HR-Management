window.onload = function() {
    const blog_content_container = document.getElementsByClassName('form-row field-content')[0]
    console.log("blog_content_container", blog_content_container);
    if (blog_content_container!=undefined){
        let blog_content_el = blog_content_container.getElementsByClassName("readonly")[0]
        if (blog_content_el!=undefined){
            blog_content_el.innerHTML = blog_content_el.innerText
        }
}
    // console.log(blog_content_el.innerText);

    const blog_context_group = document.getElementById("blog_contexts-group")
    if(blog_context_group!=undefined){
        const blog_context_field_container = blog_context_group.getElementsByClassName("inline-related")
        if(blog_context_field_container!=undefined){

            for (let i = 0; i < blog_context_field_container.length; i++) {
    
                const blog_context_description = blog_context_field_container[i].getElementsByClassName("form-row field-description")[0]
                const description = blog_context_description.getElementsByClassName("readonly")[0]
                if(description!=undefined){
    
                    description.innerHTML = description.innerText
                    console.log(description);
                }
    
            }
        }

    }


    const blog_feedback_group = document.getElementById("blogmoderatorfeedback_set-group")
    
    const blog_feedback_field_container = blog_feedback_group.getElementsByClassName("inline-related")
    console.log(blog_feedback_field_container.length);

    
    for (let index = 0; index < blog_feedback_field_container.length; index++) {
        const element = blog_feedback_field_container[index];
        if(element!=undefined){
            const feedback_container = element.getElementsByClassName("form-row field-feedback")[0]
            if(feedback_container!=undefined){
                const feedback = feedback_container.getElementsByClassName("readonly")[0]
                if(feedback!=undefined){
                feedback.innerHTML = feedback.innerText
                }
        }
        
        }
    }
    
}