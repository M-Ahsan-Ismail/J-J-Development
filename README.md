# J&J-Development
Dual Approvals On Purchase ,Budget,Inventory, Asset, Sale , Accounting and visibility of Bom Cost and develpment of gate pass module and backdate entries module.

## Procrutment
Developed Purchase Order (PO) Request system to manage procurement that enables users to create (PO) requests with details like products, quantities, vendors, featuring dynamic approval workflows. Users can assign multiple vendors per product, and the system intelligently groups lines to create a single RFQ for the same vendor across different or identical products. It automatically generates RFQs and includes a PDF report. it has modern Kanban views and  smart buttons to  view related purchase orders, RFQs, ,procurement  and  approval requests.


## Cost Sheet Builder
Deveoped cost sheet module for streamlining the quotation creation from crm , instead we selct the opputunity in our costModule and then calculating the cost.
it has workflow of submiting cost sheet then manager can approve or rejct if reject give remarks and on approval can convert the cost sheet into quotation by adding products qty uom unit_cost and validating single quotation against 1 cost sheet and canceling cost sheet cancels its quotation if in draft or sent state if in sale_order then cant cancel costsheet.workflow of archiving record on cancel and have validations on deleting if any quotation in sale_order then cant delete.
Smart buttons for proper linking btw cost sheet and quotation.
Can adjust quotation after creation from cost sheet if any desire of chnaging product or anything.
Moderan Kanban views displaying count of sale orders and quotations.
Report showing the detais of cost sheet


## Gate Pass Module
Developed the gate pass module on stock picking , having menus of inward pass  , outward pass in configuration uder label Gate Pass Info.

It tracks gate passes for stuff coming in or going out, shows driver and vehicle details. Each stock picking has a button to see related passes, each pass has a button for its picking, with product and quantity info. Reports show driver, vehicle, pass number, date, products, quantity, and signature lines.

## backdate_entries
developed the module for adding sale order , manufacturing order , purchase order , inventory in previous dates , as system dont allow creating them in previous dates.

stock_valutaiion_layer --- > 
Sets the create_date to the past.
If there’s any accounting  (account_move_ids) , updates those dates too and reposts them.

slae_order------------------>
updating the date_order , to past.
Fixes the journal entries by switching them to draft, setting their invoice_date , date to the past , then Reposting.
Updating stock moves(date), stock valuation layer(create_date), and stock move lines(date)  to past date.
Updating picking’s (scheduled_date, date_deadline,  date_done) to past.

Purchase Order----------------->
Updates the date_order , date_approve  to  past.
updating all related things—like journal entries(invoice_date), stock moves(date), stock valuation layers(create_date), stock move lines(date), and picking dates(scheduled_date,date_deadline,date_done)—to  past date.

Stock Picking---------------->
Updating dates in journal entries(invoice_date) , stock moves(date), stock move lines(date),  stock valuation layers(create_date).
Updates picking’s scheduled_date, date_deadline, and date_done to  past date.


Manufacturing Order (MRP)------------>
Updating date for stock moves (raw materials and finished goods), stock move lines, and create_date for stock valuation layers.
Sets the manufacturing order’s date_start, date_finished,  create_date dates to  past date.



## Employee Expense Module
Developed an separate module for handling employee expenses , An default expenese manager an be seted in settings of employee.
employee can selct the amount and submits the request other fileds got auto filled , expense manager fetched by default_get ,get_param.
A email goes to expense manager refering employeee that has submitted an expense.
manager has its button approval , having approve , reject. if reject give remarks and will be looged in chatter and also an email will be sent to employee regarding his status that has been rejected.
if Approved an email with link to expense will be sent to finance users group having employee, expenese id and amount details.Finance team then can register payment.after creating payment the created payment and expense will be linked together.
can view the related payment and confirm it.


## Auto Invoice On Base Of Payment Terms
generates an invoice of an sale order when due date arises depending on its payment terms.
It first fetches all confirmed sale orders (state = 'sale').       
it 1st checks is sale order has payment terms or not , if not skip.
if yes then:
1st it checks all invoices linked to this sale order and sum up there amount and check weather the amount equals to current sale order if equal skip , 
if amount to invoice less then total amount then it tries to invoice remaining amount base of no.of days passed after invoice date of sale order form and if these days count matches any line of terms id then invoice else skips.









## Accounting_late_payment_surcharge

## Accounting: Force Payments to Stay in Draft Created From Vendor Bills or Invoices
This module ensures that payments created from bills or invoices remain in the draft state. It overrides the create, _prepare_payment_vals, and _create_payments methods to enforce this behavior, preventing automatic validation of payments.

## Manufacturing_Access
Modified the existing BoM Form View (mrp.bom.form) by inheriting it.
Added a group restriction (bss_mrp_access.group_mrp_cost) to control access to the BoM report button (previously available to all).
Now, only users in the group_mrp_cost can see the report button.

#### Dynamically Controlling BoM Cost Visibility by JavaScript:

Patched BomOverviewComponent to modify the behavior of getBomData().

Used Odoo’s user.hasGroup() method to dynamically check if the user belongs to bss_mrp_access.group_mrp_cost.

If the user is in the group, the "Cost" option is shown; otherwise, it's hidden.

Patched BomOverviewDisplayFilter and removed "Costs" from the available filters.

This ensures that users cannot enable "Costs" unless they have the required access.




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




## Payment Approvals
Custom Payment States: Adds new states like "Verified," "Approved," and "In Process" for better tracking.
✅ Approval Workflow: Users in specific groups (Level 1, Level 2) must approve payments before proceeding.
✅ Automated Activities: System creates approval tasks for designated users at each level.
✅ Email Notifications: Sends approval requests via email with a clickable payment link.
✅ User Permissions: Only authorized users can approve payments.








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









