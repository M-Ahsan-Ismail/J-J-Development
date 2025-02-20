Installation
============

1. Navigate to **Apps**;
2. Find with keyword *to_attendance_device*;
3. Press **Install**.

Usages
======

**Instruction video:** `Biometric Attendance Machines Integration <https://youtu.be/wfnJ_5d8_L8>`_

Concepts
--------

#. **Machine Position** is a model to store locations where your attendance machines are installed. Each location consists of the following information:

   * Name: the name of the location.
   * Time zone: the time zone of the location. This is to support attendance logs at multiple locations in different time zones.

#. **Attendance State** is a model to store states of attendance activity that can be defined by users. States could be Check-in, Check-out, Overtime Check-in, Overtime Start, etc. Please navigate to **Attendance > Configuration > Attendance Status** to see the list of default states that were created during the installation of this application.

#. **Attendance Activity** is a model that classifies attendance in activities such as Normal Working, Overtime, etc. Navigate to **Attendance > Configuration > Attendance Activity** to see the list of default activities that were created during the installation of this application. Each Attendance Activity is defined with the following:

   * Name: the unique name of the activity.
   * Attendance Status: list of the attendance states that are applied to this activity.

#. **Machine User** is a model that stores all the machines' users in your Odoo instance and map such users with Employees in the system. Each Machine User consists of (but is not limited to) the following information:

   * Name: the name of the user stored in the machine.
   * Attendance Machine: the machine to which this user belongs.
   * UID: The ID (technical field) of the user in the machine storage, which is usually invisible at the machine's interface/screen.
   * ID Number: the ID Number of the user/employee in the machine storage. It is also known as "User ID" in some machines.
   * Employee: the employee that is mapped with this user. If you have multiple machines, each employee may map with multiple corresponding machine users.

#. **User Attendance** is a model that stores all the attendance records downloaded from all the machines. In other words,it is a central database of attendance logs for all your machines. This log will be used as the base to create HR Attendance. During that creation, the software will also check for the validity of the attendance to ensure that the HR Attendance data is clean and valid.

#. **HR Attendance** is a model offered by Odoo's standard module `hr_attendance` and is extended to have the following fields:

   * Check-in: the time of check-in.
   * Check-out: the time of check-out.
   * Employee: the related employee.
   * Checkin Machine: the attendance machine that logged the check-in.
   * Checkout Machine: the attendance machine that logged the check-out.

   HR Attendance records are created automatically and periodically by the Scheduled Action named **Synchronize attendances schedule**.

#. **Employee** is a model in Odoo that is extended for the additional following information:

   * Unmapped Machines: to show the list of attendance machines that have not to gotten this employee mapped.
   * Created from Machine: to indicate if the employee profile was created from a machine (e.g. Download users -> auto create employee-> auto map them). This will helps you filter your employees to see ones that were or were not created from machines.

#. **Attendance Machine** is a model that stores all the information of an attendance machine. It also provides a lot of tools such as:

   * Upload Users: to upload all your employee to an attendance machine (e.g a new and fresh machine).
   * Download Users: to download all the machine's users' data into odoo and map those users with employees (if an auto mapping is set).
   * Map Employee: to map machine users with employees in your Odoo instance.
   * Check connection: to check if your Odoo instance could connect to the machine.
   * Get Machine Info: to get the most important information about the machine (e.g. OEM Vendor, Machine Name, Serial Number, Firmware Version, etc).
   * Download Attendance: to download manually all the attendance data from the machine into your Odoo database, although this could be done automatically by the scheduled action named "Download attendances scheduler".
   * Restart: to restart the machine.
   * Clear Data: this is to empty your data. It is a very DANGEROUS function and is visible to and accessible by the HR Attendance Manager only.
   * And many more...

