.. image:: https://www.gnu.org/graphics/lgplv3-with-text-154x68.png
   :target: https://www.gnu.org/licenses/lgpl-3.0.en.html
   :alt: License: LGPL-v3

=================
Approval Notifier
=================

This module is for notify user to approve records
which are waiting. Some time user forgot to approve.
With this user can configure the model which will need to approve.
For example there some sale orders are pending for draft state for approving. User forgot to approve.
With this module user need to configure approval model with
model=='Sale Order', approval group == 'Sales/User:All Documents', state='draft'.
Then scheduler will send mail with link to approval user. Then user can approve easily.

Usage
=====

This module useful to approval notification.

Credits
=======

 * Shah Alam Sumon

Maintainer
==========

This module is maintained by Shah Alam Sumon.

Visit https://github.com/ShahAlamSumon

Contributors
------------
* Shah Alam Sumon: sacsesumon@gmail.com

To contribute to this module, please visit https://github.com/ShahAlamSumon
