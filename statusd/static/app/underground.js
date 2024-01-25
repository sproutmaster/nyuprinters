$(document).ready(function () {
    const modalPrinterTitle = $('#printerModalTitle');
    const modalPrinterName = $('#printerModalName');
    const modalPrinterIP = $('#printerModalIP');
    const modalPrinterBrand = $('#printerModalBrand');
    const modalPrinterLocation = $('#printerModalLocation');
    const modalPrinterModel = $('#printerModalModel');
    const modalPrinterSerial = $('#printerModalSerial');
    const modalPrinterComment = $('#printerModalComment');
    const modalPrinterType = $('#printerModalType');
    const modalPrinterDisplay = $('#printerModalDisplay');
    const modalPrinterSubmit = $('#printerModalSubmit');

    const modalDelete = $('#deleteModal');
    const modalDeleteTitle = $('#deleteModalTitle');
    const modalDeleteSubmit = $('#deleteModalSubmit');
    const modalDeleteMessage = $('#deleteModalMessage');

    const modalLocation = $('#locationModal');
    const modalLocationTitle = $('#locationModalTitle');
    const modalLocationName = $('#locationModalName');
    const modalLocationShort = $('#locationModalShort');
    const modalLocationDescription = $('#locationModalDescription');
    const modalLocationVisible = $('#locationModalVisible');
    const modalLocationSubmit = $('#locationModalSubmit');

    let addPrinterMode = false;
    let smartfetchFinished = false;
    let addPrinterModeIP;
    let current_printer_id;
    let current_location_id;
    let locationAction;
    let deleteAction;


    modalLocation.on('show.bs.modal', function (e) {
        const button = $(e.relatedTarget);
        current_location_id = button.data('location-id');
        if (button.data('action') === 'add_location') {
            locationAction = 'add_location';
            modalLocationTitle.text('Add Location');
        }
        else {
            modalLocationTitle.text('Edit Location');
            locationAction = 'edit_location';
            $.ajax({
                url: $(location).attr('origin') + '/api/locations',
                type: 'GET',
                data: {
                    location_id: button.data('location-id'),
                },
                success: (data) => {
                    modalLocationName.val(data.name).text(data.name);
                    modalLocationShort.val(data.short).text(data.short);
                    modalLocationDescription.val(data.description).text(data.description);
                    modalLocationVisible.prop('checked', data.visible);
                },
                error: () => {
                    alert('Cannot connect to server');
                }
            });
        }
    });

    modalLocationSubmit.on('click', function () {
        if (modalLocationName.val() === '' || modalLocationShort.val() === '') {
            alert('Please fill all required fields');
            return;
        }

        if (locationAction === 'add_location') {
            location_actions('PUT', 0, modalLocationName.val(), modalLocationShort.val(), modalLocationDescription.val(), modalLocationVisible.is(":checked"));
        }
        else if (locationAction === 'edit_location') {
            location_actions('PATCH', current_location_id, modalLocationName.val(), modalLocationShort.val(), modalLocationDescription.val(), modalLocationVisible.is(":checked"));
        }
        modalLocation.modal('hide');
        setTimeout(fill_locations_table, 500);
    });


    $(document).on('show.bs.modal', '#deleteModal', function (e) {
        const button = $(e.relatedTarget); // Button that triggered the modal
        deleteAction = button.data('action');

        if (deleteAction === 'delete_printer') {
            current_printer_id = button.data('printer-id');
            modalDeleteTitle.text('Delete Printer');
            modalDeleteMessage.text(`Are you sure you want to delete ${button.data('printer-name')}?`);
        } else if (deleteAction === 'delete_location') {
            current_location_id = button.data('location-id');
            modalDeleteTitle.text('Delete Location');
            modalDeleteMessage.text(`Are you sure you want to delete ${button.data('location-name')}?`);
        }
    });

    $(document).on('hide.bs.modal', '#deleteModal', function (e) {
        current_printer_id = null;
        deleteAction = null;
    });

    modalDeleteSubmit.on('click', function () {
        if (deleteAction === 'delete_printer') {
            $.ajax({
                url: $(location).attr('origin') + '/api/printers',
                type: 'DELETE',
                data: {
                    printer_id: current_printer_id,
                },
                success: (data) => {
                    alert(data.message);
                    modalDelete.modal('hide');
                    window.location.reload();
                },
                error: (data) => {
                    alert('Cannot connect to server');
                }
            });
        } else if (deleteAction === 'delete_location') {
            location_actions('DELETE', current_location_id);
            setTimeout(fill_locations_table, 500);
        }
        modalDelete.modal('hide');
    });


    $(document).on('show.bs.modal', '#printerModal', function (e) {
        const button = $(e.relatedTarget); // Button that triggered the modal
        current_printer_id = button.data('printer-id');
         // Add title to modal
        if (button.data('action') === 'add_printer') {
            addPrinterMode = true;
            modalPrinterTitle.text('Add Printer');
            modalPrinterName.prop('placeholder', 'Leave blank for Smartfetch™');
            modalPrinterModel.prop('placeholder', 'Leave blank for Smartfetch™');
            modalPrinterSerial.prop('placeholder', 'Leave blank for Smartfetch™');
            modalPrinterType.prop('disabled', true);
            modalPrinterSubmit.text('Continue');
            fill_location_data(); // Fill available locations inside printer modal
        } else {
            modalPrinterTitle.text('Edit Printer');
            modalPrinterName.prop('placeholder', 'Enter printer name (30 chars max)');
            modalPrinterModel.prop('placeholder', 'Enter printer model (30 chars max)');
            modalPrinterSerial.prop('placeholder', 'Enter printer serial (30 chars max)');
            modalPrinterType.prop('disabled', false);
        }
        fill_printer_data(current_printer_id); // Fill printer data inside printer modal
    });

    $(document).on('hide.bs.modal', '#printerModal', function (e) {
        addPrinterMode = false;
        smartfetchFinished = false;
        current_printer_id = null;
        set_write_perm(modalPrinterIP, true);
        modalPrinterName.val('');
        modalPrinterIP.val('');
        modalPrinterModel.val('');
        modalPrinterSerial.val('');
        modalPrinterComment.val('');
        modalPrinterType.prop('checked', false);
    });

    modalPrinterSubmit.on('click', function () {
        if (!addPrinterMode || (addPrinterMode && smartfetchFinished)) {
            if (!req_printer_fields_filled()) {
                alert('Please fill all required fields');
                return;
            }
        }
        if (!isValidIP(modalPrinterIP.val())) {
            alert('Please enter a valid IP address');
            return;
        }

        // Get data from sourced and present it to user to confirm before adding
        if (addPrinterMode && !smartfetchFinished) {
            modalPrinterSubmit.append($('<span></span>').addClass('spinner-border spinner-border-sm').attr('role', 'status'));
            modalPrinterSubmit.prop('disabled', true);
            set_write_perm(modalPrinterIP, false);
            addPrinterModeIP = modalPrinterIP.val();
            $.ajax({
                url: $(location).attr('origin') + '/api/printers',
                type: 'POST',
                data: {
                    ip: addPrinterModeIP,
                },
                success: (data) => {
                    if (data.response.status === 'success') {
                        smartfetchFinished = true;
                        modalPrinterSubmit.text('Add').prop('disabled', false);

                        let name = data.response.message.name;
                        let model = data.response.message.model;
                        let serial = data.response.message.serial;
                        let color = data.response.message.type === 'color';

                        if (!modalPrinterName.val()) modalPrinterName.val(name).text(name);
                        if (!modalPrinterModel.val()) modalPrinterModel.val(model).text(model);
                        if (!modalPrinterSerial.val()) modalPrinterSerial.val(serial).text(serial);
                        modalPrinterType.val(data.type).prop('checked', color);
                        modalPrinterType.prop('disabled', false);
                    } else {
                        alert(data.response.message);
                        set_write_perm(modalPrinterIP, true);
                    }
                    modalPrinterSubmit.find('span').remove();
                    modalPrinterSubmit.prop('disabled', false);
                }
            });
        } else if (addPrinterMode && smartfetchFinished) {
            send_printer_data('PUT');
        } else {
            send_printer_data('PATCH');
        }
    });

    function send_printer_data(method) {
        $.ajax({
            url: $(location).attr('origin') + '/api/printers',
            type: method,
            data: {
                printer_id: current_printer_id,
                name: modalPrinterName.val(),
                ip: modalPrinterIP.val(),
                brand: modalPrinterBrand.val(),
                location: modalPrinterLocation.val(),
                model: modalPrinterModel.val(),
                serial: modalPrinterSerial.val(),
                comment: modalPrinterComment.val(),
                type: modalPrinterType.is(":checked"),
                visible: modalPrinterDisplay.is(":checked"),
            },
            success: (data) => {
                alert(data.message);
                $('#printerModal').modal('hide');
                window.location.reload();
            },
            error: (data) => {
                alert('Cannot connect to server');
            }
        });
    }

    function fill_location_data(selectedOption = null) {
        $.ajax({
            url: $(location).attr('origin') + '/api/locations',
            type: 'GET',
            success: (data) => {
                if (selectedOption) modalPrinterLocation.empty(); // Remove all options for location
                else modalPrinterLocation.find('option:gt(0)').remove(); // Remove all options except first for location

                data.forEach((item) => {
                    let sel = (item.short === selectedOption) ? 'selected' : '';
                    let option = `<option value="${item.short}" ${sel}>${item.name}</option>`
                    modalPrinterLocation.append(option);
                });
            },
            error: (data) => {
                alert('Cannot connect to server');
            }
        });
    }

    function fill_printer_data(id) {
        if (id) {
            $.ajax({
                url: $(location).attr('origin') + '/api/printers',
                type: 'GET',
                data: {
                    printer_id: id,
                },
                success: (data) => {
                    modalPrinterName.val(data.meta.name);
                    modalPrinterIP.val(data.meta.ip);
                    // modalPrinterBrand.val(data.meta.brand).text(data.meta.brand).change();
                    fill_location_data(data.meta.location);
                    modalPrinterModel.val(data.meta.model);
                    modalPrinterSerial.val(data.meta.serial);
                    modalPrinterComment.val(data.meta.comment);
                    modalPrinterType.prop('checked', data.meta.type === 'color');
                    modalPrinterDisplay.prop('checked', data.meta.visible);
                },
                error: (data) => {
                    alert('Cannot connect to server');
                }
            });
        }
    }
});

