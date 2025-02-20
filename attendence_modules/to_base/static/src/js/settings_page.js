/** @odoo-module **/

import { SettingsPage } from "@web/webclient/settings_form_view/settings/settings_page"
import { patch } from "@web/core/utils/patch";
import { useEffect } from "@odoo/owl";

patch(SettingsPage.prototype, "setup", {
    setup(){
        this._super(...arguments);
        this.state.modules = this.props.modules.map(m=>({...m, imgurl: null}))
        let self = this
        useEffect(
            ()=>{
                self.env.model.orm.call('res.config.settings', 'get_viin_brand_modules_icon', [], {
                    modules: self.props.modules.map(m=>m.key)
                }).then(res=>{
                    let modules = [...self.props.modules]
                    modules.forEach((child, index)=>{
                        child.imgurl = res[index]
                    })
                    self.state.modules = modules
                })
            },
            ()=>[]
        )
    }
})
