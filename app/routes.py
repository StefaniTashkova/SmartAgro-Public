from .controllers import *

app.add_url_rule('/', 'home', view_func=HomeController.render_home_page, methods=['GET'])
app.add_url_rule('/', view_func=HomeController.login_or_contact, methods=['POST'])
app.add_url_rule('/logout', 'logout', view_func=HomeController.logout, methods=['GET'])
app.add_url_rule('/owners', 'owners', view_func=OwnerController.render_owners_page, methods=['GET'])
app.add_url_rule('/owners', 'add_owner', view_func=OwnerController.add_owner, methods=['POST'])
app.add_url_rule('/owners/<int:owner_id>', 'owner', view_func=OwnerController.render_owner_page, methods=['GET'])
app.add_url_rule('/owners/<int:owner_id>', 'edit_owner', view_func=OwnerController.edit_owner, methods=['POST'])
app.add_url_rule('/owners/<int:owner_id>', 'delete_owner', view_func=OwnerController.delete_owner,
                 methods=['DELETE'])
app.add_url_rule('/plots', 'plots', view_func=PlotController.render_plots_page, methods=['GET'])
app.add_url_rule('/plots', 'add_plot', view_func=PlotController.add_plot, methods=['POST'])
app.add_url_rule('/plots/<int:ownership_id>', 'plot', view_func=PlotController.render_plot_page, methods=['GET'])
app.add_url_rule('/plots/<int:ownership_id>', 'edit_plot', view_func=PlotController.edit_plot, methods=['POST'])
app.add_url_rule('/plots/<int:ownership_id>', 'delete_plot', view_func=PlotController.delete_plot,
                 methods=['DELETE'])
app.add_url_rule('/contracts', 'contracts', view_func=ContractController.render_contracts_page, methods=['GET'])
app.add_url_rule('/contracts', 'add_contract', view_func=ContractController.add_contract, methods=['POST'])
app.add_url_rule('/contracts/download', 'download_contracts', view_func=ContractController.download_contracts,
                 methods=['GET'])
app.add_url_rule('/contracts/<contract_id>', 'contract', view_func=ContractController.render_contract_page,
                 methods=['GET'])
app.add_url_rule('/contracts/<contract_id>', 'edit_contract', view_func=ContractController.edit_contract,
                 methods=['POST'])
app.add_url_rule('/contracts/<contract_id>', 'delete_contract', view_func=ContractController.delete_contract,
                 methods=['DELETE'])
app.add_url_rule('/payments', 'payments', view_func=PaymentController.render_payments_page, methods=['GET'])
app.add_url_rule('/payments', 'generate_payments', view_func=PaymentController.generate_payments, methods=['POST'])
app.add_url_rule('/payments/make/<int:payment_id>', 'get_payment_data', view_func=PaymentController.get_payment_data, methods=['GET'])
app.add_url_rule('/payments/<int:payment_id>', 'make_payment', view_func=PaymentController.make_edit_payment, methods=['POST'])
app.add_url_rule('/payments/download', 'download_generated_payments_docs',
                 view_func=PaymentController.download_generated_payments_docs,
                 methods=['GET'])
app.add_url_rule('/payments/<int:payment_id>', 'edit_payment', view_func=PaymentController.make_edit_payment,
                 methods=['POST'])
app.add_url_rule('/payments/<int:payment_id>', 'payment', view_func=PaymentController.render_payment_page,
                 methods=['GET'])
app.add_url_rule('/payments/<int:payment_id>', 'delete_payment', view_func=PaymentController.delete_payment,
                 methods=['DELETE'])
app.add_url_rule('/user/settings', 'settings', view_func=UserController.render_settings_page, methods=['GET'])
app.add_url_rule('/user/settings', 'edit_user', view_func=UserController.edit_user, methods=['POST'])
app.add_url_rule('/user/settings/rent', 'edit_rent_settings', view_func=UserController.edit_rent_settings,
                 methods=['POST'])
app.add_url_rule('/user/settings/contract', 'edit_contract_settings', view_func=UserController.edit_contract_settings,
                 methods=['POST'])
app.add_url_rule('/user/settings/template', 'edit_template_settings', view_func=UserController.edit_template_settings,
                 methods=['POST'])
