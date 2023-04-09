$(document).ready(function() {
    var maxForms = 2

    $('#add-form-button').click(function() {
        var formsetContainer = $('#formset-container tbody');
        var lastForm = formsetContainer.find('tr:last');
        var newForm = lastForm.clone();
        maxForms += 1
        newForm.find('input').val('');
        formsetContainer.append(newForm);
    });
    $(document).on('click', '.delete-form', function(){
        $(this).closest('tr').remove();
    });
});
