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
