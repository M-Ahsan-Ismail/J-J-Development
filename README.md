# J&J-Development
Dual Approvals On Purchase , Sale , Accounting and develpment of gate pass module.


## Gate Pass Module







## Asset Approvals18
This module extends the Asset Management workflow in Odoo by introducing a structured approval process with new states:
Submit for Approval → Verified → Approved 
#### State Field Inheritance: 
The state field of the account.asset model is extended to include additional approval stages.
#### Flow
Assets start in Draft.

The Submit for Approval button appears in Draft state.

Upon submission, the system checks if users are assigned to the First-Level Approval group. If no users are found, an error is raised. Otherwise, a To-Do Activity is created for the approvers.

First-Level Approval (Verified): Once verified, the system assigns the request to Second-Level Approvers.

Second-Level Approval (Approved): The final approval step changes the asset status to Approved and marks previous approval activities as completed.

##### Security Group Validation: 
Before assigning an approval task, the system ensures that at least one user is assigned to the respective security group. If not, it raises an error.

##### Automated Activities: 
At each step, a mail activity is created for the assigned users, prompting them to take action on the asset approval.






## Budget Approvals18
This module extends the Budget Management process by introducing a structured approval workflow with multiple stages:
Submit for Approval → Verified → Approved → Open
#### State Field Inheritance: 
The state field of the budget.analytic model is extended to include additional approval stages.
#### Approval Flow:
Budgets start in Draft.

The Submit for Approval button appears in Draft state.

Upon submission, the system checks if users are assigned to the First-Level Approval group. If no users are found, an error is raised. Otherwise, a To-Do Activity is created for the approvers.

First-Level Approval (Verified): Once verified, the system assigns the request to Second-Level Approvers.

Second-Level Approval (Approved): The final approval step changes the budget status to Approved and marks previous approval activities as completed.

##### Security Group Validation: 
Before assigning an approval task, the system ensures that at least one user is assigned to the respective security group. If not, it raises an error.
##### Automated Activities: 
At each step, a mail activity is created for the assigned users, prompting them to take action on the budget approval.




## Inventory Access18 
Customizes inventory views by restricting access to cost-related fields (like unit_cost, value, remaining_value, avg_cost, and total_value) based on user permissions. Only users with the Inventory Access Rights group can see these fields in stock valuation, product, and stock quant views. This ensures sensitive financial data is only visible to authorized users.





## Inventory Approval18
It adds an approval workflow to Stock Transfers (Receipts & Deliveries) in Odoo. It introduces new approval states (submit_for_approval, manager_approved, ceo_approved) before a transfer is completed. Users in designated approval groups receive automated activities to review and approve transfers at different levels. The workflow requires manager and CEO approvals before final processing.





## Manufactiring Approvals18
This module adds an approval workflow to Manufacturing Orders (MO) and Work Orders (WO). Multi-level approvals (Manager & CEO) before a manufacturing process can begin, ensuring controlled validation.
Approval actions trigger automated activities for assigned users.

##### Activity Notifications
Users in manufacturing_approval_level1 & manufacturing_approval_level2 groups receive automated tasks when approvals are needed.
Activities are updated when approvals are completed.





## MRP Access
Modified the existing BoM Form View (mrp.bom.form) by inheriting it.
Added a group restriction (bss_mrp_access.group_mrp_cost) to control access to the BoM report button (previously available to all).
Now, only users in the group_mrp_cost can see the report button.

#### Dynamically Controlling BoM Cost Visibility by JavaScript:

Patched BomOverviewComponent to modify the behavior of getBomData().

Used Odoo’s user.hasGroup() method to dynamically check if the user belongs to bss_mrp_access.group_mrp_cost.

If the user is in the group, the "Cost" option is shown; otherwise, it's hidden.

Patched BomOverviewDisplayFilter and removed "Costs" from the available filters.

This ensures that users cannot enable "Costs" unless they have the required access.






## Payment Approvals
Custom Payment States: Adds new states like "Verified," "Approved," and "In Process" for better tracking.
✅ Approval Workflow: Users in specific groups (Level 1, Level 2) must approve payments before proceeding.
✅ Automated Activities: System creates approval tasks for designated users at each level.
✅ Email Notifications: Sends approval requests via email with a clickable payment link.
✅ User Permissions: Only authorized users can approve payments.




## Accounting: Force Payments to Stay in Draft Created From Vendor Bills or Invoices
This module ensures that payments created from bills or invoices remain in the draft state. It overrides the create, _prepare_payment_vals, and _create_payments methods to enforce this behavior, preventing automatic validation of payments.



## Sale Dual Approvals
I customized the Sales Order approval process by inheriting the state field and adding two new approval stages: Manager Approval and CEO Approval.

When a quotation is created, the Manager Approval button is shown. Clicking it moves the order to the Manager Approval stage.

By approved from Manager, the CEO Approval button appears, allowing the CEO to approve it.

After CEO approval, the Confirm Order button is enabled, allowing the order to be confirmed and moved to the Sales Order state.

Only users in the Manager Approval and CEO Approval groups can see their respective approval buttons.




## Purchase Dual Approvals 
I developed a custom approval workflow in the Purchase module by inheriting the state field in purchase.order and introducing approval stages for the Manager and CEO. I implemented two approval buttons:

Manager Approval: Visible only when the purchase order is in the "Draft" state, accessible to users with the "Manager Approval" group.

CEO Approval: Becomes visible after the Manager's approval and is accessible only to users in the "CEO Approval" group.

Once both approvals are granted, the order can be confirmed, progressing through the standard purchase order workflow. I also created custom access rights for Manager and CEO roles, ensuring that only authorized users can proceed with the respective approvals.









