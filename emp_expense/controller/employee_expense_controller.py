from odoo import http, fields, _
from odoo.addons.base.models.ir_actions_report import available
from odoo.exceptions import ValidationError
from odoo.http import request
from datetime import date, datetime


class EmployeeExpenseController(http.Controller):
    @http.route('/employee/expense', type='http', auth='user', website=True, methods=['GET'])
    def get_employee_expense(self, **kw):
        current_user = request.env.user
        print(current_user)

        user_expenses = request.env['expense.request'].search([('employee_id', '=', current_user.name)])

        user_expenses_list = []
        for expense in user_expenses:
            user_expenses_list.append({
                'expense_id': expense.name,
                'expense_date': expense.expense_date,
                'expense_amount': expense.amount,
                'currency_id': expense.currency_id.name,
                'state': expense.state,
            })
        print(user_expenses)
        print(user_expenses_list)

        return request.render('expense_employee.employee_expense_form',
                              {'user_expenses_list': user_expenses_list, 'current_user': current_user})