function isValidIP(str) {
    const octet = '(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]?|0)';
    const regex = new RegExp(`^${octet}\\.${octet}\\.${octet}\\.${octet}$`);
    return regex.test(str);
}

function show_tab(tab) {
    const tabs = ['printersContainer', 'locationsContainer', 'settingsContainer', 'usersContainer', 'profileContainer', 'aboutContainer'];
    tabs.forEach((item) => {
        if (item === tab)
            $('#' + item).removeClass('_hidden');
        else
            $('#' + item).addClass('_hidden');
    });
}

function set_write_perm(dom, perm) {
    if (perm) {
        dom.parent().removeClass('form-outline');
        dom.removeClass('theme-dark');
    } else {
        dom.parent().addClass('form-outline');
        dom.addClass('theme-dark');
    }
    dom.prop('readonly', !perm);
}

function req_printer_fields_filled() {
    return (
        $('#printerModalName').val() !== '' &&
        $('#printerModalBrand').val() !== '' &&
        $('#printerModalLocation').val() !== 'Select one'
    );
}

function location_actions(action, id = 0, name = '', short = '', desc = '', visible = false) {
    $.ajax({
        url: $(location).attr('origin') + '/api/locations',
        type: action,
        data: {
            location_id: id,
            name: name,
            short: short,
            description: desc,
            visible: visible,
        },
        success: (data) => {
            alert(data.message);
        },
        error: (data) => {
            alert('Cannot connect to server');
        }
    });
}

