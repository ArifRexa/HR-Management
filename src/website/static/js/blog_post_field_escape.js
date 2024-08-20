window.onload = function() {
    let blog_content_el = document.getElementsByClassName('form-row field-content')[0].getElementsByClassName("readonly")[0]

    blog_content_el.innerHTML = blog_content_el.innerText
    // console.log(blog_content_el.innerText);

    const blog_context_group = document.getElementById("blog_contexts-group")
    const blog_context_field_container = blog_context_group.getElementsByClassName("inline-related")
    for (let i = 0; i < blog_context_field_container.length; i++) {

        const blog_context_description = blog_context_field_container[i].getElementsByClassName("form-row field-description")[0]
        const description = blog_context_description.getElementsByClassName("readonly")[0]
        description.innerHTML = description.innerText
        console.log(description);

    }
    
    
}