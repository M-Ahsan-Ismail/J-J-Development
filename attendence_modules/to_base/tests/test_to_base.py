import datetime
from dateutil import tz

from odoo.tools import relativedelta
from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError


class TestToBase(TransactionCase):

    def setUp(self):
        super(TestToBase, self).setUp()

    def test_000_float_hours_to_time(self):
        test_value = [10.5, 10, 0]
        check_vals = [datetime.time(10, 30), datetime.time(10, 0), datetime.time(0, 0)]
        for i in range(len(test_value)):
            result = self.env['to.base'].float_hours_to_time(test_value[i])
            self.assertEqual(result, check_vals[i])

        result = self.env['to.base'].float_hours_to_time(20.5, 'Asia/Ho_Chi_Minh')
        self.assertEqual(result, datetime.time(20, 30))
        self.assertEqual(str(result.tzinfo), 'Asia/Ho_Chi_Minh')

    # TC01
    def test_010_barcode_exists(self):
        test_values = [{'name': f'{x}00' * 3} for x in range(10)]
        self.env['res.partner'].create(test_values)

        self.assertTrue(
            self.env['to.base'].barcode_exists(
                barcode='000000000',
                model_name='res.partner',
                barcode_field='name',
                inactive_rec=False,
            ),
            "\nTest case TC01",
        )

    # TC02
    def test_020_get_ean13(self):
        # Test with valid values
        test_vals = [
            '123123123123',
            '978020137962',
            '978053237962',
            '978053225412',
            '1234',
            '0',
        ]

        check_vals = [
            '1231231231232',
            '9780201379624',
            '9780532379621',
            '9780532254126',
            '0000000012348',
            '0000000000000',
        ]

        for i in range(len(test_vals)):
            self.assertEqual(
                check_vals[i],
                self.env['to.base'].get_ean13(test_vals[i]),
                'Test case TC02',
            )

        # Test with invalid values
        with self.assertRaises(ValueError):
            self.env['to.base'].get_ean13('abcdef')

    # TC03
    def test_030_convert_local_to_utc(self):
        test_dt = datetime.datetime(2020, 2, 2, 18, 32, 11)
        converted_dt = self.env['to.base'].convert_local_to_utc(dt=test_dt, force_local_tz_name='Asia/Ho_Chi_Minh')
        check_dt = datetime.datetime(2020, 2, 2, 11, 32, 11, tzinfo=tz.UTC)
        self.assertEqual(check_dt, converted_dt, 'Test case TC03')

    # TC04
    def test_040_convert_utc_to_local(self):
        test_dt = datetime.datetime(2020, 2, 2, 11, 42, 23)
        converted_dt = self.env['to.base'].convert_utc_to_local(
            utc_dt=test_dt, force_local_tz_name='Asia/Ho_Chi_Minh'
        )

        check_dt = datetime.datetime(2020, 2, 2, 18, 42, 23)
        check_dt = check_dt.replace(tzinfo=tz.gettz('Asia/Ho_Chi_Minh'))

        self.assertEqual(check_dt, converted_dt, 'Test case TC04')

    def test_045_convert_relativedelta_to_timedelta(self):
        convert_relativedelta_to_timedelta = self.env['to.base'].convert_relativedelta_to_timedelta

        timedelta_data = datetime.timedelta(days=1)
        relativedelta_data = relativedelta(days=1)
        timedelta_converted = convert_relativedelta_to_timedelta(relativedelta_data)
        self.assertEqual(timedelta_data, timedelta_converted)

        timedelta_data = datetime.timedelta(days=1, seconds=5400)   # 1h30m = 5400s
        relativedelta_data = relativedelta(days=1, hours=1, minutes=30)
        timedelta_converted = convert_relativedelta_to_timedelta(relativedelta_data)
        self.assertEqual(timedelta_data, timedelta_converted)

        timedelta_data = datetime.timedelta(days=2, seconds=5450, microseconds=5000)   # 1h30m50s = 5450s
        relativedelta_data = relativedelta(days=2, hours=1, minutes=30, seconds=50, microseconds=5000)
        timedelta_converted = convert_relativedelta_to_timedelta(relativedelta_data)
        self.assertEqual(timedelta_data, timedelta_converted)

    def test_046_get_total_seconds_from_relativedelta(self):
        relativedelta_data = relativedelta(days=1)
        seconds = self.env['to.base'].get_total_seconds_from_relativedelta(relativedelta_data)
        # 1 days = 24*60*60 = 86400s
        self.assertEqual(seconds, 86400)

        relativedelta_data = relativedelta(days=1, hours=1, minutes=30)
        seconds = self.env['to.base'].get_total_seconds_from_relativedelta(relativedelta_data)
        # 1 day = 86400s, 1 hour = 3600s, 30 minutes = 1800s
        self.assertEqual(seconds, 91800)

        relativedelta_data = relativedelta(days=2, hours=1, minutes=30, seconds=50, microseconds=5000)
        seconds = self.env['to.base'].get_total_seconds_from_relativedelta(relativedelta_data)
        # 2 day = 172800s, 1 hour = 3600s, 30 minutes = 1800s, 5000 = 0.005s
        self.assertEqual(seconds, 178250.005)

    # TC05
    def test_050_time_to_float_hour(self):
        test_vals = [
            datetime.datetime(2020, 1, 1, 12, 30, 0),
            datetime.datetime(2020, 1, 1, 12, 0, 0)
        ]
        check_vals = [12.5, 12]
        for i in range(len(test_vals)):
            self.assertEqual(
                check_vals[i],
                self.env['to.base'].time_to_float_hour(dt=test_vals[i]),
                "\nTest case TC05",
            )

    # TC06
    def test_060_find_first_date_of_period(self):
        # Test weekly

        test_weekly = [
            datetime.datetime(2021, 3, 4, 18, 0, 0),
            datetime.datetime(2021, 3, 1),
            datetime.datetime(2021, 3, 7, 23, 59, 59),
            datetime.datetime(2021, 8, 16),
            datetime.datetime(2021, 8, 17),
            datetime.datetime(2021, 8, 18),
            datetime.datetime(2021, 8, 19),
            datetime.datetime(2021, 8, 20),
            datetime.datetime(2021, 8, 21),
            datetime.datetime(2021, 8, 22),
            datetime.datetime(2021, 8, 23)
        ]
        check_weekly = [
            datetime.datetime(2021, 3, 1),
            datetime.datetime(2021, 3, 1),
            datetime.datetime(2021, 3, 1),
            datetime.datetime(2021, 8, 16),
            datetime.datetime(2021, 8, 16),
            datetime.datetime(2021, 8, 16),
            datetime.datetime(2021, 8, 16),
            datetime.datetime(2021, 8, 16),
            datetime.datetime(2021, 8, 16),
            datetime.datetime(2021, 8, 16),
            datetime.datetime(2021, 8, 23)
        ]
        for i in range(len(test_weekly)):
            self.assertEqual(
                check_weekly[i],
                self.env['to.base'].find_first_date_of_period(
                    'weekly', test_weekly[i]
                ),
                "\nTest case TC06.01 - Test weekly",
            )

        # Test monthly
        test_monthly = [
            datetime.datetime(2021, 3, 12, 19, 53, 11),
            datetime.datetime(2021, 3, 1),
            datetime.datetime(2021, 3, 1, 23, 59, 0),
            datetime.datetime(2021, 2, 1)
        ]
        check_monthly = [
            datetime.datetime(2021, 3, 1),
            datetime.datetime(2021, 3, 1),
            datetime.datetime(2021, 3, 1),
            datetime.datetime(2021, 2, 1)
        ]
        for i in range(len(test_monthly)):
            self.assertEqual(
                check_monthly[i],
                self.env['to.base'].find_first_date_of_period(
                    'monthly', test_monthly[i]
                ),
                "\nTest case TC06.02 - Test monthly",
            )

        # Test quarterly
        test_quarterly = [
            datetime.datetime(2021, 3, 4, 18, 3, 24),
            datetime.datetime(2021, 5, 1, 0, 1, 1),
            datetime.datetime(2021, 9, 25, 19, 50, 11),
            datetime.datetime(2021, 11, 12, 14, 20, 11),
            datetime.datetime(2021, 1, 1),
            datetime.datetime(2021, 3, 31, 23, 59, 59),
            datetime.datetime(2021, 4, 1),
            datetime.datetime(2021, 6, 30, 23, 59, 59),
            datetime.datetime(2021, 7, 1),
            datetime.datetime(2021, 9, 30, 23, 59, 59),
            datetime.datetime(2021, 10, 1),
            datetime.datetime(2021, 12, 31)
        ]
        check_quarterly = [
            datetime.datetime(2021, 1, 1),
            datetime.datetime(2021, 4, 1),
            datetime.datetime(2021, 7, 1),
            datetime.datetime(2021, 10, 1),
            datetime.datetime(2021, 1, 1),
            datetime.datetime(2021, 1, 1),
            datetime.datetime(2021, 4, 1),
            datetime.datetime(2021, 4, 1),
            datetime.datetime(2021, 7, 1),
            datetime.datetime(2021, 7, 1),
            datetime.datetime(2021, 10, 1),
            datetime.datetime(2021, 10, 1)
        ]
        for i in range(len(test_quarterly)):
            self.assertEqual(
                check_quarterly[i],
                self.env['to.base'].find_first_date_of_period(
                    'quarterly', test_quarterly[i]
                ),
                "\nTest case TC06.03 - Test quarterly",
            )

        # Test biannually
        test_biannually = [
            datetime.datetime(2021, 3, 4, 18, 0, 0),
            datetime.datetime(2021, 10, 25, 8, 1, 0),
            datetime.datetime(2021, 1, 1),
            datetime.datetime(2021, 6, 30, 23, 59, 59),
            datetime.datetime(2021, 7, 1),
            datetime.datetime(2021, 12, 31),
        ]
        check_biannually = [
            datetime.datetime(2021, 1, 1),
            datetime.datetime(2021, 7, 1),
            datetime.datetime(2021, 1, 1),
            datetime.datetime(2021, 1, 1),
            datetime.datetime(2021, 7, 1),
            datetime.datetime(2021, 7, 1),
        ]
        for i in range(len(test_monthly)):
            self.assertEqual(
                check_biannually[i],
                self.env['to.base'].find_first_date_of_period(
                    'biannually', test_biannually[i]
                ),
                "\nTest case TC06.04 - Test biannually",
            )

    def test_065_find_first_date_of_period(self):
        # Test weekly

        test_weekly = [
            datetime.date(2021, 3, 4),
            datetime.date(2021, 3, 1),
            datetime.date(2021, 3, 7),
            datetime.date(2021, 8, 16),
            datetime.date(2021, 8, 17),
            datetime.date(2021, 8, 18),
            datetime.date(2021, 8, 19),
            datetime.date(2021, 8, 20),
            datetime.date(2021, 8, 21),
            datetime.date(2021, 8, 22),
            datetime.date(2021, 8, 23)
        ]
        check_weekly = [
            datetime.date(2021, 3, 1),
            datetime.date(2021, 3, 1),
            datetime.date(2021, 3, 1),
            datetime.date(2021, 8, 16),
            datetime.date(2021, 8, 16),
            datetime.date(2021, 8, 16),
            datetime.date(2021, 8, 16),
            datetime.date(2021, 8, 16),
            datetime.date(2021, 8, 16),
            datetime.date(2021, 8, 16),
            datetime.date(2021, 8, 23)
        ]
        for i in range(len(test_weekly)):
            self.assertEqual(
                check_weekly[i],
                self.env['to.base'].find_first_date_of_period(
                    'weekly', test_weekly[i]
                ),
                "\nTest case TC06.01 - Test weekly",
            )

        # Test monthly
        test_monthly = [
            datetime.date(2021, 3, 12),
            datetime.date(2021, 3, 1),
            datetime.date(2021, 3, 1),
            datetime.date(2021, 2, 1)
        ]
        check_monthly = [
            datetime.date(2021, 3, 1),
            datetime.date(2021, 3, 1),
            datetime.date(2021, 3, 1),
            datetime.date(2021, 2, 1)
        ]
        for i in range(len(test_monthly)):
            self.assertEqual(
                check_monthly[i],
                self.env['to.base'].find_first_date_of_period(
                    'monthly', test_monthly[i]
                ),
                "\nTest case TC06.02 - Test monthly",
            )

        # Test quarterly
        test_quarterly = [
            datetime.date(2021, 3, 4),
            datetime.date(2021, 5, 1),
            datetime.date(2021, 9, 25),
            datetime.date(2021, 11, 12),
            datetime.date(2021, 1, 1),
            datetime.date(2021, 3, 31),
            datetime.date(2021, 4, 1),
            datetime.date(2021, 6, 30),
            datetime.date(2021, 7, 1),
            datetime.date(2021, 9, 30),
            datetime.date(2021, 10, 1),
            datetime.date(2021, 12, 31)
        ]
        check_quarterly = [
            datetime.date(2021, 1, 1),
            datetime.date(2021, 4, 1),
            datetime.date(2021, 7, 1),
            datetime.date(2021, 10, 1),
            datetime.date(2021, 1, 1),
            datetime.date(2021, 1, 1),
            datetime.date(2021, 4, 1),
            datetime.date(2021, 4, 1),
            datetime.date(2021, 7, 1),
            datetime.date(2021, 7, 1),
            datetime.date(2021, 10, 1),
            datetime.date(2021, 10, 1)
        ]
        for i in range(len(test_quarterly)):
            self.assertEqual(
                check_quarterly[i],
                self.env['to.base'].find_first_date_of_period(
                    'quarterly', test_quarterly[i]
                ),
                "\nTest case TC06.03 - Test quarterly",
            )

        # Test biannually
        test_biannually = [
            datetime.date(2021, 3, 4),
            datetime.date(2021, 10, 25),
            datetime.date(2021, 1, 1),
            datetime.date(2021, 6, 30),
            datetime.date(2021, 7, 1),
            datetime.date(2021, 12, 31),
        ]
        check_biannually = [
            datetime.date(2021, 1, 1),
            datetime.date(2021, 7, 1),
            datetime.date(2021, 1, 1),
            datetime.date(2021, 1, 1),
            datetime.date(2021, 7, 1),
            datetime.date(2021, 7, 1),
        ]
        for i in range(len(test_monthly)):
            self.assertEqual(
                check_biannually[i],
                self.env['to.base'].find_first_date_of_period(
                    'biannually', test_biannually[i]
                ),
                "\nTest case TC06.04 - Test biannually",
            )

    def test_070_find_last_date_of_period_from_period_start_date(self):
        with self.assertRaises(ValidationError):
            self.env['to.base']._find_last_date_of_period_from_period_start_date('week', datetime.datetime(2021, 2, 1))

        with self.assertRaises(ValidationError):
            self.env['to.base']._find_last_date_of_period_from_period_start_date('weekly', 'x')

        # test weekly
        self.assertEqual(
            self.env['to.base']._find_last_date_of_period_from_period_start_date('weekly', datetime.datetime(2021, 8, 19)),
            datetime.datetime(2021, 8, 25, 23, 59, 59, 999999)
            )
        self.assertEqual(
            self.env['to.base']._find_last_date_of_period_from_period_start_date('weekly', datetime.date(2021, 8, 19)),
            datetime.date(2021, 8, 25)
            )
        # test monthly
        self.assertEqual(
            self.env['to.base']._find_last_date_of_period_from_period_start_date('monthly', datetime.datetime(2021, 8, 19)),
            datetime.datetime(2021, 9, 18, 23, 59, 59, 999999)
            )
        self.assertEqual(
            self.env['to.base']._find_last_date_of_period_from_period_start_date('monthly', datetime.date(2021, 8, 19)),
            datetime.date(2021, 9, 18)
            )
        # test quarterly
        self.assertEqual(
            self.env['to.base']._find_last_date_of_period_from_period_start_date('quarterly', datetime.datetime(2021, 8, 19)),
            datetime.datetime(2021, 11, 18, 23, 59, 59, 999999)
            )
        self.assertEqual(
            self.env['to.base']._find_last_date_of_period_from_period_start_date('quarterly', datetime.date(2021, 8, 19)),
            datetime.date(2021, 11, 18)
            )
        # test biannually
        self.assertEqual(
            self.env['to.base']._find_last_date_of_period_from_period_start_date('biannually', datetime.datetime(2021, 8, 19)),
            datetime.datetime(2022, 2, 18, 23, 59, 59, 999999)
            )
        self.assertEqual(
            self.env['to.base']._find_last_date_of_period_from_period_start_date('biannually', datetime.date(2021, 8, 19)),
            datetime.date(2022, 2, 18)
            )
        # test annually
        self.assertEqual(
            self.env['to.base']._find_last_date_of_period_from_period_start_date('annually', datetime.datetime(2021, 8, 19)),
            datetime.datetime(2022, 8, 18, 23, 59, 59, 999999)
            )
        self.assertEqual(
            self.env['to.base']._find_last_date_of_period_from_period_start_date('annually', datetime.date(2021, 8, 19)),
            datetime.date(2022, 8, 18)
            )

    def test_080_find_last_date_of_period(self):
        # Test weekly
        test_weekly = [
            datetime.datetime(2021, 3, 4, 18, 11, 23),
            datetime.datetime(2021, 3, 1),
            datetime.datetime(2021, 3, 7, 23, 59, 59),
        ]
        check_weekly = [
            datetime.datetime(2021, 3, 7, 23, 59, 59, 999999),
            datetime.datetime(2021, 3, 7, 23, 59, 59, 999999),
            datetime.datetime(2021, 3, 7, 23, 59, 59, 999999),
        ]
        for i in range(len(test_weekly)):
            self.assertEqual(
                check_weekly[i],
                self.env['to.base'].find_last_date_of_period(
                    'weekly', test_weekly[i]
                ),
                "\nTest case TC07.01 - Test weekly",
            )

        # Test monthly
        test_monthly = [
            datetime.datetime(2021, 3, 12, 19, 53, 11),
            datetime.datetime(2021, 3, 1),
            datetime.datetime(2021, 3, 31, 23, 59, 59),
            datetime.datetime(2021, 2, 1),
            datetime.datetime(2024, 2, 1),
            datetime.datetime(2024, 4, 1)
        ]
        check_monthly = [
            datetime.datetime(2021, 3, 31, 23, 59, 59, 999999),
            datetime.datetime(2021, 3, 31, 23, 59, 59, 999999),
            datetime.datetime(2021, 3, 31, 23, 59, 59, 999999),
            datetime.datetime(2021, 2, 28, 23, 59, 59, 999999),
            datetime.datetime(2024, 2, 29, 23, 59, 59, 999999),
            datetime.datetime(2024, 4, 30, 23, 59, 59, 999999)
        ]
        for i in range(len(test_monthly)):
            self.assertEqual(
                check_monthly[i],
                self.env['to.base'].find_last_date_of_period(
                    'monthly', test_monthly[i]
                ),
                "\nTest case TC07.02 - Test monthly",
            )

        # Test quarterly
        test_quarterly = [
            datetime.datetime(2021, 3, 4, 18, 3, 24),
            datetime.datetime(2021, 5, 1, 0, 1, 1),
            datetime.datetime(2021, 9, 25, 19, 50, 11),
            datetime.datetime(2021, 11, 12, 14, 20, 11),
            datetime.datetime(2021, 1, 1),
            datetime.datetime(2021, 3, 31, 23, 59, 59),
            datetime.datetime(2021, 4, 1),
            datetime.datetime(2021, 6, 30, 23, 59, 59),
            datetime.datetime(2021, 7, 1),
            datetime.datetime(2021, 9, 30, 23, 59, 59),
            datetime.datetime(2021, 10, 1),
            datetime.datetime(2021, 12, 31, 23, 59, 59),
        ]
        check_quarterly = [
            datetime.datetime(2021, 3, 31, 23, 59, 59, 999999),
            datetime.datetime(2021, 6, 30, 23, 59, 59, 999999),
            datetime.datetime(2021, 9, 30, 23, 59, 59, 999999),
            datetime.datetime(2021, 12, 31, 23, 59, 59, 999999),
            datetime.datetime(2021, 3, 31, 23, 59, 59, 999999),
            datetime.datetime(2021, 3, 31, 23, 59, 59, 999999),
            datetime.datetime(2021, 6, 30, 23, 59, 59, 999999),
            datetime.datetime(2021, 6, 30, 23, 59, 59, 999999),
            datetime.datetime(2021, 9, 30, 23, 59, 59, 999999),
            datetime.datetime(2021, 9, 30, 23, 59, 59, 999999),
            datetime.datetime(2021, 12, 31, 23, 59, 59, 999999),
            datetime.datetime(2021, 12, 31, 23, 59, 59, 999999),
        ]
        for i in range(len(test_quarterly)):
            self.assertEqual(
                check_quarterly[i],
                self.env['to.base'].find_last_date_of_period(
                    'quarterly', test_quarterly[i]
                ),
                "\nTest case TC07.03 - Test quarterly",
            )

        # Test biannually
        test_biannually = [
            datetime.datetime(2021, 3, 4, 18, 0, 0),
            datetime.datetime(2021, 10, 25, 8, 1, 0),
            datetime.datetime(2021, 1, 1),
            datetime.datetime(2021, 6, 30, 23, 59, 59),
            datetime.datetime(2021, 7, 1),
            datetime.datetime(2021, 12, 31, 23, 59, 59),
        ]
        check_biannually = [
            datetime.datetime(2021, 6, 30, 23, 59, 59, 999999),
            datetime.datetime(2021, 12, 31, 23, 59, 59, 999999),
            datetime.datetime(2021, 6, 30, 23, 59, 59, 999999),
            datetime.datetime(2021, 6, 30, 23, 59, 59, 999999),
            datetime.datetime(2021, 12, 31, 23, 59, 59, 999999),
            datetime.datetime(2021, 12, 31, 23, 59, 59, 999999),
        ]
        for i in range(len(test_biannually)):
            self.assertEqual(
                check_biannually[i],
                self.env['to.base'].find_last_date_of_period(
                    'biannually', test_biannually[i]
                ),
                "\nTest case TC07.04 - Test biannually",
            )

    def test_085_find_last_date_of_period(self):
        # Test weekly
        test_weekly = [
            datetime.date(2021, 3, 4),
            datetime.date(2021, 3, 1),
            datetime.date(2021, 3, 7),
        ]
        check_weekly = [
            datetime.date(2021, 3, 7),
            datetime.date(2021, 3, 7),
            datetime.date(2021, 3, 7),
        ]
        for i in range(len(test_weekly)):
            self.assertEqual(
                check_weekly[i],
                self.env['to.base'].find_last_date_of_period(
                    'weekly', test_weekly[i]
                ),
                "\nTest case TC07.01 - Test weekly",
            )

        # Test monthly
        test_monthly = [
            datetime.date(2021, 3, 12),
            datetime.date(2021, 3, 1),
            datetime.date(2021, 3, 31),
            datetime.date(2021, 2, 1),
            datetime.date(2024, 2, 1),
            datetime.date(2024, 4, 1)
        ]
        check_monthly = [
            datetime.date(2021, 3, 31),
            datetime.date(2021, 3, 31),
            datetime.date(2021, 3, 31),
            datetime.date(2021, 2, 28),
            datetime.date(2024, 2, 29),
            datetime.date(2024, 4, 30)
        ]
        for i in range(len(test_monthly)):
            self.assertEqual(
                check_monthly[i],
                self.env['to.base'].find_last_date_of_period(
                    'monthly', test_monthly[i]
                ),
                "\nTest case TC07.02 - Test monthly",
            )

        # Test quarterly
        test_quarterly = [
            datetime.date(2021, 3, 4),
            datetime.date(2021, 5, 1),
            datetime.date(2021, 9, 25),
            datetime.date(2021, 11, 12),
            datetime.date(2021, 1, 1),
            datetime.date(2021, 3, 31),
            datetime.date(2021, 4, 1),
            datetime.date(2021, 6, 30),
            datetime.date(2021, 7, 1),
            datetime.date(2021, 9, 30),
            datetime.date(2021, 10, 1),
            datetime.date(2021, 12, 31),
        ]
        check_quarterly = [
            datetime.date(2021, 3, 31),
            datetime.date(2021, 6, 30),
            datetime.date(2021, 9, 30),
            datetime.date(2021, 12, 31),
            datetime.date(2021, 3, 31),
            datetime.date(2021, 3, 31),
            datetime.date(2021, 6, 30),
            datetime.date(2021, 6, 30),
            datetime.date(2021, 9, 30),
            datetime.date(2021, 9, 30),
            datetime.date(2021, 12, 31),
            datetime.date(2021, 12, 31),
        ]
        for i in range(len(test_quarterly)):
            self.assertEqual(
                check_quarterly[i],
                self.env['to.base'].find_last_date_of_period(
                    'quarterly', test_quarterly[i]
                ),
                "\nTest case TC07.03 - Test quarterly",
            )

        # Test biannually
        test_biannually = [
            datetime.date(2021, 3, 4),
            datetime.date(2021, 10, 25),
            datetime.date(2021, 1, 1),
            datetime.date(2021, 6, 30),
            datetime.date(2021, 7, 1),
            datetime.date(2021, 12, 31),
        ]
        check_biannually = [
            datetime.date(2021, 6, 30),
            datetime.date(2021, 12, 31),
            datetime.date(2021, 6, 30),
            datetime.date(2021, 6, 30),
            datetime.date(2021, 12, 31),
            datetime.date(2021, 12, 31),
        ]
        for i in range(len(test_biannually)):
            self.assertEqual(
                check_biannually[i],
                self.env['to.base'].find_last_date_of_period(
                    'biannually', test_biannually[i]
                ),
                "\nTest case TC07.04 - Test biannually",
            )

    def test_086_find_last_date_of_period(self):
        # Test date_is_start_date is True
        self.assertEqual(
            self.env['to.base'].find_last_date_of_period('weekly', datetime.date(2021, 11, 5),
                                                         date_is_start_date=True),
            datetime.date(2021, 11, 11))
        self.assertEqual(
            self.env['to.base'].find_last_date_of_period('monthly', datetime.date(2021, 11, 5),
                                                         date_is_start_date=True),
            datetime.date(2021, 12, 4))
        self.assertEqual(
            self.env['to.base'].find_last_date_of_period('quarterly', datetime.date(2021, 11, 5),
                                                         date_is_start_date=True),
            datetime.date(2022, 2, 4))
        self.assertEqual(
            self.env['to.base'].find_last_date_of_period('biannually', datetime.date(2021, 11, 5),
                                                         date_is_start_date=True),
            datetime.date(2022, 5, 4))
        self.assertEqual(
            self.env['to.base'].find_last_date_of_period('annually', datetime.date(2021, 11, 5),
                                                         date_is_start_date=True),
            datetime.date(2022, 11, 4))

    def test_090_period_iter_arg_type(self):
        with self.assertRaises(ValidationError):
            self.env['to.base'].period_iter('weekly', datetime.datetime(2021, 2, 1), datetime.date(2021, 3, 1))
        with self.assertRaises(ValidationError):
            self.env['to.base'].period_iter('weekly', datetime.date(2021, 2, 1), datetime.datetime(2021, 3, 1))
        with self.assertRaises(ValidationError):
            self.env['to.base'].period_iter('weekly', datetime.datetime(2021, 2, 1), datetime.datetime(2021, 3, 1), start_day_offset=-1)
        with self.assertRaises(ValidationError):
            self.env['to.base'].period_iter('week', datetime.datetime(2021, 2, 1), datetime.datetime(2021, 3, 1))

    # TC08
    def test_091_period_iter__datetime(self):
        # weekly
        test_vals = [
            {
                'period_name': 'weekly',
                'dt_start': datetime.datetime(2021, 2, 1),
                'dt_end': datetime.datetime(2021, 3, 1),
            }
        ]
        check_vals = [
            [
                datetime.datetime(2021, 2, 1),
                datetime.datetime(2021, 2, 7, 23, 59, 59, 999999),
                datetime.datetime(2021, 2, 14, 23, 59, 59, 999999),
                datetime.datetime(2021, 2, 21, 23, 59, 59, 999999),
                datetime.datetime(2021, 2, 28, 23, 59, 59, 999999),
                datetime.datetime(2021, 3, 1)
            ]
        ]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].period_iter(**test_vals[i]),
                check_vals[i],
                '\nTest case TC08',
            )

        # monthly
        test_vals = [
            {
                'period_name': 'monthly',
                'dt_start': datetime.datetime(2021, 1, 15),
                'dt_end': datetime.datetime(2021, 3, 1),
            }
        ]
        check_vals = [
            [
                datetime.datetime(2021, 1, 15),
                datetime.datetime(2021, 1, 31, 23, 59, 59, 999999),
                datetime.datetime(2021, 2, 28, 23, 59, 59, 999999),
                datetime.datetime(2021, 3, 1)
            ]
        ]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].period_iter(**test_vals[i]),
                check_vals[i],
                '\nTest case TC08',
            )

        # quarterly
        test_vals = [
            {
                'period_name': 'quarterly',
                'dt_start': datetime.datetime(2021, 1, 15),
                'dt_end': datetime.datetime(2021, 3, 1),
            },
            {
                'period_name': 'quarterly',
                'dt_start': datetime.datetime(2021, 1, 15),
                'dt_end': datetime.datetime(2021, 11, 29),
            }
        ]
        check_vals = [
            [
                datetime.datetime(2021, 1, 15),
                datetime.datetime(2021, 3, 1)
            ],
            [
                datetime.datetime(2021, 1, 15),
                datetime.datetime(2021, 3, 31, 23, 59, 59, 999999),
                datetime.datetime(2021, 6, 30, 23, 59, 59, 999999),
                datetime.datetime(2021, 9, 30, 23, 59, 59, 999999),
                datetime.datetime(2021, 11, 29)
            ],
        ]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].period_iter(**test_vals[i]),
                check_vals[i],
                '\nTest case TC08',
            )

        # biannually
        test_vals = [
            {
                'period_name': 'biannually',
                'dt_start': datetime.datetime(2021, 1, 15),
                'dt_end': datetime.datetime(2021, 3, 1),
            },
            {
                'period_name': 'biannually',
                'dt_start': datetime.datetime(2021, 1, 15),
                'dt_end': datetime.datetime(2021, 11, 29),
            }
        ]
        check_vals = [
            [
                datetime.datetime(2021, 1, 15),
                datetime.datetime(2021, 3, 1)
            ],
            [
                datetime.datetime(2021, 1, 15),
                datetime.datetime(2021, 6, 30, 23, 59, 59, 999999),
                datetime.datetime(2021, 11, 29)
            ],
        ]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].period_iter(**test_vals[i]),
                check_vals[i],
                '\nTest case TC08',
            )

        # annually
        test_vals = [
            {
                'period_name': 'annually',
                'dt_start': datetime.datetime(2021, 1, 15),
                'dt_end': datetime.datetime(2021, 3, 1),
            },
            {
                'period_name': 'annually',
                'dt_start': datetime.datetime(2021, 1, 15),
                'dt_end': datetime.datetime(2021, 11, 29),
            },
            {
                'period_name': 'annually',
                'dt_start': datetime.datetime(2021, 1, 15),
                'dt_end': datetime.datetime(2022, 11, 29),
            }
        ]
        check_vals = [
            [
                datetime.datetime(2021, 1, 15),
                datetime.datetime(2021, 3, 1)
            ],
            [
                datetime.datetime(2021, 1, 15),
                datetime.datetime(2021, 11, 29)
            ],
            [
                datetime.datetime(2021, 1, 15),
                datetime.datetime(2021, 12, 31, 23, 59, 59, 999999),
                datetime.datetime(2022, 11, 29)
            ],
        ]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].period_iter(**test_vals[i]),
                check_vals[i],
                '\nTest case TC08',
            )

    # TC08
    def test_092_period_iter__date(self):
        # weekly
        test_vals = [
            {
                'period_name': 'weekly',
                'dt_start': datetime.date(2021, 2, 1),
                'dt_end': datetime.date(2021, 3, 1),
            }
        ]
        check_vals = [
            [
                datetime.date(2021, 2, 1),
                datetime.date(2021, 2, 7),
                datetime.date(2021, 2, 14),
                datetime.date(2021, 2, 21),
                datetime.date(2021, 2, 28),
                datetime.date(2021, 3, 1)
            ]
        ]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].period_iter(**test_vals[i]),
                check_vals[i],
                '\nTest case TC08',
            )

        # monthly
        test_vals = [
            {
                'period_name': 'monthly',
                'dt_start': datetime.date(2021, 1, 15),
                'dt_end': datetime.date(2021, 3, 1),
            }
        ]
        check_vals = [
            [
                datetime.date(2021, 1, 15),
                datetime.date(2021, 1, 31),
                datetime.date(2021, 2, 28),
                datetime.date(2021, 3, 1)
            ]
        ]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].period_iter(**test_vals[i]),
                check_vals[i],
                '\nTest case TC08',
            )

        # quarterly
        test_vals = [
            {
                'period_name': 'quarterly',
                'dt_start': datetime.date(2021, 1, 15),
                'dt_end': datetime.date(2021, 3, 1),
            },
            {
                'period_name': 'quarterly',
                'dt_start': datetime.date(2021, 1, 15),
                'dt_end': datetime.date(2021, 11, 29),
            }
        ]
        check_vals = [
            [
                datetime.date(2021, 1, 15),
                datetime.date(2021, 3, 1)
            ],
            [
                datetime.date(2021, 1, 15),
                datetime.date(2021, 3, 31),
                datetime.date(2021, 6, 30),
                datetime.date(2021, 9, 30),
                datetime.date(2021, 11, 29)
            ],
        ]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].period_iter(**test_vals[i]),
                check_vals[i],
                '\nTest case TC08',
            )

        # biannually
        test_vals = [
            {
                'period_name': 'biannually',
                'dt_start': datetime.date(2021, 1, 15),
                'dt_end': datetime.date(2021, 3, 1),
            },
            {
                'period_name': 'biannually',
                'dt_start': datetime.date(2021, 1, 15),
                'dt_end': datetime.date(2021, 11, 29),
            }
        ]
        check_vals = [
            [
                datetime.date(2021, 1, 15),
                datetime.date(2021, 3, 1)
            ],
            [
                datetime.date(2021, 1, 15),
                datetime.date(2021, 6, 30),
                datetime.date(2021, 11, 29)
            ],
        ]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].period_iter(**test_vals[i]),
                check_vals[i],
                '\nTest case TC08',
            )

        # annually
        test_vals = [
            {
                'period_name': 'annually',
                'dt_start': datetime.date(2021, 1, 15),
                'dt_end': datetime.date(2021, 3, 1),
            },
            {
                'period_name': 'annually',
                'dt_start': datetime.date(2021, 1, 15),
                'dt_end': datetime.date(2021, 11, 29),
            },
            {
                'period_name': 'annually',
                'dt_start': datetime.date(2021, 1, 15),
                'dt_end': datetime.date(2022, 11, 29),
            }
        ]
        check_vals = [
            [
                datetime.date(2021, 1, 15),
                datetime.date(2021, 3, 1)
            ],
            [
                datetime.date(2021, 1, 15),
                datetime.date(2021, 11, 29)
            ],
            [
                datetime.date(2021, 1, 15),
                datetime.date(2021, 12, 31),
                datetime.date(2022, 11, 29)
            ],
        ]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].period_iter(**test_vals[i]),
                check_vals[i],
                '\nTest case TC08',
            )

    # TC08
    def test_095_period_iter__start_day_offset(self):
        # weekly
        test_vals = [
            {
                'period_name': 'weekly',
                'dt_start': datetime.datetime(2021, 2, 1),
                'dt_end': datetime.datetime(2021, 3, 1),
                'start_day_offset': 2,
            }
        ]
        check_vals = [
            [
                datetime.datetime(2021, 2, 1),
                datetime.datetime(2021, 2, 2, 23, 59, 59, 999999),
                datetime.datetime(2021, 2, 9, 23, 59, 59, 999999),
                datetime.datetime(2021, 2, 16, 23, 59, 59, 999999),
                datetime.datetime(2021, 2, 23, 23, 59, 59, 999999),
                datetime.datetime(2021, 3, 1)
            ]
        ]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].period_iter(**test_vals[i]),
                check_vals[i],
                '\nTest case TC08',
            )

        # monthly
        test_vals = [
            {
                'period_name': 'monthly',
                'dt_start': datetime.datetime(2021, 1, 15),
                'dt_end': datetime.datetime(2021, 3, 1),
                'start_day_offset': 2,
            }
        ]
        check_vals = [
            [
                datetime.datetime(2021, 1, 15),
                datetime.datetime(2021, 2, 2, 23, 59, 59, 999999),
                datetime.datetime(2021, 3, 1)
            ]
        ]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].period_iter(**test_vals[i]),
                check_vals[i],
                '\nTest case TC08',
            )

        # quarterly
        test_vals = [
            {
                'period_name': 'quarterly',
                'dt_start': datetime.datetime(2021, 1, 15),
                'dt_end': datetime.datetime(2021, 3, 1),
                'start_day_offset': 2,
            },
            {
                'period_name': 'quarterly',
                'dt_start': datetime.datetime(2021, 1, 15),
                'dt_end': datetime.datetime(2021, 11, 29),
                'start_day_offset': 2,
            }
        ]
        check_vals = [
            [
                datetime.datetime(2021, 1, 15),
                datetime.datetime(2021, 3, 1)
            ],
            [
                datetime.datetime(2021, 1, 15),
                datetime.datetime(2021, 4, 2, 23, 59, 59, 999999),
                datetime.datetime(2021, 7, 2, 23, 59, 59, 999999),
                datetime.datetime(2021, 10, 2, 23, 59, 59, 999999),
                datetime.datetime(2021, 11, 29)
            ],
        ]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].period_iter(**test_vals[i]),
                check_vals[i],
                '\nTest case TC08',
            )

        # biannually
        test_vals = [
            {
                'period_name': 'biannually',
                'dt_start': datetime.datetime(2021, 1, 15),
                'dt_end': datetime.datetime(2021, 3, 1),
                'start_day_offset': 2,
            },
            {
                'period_name': 'biannually',
                'dt_start': datetime.datetime(2021, 1, 15),
                'dt_end': datetime.datetime(2021, 11, 29),
                'start_day_offset': 2,
            }
        ]
        check_vals = [
            [
                datetime.datetime(2021, 1, 15),
                datetime.datetime(2021, 3, 1)
            ],
            [
                datetime.datetime(2021, 1, 15),
                datetime.datetime(2021, 7, 2, 23, 59, 59, 999999),
                datetime.datetime(2021, 11, 29)
            ],
        ]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].period_iter(**test_vals[i]),
                check_vals[i],
                '\nTest case TC08',
            )

        # annually
        test_vals = [
            {
                'period_name': 'annually',
                'dt_start': datetime.datetime(2021, 1, 15),
                'dt_end': datetime.datetime(2021, 3, 1),
                'start_day_offset': 2,
            },
            {
                'period_name': 'annually',
                'dt_start': datetime.datetime(2021, 1, 15),
                'dt_end': datetime.datetime(2021, 11, 29),
                'start_day_offset': 2,
            },
            {
                'period_name': 'annually',
                'dt_start': datetime.datetime(2021, 1, 15),
                'dt_end': datetime.datetime(2022, 11, 29),
                'start_day_offset': 2,
            }
        ]
        check_vals = [
            [
                datetime.datetime(2021, 1, 15),
                datetime.datetime(2021, 3, 1)
            ],
            [
                datetime.datetime(2021, 1, 15),
                datetime.datetime(2021, 11, 29)
            ],
            [
                datetime.datetime(2021, 1, 15),
                datetime.datetime(2022, 1, 2, 23, 59, 59, 999999),
                datetime.datetime(2022, 11, 29)
            ],
        ]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].period_iter(**test_vals[i]),
                check_vals[i],
                '\nTest case TC08',
            )

    # TC09
    def test_100_get_days_of_month_from_date(self):
        test_vals = [
            datetime.datetime(2021, 3, 3),
            datetime.datetime(2021, 2, 15),
        ]
        check_vals = [31, 28]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].get_days_of_month_from_date(test_vals[i]),
                check_vals[i],
                "\nTest case TC09",
            )

    # TC10
    def test_110_get_day_of_year_from_date(self):
        test_vals = [
            datetime.date(2021, 1, 21),
            datetime.date(2021, 2, 21),
        ]
        check_vals = [21, 52]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].get_day_of_year_from_date(date=test_vals[i]),
                check_vals[i],
                "\nTest case TC10",
            )

    # TC11
    def test_120_get_days_between_dates(self):
        test_vals = [
            (datetime.datetime(2021, 1, 12), datetime.datetime(2021, 2, 21)),
            (datetime.datetime(2021, 2, 1), datetime.datetime(2021, 3, 1)),
            (datetime.datetime(2021, 1, 1), datetime.datetime(2021, 2, 1)),
            (datetime.datetime(2021, 1, 1), datetime.datetime(2022, 1, 1)),
            (datetime.datetime(2024, 1, 1), datetime.datetime(2025, 1, 1))
        ]
        check_vals = [40, 28, 31, 365, 366]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].get_days_between_dates(*test_vals[i]),
                check_vals[i],
                "\nTest case TC11",
            )

    # TC12
    def test_130_get_months_between_dates(self):
        test_vals = [
            (datetime.datetime(2021, 1, 12), datetime.datetime(2021, 2, 21)),
            (datetime.datetime(2021, 1, 12), datetime.datetime(2021, 1, 15)),
            (datetime.datetime(2021, 2, 1), datetime.datetime(2021, 3, 1)),
            (datetime.datetime(2021, 1, 1), datetime.datetime(2021, 2, 15)),
            (datetime.datetime(2021, 3, 1), datetime.datetime(2021, 5, 1))
        ]
        check_vals = [1.359447004608295, 0.0967741935483871, 1.0, 1.5, 2.0]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].get_months_between_dates(*test_vals[i]),
                check_vals[i],
                "\nTest case TC12",
            )

        test_vals = [
            (datetime.date(2021, 1, 12), datetime.date(2021, 2, 21)),
            (datetime.date(2021, 1, 12), datetime.date(2021, 1, 15)),
            (datetime.date(2021, 2, 1), datetime.date(2021, 3, 1)),
            (datetime.date(2021, 1, 1), datetime.date(2021, 2, 15)),
            (datetime.date(2021, 3, 1), datetime.date(2021, 5, 1))
        ]
        check_vals = [1.359447004608295, 0.0967741935483871, 1.0, 1.5, 2.0]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].get_months_between_dates(*test_vals[i]),
                check_vals[i],
                "\nTest case TC12",
            )

    # TC13
    def test_140_get_weekdays_for_period(self):
        test_vals = [
            (datetime.datetime(2021, 3, 2), datetime.datetime(2021, 3, 5)),
        ]
        check_vals = [
            {
                1: datetime.date(2021, 3, 2),
                2: datetime.date(2021, 3, 3),
                3: datetime.date(2021, 3, 4),
                4: datetime.date(2021, 3, 5),
            }
        ]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].get_weekdays_for_period(*test_vals[i]),
                check_vals[i],
                "\nTest case TC13",
            )

        test_invalid_vals = (
            datetime.datetime(2021, 3, 2),
            datetime.datetime(2021, 3, 10)
        )
        with self.assertRaises(ValidationError):
            self.env['to.base'].get_weekdays_for_period(*test_invalid_vals)

    # TC14
    def test_150_next_weekday(self):
        test_vals = [
            {'date': datetime.datetime(2021, 3, 2), 'weekday': None},
            {'date': datetime.date(2021, 3, 4), 'weekday': None},
            {'date': datetime.datetime(2021, 3, 1), 'weekday': 2},
            {'date': datetime.datetime(2021, 3, 7), 'weekday': 3},
            {'date': datetime.datetime(2021, 8, 24), 'weekday': 0},
            {'date': datetime.datetime(2021, 8, 24), 'weekday': 1},
            {'date': datetime.datetime(2021, 8, 24), 'weekday': 2},
            {'date': datetime.datetime(2021, 8, 24), 'weekday': 3},
            {'date': datetime.datetime(2021, 8, 24), 'weekday': 4},
            {'date': datetime.datetime(2021, 8, 24), 'weekday': 5},
            {'date': datetime.datetime(2021, 8, 24), 'weekday': 6},
            {'date': datetime.datetime(2021, 8, 24), 'weekday': None},
        ]
        check_vals = [
            datetime.datetime(2021, 3, 9),
            datetime.date(2021, 3, 11),
            datetime.datetime(2021, 3, 10),
            datetime.datetime(2021, 3, 11),
            datetime.datetime(2021, 8, 30),
            datetime.datetime(2021, 8, 31),
            datetime.datetime(2021, 9, 1),
            datetime.datetime(2021, 9, 2),
            datetime.datetime(2021, 9, 3),
            datetime.datetime(2021, 9, 4),
            datetime.datetime(2021, 9, 5),
            datetime.datetime(2021, 8, 31),
        ]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].next_weekday(**test_vals[i]),
                check_vals[i],
                "\nTest case TC14",
            )

    # TC15
    def test_160_split_date(self):
        test_vals = [
            datetime.date(2020, 12, 24),
            datetime.date(2021, 3, 1)
        ]
        check_vals = [(2020, 12, 24), (2021, 3, 1)]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].split_date(test_vals[i]),
                check_vals[i],
                '\nTest case TC15',
            )

    # TC16
    def test_170_hours_time_string(self):
        test_vals = [2.0, 1.5, 1.333333, 20, 30.5]
        check_vals = ['02:00', '01:30', '01:20', '20:00', '30:30']
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].hours_time_string(test_vals[i]),
                check_vals[i],
                '\nTest case TC16',
            )

    # TC18
    def test_180_zip_dirs(self):
        pass

    # TC19
    def test_190_guess_lang(self):
        pass

    # TC20
    def test_200_strip_accents(self):
        test_vals = [
            'Đây là một câu tiếng việt có dấu.',
            'Đâylàmộtcâutiếngviệtcódấu.',
            'á à ả ã ạ ă ắ ằ ẳ ẵ ặ â ấ ầ ẩ ẫ ậ',
            'í ì ỉ ĩ ị',
            'ú ù ủ ũ ụ ư ứ ừ ử ữ ự',
            'é è ẻ ẽ ẹ ê ế ề ể ễ ệ',
            'ó ò ỏ õ ọ ô ố ồ ổ ỗ ộ ơ ớ ờ ở ỡ ợ',
            'ý ỳ ỷ ỹ ỵ',
            'đ',
            'Á À Ả Ã Ạ Ă Ắ Ằ Ẳ Ẵ Ặ Â Ấ Ầ Ẩ Ẫ Ậ',
            'Í Ì Ỉ Ĩ Ị',
            'Ú Ù Ủ Ũ Ụ Ư Ứ Ừ Ử Ữ Ự',
            'É È Ẻ Ẽ Ẹ Ê Ế Ề Ể Ễ Ệ',
            'Ó Ò Ỏ Õ Ọ Ô Ố Ồ Ổ Ỗ Ộ Ơ Ớ Ờ Ở Ỡ Ợ',
            'Ý Ỳ Ỷ Ỹ Ỵ',
            'Đ',
        ]
        check_vals = [
            'Day la mot cau tieng viet co dau.',
            'Daylamotcautiengvietcodau.',
            'a a a a a a a a a a a a a a a a a',
            'i i i i i',
            'u u u u u u u u u u u',
            'e e e e e e e e e e e',
            'o o o o o o o o o o o o o o o o o',
            'y y y y y',
            'd',
            'A A A A A A A A A A A A A A A A A',
            'I I I I I',
            'U U U U U U U U U U U',
            'E E E E E E E E E E E',
            'O O O O O O O O O O O O O O O O O',
            'Y Y Y Y Y',
            'D',
        ]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].strip_accents(test_vals[i]),
                check_vals[i],
                '\nTest case TC20',
            )

    # TC21
    def test_210_sum_digits(self):
        test_vals = (
            {'n': 178, 'number_of_digit_return': 2},
            {'n': 178, 'number_of_digit_return': 1},
        )
        check_vals = [16, 7]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].sum_digits(**test_vals[i]),
                check_vals[i],
                '\nTest case TC21',
            )

    # TC22
    def test_220_find_nearest_lucky_number(self):
        test_vals = (
            {'n': 12345, 'rounding': 2, 'round_up': False},
            {'n': 12345, 'rounding': 0, 'round_up': True},
        )
        check_vals = (11700, 12348)

        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].find_nearest_lucky_number(**test_vals[i]),
                check_vals[i],
                '\nTest case TC22',
            )

    def test_310_years_between_dates(self):
        test_data = [
            # (dt_from, dt_to, years)
            (datetime.date(2019, 2, 28), datetime.date(2020, 2, 29), 1.002739726),  # 1 year 1 days | year 365 days
            (datetime.date(2019, 2, 28), datetime.date(2020, 2, 28), 1.0),  # 1 year | year 365 days
            (datetime.date(2019, 2, 27), datetime.date(2020, 2, 27), 1.0),  # 1 year | year 365 days
            (datetime.date(2019, 2, 27), datetime.date(2020, 2, 28), 1.002739726),  # 1 year 1 days | year 365 days
            (datetime.date(2019, 2, 28), datetime.date(2020, 3, 1), 1.005464481),  # 1 years 2 days | year 366 days
            (datetime.date(2019, 3, 1), datetime.date(2020, 3, 1), 1.0),  # 1 years 0 days | year 366 days
            (datetime.date(2019, 3, 1), datetime.date(2020, 3, 2), 1.002732240),  # 1 years 1 days | year 366 days
            (datetime.date(2020, 3, 1), datetime.date(2020, 3, 2), 0.002732240),  # 0 years 1 days | year 366 days
            (datetime.date(2018, 2, 28), datetime.date(2020, 2, 29), 2.002739726),  # 2 year 1 days | year 365 days
            (datetime.date(2015, 2, 28), datetime.date(2020, 2, 29), 5.002739726),  # 5 year 1 days | year 365 days
            ]
        for dt_from, dt_to, years in test_data:
            self.assertAlmostEqual(
                self.env['to.base'].get_number_of_years_between_dates(dt_from, dt_to),
                years,
                9,
                "Number of years from %s to %s should be %s" % (dt_from, dt_to, years)
                )

    def test_320_years_between_dates(self):
        test_data = [
            # (dt_from, dt_to, years)
            (datetime.datetime(2019, 2, 27), datetime.datetime(2020, 2, 27, 0, 0, 0, 0), 1.0),  # 1 year | year 365 days
            (datetime.datetime(2019, 2, 28), datetime.datetime(2020, 2, 28, 0, 0, 0, 0), 1.0),  # 1 year | year 365 days
            (datetime.datetime(2019, 2, 28), datetime.datetime(2020, 2, 28, 23, 59, 59, 999999), 1.002739726),  # 1 year ~ 1 day | year 365 days
            (datetime.datetime(2019, 2, 28), datetime.datetime(2020, 2, 29, 0, 0, 0, 0), 1.002739726),  # 1 year 1 day | year 365 days
            (datetime.datetime(2019, 2, 28), datetime.datetime(2020, 2, 29, 23, 59, 59, 999999), 1.005464481),  # 1 year ~2 days | year 366 days
            (datetime.datetime(2019, 2, 28), datetime.datetime(2020, 3, 1, 23, 59, 59, 999999), 1.008196721),  # 1 years ~3 days | year 366 days
            (datetime.datetime(2019, 3, 1), datetime.datetime(2020, 3, 1, 23, 59, 59, 999999), 1.002732240),  # 1 years ~1 days | year 366 days
            (datetime.datetime(2019, 3, 1), datetime.datetime(2020, 3, 2, 23, 59, 59, 999999), 1.005464481),  # 1 years 2 days | year 366 days
            (datetime.datetime(2020, 3, 1), datetime.datetime(2020, 3, 2, 23, 59, 59, 999999), 0.005464481),  # 0 years 2 days | year 366 days
            (datetime.datetime(2015, 3, 1), datetime.datetime(2020, 3, 2, 23, 59, 59, 999999), 5.005464481),  # 5 years 2 days | year 366 days
            ]
        for dt_from, dt_to, years in test_data:
            self.assertAlmostEqual(
                self.env['to.base'].get_number_of_years_between_dates(dt_from, dt_to),
                years,
                9,
                "Number of years from %s to %s should be %s" % (dt_from, dt_to, years)
                )

    def test_get_ratio_between_periods(self):
        test_vals = [
            ('hourly', 'hourly'),
            ('annually', 'monthly'),
            ('monthly', 'annually'),
            ('annually', 'monthly', datetime.datetime(2021, 2, 1)),
            ('annually', 'weekly', datetime.datetime(2022, 2, 9)),
            ('monthly', 'daily', datetime.datetime(2024, 2, 9)),
            ('monthly', 'weekly', datetime.datetime(2024, 2, 9)),
            ('monthly', 'hourly', datetime.datetime(2024, 2, 9)),
            ('hourly', 'monthly', datetime.datetime(2024, 2, 9)),
            ('annually', 'weekly', datetime.datetime(2024, 2, 9)),
        ]
        check_vals = [1, 12, 1/12, 12, 365/7, 29, 29/7, 29*24, 1/(29*24), 366/7]
        for i in range(len(test_vals)):
            self.assertEqual(
                self.env['to.base'].get_ratio_between_periods(*test_vals[i]),
                check_vals[i]
            )

    def test_calculate_weights(self):
        list_val_1 = [2, 4, 6, 8]
        check_val_1 = [0.10, 0.20, 0.30, 0.40]
        self.assertEqual(
            self.env['to.base'].calculate_weights(*list_val_1),
            check_val_1
        )

        # "Test if the sum of the weights is 100% with odd % numbers"
        list_val_2 = [0, 0, 0, 0, 0, 0]
        self.assertEqual(sum(self.env['to.base'].calculate_weights(*list_val_2)), 1)

    def test_330_break_timerange_for_midnight(self):
        test_data = [
            # (dt_start, dt_end, result)
            (datetime.datetime(2019, 2, 27, 8, 0), datetime.datetime(2019, 2, 28, 8, 0),
                [datetime.datetime(2019, 2, 27, 8, 0), datetime.datetime(2019, 2, 28, 0, 0), datetime.datetime(2019, 2, 28, 8, 0)]),
            (datetime.datetime(2019, 2, 27, 0, 0), datetime.datetime(2019, 2, 28, 8, 0),
                [datetime.datetime(2019, 2, 27, 0, 0), datetime.datetime(2019, 2, 28, 0, 0), datetime.datetime(2019, 2, 28, 8, 0)]),
            (datetime.datetime(2019, 2, 27, 8, 0), datetime.datetime(2019, 2, 28, 0, 0),
                [datetime.datetime(2019, 2, 27, 8, 0), datetime.datetime(2019, 2, 28, 0, 0)]),
            (datetime.datetime(2019, 2, 27, 0, 0), datetime.datetime(2019, 2, 28, 0, 0),
                [datetime.datetime(2019, 2, 27, 0, 0), datetime.datetime(2019, 2, 28, 0, 0)]),
            ]
        for dt_start, dt_end, result in test_data:
            self.assertEqual(
                self.env['to.base'].break_timerange_for_midnight(dt_start, dt_end),
                result,
                )
