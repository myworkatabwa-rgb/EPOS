$(document).ready(function () {
    const table = $('#itemTable').DataTable({
        pageLength: 10,
        lengthChange: true,
        dom: 'Bfrtip',
        buttons: [
            { extend: 'excel', className: 'btn btn-sm btn-outline-secondary' },
            { extend: 'pdf', className: 'btn btn-sm btn-outline-secondary' },
            { extend: 'csv', className: 'btn btn-sm btn-outline-secondary' },
            { extend: 'colvis', className: 'btn btn-sm btn-outline-secondary' }
        ]
    });

    table.buttons().container().appendTo('#tableButtons');

    $('#itemSearch').on('keyup', function () {
        table.search(this.value).draw();
    });
});
$(document).ready(function () {

    const table = $('#itemTable').DataTable({
        pageLength: 10,
        dom: 'Bfrtip',
        buttons: ['excel', 'csv', 'pdf', 'colvis']
    });

    table.buttons().container().appendTo('#tableButtons');

    $('#itemSearch').on('keyup', function () {
        table.search(this.value).draw();
    });

    // IMPORT FORM
    $('#importForm').on('submit', function (e) {
        e.preventDefault();

        let formData = new FormData(this);

        $('#importStatus').html('<span class="text-info">Importing...</span>');

        $.ajax({
            url: "/items/import/",
            method: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function () {
                $('#importStatus').html('<span class="text-success">Import successful</span>');
                $('#importModal').modal('hide');

                // Reload page to refresh items
                location.reload();
            },
            error: function (xhr) {
                $('#importStatus').html(
                    '<span class="text-danger">' + xhr.responseText + '</span>'
                );
            }
        });
    });

});
