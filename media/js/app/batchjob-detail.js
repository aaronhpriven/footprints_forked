(function() {
    window.BatchJobDetailView = Backbone.View.extend({
        events: {
            'click .batch-job-row-container table td': 'clickRecord',
            'click button.update-record': 'updateRecord',
            'click button.delete-record': 'confirmDeleteRecord',
            'click #confirm-delete-modal .btn-primary': 'deleteRecord',
            'click #process-job': 'confirmProcessJob',
            'click #confirm-process-modal .btn-primary': 'processJob'
        },
        initialize: function(options) {
            _.bindAll(this, 'clickRecord', 'updateRecord', 'refreshRecord',
                'deleteRecord', 'confirmDeleteRecord', 'checkErrorState',
                'showModal', 'showSuccessModal', 'showErrorModal',
                'onKeydown', 'openRecord', 'closeRecord',
                'confirmProcessJob', 'processJob');

            this.baseUpdateUrl = options.baseUpdateUrl;

            this.checkErrorState();

            jQuery('body').click(this.closeRecord);
            jQuery('body').keydown(this.onKeydown);
        },
        checkErrorState: function() {
            if (jQuery(this.el).find('.has-error').length > 0) {
                jQuery(this.el).find('#process-job')
                               .attr('disabled', 'disabled');
                jQuery(this.el).find('.alert-danger').show();
            } else {
                jQuery(this.el).find('#process-job').removeAttr('disabled');
                jQuery(this.el).find('.alert-danger').hide();
            }
        },
        openRecord: function(dataId) {
            jQuery(this.el)
                .find('td[data-record-id="' + dataId + '"]')
                .addClass('selected');
            return false;
        },
        closeRecord: function(evt) {
            jQuery(this.el).find('td.selected').removeClass('selected');
            jQuery(this.el).find('.error-message, .success-message').hide();
        },
        onKeydown: function(evt) {
            var dataId;
            switch (evt.which) {
                case 37: // left
                    dataId = jQuery(this.el).find('td.selected').first()
                        .prev().data('record-id');
                    break;

                case 39: // right
                    dataId = jQuery(this.el).find('td.selected').first()
                        .next().data('record-id');
                    break;
                default:
                    return; // exit this handler for other keys
            }
            evt.preventDefault();
            if (dataId) {
                this.closeRecord();
                this.openRecord(dataId);
            }
            return false;
        },
        clickRecord: function(evt) {
            evt.preventDefault();
            var $td = jQuery(evt.currentTarget);
            jQuery(this.el).find('td.selected').removeClass('selected');

            var dataId = $td.data('record-id');
            this.openRecord(dataId);
            return false;
        },
        refreshRecord: function(json, textStatus, xhr) {
            // remove all status classes
            jQuery(this.el).find('td.selected').attr('class', 'selected');
            jQuery(this.el).find('.error-message, .success-message').hide();

            // update each record with its new status class(es)
            for (var field in json.errors) {
                var selector = 'td.selected input[type="text"][name="' +
                    field + '"]';
                var $elt = jQuery(this.el).find(selector).parents('td');
                if (json.errors.hasOwnProperty(field)) {
                    $elt.addClass(json.errors[field]);
                }
            }

            if (jQuery(this.el).find('td.selected.has-error').length === 0) {
                jQuery(this.el).find('td.selected .success-message').show();
            } else {
                jQuery(this.el).find('td.selected .error-message').show();
            }

            this.checkErrorState();
        },
        showModal: function(id) {
            jQuery(id).modal({
                'show': true,
                'backdrop': 'static',
                'keyboard': false
            });
        },
        showErrorModal: function() {
            this.showModal('#error-modal');
        },
        showSuccessModal: function() {
            this.showModal('#success-modal');
        },
        updateRecord: function(evt) {
            var self = this;
            var $target = jQuery(evt.currentTarget);

            var recordId = $target.parents('td').data('record-id');
            var url = this.baseUpdateUrl.replace(/(\d+)/g, recordId);

            var data = {};
            jQuery(this.el).find('td.selected input').each(function() {
                data[jQuery(this).attr('name')] = jQuery(this).val();
            });

            jQuery.ajax({
                url: url,
                type: 'post',
                data: data,
                success: self.refreshRecord,
                error: self.showErrorModal
            });
        },
        confirmDeleteRecord: function(evt) {
            evt.preventDefault();
            this.$form = jQuery(evt.currentTarget).parents('form');
            jQuery('#confirm-delete-modal').modal({
                'show': true, 'backdrop': 'static'
            });
            return false;
        },
        deleteRecord: function(evt) {
            this.$form.submit();
        },
        confirmProcessJob: function(evt) {
            evt.preventDefault();
            this.$process = jQuery(evt.currentTarget).parents('form');
            jQuery('#confirm-process-modal').modal({
                'show': true, 'backdrop': 'static'
            });
            return false;
        },
        processJob: function(evt) {
            this.$process.submit();
        }
    });
})();