Setup a new attendance machine
------------------------------
#. Navigate to **Attendances > Attendance Machines > Machines Manager**.
#. Click **Create** button to open a machine form view.
#. Input the name of the machine (optional).
#. Enter the IP of the machine. It must be accessible from your Odoo server. If your Odoo instance is on the Internet while the machine is in your office, behind a router, please ensure that port forwarding is enabled and the machine's network configuration is properly set to allow accessing your machine from outside via the Internet. You may need to refer to your router manufacturers for documentation on how to do NAT/port forwarding.
#. **Port**: the port of the machine. It is usually 4370.
#. **Protocol**: which is either UDP or TCP. Most modern machines nowadays support both. TCP is more reliable but may not be supported by a behind-a-decade machine.
#. **Location**: the location where the machine is physically installed. The time zone of the location must be correct.
#. You may want to see other options (e.g. Map Employee Before Download, Time zone, Generate Employees During Mapping, etc).
#. Hit the **Save** button to create a new machine in your Odoo.
#. Hit **Check Connection** to test if the connection works. If it did not work, please troubleshoot for the following cases:

   * Check network settings inside the physical machine: IP, Gateway, Port, Net Mask.
   * Check your firewall/router to see if it blocks connection from your Odoo instance.
   * Try on switching between UDP and TCP.

Refer to the article `Biometric attendance device intergration. <https://viindoo.com/documentation/15.0/applications/human-resources/attendances/operations/biometric-attendance-device-intergration.html#biometric-attendance-device-intergration>`_

.. image:: 6-thong-tin-chung.en.jpg
   :align: center
   :height: 500
   :width: 1100
   :alt: Intergrate with biometric machine

Map Machines Users and Employees
--------------------------------

* If this is a fresh machine without any data stored inside:

  * Click **Upload users**.

* If this is not a fresh machine:

  * You may want to clear data before doing step 10.1 mentioned above.
  * Or, you may want to Download Users and map them to an existing employee or create a new employee accordingly.

* Validate the result:

  * All Machine Users should link to a corresponding employee.
  * No unmapped employees are shown on the machine form view.

Refer to the article `Link Attendance device users with employees in Viindoo system. <https://viindoo.com/documentation/15.0/applications/human-resources/attendances/operations/link_attendance_device_users_with_employees_in_viindoo_system.html#link-attendance-device-users-with-employees-in-viindoo-system>`_

.. image:: 2-linkage-employee-user.en.jpg
   :align: center
   :height: 500
   :width: 1100
   :alt: Intergrate with biometric machine

* Test Attendance Data download and synchronization:

  * Do some check-in and check-out at the physical machine:

    * Wait for seconds between check-in and check-out.
    * Try some wrong actions: check-in a few times before checking-out.

  * Come back to the machine form view in Odoo:

    * Hit Download Attendance Data and wait for its completion. For just a few attendance records, it may take only a couple of seconds even if your device is located in a country other than the Odoo instance's.

  * Validate the result:

    * Navigate to **Attendances > Attendance Machines > Attendance Data** to validate if the attendance log is recorded there.
    * If found, you are done now. You can continue with the following steps to bring the new machine into production:

      * Clear the sample attendance data you have created:

        * Navigate to Attendances > Attendance Machines > Attendance Data, find and delete those sample records.
        * Navigate to Attendances > Attendance Machines > Synchronize and hit Clear Attendance Data button.

      * Hit the Confirmed state in the header of the machine form view. If you don't do it, the schedulers will ignore the machine during their runs.

    * If not found, there should be some trouble that needs further investigation:

      * Check the connection.
      * Try to get the machine information.
      * Check the work codes of the machine if they match the ones specified in the "Attendance Status Codes" table in the machine form view.
      * Contact the author of the "Attendance Machine" application if you could not solve the problem yourself.

Set up for a new Employee
-------------------------
#. Create an employee as usual.
#. Hit the Action button in the header area of the employee form view to find the menu item "Upload to Attendance Machine" in the dropped-down list.
#. Select the machine(s) that will be used for this employee then hit the Upload Employees button.
#. You can also do mass upload by selecting employees from the employee list view. Or go to the machines.

How the automation works
------------------------

There are two scheduled actions:

#. **Download attendances scheduler**: by default, it runs every 30 minutes to:

   * Download the attendance log/data from all your machines that are set in Confirmed status. Machines that are not in this status will be ignored.
   * Create User Attendance records in your Odoo database.
   * Depending on the configuration you made on the machines, it may also do the following automatically:

     * Create new employees and map with the corresponding machine users if new users are found in the machines.
     * Clear the attendance data from the machine if it's time to do it.

#. **Synchronize attendances scheduler**: by default, it runs every 30 minutes to:

   * Find the valid attendance in the user attendance log.
   * Create HR Attendance records from such the log.