function fill_locations_table() {
    $('#locationsTable tbody').empty();
    $.ajax({
        url: $(location).attr('origin') + '/api/locations',
        method: 'GET',
        success: (data) => {
            data.forEach((item) => {
                const row = '<tr>' +
                    '<td>' + item.name + '</td>' +
                    '<td>' + item.short + '</td>' +
                    '<td>' + item.printer_count + '</td>' +
                    '<td>' +
                    '<div>' +
                    '<button type="button" class="btn btn-link btn-sm" style="margin-right: -3px" data-mdb-modal-init ' +
                    'data-mdb-target="#locationModal" data-action="edit_location" data-location-id="' + item.id + '">' +

                    '<i class="fas fa-pencil"></i>' +
                    '</button>' +
                    '<button type="button" class="btn btn-link btn-sm" style="margin-left: -3px" data-mdb-modal-init ' +
                    'data-mdb-target="#deleteModal" data-action="delete_location" data-location-id="' + item.id + '" data-location-name="' + item.name + '">' +
                    '<i class="fas fa-times"></i>' +
                    '</button>' +
                    '</div>' +
                    '</td>' +
                    '</tr>';
                $('#locationsTable tbody').append(row);
            });
        },
        error: function () {
            console.error('Cannot connect to server');
        }
    });
}


function fill_settings() {
    $('')
}