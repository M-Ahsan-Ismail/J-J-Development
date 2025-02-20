/** @odoo-module */

import { ViewButton } from '@web/views/view_button/view_button';
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

const { useState } = owl;

class SafeConfirmation extends ConfirmationDialog{
	setup() {
		this.state = useState({hidden: true});
		this.env.dialogData.close = () => this._cancel();
		this.isConfirmedOrCancelled = false;
	}
	_toggleCheckBox() {
  		this.state.hidden = !this.state.hidden;
	}
	disableButtons() {}
    async _cancelButton() {
		if (this.isConfirmedOrCancelled) {
            return;
        }
        this.isConfirmedOrCancelled = true;
        this.disableButtons();
        if (this.props.cancel) {
            try {
                await this.props.cancel();
            } catch (e) {
                this.props.close();
                throw e;
            }
        }
        this.props.close();
	}
	async _confirmButton() {
        if (this.isConfirmedOrCancelled) {
            return;
        }
        this.isConfirmedOrCancelled = true;
        this.disableButtons();
        if (this.props.confirm) {
            try {
                await this.props.confirm();
            } catch (e) {
                this.props.close();
                throw e;
            }
        }
        this.props.close();
    }
}

SafeConfirmation.template = 'to_safe_confirm_button.ConfirmationDialog';
patch(ViewButton.prototype, "to_safe_confirm_button.view_button", {
	setup() {
		this._super(...arguments);
		this.dialog = useService("dialog");
	},
    onClick(ev) {
		const self_super = this._super;
		const self_args = arguments;
		if (this.props.attrs && this.props.attrs.safe_confirm) {
	            this.dialog.add(SafeConfirmation, {
				body: this.props.attrs.safe_confirm,
				confirm: () => {
					self_super(...self_args)
				},
				cancel: () => {},
			})
        } else {
            this._super(...arguments);
        }
	}
});
