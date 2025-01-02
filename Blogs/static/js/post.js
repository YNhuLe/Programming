//clear out the comment text field after submission
//wait for the DOM fully loaded
document.addEventListener("DOMContentLoaded", function(){
    document.getElementById("myForm").addEventListener('submit', function(event){

        setTimeout(() => {
        const editor = CKEDITOR.instances['comment_text'];
        if (editor){ // check if the editor instance exist
            editor.setData('');  //clears the content of the CKEditor field after the form submission is completed

        }
    }, 100);// add the delay which allows the submission to complete
    });

});