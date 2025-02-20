/** @odoo-module **/

import {BomOverviewComponent} from "@mrp/components/bom_overview/mrp_bom_overview";
import {BomOverviewDisplayFilter} from "@mrp/components/bom_overview_display_filter/mrp_bom_overview_display_filter";
import {user} from "@web/core/user";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(BomOverviewComponent.prototype, {
    // Inherit getBomData and modify it to set costs dynamically
    async getBomData() {
        debugger;
        const bomData = await super.getBomData();  // Call the original getBomData
        // Update the costs option based on user group dynamically
        this.state.showOptions.costs = await user.hasGroup('bss_mrp_access.group_mrp_cost');
        return bomData;  // Return the modified bomData
    }
})

patch(BomOverviewDisplayFilter.prototype, {
    setup() {
        this.displayOptions = {
            availabilities: _t('Availabilities'),
            leadTimes: _t('Lead Times'),
            // costs: _t('Costs'),
            operations: _t('Operations'),
        };
    }
})
