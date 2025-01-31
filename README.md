# J&J-Development
Dual Approvals On Purchase , Sale , Accounting and develpment of gate pass module.


## Gate Pass Module


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


